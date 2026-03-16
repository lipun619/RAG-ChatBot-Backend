import logging
import os

from langchain_core.documents import Document
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def load_resume() -> list[Document]:
    """Extract text from a resume PDF and return as a document."""
    resume_path = os.getenv("RESUME_PATH", "")
    if not resume_path:
        logger.warning("RESUME_PATH not set — skipping resume ingestion")
        return []

    if not os.path.isfile(resume_path):
        logger.warning("Resume file not found at %s — skipping", resume_path)
        return []

    try:
        reader = PdfReader(resume_path)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

        full_text = "\n\n".join(pages_text)

        if not full_text.strip():
            logger.warning("Resume PDF is empty — skipping")
            return []

        doc = Document(
            page_content=full_text,
            metadata={
                "source": "resume",
                "file": os.path.basename(resume_path),
            },
        )
        logger.info("Loaded resume: %s (%d pages)", resume_path, len(reader.pages))
        return [doc]

    except Exception as e:
        logger.error("Error reading resume PDF: %s", e)
        return []
