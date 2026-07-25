"""
Tests for the /api/health and /api/generate-test endpoints.

Uses FastAPI's TestClient. Groq + Piston + Supabase are all unconfigured
in tests, so we exercise the fallback paths and the validation layer.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


# ────────────────────────────────────────────────────────────────────
# Health
# ────────────────────────────────────────────────────────────────────


def test_health_endpoint_returns_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["version"] == "3.0.0"
    assert "environment" in body
    assert isinstance(body["supabase_configured"], bool)
    assert isinstance(body["groq_configured"], bool)


def test_root_endpoint_returns_metadata(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "SkillSync API"
    assert body["health"] == "/api/health"


# ────────────────────────────────────────────────────────────────────
# /api/generate-test — validation
# ────────────────────────────────────────────────────────────────────


def test_generate_test_rejects_invalid_sector(client):
    resp = client.post(
        "/api/generate-test",
        json={
            "sector": "finance",  # not in ALLOWED_SECTORS
            "problem_description": "Build a trading dashboard",
        },
    )
    assert resp.status_code == 422
    body = resp.json()
    # FastAPI returns the field name in the detail
    assert any("sector" in str(err.get("loc", [])) for err in body.get("detail", []))


def test_generate_test_rejects_short_problem_description(client):
    resp = client.post(
        "/api/generate-test",
        json={
            "sector": "web_dev",
            "problem_description": "short",  # < 10 chars
        },
    )
    assert resp.status_code == 422


def test_generate_test_rejects_too_many_questions(client):
    resp = client.post(
        "/api/generate-test",
        json={
            "sector": "web_dev",
            "problem_description": "Build a real-time dashboard",
            "num_questions": 100,  # > 20
        },
    )
    assert resp.status_code == 422


def test_generate_test_rejects_invalid_difficulty(client):
    resp = client.post(
        "/api/generate-test",
        json={
            "sector": "web_dev",
            "problem_description": "Build a real-time dashboard",
            "difficulty": "Impossible",
        },
    )
    assert resp.status_code == 422


# ────────────────────────────────────────────────────────────────────
# /api/generate-test — fallback path (no GROQ_API_KEY in test env)
# ────────────────────────────────────────────────────────────────────


def test_generate_test_falls_back_when_groq_unconfigured(client):
    resp = client.post(
        "/api/generate-test",
        json={
            "sector": "web_dev",
            "problem_description": "Build a real-time dashboard with React and WebSockets.",
            "difficulty": "Medium",
            "num_questions": 5,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "title" in body
    assert isinstance(body["round1_questions"], list)
    assert len(body["round1_questions"]) == 5
    # Each question must have the expected keys.
    q = body["round1_questions"][0]
    assert {"id", "question", "options", "correct"} <= set(q.keys())
    assert len(q["options"]) == 4
    assert 0 <= q["correct"] <= 3


def test_generate_test_fallback_uses_sector_specific_questions(client):
    """Each sector must return its own question bank, not a generic one."""
    resp = client.post(
        "/api/generate-test",
        json={
            "sector": "cybersecurity",
            "problem_description": "Audit a fintech web application for vulnerabilities.",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    first_q = body["round1_questions"][0]["question"]
    # The cybersecurity bank has a specific first question about A/B/C/D family.
    assert "A is B's sister" in first_q


def test_generate_test_caches_identical_requests(client):
    """Two identical requests must hit the cache on the second call."""
    payload = {
        "sector": "data_ai",
        "problem_description": "Deploy an ML model with monitoring and A/B testing.",
        "difficulty": "Medium",
        "num_questions": 5,
    }
    r1 = client.post("/api/generate-test", json=payload)
    assert r1.status_code == 200
    r2 = client.post("/api/generate-test", json=payload)
    assert r2.status_code == 200
    # Cached response should be byte-identical in content.
    assert r1.json() == r2.json()


# ────────────────────────────────────────────────────────────────────
# /api/evaluate-code — validation + Piston-unavailable path
# ────────────────────────────────────────────────────────────────────


def test_evaluate_code_rejects_unknown_language(client):
    resp = client.post(
        "/api/evaluate-code",
        json={
            "code": "print('hi')",
            "language": "brainfuck",
        },
    )
    assert resp.status_code == 422


def test_evaluate_code_rejects_empty_code(client):
    resp = client.post(
        "/api/evaluate-code",
        json={
            "code": "",
            "language": "python",
        },
    )
    assert resp.status_code == 422


def test_evaluate_code_rejects_oversized_code(client):
    resp = client.post(
        "/api/evaluate-code",
        json={
            "code": "x" * 100_000,  # > 50_000 limit
            "language": "python",
        },
    )
    assert resp.status_code == 422
