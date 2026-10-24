import os
import asyncio
from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from supabase import Client, create_client

from ..schemas.models import VolunteerOpportunity


load_dotenv()

TABLE = "saved_opportunities"
_FIELDS = set(VolunteerOpportunity.model_fields)


@lru_cache(maxsize=1)
def _client() -> Client:
    url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set.")
    return create_client(url, key)


async def save_opportunity_to_db(user_id: str, opportunity: VolunteerOpportunity) -> None:
    # `id` is assigned by the database.
    payload = {"user_id": user_id, **opportunity.model_dump(exclude={"id"})}
    await asyncio.to_thread(lambda: _client().table(TABLE).insert(payload).execute())


async def get_saved_roles(user_id: str) -> List[VolunteerOpportunity]:
    response = await asyncio.to_thread(
        lambda: _client().table(TABLE).select("*").eq("user_id", user_id).execute()
    )
    return [
        VolunteerOpportunity(**{
            **{k: v for k, v in row.items() if k in _FIELDS and v is not None},
            "id": str(row["id"]),
        })
        for row in response.data or []
    ]


async def delete_saved_role(user_id: str, opportunity_id: str) -> bool:
    """Delete one saved role. Scoped by user_id so users can only delete their own rows."""
    response = await asyncio.to_thread(
        lambda: _client().table(TABLE).delete()
        .eq("id", opportunity_id).eq("user_id", user_id).execute()
    )
    return bool(response.data)
