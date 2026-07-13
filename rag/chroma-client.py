import chromadb
from pathlib import Path


# To save all related to ChromaDb in the Disk
CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"
chroma_client = chromadb(path=str(CHROMA_PATH))


client = chromadb.PersistentClient(path=str(CHROMA_PATH))


def get_collection(name: str = "hr_policies"):
    return client.get_or_create_collection(name=name)
