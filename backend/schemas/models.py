from __future__ import annotations

from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class VolunteerOpportunity(BaseModel):
    id: Optional[str] = Field(
        default=None, description="Unique ID from database")
    title: str = Field(default="Untitled Role",
                       description="The title of the volunteer role")
    organization: str = Field(
        default="Unknown Organization", description="Name of the NGO or group")
    location: str = Field(default="Remote/Unspecified",
                          description="City or specific location")
    summary: str = Field(default="No summary available.",
                         description="A 1-sentence summary")
    url: str = Field(
        default="", description="The direct link to apply or read more")
    full_text: Optional[str] = Field(
        default=None, description="Scraped content for RAG")


class OpportunityList(BaseModel):
    items: List[VolunteerOpportunity] = Field(
        default_factory=list,
        description="Structured list of vetted volunteer opportunities.",
    )


class SearchRequest(BaseModel):
    user_request: str = Field(
        description="Natural language description of what the user is looking for."
    )


class SearchResponse(BaseModel):
    message: str = Field(
        description="Natural language formatted response containing opportunities."
    )
    opportunities: List[VolunteerOpportunity] = Field(
        description="Structured list of vetted and filtered opportunities."
    )


class ChatMessage(BaseModel):
    """Simple chat message representation for the Inquiry Agent."""

    role: Literal["user", "assistant", "system"] = Field(
        description="Speaker role for the message."
    )
    content: str = Field(description="Text content of the message.")


class ChatRequest(BaseModel):
    full_text: str = Field(
        description=(
            "The scraped full_text for a single volunteer role. "
            "The Inquiry Agent must rely exclusively on this text."
        )
    )
    user_query: str = Field(
        description="The user's question about this specific role."
    )
    chat_history: Optional[List[ChatMessage]] = Field(
        default=None,
        description=(
            "Optional prior conversation turns for extra context. "
            "The agent should stay grounded in `full_text` regardless."
        ),
    )


class ChatResponse(BaseModel):
    answer: str = Field(
        description="The Inquiry Agent's answer grounded strictly in the provided full_text."
    )


class SaveRequest(BaseModel):
    """
    Request payload for saving a volunteer opportunity for a user.

    In a future iteration, `user_id` will be derived from Clerk,
    but for now it is accepted directly in the JSON body.
    """
    user_id: str = Field(
        description="The unique identifier for the user saving the opportunity."
    )
    opportunity: VolunteerOpportunity = Field(
        description="The volunteer opportunity the user wants to save."
    )
