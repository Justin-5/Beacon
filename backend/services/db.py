import os
import asyncio
from typing import Any, Dict, List

from dotenv import load_dotenv
from supabase import create_client

from ..schemas.models import VolunteerOpportunity


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def _get_supabase_client():
    """
    Lazily initialize and return a singleton Supabase client.

    This avoids re-creating the client on every request while still
    deferring initialization until the credentials are available.
    """
    global _supabase_client  # type: ignore[assignment]

    if "_supabase_client" not in globals():
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError(
                "Supabase configuration is missing. "
                "Ensure SUPABASE_URL and SUPABASE_KEY are set in the environment."
            )
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

    return _supabase_client  # type: ignore[return-value]


async def save_opportunity_to_db(
    user_id: str,
    opportunity: VolunteerOpportunity,
) -> Dict[str, Any]:
    """
    Persist a single volunteer opportunity for a given user in Supabase.

    Assumes there is a `saved_opportunities` table with at least:
      - user_id (text)
      - title (text)
      - organization (text)
      - location (text)
      - summary (text)
      - url (text)
    """
    client = _get_supabase_client()

    payload = {
        "user_id": user_id,
        **opportunity.model_dump(),
    }

    def _insert():
        return client.table("saved_opportunities").insert(payload).execute()

    response = await asyncio.to_thread(_insert)

    # supabase-py returns an object with `data` and `error` attributes
    error = getattr(response, "error", None)
    if error:
        raise RuntimeError(f"Supabase insert failed: {error}")

    data = getattr(response, "data", None)
    # Return whatever Supabase returned so callers can inspect if needed.
    return data or payload


async def get_saved_roles(user_id: str) -> List[VolunteerOpportunity]:
    """
    Fetch all saved volunteer opportunities for a given user.

    Returns a list of `VolunteerOpportunity` instances to align with
    the public API schema.
    """
    client = _get_supabase_client()

    def _select():
        return (
            client.table("saved_opportunities")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

    response = await asyncio.to_thread(_select)

    error = getattr(response, "error", None)
    if error:
        raise RuntimeError(f"Supabase select failed: {error}")

    rows = getattr(response, "data", []) or []

    opportunities: List[VolunteerOpportunity] = []
    for row in rows:
        # Map only the fields defined on VolunteerOpportunity
        try:
            opportunities.append(
                VolunteerOpportunity(
                    title=row.get("title", ""),
                    organization=row.get("organization", ""),
                    location=row.get("location", ""),
                    summary=row.get("summary", ""),
                    url=row.get("url", ""),
                    full_text=row.get("full_text", ""),
                )
            )
        except Exception:
            # Skip any malformed row rather than failing the whole request
            continue

    return opportunities
