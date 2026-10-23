
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_DIR = PROJECT_ROOT / "backend" / "chroma_db"

COLLECTION_NAME = "medical_knowledge"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_vector_store():
    if not DB_DIR.exists():
        raise FileNotFoundError(
            "Vector database not found. Run ingest.py first."
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME
    )

    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
        embedding_function=embeddings,
    )


def search_knowledge(query: str, k: int = 3):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("k must be a positive integer.")

    vector_store = get_vector_store()

    results = vector_store.similarity_search(
        query=query.strip(),
        k=k,
        filter={"review_status": "approved"},
    )

    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Unknown"),
            "title": doc.metadata.get("title", ""),
            "publisher": doc.metadata.get("publisher", ""),
            "source_url": doc.metadata.get("source_url", ""),
            "version": doc.metadata.get("version", ""),
            "review_status": doc.metadata.get(
                "review_status", "unknown"
            ),
            "last_reviewed": doc.metadata.get("last_reviewed", ""),
            "reviewed_by": doc.metadata.get("reviewed_by", ""),
            "content_sha256": doc.metadata.get("content_sha256", ""),
            "chunk": doc.metadata.get("chunk", -1),
        }
        for doc in results
        if doc.metadata.get("review_status") == "approved"
    ]


if __name__ == "__main__":
    results = search_knowledge(
        "What information is available about first aid?"
    )

    if not results:
        print("No approved source matched this query.")
    else:
        for result in results:
            print("\nTitle:", result["title"])
            print("Publisher:", result["publisher"])
            print("Source URL:", result["source_url"])
            print("Review date:", result["last_reviewed"])
            print("Review status:", result["review_status"])
            print("Content:", result["content"])
