"""
Tests for the auth dependency — JWT verification + role checks.
"""
import time

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import require_user, require_role


def _make_token(role: str = "applicant", secret: str = "test-secret-for-jwt-signing-only") -> str:
    payload = {
        "sub": "user-123",
        "email": "test@skillsync.dev",
        "exp": int(time.time()) + 3600,
        "aud": "authenticated",
        "user_metadata": {"role": role},
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def auth_app():
    app = FastAPI()

    @app.get("/me")
    async def me(user=Depends(require_user)):
        return {"id": user["sub"], "email": user.get("email")}

    @app.post("/company-only")
    async def company_only(user=Depends(require_role("company"))):
        return {"ok": True, "id": user["sub"]}

    @app.post("/multi-role")
    async def multi_role(user=Depends(require_role("company", "employee"))):
        return {"ok": True}

    return app


def test_require_user_rejects_missing_token(auth_app):
    with TestClient(auth_app) as c:
        resp = c.get("/me")
        assert resp.status_code == 401
        assert "Missing Authorization" in resp.json()["detail"]


def test_require_user_rejects_malformed_token(auth_app):
    with TestClient(auth_app) as c:
        resp = c.get("/me", headers={"Authorization": "Bearer not.a.jwt"})
        assert resp.status_code == 401
        assert "Invalid token" in resp.json()["detail"]


def test_require_user_accepts_valid_token(auth_app):
    token = _make_token(role="applicant")
    with TestClient(auth_app) as c:
        resp = c.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == "user-123"
        assert body["email"] == "test@skillsync.dev"


def test_require_role_rejects_wrong_role(auth_app):
    token = _make_token(role="applicant")
    with TestClient(auth_app) as c:
        resp = c.post("/company-only", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
        assert "company" in resp.json()["detail"]


def test_require_role_accepts_correct_role(auth_app):
    token = _make_token(role="company")
    with TestClient(auth_app) as c:
        resp = c.post("/company-only", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200


def test_require_role_accepts_one_of_multiple_allowed_roles(auth_app):
    token_emp = _make_token(role="employee")
    token_co = _make_token(role="company")
    with TestClient(auth_app) as c:
        assert c.post("/multi-role", headers={"Authorization": f"Bearer {token_emp}"}).status_code == 200
        assert c.post("/multi-role", headers={"Authorization": f"Bearer {token_co}"}).status_code == 200


def test_expired_token_is_rejected(auth_app):
    payload = {
        "sub": "user-123",
        "exp": int(time.time()) - 10,  # expired 10s ago
        "aud": "authenticated",
        "user_metadata": {"role": "applicant"},
    }
    token = jwt.encode(payload, "test-secret-for-jwt-signing-only", algorithm="HS256")
    with TestClient(auth_app) as c:
        resp = c.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"].lower()
