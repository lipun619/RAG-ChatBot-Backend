import logging
import os

import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

PAGES = ["/about", "/skills", "/projects"]


def load_website() -> list[Document]:
    """Scrape portfolio website pages and return as documents."""
    base_url = os.getenv("PORTFOLIO_URL", "").rstrip("/")
    if not base_url:
        logger.warning("PORTFOLIO_URL not set — skipping website ingestion")
        return []

    documents: list[Document] = []

    for page in PAGES:
        url = f"{base_url}{page}"
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style tags
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)

            if text:
                doc = Document(
                    page_content=text,
                    metadata={
                        "source": "website",
                        "page": page,
                        "url": url,
                    },
                )
                documents.append(doc)
                logger.info("Loaded website page: %s", page)

        except Exception as e:
            logger.error("Error scraping %s: %s", url, e)

    logger.info("Website loader: %d documents loaded", len(documents))
    return documents
