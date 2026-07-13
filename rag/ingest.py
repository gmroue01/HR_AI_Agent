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


def chunk_test(text: str, chunk_size: int = 500, overlap: int = 500) -> list[str]:
    """Fixed-size character chunking with overlap"""

    chunks = []
    start = 0
    while start < len(text):
        print(f"It remains {len(text) - start}.")
        end = start + chunk_size
        chunks.append(text[start:end])
        start = chunk_size - overlap
    return chunks


if __name__ == "__main__":
    print(extract_pdf_text("./data/hr_policies/expense_policy.pdf"))
