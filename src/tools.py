import os
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")


def fetch_page_content(url: str) -> str:
    """
    Visits a URL and returns the clean text content.
    We limit it to 2000 characters to keep the LLM context manageable.
    """
    try:
        # User-Agent header is important so websites don't block the bot
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 1. Fetch the page with a 5-second timeout
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()  # Raise error if status is 404, 500, etc.

        # 2. Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        if not soup:
            return "Page content was empty."

        # 3. Clean up: Remove scripts, styles, and navigation elements
        # [FIX] Use find_all explicitly and decompose() instead of destroy()
        tags_to_remove = ["script", "style", "nav",
                          "footer", "header", "aside", "iframe"]
        for element in soup.find_all(tags_to_remove):
            element.decompose()

        # 4. Extract text and clean whitespace
        # Use space separator to avoid merging words
        text = soup.get_text(separator=' ')

        # Simple whitespace cleanup
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip()
                  for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)

        # 5. Return the first 2000 characters
        return clean_text[:2000]

    except Exception as e:
        print(f"Warning: Could not scrape {url}: {e}")
        return "Page content could not be retrieved."


def search_volunteer_sites(query_text: str) -> list[dict]:
    """
    Searches volunteer websites and now includes the FULL page content
    for the RAG agent to analyze.
    """
    print(f"--- 🛠️ Tool: Searching for: {query_text} ---")

    if not API_KEY or not SEARCH_ENGINE_ID:
        print("Error: API_KEY or SEARCH_ENGINE_ID not found in .env file.")
        return []

    service = build("customsearch", "v1", developerKey=API_KEY)

    try:
        # 1. Perform the Google Search
        result = service.cse().list(
            q=query_text,
            cx=SEARCH_ENGINE_ID,
            num=5
        ).execute()

        final_results = []

        if 'items' in result:
            # 2. Loop through results and "read" each page
            for item in result['items']:
                print(f"   -> Scraping: {item['title']}...")

                full_content = fetch_page_content(item['link'])

                final_results.append({
                    "title": item['title'],
                    "link": item['link'],
                    "snippet": item['snippet'],      # Google's summary
                    "full_text": full_content        # The actual page content
                })

            return final_results
        else:
            return []

    except Exception as e:
        print(f"Error during search: {e}")
        return []
