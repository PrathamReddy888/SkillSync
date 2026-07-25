"""
Auth dependency — verifies a Supabase-issued JWT and (optionally) checks
the bearer's role against an allowlist.

Usage:
    from app.auth import require_user, require_role

    @router.get("/me")
    async def me(user=Depends(require_user)):
        return {"id": user["sub"], "email": user.get("email")}

    @router.post("/challenges")
    async def create_challenge(
        user=Depends(require_role("company")),
        ...
    ):
        ...
"""
from typing import Dict, Optional, Sequence

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

# `HTTPBearer` auto-documents the endpoint as requiring a Bearer token.
_bearer = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> Dict:
    settings = get_settings()
    if not settings.supabase_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth is not configured on the server (SUPABASE_JWT_SECRET missing).",
        )
    try:
        # Supabase signs JWTs with the HS256 shared secret exposed in
        # the project dashboard. We verify both signature and expiry.
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )


def require_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Dict:
    """Verify the bearer token and return the decoded JWT payload."""
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Expected: Bearer <token>",
        )
    return _decode_token(creds.credentials)


def require_role(*allowed_roles: str):
    """
    Dependency factory: verify the token AND require one of the given
    roles. Roles come from the `user_metadata.role` claim that the
    SkillSync signup flow sets on the Supabase auth user.

    Usage:
        @router.post("/challenges", dependencies=[Depends(require_role("company"))])
    """
    allowed = set(allowed_roles)

    def _checker(user: Dict = Depends(require_user)) -> Dict:
        # `role` is stored in user_metadata during signup (see AuthContext.jsx).
        role = (
            user.get("user_metadata", {}).get("role")
            or user.get("role")  # fallback if placed at top-level
        )
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This endpoint requires one of the following roles: {sorted(allowed)}. "
                       f"Your role: {role!r}.",
            )
        return user

    return _checker
