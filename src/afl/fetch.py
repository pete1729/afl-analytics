"""Polite, cached fetching of web pages.

Every page goes through `fetch()`. It checks the local cache in data/raw/
first and only downloads when the page isn't already there, so each page is
downloaded at most once. Real downloads are spaced 1-2 seconds apart and
retried at most twice.
"""

import logging
import random
import time
from pathlib import Path
from urllib.parse import quote, urlparse

import requests

logger = logging.getLogger(__name__)

# src/afl/fetch.py -> project root is two folders up from src/afl/
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

USER_AGENT = "afl-analytics hobby project (contact: peter1729@gmail.com)"
MAX_RETRIES = 2
RETRY_PAUSE_SECONDS = 10  # longer pause before each retry

# Status codes worth retrying: the server is busy or briefly broken.
# Anything else (e.g. 404 Not Found) won't change on retry.
RETRYABLE_STATUS = {429, 500, 502, 503, 504}

# Time of our last real request, shared by all calls in this Python session.
_last_request_time = 0.0


def cache_path(url: str) -> Path:
    """Map a URL to a file in data/raw/, mirroring the site's folder layout.

    https://afltables.com/afl/seas/2025.html
        -> data/raw/afltables.com/afl/seas/2025.html
    """
    parts = urlparse(url)
    path = parts.path.strip("/")
    if "." not in path.split("/")[-1]:
        # Extensionless paths like /years/2015 become years/2015/index.html,
        # so that /years/2015/... pages can still live inside that folder.
        path = (path + "/index.html").lstrip("/")
    if parts.query:
        # Keep query strings in the filename, made safe for the filesystem.
        path += "__" + quote(parts.query, safe="")
    return RAW_DIR / parts.netloc / path


def _wait_politely() -> None:
    """Sleep so that real requests are at least 1-2 seconds apart."""
    gap = random.uniform(1.0, 2.0)
    elapsed = time.monotonic() - _last_request_time
    if elapsed < gap:
        time.sleep(gap - elapsed)


def _download(url: str) -> bytes | None:
    """Download a URL, retrying temporary failures. Returns None on failure."""
    global _last_request_time

    for attempt in range(1 + MAX_RETRIES):
        if attempt > 0:
            logger.info("Retry %d/%d for %s", attempt, MAX_RETRIES, url)
            time.sleep(RETRY_PAUSE_SECONDS * attempt)

        _wait_politely()
        _last_request_time = time.monotonic()
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        except requests.RequestException as error:
            logger.warning("Request error for %s: %s", url, error)
            continue  # network problems are worth retrying

        if response.status_code == 200:
            return response.content
        if response.status_code not in RETRYABLE_STATUS:
            logger.warning("HTTP %d for %s, skipping", response.status_code, url)
            return None
        logger.warning("HTTP %d for %s", response.status_code, url)

    logger.error("Giving up on %s after %d retries", url, MAX_RETRIES)
    return None


def fetch(url: str, encoding: str = "utf-8") -> str | None:
    """Return the HTML for `url`, from the cache if possible.

    Use encoding="latin-1" for AFL Tables pages.
    Returns None if the page couldn't be downloaded (the failure is logged).
    """
    path = cache_path(url)
    if path.exists():
        return path.read_bytes().decode(encoding)

    logger.info("Downloading %s", url)
    content = _download(url)
    if content is None:
        return None  # don't cache failures, so a later run can try again

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return content.decode(encoding)
