
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_invalid_travel_request():
    response = client.post(
        "/api/travel/plan",
        json={"user_request": "Hi"}
    )
    assert response.status_code == 422

def test_travel_plan_success(monkeypatch):
    from agent.workflow import run_travel_workflow

    def mock_workflow(**kwargs):
        return "Mock Goa travel itinerary"

    monkeypatch.setattr(
        "agent.workflow.run_travel_workflow",
        mock_workflow
    )

    response = client.post(
        "/api/travel/plan",
        json={
            "user_request": "Plan a Goa trip",
            "origin": "Mumbai",
            "destination": "Goa"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["itinerary"] == "Mock Goa travel itinerary"

def test_travel_plan_failure(monkeypatch):
    def mock_workflow(**kwargs):
        raise RuntimeError("Simulated workflow failure")

    monkeypatch.setattr(
        "agent.workflow.run_travel_workflow",
        mock_workflow
    )

    response = client.post(
        "/api/travel/plan",
        json={
            "user_request": "Plan a Goa trip",
            "origin": "Mumbai",
            "destination": "Goa"
        }
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Travel planning failed. Check the backend logs."
    )
