from fastapi import APIRouter, HTTPException
from fastapi import status

from ..schemas.models import (
    SearchRequest,
    SearchResponse,
    ChatRequest,
    ChatResponse,
    SaveRequest,
)
from ..services.agents import (
    run_volunteer_agent_flow_async,
    run_inquiry_agent_async,
)
from ..services.db import save_opportunity_to_db


router = APIRouter()


@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search for vetted volunteer opportunities.",
)
async def search_opportunities(payload: SearchRequest) -> SearchResponse:
    """
    Orchestrates the Research, Tool, and Filter agents to find
    vetted volunteer opportunities for the user.
    """
    try:
        final_response, opportunities = await run_volunteer_agent_flow_async(
            user_request=payload.user_request
        )
        return SearchResponse(
            message=final_response,
            opportunities=opportunities.items,
        )
    except Exception as exc:  # pragma: no cover - defensive
        # Centralized error surface for the client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process search request: {exc}",
        ) from exc


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask contextual questions about a single volunteer role.",
)
async def chat_with_inquiry_agent(payload: ChatRequest) -> ChatResponse:
    """
    Contextual Inquiry Agent endpoint.
    The agent must answer **only** from the provided `full_text` for a single role.
    """
    try:
        answer = await run_inquiry_agent_async(
            full_text=payload.full_text,
            user_query=payload.user_query,
            chat_history=payload.chat_history or [],
        )
        return ChatResponse(answer=answer)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {exc}",
        ) from exc


@router.post(
    "/save",
    status_code=status.HTTP_201_CREATED,
    summary="Save a volunteer opportunity for a user.",
)
async def save_opportunity(payload: SaveRequest):
    """
    Persist a single volunteer opportunity for the given user in Supabase.
    """
    try:
        await save_opportunity_to_db(
            user_id=payload.user_id,
            opportunity=payload.opportunity,
        )
        return {"success": True}
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save opportunity: {exc}",
        ) from exc

