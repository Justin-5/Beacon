import os
import asyncio
from typing import Any, Dict

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

