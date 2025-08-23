from __future__ import annotations

import functools
from datetime import datetime, timezone
from typing import Annotated, Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel

# ----------------------------
# Settings (env-driven)
# ----------------------------

class AuthSettings(BaseModel):
    """Auth config read from environment."""
    algorithm: str = "HS256"
    secret: str
    issuer: Optional[str] = None
    audience: Optional[str] = None


def get_auth_settings() -> AuthSettings:
    import os
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not set")
    return AuthSettings(
        secret=secret,
        algorithm=os.getenv("JWT_ALG", "HS256"),
        issuer=os.getenv("JWT_ISSUER") or None,
        audience=os.getenv("JWT_AUD") or None,
    )

# ----------------------------
# Utilities
# ----------------------------

class Principal(BaseModel):
    """Authenticated principal embedded in request.state/user context."""
    sub: str
    scopes: list[str] = []
    claims: Dict[str, Any] = {}

def _extract_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return auth[7:].strip()


def _validate_time(claims: Dict[str, Any]) -> None:
    now = datetime.now(tz=timezone.utc).timestamp()
    if "exp" in claims and float(claims["exp"]) < now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    if "nbf" in claims and float(claims["nbf"]) > now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not yet valid")


def _validate_standard_claims(claims: Dict[str, Any], settings: AuthSettings) -> None:
    if settings.issuer and claims.get("iss") != settings.issuer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid issuer")
    aud = settings.audience
    if aud:
        token_aud = claims.get("aud")
        if token_aud != aud and (not isinstance(token_aud, list) or aud not in token_aud):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience")

# ----------------------------
# Public dependencies
# ----------------------------


def require_auth(required_scopes: Optional[list[str]] = None):
    """Factory that returns a FastAPI dependency to enforce JWT auth.

    Args:
        required_scopes: Optional list of scopes that must be present in `scope` or `scp` claim.

    Returns:
        A dependency usable with Depends(...).
    """
    required_scopes = required_scopes or []


    def _dep(request: Request, settings: Annotated[AuthSettings, Depends(get_auth_settings)]) -> Principal:
        token = _extract_bearer_token(request)
        try:
            # For HS256 shared-secret verification
            claims = jwt.decode(
                token,
                key=settings.secret,
                algorithms=[settings.algorithm],
                options={"require": ["exp", "iat"], "verify_signature": True, "verify_aud": False},
            )
        except jwt.PyJWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}") from exc

        _validate_time(claims)
        _validate_standard_claims(claims, settings)

        scopes: list[str] = []
        if isinstance(claims.get("scp"), list):
            scopes = [str(s) for s in claims["scp"]]
        elif isinstance(claims.get("scope"), str):
            scopes = claims["scope"].split()

        # Checking required scopes
        missing = [s for s in required_scopes if s not in scopes]
        if missing:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing scopes: {missing}")

        sub = str(claims.get("sub") or "")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject")

        return Principal(sub=sub, scopes=scopes, claims=claims)

    return _dep
