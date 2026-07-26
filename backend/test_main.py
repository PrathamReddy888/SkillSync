import pytest
from fastapi.testclient import TestClient
from main import app, supabase
from unittest.mock import MagicMock, patch

client = TestClient(app)

@patch("main.supabase")
def test_get_leaderboard_success(mock_supabase):
    # Mocking Supabase query chain
    mock_query = MagicMock()
    mock_supabase.table.return_value.select.return_value = mock_query
    mock_query.order.return_value.range.return_value.execute.return_value = MagicMock(
        data=[{"username": "user1", "score": 100}, {"username": "user2", "score": 90}],
        count=2
    )
    
    response = client.get("/api/leaderboard?page=1&limit=2")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert "metadata" in json_data
    assert len(json_data["data"]) == 2
    assert json_data["data"][0]["rank"] == 1
    assert json_data["data"][1]["rank"] == 2
    assert json_data["metadata"]["total"] == 2
    assert json_data["metadata"]["page"] == 1

def test_get_leaderboard_invalid_page():
    response = client.get("/api/leaderboard?page=0")
    assert response.status_code == 400
    assert response.json()["detail"] == "Page must be >= 1"

def test_get_leaderboard_invalid_limit():
    response = client.get("/api/leaderboard?limit=150")
    assert response.status_code == 400
    assert response.json()["detail"] == "Limit must be between 1 and 100"
