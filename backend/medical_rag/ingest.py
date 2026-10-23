
import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "backend" / "medical_data" / "raw"
REGISTRY_PATH = PROJECT_ROOT / "backend" / "medical_data" / "source_registry.json"
DB_DIR = PROJECT_ROOT / "backend" / "chroma_db"

COLLECTION_NAME = "medical_knowledge"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_registry():
    if not REGISTRY_PATH.is_file():
        raise FileNotFoundError(
            f"Approval registry not found: {REGISTRY_PATH}"
        )

    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    if not isinstance(data, dict) or not isinstance(
        data.get("documents"), list
    ):
        raise ValueError("Registry must contain a 'documents' list.")

    registry = {}

    for entry in data["documents"]:
        if not isinstance(entry, dict):
            raise ValueError("Every registry document must be a JSON object.")

        name = entry.get("file_name", "")

        if (
            not isinstance(name, str)
            or not name
            or Path(name).name != name
            or not name.endswith(".txt")
        ):
            raise ValueError(f"Invalid registry file_name: {name!r}")

        if name in registry:
            raise ValueError(f"Duplicate registry entry: {name}")

        status = entry.get("review_status")
        if status not in {"pending", "approved", "rejected"}:
            raise ValueError(
                f"Invalid review_status for {name}: {status!r}"
            )

        registry[name] = entry

    return registry


def validate_approval(entry, file_path):
    required = [
        "title",
        "publisher",
        "source_url",
        "version",
        "last_reviewed",
        "reviewed_by",
        "review_notes",
    ]

    missing = [
        key
        for key in required
        if not isinstance(entry.get(key), str) or not entry[key].strip()
    ]

    if missing:
        raise ValueError(
            f"{file_path.name}: approved record is missing: "
            + ", ".join(missing)
        )

    parsed_url = urlparse(entry["source_url"])
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError(
            f"{file_path.name}: approved sources require a valid HTTPS URL."
        )

    try:
        reviewed_date = date.fromisoformat(entry["last_reviewed"])
    except ValueError as exc:
        raise ValueError(
            f"{file_path.name}: last_reviewed must use YYYY-MM-DD."
        ) from exc

    if reviewed_date > date.today():
        raise ValueError(
            f"{file_path.name}: last_reviewed cannot be in the future."
        )


def prepare_documents(registry):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
    )

    documents = []
    ids = []
    approved_files = 0

    for file_name, entry in registry.items():
        status = entry["review_status"]

        if status != "approved":
            print(f"Skipping {file_name}: status={status}")
            continue

        file_path = DATA_DIR / file_name

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Approved document is missing: {file_path}"
            )

        validate_approval(entry, file_path)

        content = file_path.read_text(encoding="utf-8-sig").strip()
        if not content:
            raise ValueError(f"Approved document is empty: {file_name}")

        approved_files += 1
        content_hash = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        chunks = splitter.split_text(content)

        if not chunks:
            raise ValueError(
                f"Approved document produced no chunks: {file_name}"
            )

        for index, chunk in enumerate(chunks):
            metadata = {
                "source": file_name,
                "title": entry["title"],
                "publisher": entry["publisher"],
                "source_url": entry["source_url"],
                "version": entry["version"],
                "review_status": "approved",
                "last_reviewed": entry["last_reviewed"],
                "reviewed_by": entry["reviewed_by"],
                "review_notes": entry["review_notes"],
                "content_sha256": content_hash,
                "chunk": index,
            }

            documents.append(
                Document(page_content=chunk, metadata=metadata)
            )
            ids.append(
                f"{file_name}::{content_hash[:16]}::{index}"
            )

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate chunk IDs generated; refusing to continue.")

    return documents, ids, approved_files


def ingest_documents(apply_changes=False, allow_empty=False):
    registry = load_registry()
    documents, ids, approved_files = prepare_documents(registry)

    print(f"Approved source files validated: {approved_files}")
    print(f"Chunks prepared: {len(documents)}")
    print(f"Database location: {DB_DIR}")

    if not apply_changes:
        print("DRY RUN: no database changes were made.")
        print("Review the output before running with --apply.")
        return

    if not documents and not allow_empty:
        raise RuntimeError(
            "Refusing to clear the index because there are zero approved "
            "chunks. Approve and validate a real source first. If you "
            "intentionally want an empty index, use --apply --allow-empty."
        )

    DB_DIR.mkdir(parents=True, exist_ok=True)

    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
    )

    # All validation finishes before the existing index is modified.
    existing = vector_store.get()
    existing_ids = existing.get("ids", [])

    if existing_ids:
        vector_store.delete(ids=existing_ids)
        print(f"Removed previous chunks: {len(existing_ids)}")

    if documents:
        vector_store.add_documents(documents=documents, ids=ids)

    print(f"Approved documents indexed: {len(documents)} chunks")
    print("Ingestion finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate and index approved medical reference documents."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually modify the Chroma index. Default is dry-run only.",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Explicitly permit clearing the index when no approved chunks exist.",
    )
    args = parser.parse_args()

    if args.allow_empty and not args.apply:
        parser.error("--allow-empty requires --apply.")

    ingest_documents(
        apply_changes=args.apply,
        allow_empty=args.allow_empty,
    )
