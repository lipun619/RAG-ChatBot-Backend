import logging
import os
import shutil
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.ingestion.local_loader import load_local

logger = logging.getLogger(__name__)

VECTOR_DB_DIR = str(Path(__file__).resolve().parent.parent.parent / "vector_db")
COLLECTION_NAME = "lipun_knowledge"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-MiniLM-L3-v2"


def run_ingestion() -> None:
    """Run the ingestion pipeline: load local docs → chunk → embed → store."""
    logger.info("Starting ingestion pipeline...")

    # 1. Collect documents from local data
    documents = load_local()

    if not documents:
        logger.warning("No documents collected — skipping vector DB update")
        return

    logger.info("Total documents collected: %d", len(documents))

    # 2. Chunk documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
    )
    chunks = text_splitter.split_documents(documents)
    logger.info("Total chunks after splitting: %d", len(chunks))

    # 3. Wipe entire vector_db directory to rebuild fresh (avoids orphaned segment folders)
    vector_db_path = Path(VECTOR_DB_DIR)
    if vector_db_path.exists() and vector_db_path.is_dir():
        shutil.rmtree(vector_db_path)
        logger.info("Deleted vector_db directory for clean rebuild")
    elif vector_db_path.exists() and vector_db_path.is_file():
        vector_db_path.unlink()
        logger.info("Deleted stale vector_db file for clean rebuild")

    vector_db_path.mkdir(parents=True, exist_ok=True)
    os.chmod(vector_db_path, 0o755)
    logger.info("Ensured vector_db directory exists and is writable: %s", vector_db_path)

    # 4. Generate embeddings and store in ChromaDB
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR,
        collection_name=COLLECTION_NAME,
    )

    logger.info(
        "Ingestion complete — %d chunks stored in collection '%s'",
        len(chunks),
        COLLECTION_NAME,
    )
