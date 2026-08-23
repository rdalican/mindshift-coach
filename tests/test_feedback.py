import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_submit_reframe_feedback():
    sync_key = f"MIND-FEEDBACK-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "sync_key": sync_key,
        "shift_id": f"shift-{uuid.uuid4().hex[:6]}",
        "reframe_type": "Ristrutturazione di Significato",
        "rating": 5,
        "comment": "Risonanza fantastica, mi ha sbloccato immediatamente!"
    }
    res = client.post("/api/feedback/reframe", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["recorded_rating"] == 5
