import logging
import time
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

logger = logging.getLogger(__name__)

VECTOR_DB_DIR = str(Path(__file__).resolve().parent.parent.parent / "vector_db")
COLLECTION_NAME = "lipun_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_retriever = None


def get_retriever():
    """Load the persisted ChromaDB and return a LangChain retriever (cached)."""
    global _retriever
    if _retriever is not None:
        logger.info("Using cached retriever (no model download)")
        return _retriever

    logger.info("Initializing retriever — loading embedding model '%s'...", EMBEDDING_MODEL)
    start = time.time()

    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    except (ImportError, OSError) as exc:
        raise RuntimeError(
            "Failed to initialize HuggingFaceEmbeddings because SentenceTransformers/Torch "
            "could not be loaded. On macOS Apple Silicon, install a compatible PyTorch wheel using:\n"
            "  python -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu\n"
            "Then reinstall sentence-transformers."
        ) from exc

    elapsed = time.time() - start
    logger.info("Embedding model loaded in %.2fs", elapsed)

    vectorstore = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )

    _retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    logger.info("Retriever initialized and cached")
    return _retriever
