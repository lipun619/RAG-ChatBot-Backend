from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

VECTOR_DB_DIR = str(Path(__file__).resolve().parent.parent.parent / "vector_db")
COLLECTION_NAME = "lipun_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_retriever = None


def get_retriever():
    """Load the persisted ChromaDB and return a LangChain retriever (cached)."""
    global _retriever
    if _retriever is not None:
        return _retriever

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectorstore = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )

    _retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    return _retriever
