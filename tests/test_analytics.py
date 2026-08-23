import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_vak_analytics_empty():
    sync_key = f"MIND-ANALYTICS-EMPTY-{uuid.uuid4().hex[:6].upper()}"
    res = client.get(f"/api/analytics/vak?sync_key={sync_key}")
    assert res.status_code == 200
    data = res.json()
    assert data["total_shifts"] == 0
    assert "distribution" in data

def test_vak_analytics_with_shifts():
    sync_key = f"MIND-ANALYTICS-FULL-{uuid.uuid4().hex[:6].upper()}"
    
    # Inserisci 2 shift visivi e 1 cinestesico
    shift1 = {
        "id": f"s1-{uuid.uuid4().hex[:6]}",
        "sync_key": sync_key,
        "original_thought": "Non vedo una prospettiva chiara.",
        "context": "Business",
        "detected_channel": "Visivo (V)",
        "meta_category": "Cancellazione",
        "meta_subtype": "Cancellazione Semplice",
        "context_reframe": "Allargando lo sguardo vedi le soluzioni.",
        "meaning_reframe": "La vista migliora con l'azione.",
        "socratic_question": "Cosa vedi se guardi oltre?",
        "empowering_micro_action": "Visualizza l'obiettivo.",
        "reframes": []
    }
    shift2 = {
        "id": f"s2-{uuid.uuid4().hex[:6]}",
        "sync_key": sync_key,
        "original_thought": "Vedo tutto buio nel mio lavoro.",
        "context": "Lavoro",
        "detected_channel": "Visivo (V)",
        "meta_category": "Distorsione",
        "meta_subtype": "Lettura del Pensiero",
        "context_reframe": "Il buio precede sempre l'alba.",
        "meaning_reframe": "La luce si accende con la prima mossa.",
        "socratic_question": "Dove c'è un barlume di luce?",
        "empowering_micro_action": "Accendi la luce.",
        "reframes": []
    }
    shift3 = {
        "id": f"s3-{uuid.uuid4().hex[:6]}",
        "sync_key": sync_key,
        "original_thought": "Sento un peso insostenibile sul petto.",
        "context": "Salute",
        "detected_channel": "Cinestesico (K)",
        "meta_category": "Generalizzazione",
        "meta_subtype": "Quantificatore Universale",
        "context_reframe": "Il peso è energia che si accumula.",
        "meaning_reframe": "La leggerezza è una scelta respiratoria.",
        "socratic_question": "Come trasformi il peso in spinta?",
        "empowering_micro_action": "Fai 3 respiri profondi.",
        "reframes": []
    }

    client.post("/api/sync/shifts", json=shift1)
    client.post("/api/sync/shifts", json=shift2)
    client.post("/api/sync/shifts", json=shift3)

    res = client.get(f"/api/analytics/vak?sync_key={sync_key}")
    assert res.status_code == 200
    data = res.json()
    assert data["total_shifts"] == 3
    assert data["distribution"]["visual_pct"] > 50.0
    assert "Visivo" in data["distribution"]["dominant_channel"]
    assert len(data["categories_breakdown"]) >= 2
