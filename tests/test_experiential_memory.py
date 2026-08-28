import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal, get_db
from app.core.db_models import UserSyncProfile, SavedMindShift
from app.core.experiential_memory import ExperientialMemoryEngine
from app.core.models import MindShiftRequest, SessionStepRequest

client = TestClient(app)

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_experiential_memory_empty_sync_key(db_session: Session):
    test_key = "MIND-TEST-EMPTY-001"
    profile = ExperientialMemoryEngine.synthesize_profile(test_key, db_session)
    assert profile is not None
    assert profile.total_episodes_analyzed == 0
    assert profile.primary_vak_channel == "Cinestesico (K)"
    assert "In attesa" in profile.core_limiting_structures[0]

def test_experiential_memory_synthesis_with_shifts(db_session: Session):
    test_key = "MIND-TEST-MULTI-002"
    
    # Pulizia preliminare
    db_session.query(SavedMindShift).filter(SavedMindShift.sync_key == test_key).delete()
    db_session.query(UserSyncProfile).filter(UserSyncProfile.sync_key == test_key).delete()
    db_session.commit()

    # Creazione di 3 sessioni storiche
    shift1 = SavedMindShift(
        id="s1",
        sync_key=test_key,
        original_thought="Quando guido perdo la pazienza con i furbi al volante",
        context="guida",
        detected_channel="Cinestesico (K)",
        meta_category="Generalizzazione",
        meta_subtype="Reattività al volante",
        identity_reframe="Non sei un guidatore reattivo: sei il Sovrano del tuo Abitacolo e della Calma Regale",
        anchoring_mantra="Al volante domino il mio spazio interiore con calma regale",
        is_favorite=True
    )
    shift2 = SavedMindShift(
        id="s2",
        sync_key=test_key,
        original_thought="Al tavolo di Bridge mi blocco se l'avversario fa una licita inattesa",
        context="bridge",
        detected_channel="Visivo (V)",
        meta_category="Distorsione",
        meta_subtype="Lettura del pensiero al tavolo",
        identity_reframe="Non sei un calcolatore rigido: sei un Navigatore Strategico delle Probabilità",
        anchoring_mantra="Ogni carta rivelata compone la mappa fluida",
        is_favorite=False
    )
    shift3 = SavedMindShift(
        id="s3",
        sync_key=test_key,
        original_thought="Devo fare più attività fisica per contrastare la perdita di massa",
        context="salute",
        detected_channel="Cinestesico (K)",
        meta_category="Cancellazione",
        meta_subtype="Inerzia di partenza",
        identity_reframe="Non sei una persona pigra: sei il Custode Attivo della tua Longevità e Forza",
        anchoring_mantra="Mentre il corpo si muove, la mente si rasserena",
        is_favorite=True
    )
    db_session.add_all([shift1, shift2, shift3])
    db_session.commit()

    # Sintesi
    profile = ExperientialMemoryEngine.synthesize_profile(test_key, db_session)
    assert profile is not None
    assert profile.total_episodes_analyzed == 3
    assert profile.primary_vak_channel == "Cinestesico (K)"
    assert profile.vak_distribution["Cinestesico (K)"] == 2
    assert profile.vak_distribution["Visivo (V)"] == 1
    assert len(profile.unlocked_mastery_archetypes) >= 2
    assert len(profile.high_resonance_mantras) >= 2
    assert "3 sessioni nel Diario" in profile.clinical_synthesis_narrative

    # Test Formattazione Prompt
    prompt_block = ExperientialMemoryEngine.format_profile_for_prompt(profile)
    assert "PROFILO ESPERIENZIALE & MEMORIA CLINICA DELL'ACCOUNT" in prompt_block
    assert "Cinestesico (K)" in prompt_block

def test_api_account_memory_endpoints(db_session: Session):
    test_key = "MIND-TEST-API-003"
    
    # GET memory
    resp = client.get(f"/api/account/memory?sync_key={test_key}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["sync_key"] == test_key
    assert "profile" in data

    # POST rebuild
    resp_rebuild = client.post("/api/account/memory/rebuild", json={"sync_key": test_key})
    assert resp_rebuild.status_code == 200
    rebuild_data = resp_rebuild.json()
    assert rebuild_data["sync_key"] == test_key
