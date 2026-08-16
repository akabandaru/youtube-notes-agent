import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Verify backend health check returns status online."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "notes_saved_count" in data

def test_generate_notes_invalid_url():
    """Verify 400 error when invalid YouTube URL is submitted."""
    response = client.post("/api/generate-notes", json={"url": "not_a_valid_youtube_url"})
    assert response.status_code == 400
    assert "Invalid YouTube URL" in response.json()["detail"]

def test_history_endpoint():
    """Verify history endpoint returns a list."""
    response = client.get("/api/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
