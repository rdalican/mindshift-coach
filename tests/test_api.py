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

def test_session_step_endpoints_flow():
    # Step 1: Chiarimento Contesto
    p1 = {
        "current_step": 1,
        "initial_thought": "Quando gioco a Bridge mi blocco dopo la licita.",
        "context": "Bridge & Giochi Strategici"
    }
    r1 = client.post("/api/session/step", json=p1)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["current_step"] == 1
    assert d1["next_step"] == 2
    assert d1["is_final_step"] is False
    assert len(d1["investigation_questions"]) >= 1

    # Step 2: Cause Storiche
    p2 = {
        "current_step": 2,
        "initial_thought": "Quando gioco a Bridge mi blocco dopo la licita.",
        "context": "Bridge & Giochi Strategici",
        "latest_user_response": "Succede quando il compagno fa una dichiarazione inaspettata."
    }
    r2 = client.post("/api/session/step", json=p2)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["current_step"] == 2
    assert d2["next_step"] == 3

    # Step 3: Influenze Esterne
    p3 = {
        "current_step": 3,
        "initial_thought": "Quando gioco a Bridge mi blocco dopo la licita.",
        "context": "Bridge & Giochi Strategici",
        "latest_user_response": "È iniziato 5 anni fa durante un torneo importante dove abbiamo perso."
    }
    r3 = client.post("/api/session/step", json=p3)
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["current_step"] == 3
    assert d3["next_step"] == 4

    # Step 4: Sintesi Finale
    p4 = {
        "current_step": 4,
        "initial_thought": "Quando gioco a Bridge mi blocco dopo la licita.",
        "context": "Bridge & Giochi Strategici",
        "latest_user_response": "Temo il giudizio del mio compagno e cerco di non sbagliare."
    }
    r4 = client.post("/api/session/step", json=p4)
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["is_final_step"] is True
    assert d4["final_shift"] is not None
    assert len(d4["final_shift"]["reframes"]) >= 3

def test_master_audio_tracks_endpoint():
    response = client.get("/api/audio/tracks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    assert any("ancoraggio_parasimpatico" in t["id"] for t in data)

def test_tts_synthesize_endpoint():
    payload = {
        "text": "Respira profondamente e ascolta questa guida.",
        "voice": "it-IT-DiegoNeural",
        "rate": "-10%",
        "pitch": "+0Hz"
    }
    response = client.post("/api/tts/synthesize", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert len(response.content) > 100


