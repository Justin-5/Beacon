import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key and configure the Gemini model
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# --- Define the prompts for our 3 agents ---

RESEARCH_PROMPT = """
You are a research assistant. Your single job is to convert the user's request into a highly effective Google search query.
Focus on keywords, location, and key phrases.
Do not add any explanation or conversational text. Output *only* the final search query.

User Request: {user_request}
Search Query:
"""

FILTER_PROMPT = """
You are a filtering analyst. You will be given a list of raw Google search results.
Your job is to read the snippets and extract *only* the actionable volunteer opportunities.
Ignore any links that are primarily about donations, news, blogs, or "about us" pages.
For each valid opportunity, extract its title, a 1-sentence summary, and the URL.

Format your output as a clean Python list of dictionaries:
[
  {"title": "Opportunity Title", "summary": "...", "url": "..."},
  {"title": "Another Opportunity", "summary": "...", "url": "..."}
]
If no results are relevant, output an empty list: []

Search Results:
{search_results}
"""

FORMAT_PROMPT = """
You are a helpful assistant. You will be given a structured list of vetted volunteer opportunities.
Your job is to format this list into a friendly, easy-to-read, and encouraging response for the user.
Use markdown (like bullet points) to make it scannable.
If the list is empty, respond with a kind message stating you couldn't find any specific matches but encourage them to try a broader search.

Vetted List:
{vetted_list}
"""


def call_llm_agent(prompt_template: str, **kwargs) -> str:
    """
    A helper function to call the LLM agent
    with a specific prompt and input.
    """
    try:
        # --- NEW ROBUST FIX ---
        # We will manually build the prompt to avoid .format() errors
        # from data that contains curly braces.

        prompt = prompt_template

        # Manually replace the keys in the template
        if "user_request" in kwargs:
            prompt = prompt.replace(
                "{user_request}", str(kwargs["user_request"]))

        if "search_results" in kwargs:
            # We must import json to handle the data as a clean string
            import json
            prompt = prompt.replace(
                "{search_results}", json.dumps(kwargs["search_results"]))

        if "vetted_list" in kwargs:
            prompt = prompt.replace(
                "{vetted_list}", str(kwargs["vetted_list"]))

        # --- END OF FIX ---

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Error calling LLM: {e}")

        # Check which prompt failed to give a safe fallback
        if "FILTER_PROMPT" in prompt_template:
            return "[]"  # Return an empty list for the filter agent
        else:
            return "LLM_AGENT_ERROR"  # Return a token for other agents
