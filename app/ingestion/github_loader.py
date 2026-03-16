import logging
import os

from github import Auth, Github
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def load_github() -> list[Document]:
    """Load repository information from GitHub using PyGithub."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.warning("GITHUB_TOKEN not set — skipping GitHub ingestion")
        return []

    documents: list[Document] = []

    try:
        g = Github(auth=Auth.Token(token))
        user = g.get_user()
        repos = user.get_repos(type="owner")

        for repo in repos:
            try:
                name = repo.name
                description = repo.description or "No description"
                url = repo.html_url
                languages = ", ".join(repo.get_languages().keys()) or "Not specified"

                # Try to get README content
                readme_content = ""
                try:
                    readme = repo.get_readme()
                    readme_content = readme.decoded_content.decode("utf-8")
                except Exception:
                    readme_content = "No README available"

                content = (
                    f"Project Name: {name}\n"
                    f"Description: {description}\n"
                    f"Technologies: {languages}\n"
                    f"Repository URL: {url}\n\n"
                    f"README:\n{readme_content}"
                )

                doc = Document(
                    page_content=content,
                    metadata={
                        "source": "github",
                        "repo_name": name,
                        "repo_url": url,
                    },
                )
                documents.append(doc)
                logger.info("Loaded GitHub repo: %s", name)

            except Exception as e:
                logger.error("Error loading repo %s: %s", repo.name, e)

        g.close()

    except Exception as e:
        logger.error("Error connecting to GitHub: %s", e)

    logger.info("GitHub loader: %d documents loaded", len(documents))
    return documents
