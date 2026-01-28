import os
import asyncio
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from dotenv import load_dotenv


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID") or os.getenv(
    "SEARCH_ENGINE_ID"
)


def _fetch_page_content(url: str) -> str:
    """
    Synchronous implementation that visits a URL and returns clean text content.
    Limited to 2000 characters to keep LLM context manageable.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        if not soup:
            return "Page content was empty."

        tags_to_remove = ["script", "style", "nav", "footer", "header", "aside", "iframe"]
        for element in soup.find_all(tags_to_remove):
            element.decompose()

        text = soup.get_text(separator=" ")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)

        return clean_text[:2000]
    except Exception as exc:
        print(f"Warning: Could not scrape {url}: {exc}")
        return "Page content could not be retrieved."


async def fetch_page_content(url: str) -> str:
    """
    Async wrapper around the synchronous HTML scraper.
    """
    return await asyncio.to_thread(_fetch_page_content, url)


def _search_volunteer_sites_sync(query_text: str) -> List[Dict]:
    """
    Synchronous implementation of the Google Custom Search + scraping flow.
    Mirrors the existing Streamlit tool logic.
    """
    print(f"--- 🛠️ Tool: Searching for: {query_text} ---")

    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        print("Error: GOOGLE_API_KEY or SEARCH_ENGINE_ID not found in .env file.")
        return []

    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)

    try:
        result = (
            service.cse()
            .list(
                q=query_text,
                cx=SEARCH_ENGINE_ID,
                num=5,
            )
            .execute()
        )

        final_results: List[Dict] = []

        if "items" in result:
            for item in result["items"]:
                print(f"   -> Scraping: {item['title']}...")
                full_content = _fetch_page_content(item["link"])
                final_results.append(
                    {
                        "title": item["title"],
                        "link": item["link"],
                        "snippet": item.get("snippet", ""),
                        "full_text": full_content,
                    }
                )
            return final_results
        return []
    except Exception as exc:
        print(f"Error during search: {exc}")
        return []


async def search_volunteer_sites(query_text: str) -> List[Dict]:
    """
    Async façade for the Google search + scraping tool.
    Calls the underlying synchronous implementation in a thread.
    """
    return await asyncio.to_thread(_search_volunteer_sites_sync, query_text)

