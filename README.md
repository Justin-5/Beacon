# Capstone Project: Local Volunteer Agent

This is my submission for the Google Capstone Project. It is an AI agent designed to help users in India find relevant, local volunteer opportunities.

## Problem

Many people want to volunteer but find it difficult and time-consuming to search multiple, separate websites (like local charities, city portals, and national NGOs) to find opportunities that match their skills and availability.

## Solution

This is an AI agent that takes a user's natural language request (e.g., "animal welfare, Saturday mornings, Mumbai") and automates the entire process. It searches a curated list of trusted Indian volunteer sites, filters out the noise, and presents a clean, actionable list of opportunities to the user.

## Features Implemented

This project demonstrates three key concepts from the course:

1.  **Multi-agent System (Sequential Agents):** The solution uses a sequential agent chain composed of three specialized agents:

    - **`ResearchAgent`**: Converts the user's natural language request into an optimal, keyword-based search query.
    - **`FilterAgent`**: "Reads" the raw search results, understands the snippets, and filters them down to _only_ scannable, actionable opportunities (ignoring blogs, donation pages, etc.).
    - **`FormatAgent`**: Takes the final, vetted list and presents it to the user in a friendly, encouraging, and easy-to-read format.

2.  **Custom Tools:** The agent uses a custom-built tool, `search_volunteer_sites`, which is powered by the **Google Custom Search JSON API**. This tool is configured to _only_ search a pre-approved list of high-quality Indian volunteer sites, including:

    - `ivolunteer.in`
    - `bhumi.ngo`
    - `vidyanjali.education.gov.in`
    - `balrakshabharat.org`
    - `akshayapatra.org`

3.  **Sessions & State Management:** The entire flow is orchestrated in `main.py`, which uses a simple Python dictionary (`session_state`) as an **in-memory session service**. This dictionary holds the state and context (e.g., the search query, the raw results, the vetted list) as it is passed from one agent to the next in the chain.

## Tech Stack

- **Language:** Python
- **LLM:** Google Gemini (`gemini-pro` / `gemini-2.5-flash-lite`) via the `google-generativeai` SDK.
- **Tools:** Google Custom Search JSON API (`google-api-python-client`).
- **Environment:** `python-dotenv` for API key management.

## How to Run

1.  Clone this repository.
2.  Create a virtual environment: `python -m venv .venv` and activate it: `.\.venv\Scripts\Activate.ps1`
3.  Install dependencies: `pip install -r requirements.txt`
4.  Create a `.env` file and add your `GOOGLE_API_KEY`, `Google Search_ENGINE_ID`, and `GEMINI_API_KEY`.
5.  Run the main application: `python main.py`
