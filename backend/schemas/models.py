from __future__ import annotations

from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class OpportunityBase(BaseModel):
    """Fields the FilterAgent extracts. Kept separate so the LLM never echoes `full_text` back."""

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


class VolunteerOpportunity(OpportunityBase):
    id: Optional[str] = Field(
        default=None, description="Unique ID from database")
    full_text: Optional[str] = Field(
        default=None, description="Scraped content for RAG")


class SearchRequest(BaseModel):
    user_request: str = Field(
        min_length=1,
        max_length=500,
        description="Natural language description of what the user is looking for.",
    )


class SearchResponse(BaseModel):
    search_query: str = Field(
        description="The keyword query the ResearchAgent generated.")
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
        max_length=10_000,
        description=(
            "The scraped full_text for a single volunteer role. "
            "The Inquiry Agent must rely exclusively on this text."
        ),
    )
    user_query: str = Field(
        min_length=1,
        max_length=1000,
        description="The user's question about this specific role.",
    )
    chat_history: List[ChatMessage] = Field(
        default_factory=list,
        max_length=20,
        description=(
            "Prior conversation turns for extra context. "
            "The agent should stay grounded in `full_text` regardless."
        ),
    )


class ChatResponse(BaseModel):
    answer: str = Field(
        description="The Inquiry Agent's answer grounded strictly in the provided full_text."
    )
