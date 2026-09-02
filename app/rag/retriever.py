import logging
import sys
import time
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

logger = logging.getLogger(__name__)

VECTOR_DB_DIR = str(Path(__file__).resolve().parent.parent.parent / "vector_db")
COLLECTION_NAME = "lipun_knowledge"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-MiniLM-L3-v2"

_retriever = None


def _ensure_compatible_python():
    """Fail fast with a clear message if the runtime is incompatible with the ML stack."""
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(
            "This project requires Python 3.12.x. The current environment is Python "
            f"{sys.version.split()[0]}. The PyTorch/SentenceTransformers stack used here is not compatible "
            "with Python 3.14 on macOS, and the local virtual environment must be recreated.\n\n"
            "Fix:\n"
            "  rm -rf venv\n"
            "  python3.12 -m venv venv\n"
            "  source venv/bin/activate\n"
            "  python -m pip install --upgrade pip setuptools wheel\n"
            "  python -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu\n"
            "  python -m pip install -r requirements.txt\n\n"
            "Then restart the API server."
        )


def get_retriever():
    """Load the persisted ChromaDB and return a LangChain retriever (cached)."""
    global _retriever
    if _retriever is not None:
        logger.info("Using cached retriever (no model download)")
        return _retriever

    try:
        _ensure_compatible_python()
    except RuntimeError:
        raise

    logger.info("Initializing retriever — loading embedding model '%s'...", EMBEDDING_MODEL)
    start = time.time()

    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    except (ImportError, OSError) as exc:
        raise RuntimeError(
            "Failed to initialize HuggingFaceEmbeddings because SentenceTransformers/Torch "
            "could not be loaded. This project requires Python 3.12.x and a clean venv. "
            "To fix this, recreate the virtual environment and reinstall the dependency stack.\n\n"
            "Fix:\n"
            "  rm -rf venv\n"
            "  python3.12 -m venv venv\n"
            "  source venv/bin/activate\n"
            "  python -m pip install --upgrade pip setuptools wheel\n"
            "  python -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu\n"
            "  python -m pip install -r requirements.txt\n\n"
            "Then restart the API server."
        ) from exc

    elapsed = time.time() - start
    logger.info("Embedding model loaded in %.2fs", elapsed)

    vectorstore = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME,
    )

    _retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    logger.info("Retriever initialized and cached with k=3 for lower token usage")
    return _retriever
