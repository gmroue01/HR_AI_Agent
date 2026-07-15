from rag.chroma_client import get_collection


def search_hr_documents_logic(query: str, n_results: int = 3) -> list[dict]:
    """
        Implements the similarity search and retrieval logic.

        Args:
            query: The user query used for the retrieval.
            n_results: The number of relevant documents to return.

        Returns:
            A dictionary containing the relevant text and source metadata for each retrieved document.
    """

    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=n_results)

    return [
        {"text": doc, "source": meta.get("source")}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]
