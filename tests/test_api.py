import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.models import RoadmapStepStatus

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "MindShift Coach"

def test_roadmap_endpoint():
    response = client.get("/api/roadmap")
    assert response.status_code == 200
    data = response.json()
    assert "current_week" in data
    assert "completion_percentage" in data
    assert len(data["weeks"]) == 4

def test_reframe_endpoint():
    payload = {
        "thought": "Non riesco mai a trovare clienti disposti a pagare il giusto.",
        "context": "Business & Micro-SaaS",
        "preferred_channel": None
    }
    response = client.post("/api/reframe", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["original_thought"] == payload["thought"]
    assert "detected_channel" in data
    assert "meta_model" in data
    assert len(data["reframes"]) >= 3
    assert "empowering_micro_action" in data

def test_toggle_roadmap_step():
    payload = {
        "step_id": "s1_step1",
        "status": "completed"
    }
    response = client.post("/api/roadmap/step/toggle", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_admin_overview_endpoint():
    response = client.get("/api/admin/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "total_active_testers" in data
    assert "total_saved_sessions" in data
    assert "total_feedback_ratings" in data
    assert "feedbacks" in data
    assert "recent_sessions" in data
