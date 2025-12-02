# src/models.py
from pydantic import BaseModel, Field


class VolunteerOpportunity(BaseModel):
    title: str = Field(description="The title of the volunteer role")
    organization: str = Field(description="Name of the NGO or group")
    location: str = Field(description="City or specific location")
    summary: str = Field(
        description="A 1-sentence summary of what the volunteer will do")
    url: str = Field(description="The direct link to apply or read more")


class OpportunityList(BaseModel):
    items: list[VolunteerOpportunity]
