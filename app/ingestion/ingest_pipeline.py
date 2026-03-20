import logging
import shutil
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.ingestion.local_loader import load_local

logger = logging.getLogger(__name__)

VECTOR_DB_DIR = str(Path(__file__).resolve().parent.parent.parent / "vector_db")
COLLECTION_NAME = "lipun_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


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
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(documents)
    logger.info("Total chunks after splitting: %d", len(chunks))

    # 3. Wipe entire vector_db directory to rebuild fresh (avoids orphaned segment folders)
    vector_db_path = Path(VECTOR_DB_DIR)
    if vector_db_path.exists():
        shutil.rmtree(vector_db_path)
        logger.info("Deleted vector_db directory for clean rebuild")

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
