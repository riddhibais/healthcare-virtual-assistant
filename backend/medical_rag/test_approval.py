
from backend.medical_rag.retriever import search_knowledge


def test_pending_document_is_not_retrieved():
    results = search_knowledge(
        "healthcare assistant evidence reviewed sources",
        k=10,
    )

    assert all(
        result["review_status"] == "approved"
        for result in results
    ), "Retriever returned an unapproved document"

    print("PASS: No unapproved documents were returned.")
    print(f"Approved results returned: {len(results)}")


if __name__ == "__main__":
    test_pending_document_is_not_retrieved()
