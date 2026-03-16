import logging
from pathlib import Path

from langchain_core.documents import Document

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_local() -> list[Document]:
    """Load markdown files from the data directory."""
    if not DATA_DIR.is_dir():
        logger.warning("Data directory not found at %s — skipping", DATA_DIR)
        return []

    documents: list[Document] = []

    for md_file in sorted(DATA_DIR.glob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")

            if not content.strip():
                logger.warning("Empty file: %s — skipping", md_file.name)
                continue

            doc = Document(
                page_content=content,
                metadata={
                    "source": "local",
                    "file": md_file.name,
                },
            )
            documents.append(doc)
            logger.info("Loaded local file: %s", md_file.name)

        except Exception as e:
            logger.error("Error reading %s: %s", md_file.name, e)

    logger.info("Local loader: %d documents loaded", len(documents))
    return documents
