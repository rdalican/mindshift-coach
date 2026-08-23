import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_pair_device_generate_new_key():
    res = client.post("/api/sync/pair", json={"device_name": "Windows Desktop"})
    assert res.status_code == 200
    data = res.json()
    assert "sync_key" in data
    assert data["sync_key"].startswith("MIND-")
    assert data["plan_status"] == "trial"

def test_pair_device_existing_key():
    key = f"MIND-PAIR-{uuid.uuid4().hex[:6].upper()}"
    res1 = client.post("/api/sync/pair", json={"sync_key": key, "device_name": "Windows PC"})
    assert res1.status_code == 200
    
    # Pair second device (Android) with same key
    res2 = client.post("/api/sync/pair", json={"sync_key": key, "device_name": "Android Phone"})
    assert res2.status_code == 200
    assert res2.json()["sync_key"] == key

def test_sync_shifts_crud_flow():
    sync_key = f"MIND-FLOW-{uuid.uuid4().hex[:6].upper()}"
    shift_id = f"shift-{uuid.uuid4().hex[:8]}"
    
    # 1. Post new shift
    shift_payload = {
        "id": shift_id,
        "sync_key": sync_key,
        "original_thought": "Ho paura di sbagliare tutto.",
        "detected_channel": "Cinestesico (K)",
        "meta_category": "Generalizzazione",
        "meta_subtype": "Quantificatore Universale",
        "context_reframe": "La paura indica che questo obiettivo conta molto per te.",
        "meaning_reframe": "Non esiste fallimento, solo feedback utile.",
        "socratic_question": "Davvero sbaglieresti assolutamente 'tutto'?",
        "empowering_micro_action": "Scrivi la prima azione semplice.",
        "reframes": []
    }
    post_res = client.post("/api/sync/shifts", json=shift_payload)
    assert post_res.status_code == 200
    assert post_res.json()["id"] == shift_id

    # 2. Get shifts
    get_res = client.get(f"/api/sync/shifts?sync_key={sync_key}")
    assert get_res.status_code == 200
    shifts_data = get_res.json()
    assert shifts_data["count"] >= 1
    assert any(s["id"] == shift_id for s in shifts_data["shifts"])

    # 3. Delete shift
    del_res = client.delete(f"/api/sync/shifts/{shift_id}?sync_key={sync_key}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"
