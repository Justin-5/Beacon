import os
from functools import lru_cache

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


load_dotenv()

_bearer = HTTPBearer()


@lru_cache(maxsize=1)
def _jwks_client() -> jwt.PyJWKClient:
    url = os.getenv("CLERK_JWKS_URL")
    if not url:
        raise RuntimeError("CLERK_JWKS_URL is not set.")
    # PyJWKClient caches the fetched keys, so this is one network call per key rotation.
    return jwt.PyJWKClient(url)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    """
    Verify the Clerk session JWT from `Authorization: Bearer <token>` and
    return the user ID (`sub`). The user ID is never taken from the request body.
    """
    token = credentials.credentials
    try:
        key = _jwks_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(token, key.key, algorithms=["RS256"], leeway=5)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return claims["sub"]
