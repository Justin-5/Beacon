"""API tests with Gemini, Google Search, Supabase and Clerk's JWKS all stubbed out."""
import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from backend.main import app
from backend.api import routes
from backend.schemas.models import OpportunityBase
from backend.services import agents, auth

client = TestClient(app, raise_server_exceptions=False)
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(autouse=True)
def fake_jwks(monkeypatch):
    signing_key = SimpleNamespace(key=KEY.public_key())
    monkeypatch.setattr(auth, "_jwks_client", lambda: SimpleNamespace(
        get_signing_key_from_jwt=lambda token: signing_key))


def token(sub="user_123", key=KEY, exp_in=60):
    return jwt.encode({"sub": sub, "exp": int(time.time()) + exp_in}, key, algorithm="RS256")


def test_search_pipeline_attaches_scraped_text(monkeypatch):
    results = [
        {"title": "Teach kids", "link": "https://bhumi.ngo/a", "snippet": "", "full_text": "PAGE A"},
        {"title": "Donate now", "link": "https://bhumi.ngo/b", "snippet": "", "full_text": "PAGE B"},
    ]

    async def fake_search(query):
        assert query == "teaching volunteer Bengaluru"
        return results

    async def fake_generate(prompt, schema=None):
        if schema is None:
            return "teaching volunteer Bengaluru"
        assert "PAGE B" in prompt  # FilterAgent sees scraped text
        return [OpportunityBase(title="Teach kids", organization="Bhumi", url="https://bhumi.ngo/a")]

    monkeypatch.setattr(agents, "search_volunteer_sites", fake_search)
    monkeypatch.setattr(agents, "_generate", fake_generate)

    res = client.post("/api/search", json={"user_request": "teach kids in Bangalore"})

    assert res.status_code == 200
    body = res.json()
    assert body["search_query"] == "teaching volunteer Bengaluru"
    assert [o["full_text"] for o in body["opportunities"]] == ["PAGE A"]


def test_search_rejects_empty_request():
    assert client.post("/api/search", json={"user_request": ""}).status_code == 422


def test_unhandled_error_is_generic_json_with_cors(monkeypatch):
    async def boom(user_request):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(routes, "run_volunteer_agent_flow_async", boom)
    res = client.post("/api/search", json={"user_request": "x"},
                      headers={"Origin": "http://localhost:3000"})

    assert res.status_code == 500
    assert "secret" not in res.text
    assert res.headers["access-control-allow-origin"] == "http://localhost:3000"


@pytest.mark.parametrize("headers", [
    {},
    {"Authorization": "Bearer not-a-jwt"},
    {"Authorization": f"Bearer {token(exp_in=-60)}"},
    {"Authorization": f"Bearer {token(key=rsa.generate_private_key(public_exponent=65537, key_size=2048))}"},
])
def test_saved_rejects_missing_bad_expired_or_forged_tokens(headers):
    assert client.get("/api/saved", headers=headers).status_code in (401, 403)


def test_saved_uses_user_id_from_token_not_request(monkeypatch):
    seen = {}

    async def fake_get(user_id):
        seen["user_id"] = user_id
        return []

    monkeypatch.setattr(routes, "get_saved_roles", fake_get)
    res = client.get("/api/saved?user_id=someone_else",
                     headers={"Authorization": f"Bearer {token('user_123')}"})

    assert res.status_code == 200
    assert seen["user_id"] == "user_123"


def test_delete_missing_role_is_404(monkeypatch):
    async def fake_delete(user_id, opportunity_id):
        return False

    monkeypatch.setattr(routes, "delete_saved_role", fake_delete)
    res = client.delete("/api/saved/42", headers={"Authorization": f"Bearer {token()}"})
    assert res.status_code == 404
