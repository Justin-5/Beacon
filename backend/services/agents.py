import os
import json
import asyncio
from typing import List, Dict

import google.generativeai as genai
from dotenv import load_dotenv

from ..schemas.models import OpportunityList, ChatMessage
from ..services.tools import search_volunteer_sites


load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Base text model used for general prompting
TEXT_MODEL_NAME = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash-lite")

text_model = genai.GenerativeModel(TEXT_MODEL_NAME)


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


INQUIRY_PROMPT = """
You are a *Contextual Inquiry Agent* helping a user understand a **single** volunteer role.

You will be given:
- The scraped `full_text` for this role (which may be noisy).
- The user's question about this role.
- Optional prior chat history.

**CRITICAL RULES**
- Only answer using information that can be reasonably inferred from the provided `full_text`.
- Do *not* fabricate details (dates, time commitments, requirements, benefits, etc.).
- If the answer is not clearly present, say politely that the information is not specified.
- Keep answers concise, friendly, and practical.

---
ROLE FULL TEXT (noisy, scraped content):
{full_text}
---

CHAT HISTORY (most recent last, may be empty):
{chat_history}
---

USER QUESTION:
{user_query}

ASSISTANT ANSWER:
"""


def _call_llm_agent_sync(prompt_template: str, **kwargs) -> str:
    """
    Synchronous helper for general text models (Research, Format, Inquiry).
    """
    prompt = prompt_template

    if "user_request" in kwargs:
        prompt = prompt.replace("{user_request}", str(kwargs["user_request"]))

    if "vetted_list" in kwargs:
        prompt = prompt.replace("{vetted_list}", str(kwargs["vetted_list"]))

    if "full_text" in kwargs:
        prompt = prompt.replace("{full_text}", str(kwargs["full_text"]))

    if "user_query" in kwargs:
        prompt = prompt.replace("{user_query}", str(kwargs["user_query"]))

    if "chat_history" in kwargs:
        prompt = prompt.replace("{chat_history}", str(kwargs["chat_history"]))

    try:
        response = text_model.generate_content(prompt)
        return (response.text or "").strip()
    except Exception as exc:
        print(f"Error calling LLM (Text Mode): {exc}")
        return "LLM_AGENT_ERROR"


async def call_llm_agent(prompt_template: str, **kwargs) -> str:
    """
    Async façade for the generic text agent.
    """
    return await asyncio.to_thread(_call_llm_agent_sync, prompt_template, **kwargs)


def _call_filter_agent_sync(search_results: List[Dict]) -> Dict:
    """
    Specialized helper for FilterAgent.
    Uses 'full_text' for RAG and enforces Pydantic JSON output.
    """
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=OpportunityList,
    )

    json_model = genai.GenerativeModel(
        TEXT_MODEL_NAME,
        generation_config=generation_config,
    )

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
        response = json_model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as exc:
        print(f"Error calling Filter Agent: {exc}")
        return {"items": []}


async def call_filter_agent(search_results: List[Dict]) -> Dict:
    """
    Async façade for the FilterAgent.
    """
    return await asyncio.to_thread(_call_filter_agent_sync, search_results)


async def run_volunteer_agent_flow_async(user_request: str):
    """
    Async orchestrator for the main volunteer search flow.
    Returns (final_response_text, OpportunityList instance).
    """
    print(f"--- Starting Agent Flow for: '{user_request}' ---")

    session_state = {
        "user_request": user_request,
        "search_query": "",
        "raw_search_results": [],
        "vetted_opportunities": OpportunityList(items=[]),
        "final_response": "",
    }

    # 1. ResearchAgent
    print("--- 🤖 Agent 1: ResearchAgent is thinking... ---")
    search_query = await call_llm_agent(
        RESEARCH_PROMPT,
        user_request=session_state["user_request"],
    )
    if search_query == "LLM_AGENT_ERROR":
        raise RuntimeError("ResearchAgent failed to generate a search query.")

    session_state["search_query"] = search_query

    # 2. Tool: Google Search + Scraping
    session_state["raw_search_results"] = await search_volunteer_sites(
        session_state["search_query"]
    )

    # 3. FilterAgent (RAG + JSON mode)
    print("--- 🤖 Agent 2: FilterAgent is thinking... ---")
    vetted_raw = await call_filter_agent(session_state["raw_search_results"])
    # Normalize into OpportunityList Pydantic model
    session_state["vetted_opportunities"] = OpportunityList(**vetted_raw)

    # 4. FormatAgent
    print("--- 🤖 Agent 3: FormatAgent is thinking... ---")
    final_response = await call_llm_agent(
        FORMAT_PROMPT,
        vetted_list=session_state["vetted_opportunities"],
    )
    if final_response == "LLM_AGENT_ERROR":
        raise RuntimeError("FormatAgent failed to format the results.")

    session_state["final_response"] = final_response

    print("--- ✅ Agent Flow Complete ---")
    return session_state["final_response"], session_state["vetted_opportunities"]


def _format_chat_history_for_prompt(chat_history: List[ChatMessage]) -> str:
    """
    Turn a list of ChatMessage objects into a simple, readable history
    string for the Inquiry prompt.
    """
    if not chat_history:
        return "No prior conversation."

    lines = []
    for msg in chat_history:
        lines.append(f"{msg.role.upper()}: {msg.content}")
    return "\n".join(lines)


async def run_inquiry_agent_async(
    full_text: str,
    user_query: str,
    chat_history: List[ChatMessage],
) -> str:
    """
    Contextual Inquiry Agent.

    Answers questions about a single volunteer role using only the provided
    `full_text`. If information is missing, the agent should state that
    transparently rather than hallucinating.
    """
    history_str = _format_chat_history_for_prompt(chat_history)

    answer = await call_llm_agent(
        INQUIRY_PROMPT,
        full_text=full_text,
        user_query=user_query,
        chat_history=history_str,
    )

    if answer == "LLM_AGENT_ERROR":
        raise RuntimeError("InquiryAgent failed to generate a response.")

    return answer

