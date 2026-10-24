import os
import asyncio
import logging
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()

log = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID") or os.getenv(
    "SEARCH_ENGINE_ID"
)
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)
MAX_PAGE_CHARS = 2000  # keeps LLM context (and cost) bounded


def _fetch_page_content(url: str) -> str:
    """
    Visit a URL and return clean text content, truncated to MAX_PAGE_CHARS.
    """
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        for element in soup.find_all(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            element.decompose()

        text = soup.get_text(separator=" ")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)[:MAX_PAGE_CHARS]
    except Exception as exc:
        log.warning("Could not scrape %s: %s", url, exc)
        return "Page content could not be retrieved."


def _google_search(query_text: str) -> List[Dict]:
    response = requests.get(
        SEARCH_URL,
        params={"cx": SEARCH_ENGINE_ID, "q": query_text, "num": 5},
        headers={"X-Goog-Api-Key": GOOGLE_API_KEY},  # header, so the key never shows up in logged URLs
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("items", [])


async def search_volunteer_sites(query_text: str) -> List[Dict]:
    """
    Google Custom Search (restricted to curated volunteer sites), then scrape
    every result page concurrently so total latency is the slowest page, not the sum.
    """
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        raise RuntimeError("GOOGLE_API_KEY or GOOGLE_SEARCH_ENGINE_ID is not set.")

    log.info("Searching for: %s", query_text)
    items = await asyncio.to_thread(_google_search, query_text)
    pages = await asyncio.gather(
        *(asyncio.to_thread(_fetch_page_content, item["link"]) for item in items)
    )
    return [
        {
            "title": item["title"],
            "link": item["link"],
            "snippet": item.get("snippet", ""),
            "full_text": page,
        }
        for item, page in zip(items, pages)
    ]
