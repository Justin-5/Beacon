from .agents import call_llm_agent, RESEARCH_PROMPT, FILTER_PROMPT, FORMAT_PROMPT
from .tools import search_volunteer_sites
import json


def run_volunteer_agent_flow(user_request: str):
    """
    This is the main orchestrator that runs the sequential agent flow.
    It uses a dictionary as the in-memory session to pass state.
    """
    print(f"--- Starting Agent Flow for: '{user_request}' ---")

    # 1. Initialize the Session State
    # This dictionary holds the memory for this single run
    session_state = {
        "user_request": user_request,
        "search_query": "",
        "raw_search_results": [],
        "vetted_opportunities_str": "[]",  # Store as string
        "final_response": ""
    }

    # 2. Run Agent 1: ResearchAgent
    print("--- 🤖 Agent 1: ResearchAgent is thinking... ---")
    session_state["search_query"] = call_llm_agent(
        RESEARCH_PROMPT,
        user_request=session_state["user_request"]
    )
    if session_state["search_query"] == "LLM_AGENT_ERROR":
        print("Error: Agent 1 (ResearchAgent) failed.")
        return "I'm sorry, I had an error processing your request. Please try again."

    # 3. Run the Custom Tool
    session_state["raw_search_results"] = search_volunteer_sites(
        session_state["search_query"]
    )

    # 4. Run Agent 2: FilterAgent
    print("--- 🤖 Agent 2: FilterAgent is thinking... ---")
    session_state["vetted_opportunities_str"] = call_llm_agent(
        FILTER_PROMPT,
        search_results=session_state["raw_search_results"]
    )

    # 5. Run Agent 3: FormatAgent
    print("--- 🤖 Agent 3: FormatAgent is thinking... ---")
    session_state["final_response"] = call_llm_agent(
        FORMAT_PROMPT,
        vetted_list=session_state["vetted_opportunities_str"]
    )
    if session_state["final_response"] == "LLM_AGENT_ERROR":
        print("Error: Agent 3 (FormatAgent) failed.")
        # Return the raw data so the user at least sees something
        return "I'm sorry, I had an error formatting the results. Here is the raw data: " + session_state["vetted_opportunities_str"]

    # 6. Return the final answer
    print("--- ✅ Agent Flow Complete ---")
    return session_state["final_response"]
