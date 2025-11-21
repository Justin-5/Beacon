import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")


def search_volunteer_sites(query_text: str) -> list[dict]:
    """
    This is our custom tool. It searches only the pre-configured
    volunteer websites (volunteermatch.org, idealist.org)
    for the user's query.
    """
    print(f"--- 🛠️ Tool: Searching for: {query_text} ---")

    # Check if keys are loaded
    if not API_KEY or not SEARCH_ENGINE_ID:
        print("Error: API_KEY or SEARCH_ENGINE_ID not found in .env file.")
        return []

    service = build("customsearch", "v1", developerKey=API_KEY)

    try:
        result = service.cse().list(
            q=query_text,
            cx=SEARCH_ENGINE_ID,
            num=5  # Get top 5 results
        ).execute()

        # Extract just the title, link, and snippet for the agent
        if 'items' in result:
            search_results = [
                {
                    "title": item['title'],
                    "link": item['link'],
                    "snippet": item['snippet']
                }
                for item in result['items']
            ]
            return search_results
        else:
            return []

    except Exception as e:
        print(f"Error during search: {e}")
        return []
