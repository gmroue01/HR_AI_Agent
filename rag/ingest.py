import os
from pathlib import Path
from rag.chroma_client import get_collection
import pdfplumber


def extract_pdf_text(file_path: str) -> str:
    """ Extract text from pdf"""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def chunk_test(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Fixed-size character chunking with overlap

    Args :

        text : Text shall be chunked.
        chunk_size : the number of characters per chunk.
        overlap : the number of characters carried over from the previous chunk.

    Return:
        chunks : the set of individual chunk.


    """

    chunks = []
    start = 0
    while start < len(text):
        print(f"It remains {len(text) - start}.")
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def ingest_documents(folder_path: str):
    collection = get_collection()
    folder = Path(folder_path)

    for file_path in list(folder.glob("*.txt")) + list(folder.glob("*.pdf")):

        if file_path.suffix == ".pdf":
            text = extract_pdf_text(file_path)
        else:
            text = file_path.read_text(encoding="utf-8")

        chunks = chunk_test(text)

        collection.add(
            documents=chunks,
            ids=[f"{file_path.stem}_{i}" for i in range(len(chunks))],
            metadatas=[{"source": file_path.name, "category": "hr_policy"}
                       for _ in chunks]
        )
        print(f"Ingested : {file_path.name} ({len(chunks)}) chunks")


if __name__ == "__main__":
    ingest_documents("data/hr_policies/")
