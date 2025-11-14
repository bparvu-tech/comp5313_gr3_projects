"""TF-IDF retrieval fallback for chatbot responses."""
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app import config

logger = logging.getLogger(__name__)

RAG_ENABLED = getattr(config, "RAG_ENABLED", True)
RAG_DATA_DIR = Path(getattr(config, "RAG_DATA_DIR", ""))
RAG_MAX_DOCS = int(getattr(config, "RAG_MAX_DOCS", 500))
RAG_MIN_SIMILARITY = float(getattr(config, "RAG_MIN_SIMILARITY", 0.22))

_DOCUMENTS: List[Dict[str, str]] = []
_VECTORIZER: Optional[TfidfVectorizer] = None
_DOCUMENT_MATRIX = None
_INDEX_INITIALIZED = False


def _data_dir_exists() -> bool:
    if RAG_DATA_DIR.is_dir():
        return True
    logger.warning("RAG data directory not found: %s", RAG_DATA_DIR)
    return False


def _extract_title(raw_text: str, fallback: str) -> str:
    for line in raw_text.splitlines():
        clean_line = line.strip()
        if clean_line.startswith("#"):
            return clean_line.lstrip("# ").strip()
    return fallback


def _extract_source(raw_text: str) -> str:
    source_match = re.search(r"\*\*Source\*\*:\s*(.+)", raw_text)
    if not source_match:
        return ""
    return source_match.group(1).strip()


def _clean_markdown(raw_text: str) -> str:
    text = re.sub(r"`{1,3}.*?`{1,3}", " ", raw_text, flags=re.DOTALL)
    text = re.sub(r"\!\[.*?\]\(.*?\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"#+\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _initialize_index() -> None:
    global _INDEX_INITIALIZED  # pylint: disable=global-statement
    if _INDEX_INITIALIZED:
        return
    _INDEX_INITIALIZED = True

    if not RAG_ENABLED:
        logger.info("RAG is disabled via configuration.")
        return

    if not _data_dir_exists():
        return

    markdown_files = sorted(RAG_DATA_DIR.glob("*.md"))[:RAG_MAX_DOCS]
    if not markdown_files:
        logger.warning("No markdown files found for RAG in %s", RAG_DATA_DIR)
        return

    documents: List[Dict[str, str]] = []
    contents: List[str] = []

    for file_path in markdown_files:
        try:
            raw_text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as file_error:
            logger.warning("Unable to read %s: %s", file_path, file_error)
            continue

        cleaned = _clean_markdown(raw_text)
        if not cleaned:
            continue

        title = _extract_title(
            raw_text, file_path.stem.replace(
                "_", " ").title())
        source = _extract_source(raw_text)
        documents.append({
            "title": title,
            "body": cleaned,
            "source": source,
            "path": str(file_path)
        })
        contents.append(cleaned)

    if not documents:
        logger.warning("No usable documents loaded for RAG.")
        return

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=50000,
        lowercase=True
    )
    matrix = vectorizer.fit_transform(contents)

    global _DOCUMENTS, _VECTORIZER, _DOCUMENT_MATRIX  # pylint: disable=global-statement
    _DOCUMENTS = documents
    _VECTORIZER = vectorizer
    _DOCUMENT_MATRIX = matrix

    logger.info("Initialized RAG index with %d documents from %s",
                len(_DOCUMENTS), RAG_DATA_DIR)


def get_best_passage(request: Dict[str, str]) -> Dict[str, Optional[str]]:
    """Return the best matching passage for a query."""
    query = (request.get("query") or "").strip()
    max_length = int(request.get("max_length", 600))

    if not query:
        logger.debug("RAG request missing query text")
        return {"text": None, "score": None, "source": None}

    if not RAG_ENABLED:
        return {"text": None, "score": None, "source": None}

    _initialize_index()

    if not _VECTORIZER or _DOCUMENT_MATRIX is None or not _DOCUMENTS:
        logger.debug("RAG index not available.")
        return {"text": None, "score": None, "source": None}

    query_vector = _VECTORIZER.transform([query])
    scores = cosine_similarity(query_vector, _DOCUMENT_MATRIX).flatten()
    if not len(scores):
        return {"text": None, "score": None, "source": None}

    best_idx = int(scores.argmax())
    best_score = float(scores[best_idx])

    if best_score < RAG_MIN_SIMILARITY:
        logger.debug("RAG best score %.3f below threshold %.3f",
                     best_score, RAG_MIN_SIMILARITY)
        return {"text": None, "score": None, "source": None}

    doc = _DOCUMENTS[best_idx]
    snippet = doc["body"][:max_length].strip()
    response_lines = [doc["title"], "", snippet]

    if doc["source"]:
        response_lines.extend(["", f"Source: {doc['source']}"])
    else:
        response_lines.extend(["", f"(From {os.path.basename(doc['path'])})"])

    response_text = "\n".join(response_lines).strip()

    logger.info(
        "RAG served passage from %s (score=%.3f)",
        doc["path"],
        best_score)
    return {
        "text": response_text,
        "score": round(best_score, 3),
        "source": doc["source"] or doc["path"]
    }
