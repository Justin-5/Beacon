from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas.models import (
    SearchRequest,
    SearchResponse,
    ChatRequest,
    ChatResponse,
    VolunteerOpportunity,
)
from ..services.agents import (
    run_volunteer_agent_flow_async,
    run_inquiry_agent_async,
)
from ..services.auth import get_current_user_id
from ..services.db import delete_saved_role, get_saved_roles, save_opportunity_to_db


router = APIRouter()


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Search for vetted volunteer opportunities.",
)
async def search_opportunities(payload: SearchRequest) -> SearchResponse:
    """
    Orchestrates the ResearchAgent, search tool, and FilterAgent to find
    vetted volunteer opportunities for the user.
    """
    search_query, opportunities = await run_volunteer_agent_flow_async(payload.user_request)
    return SearchResponse(search_query=search_query, opportunities=opportunities)


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask contextual questions about a single volunteer role.",
)
async def chat_with_inquiry_agent(payload: ChatRequest) -> ChatResponse:
    """
    Contextual Inquiry Agent endpoint.
    The agent answers **only** from the provided `full_text` for a single role.
    """
    answer = await run_inquiry_agent_async(
        full_text=payload.full_text,
        user_query=payload.user_query,
        chat_history=payload.chat_history,
    )
    return ChatResponse(answer=answer)


@router.post(
    "/saved",
    status_code=status.HTTP_201_CREATED,
    summary="Save a volunteer opportunity for the signed-in user.",
)
async def save_opportunity(
    opportunity: VolunteerOpportunity,
    user_id: str = Depends(get_current_user_id),
):
    await save_opportunity_to_db(user_id=user_id, opportunity=opportunity)
    return {"success": True}


@router.get(
    "/saved",
    response_model=List[VolunteerOpportunity],
    summary="Fetch the signed-in user's saved opportunities.",
)
async def get_saved_opportunities(user_id: str = Depends(get_current_user_id)):
    return await get_saved_roles(user_id=user_id)


@router.delete(
    "/saved/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove one of the signed-in user's saved opportunities.",
)
async def delete_saved_opportunity(
    opportunity_id: str,
    user_id: str = Depends(get_current_user_id),
):
    if not await delete_saved_role(user_id=user_id, opportunity_id=opportunity_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved role not found.")
