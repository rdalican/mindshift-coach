import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_export_shifts_markdown():
    sync_key = f"MIND-EXP-MD-{uuid.uuid4().hex[:6].upper()}"
    shift = {
        "id": f"s-exp-{uuid.uuid4().hex[:6]}",
        "sync_key": sync_key,
        "original_thought": "Non ho abbastanza tempo.",
        "detected_channel": "Cinestesico (K)",
        "meta_category": "Cancellazione",
        "meta_subtype": "Comparativa Mancante",
        "context_reframe": "Il tempo è una questione di priorità.",
        "meaning_reframe": "Seleziona solo l'essenziale.",
        "identity_reframe": "Sei un architetto strategico.",
        "socratic_question": "Come organizzeresti 1 ora al giorno?",
        "empowering_micro_action": "Fai la prima cosa.",
        "anchoring_mantra": "Io genero lo spazio per crescere.",
        "reframes": []
    }
    client.post("/api/sync/shifts", json=shift)

    res = client.get(f"/api/export/shifts?sync_key={sync_key}&format=markdown")
    assert res.status_code == 200
    assert "text/markdown" in res.headers["content-type"]
    assert "MindShift Master" in res.text
    assert "Non ho abbastanza tempo." in res.text

def test_export_shifts_json():
    sync_key = f"MIND-EXP-JSON-{uuid.uuid4().hex[:6].upper()}"
    shift = {
        "id": f"s-exp-json-{uuid.uuid4().hex[:6]}",
        "sync_key": sync_key,
        "original_thought": "Tutti mi giudicano.",
        "detected_channel": "Uditivo (A)",
        "meta_category": "Generalizzazione",
        "meta_subtype": "Quantificatore Universale",
        "context_reframe": "Chi ti giudica è focalizzato su di te.",
        "meaning_reframe": "L'empatia è una grande risorsa.",
        "identity_reframe": "Sei un pioniere dei tuoi valori.",
        "socratic_question": "Davvero 'tutti'?",
        "empowering_micro_action": "Parla con una persona fidata.",
        "anchoring_mantra": "Cammino a testa alta.",
        "reframes": []
    }
    client.post("/api/sync/shifts", json=shift)

    res = client.get(f"/api/export/shifts?sync_key={sync_key}&format=json")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["original_thought"] == "Tutti mi giudicano."
