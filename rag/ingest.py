import os
from pathlib import Path
from rag.chroma_client import get_collection
import pdfplumber
import openpyxl


def extract_pdf_text(file_path: str) -> str:
    """ Extract text from pdf

    Arg:

        file_path : the path of PDF file.

    Return:

        text : the full plain-text.

    """
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_excel_text(file_path: str) -> str:
    """
        Extract the text from a excel file/

    Arg:

        file_path : the path of PDF file.

    Return:

        text : the full plain-text.


    """

    wb = openpyxl.load_workbook(file_path, data_only=True)
    text = ""

    for sheet in wb.worksheets:
        text += f"\n--sheet : {sheet.title}--\n"
        headers = [cell.value for cell in sheet[1]]

        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_text = ", ".join(
                f"{headers[i]}: {value}" for i, value in enumerate(row) if value is not None
            )
            if row_text:
                text += row_text + "\n"

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


def ingest_documents(folder_paths: str):
    """
        Apply the chunk method and the embedding to every document.
        The embedding is operated by the default embedding function of ChromaDB (collection).

        Add the document to the on-disk vector database.

        This function accepts plain-text file, pdf file and xlsx file.

        Arg :

            folder_paths : a list of folder_path.

        Return :
            None

    """

    collection = get_collection()
    all_files = []

    for folder_path in folder_paths:
        folder = Path(folder_path)
        all_files += (list(folder.glob("*.txt")) +
                      list(folder.glob("*.pdf")) + list(folder.glob("*.xlsx")))

    for file_path in all_files:

        if file_path.suffix == ".pdf":
            text = extract_pdf_text(file_path)

        elif file_path.suffix == ".xlsx":
            text = extract_excel_text(file_path)
            collection.add(documents=[text], ids=[file_path.stem], metadatas=[
                           {"source": file_path.name, "category": "hr_policy"}])
            print(f"Ingested (no chunking ): {file_path.name}")
            continue
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
    ingest_documents(["data/hr_policies", "data/salary_grids"])
