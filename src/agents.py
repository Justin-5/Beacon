import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from .models import OpportunityList

# Load API key and configure the Gemini model
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the generic model for text tasks
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# --- Prompts ---

RESEARCH_PROMPT = """
You are a research assistant. Your single job is to convert the user's request into a highly effective Google search query.
Focus on keywords, location, and key phrases.
Do not add any explanation or conversational text. Output *only* the final search query.

User Request: {user_request}
Search Query:
"""

FORMAT_PROMPT = """
You are a helpful assistant. You will be given a structured list of vetted volunteer opportunities.
Your job is to format this list into a friendly, easy-to-read, and encouraging response for the user.
Use markdown (like bullet points) to make it scannable.
If the list is empty, respond with a kind message stating you couldn't find any specific matches but encourage them to try a broader search.

Vetted List:
{vetted_list}
"""

# --- Functions ---


def call_llm_agent(prompt_template: str, **kwargs) -> str:
    """
    Standard helper for ResearchAgent and FormatAgent.
    Returns plain text.
    """
    try:
        prompt = prompt_template

        # Simple manual replacement to avoid string formatting issues
        if "user_request" in kwargs:
            prompt = prompt.replace(
                "{user_request}", str(kwargs["user_request"]))

        if "vetted_list" in kwargs:
            # Convert the list of objects back to string for the formatter
            prompt = prompt.replace(
                "{vetted_list}", str(kwargs["vetted_list"]))

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Error calling LLM (Text Mode): {e}")
        return "LLM_AGENT_ERROR"


def call_filter_agent(search_results: list[dict]) -> dict:
    """
    Specialized helper for FilterAgent.
    Uses 'full_text' for RAG and enforces Pydantic JSON output.
    """
    # 1. Configure a specialized model for JSON mode
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=OpportunityList
    )

    json_model = genai.GenerativeModel(
        'gemini-2.5-flash-lite',
        generation_config=generation_config
    )

    # 2. RAG Prompt: Explicitly asks to read the scraped text
    prompt = f"""
    You are a filtering analyst. You have been given search results that include the scraped 'full_text' of the websites.
    
    Your Task:
    1. Read the 'full_text' of each result to verify if it is a legitimate volunteer opportunity.
    2. IGNORE general 'About Us' pages, donation pages, or blogs that don't list specific roles.
    3. Extract the title, organization, location, and a summary for valid matches.
    
    Search Results:
    {json.dumps(search_results)}
    """

    try:
        # 3. Generate and parse
        response = json_model.generate_content(prompt)

        # Because we used response_schema, this text is guaranteed to be valid JSON
        return json.loads(response.text)

    except Exception as e:
        print(f"Error calling Filter Agent: {e}")
        # Return an empty list matching the expected structure
        return {"items": []}
