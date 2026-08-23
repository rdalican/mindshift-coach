import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.core.db_models import UserSyncProfile, SavedMindShift

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

def test_user_sync_profile_creation():
    db = TestSessionLocal()
    unique_key = f"MIND-TEST-{uuid.uuid4().hex[:6].upper()}"
    try:
        profile = UserSyncProfile(
            sync_key=unique_key,
            email="test@mindshift.ai",
            device_name="Test Windows PC",
            plan_status="trial"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

        assert profile.id is not None
        assert profile.sync_key == unique_key
        assert profile.plan_status == "trial"
    finally:
        db.close()

def test_saved_mindshift_creation_and_query():
    db = TestSessionLocal()
    unique_id = f"shift-{uuid.uuid4().hex[:8]}"
    unique_key = f"MIND-TEST-{uuid.uuid4().hex[:6].upper()}"
    try:
        shift = SavedMindShift(
            id=unique_id,
            sync_key=unique_key,
            original_thought="Non sono abbastanza veloce nel lavoro.",
            detected_channel="Cinestesico (K)",
            meta_category="Cancellazione",
            meta_subtype="Comparativa Mancante",
            context_reframe="La velocità non è sempre sinonimo di qualità.",
            meaning_reframe="La precisione protegge da errori costosi.",
            socratic_question="Veloce rispetto a quale standard oggettivo?",
            empowering_micro_action="Fai 3 respiri profondi."
        )
        db.add(shift)
        db.commit()
        db.refresh(shift)

        queried = db.query(SavedMindShift).filter(SavedMindShift.id == unique_id).first()
        assert queried is not None
        assert queried.original_thought == "Non sono abbastanza veloce nel lavoro."
        assert queried.sync_key == unique_key
        assert queried.detected_channel == "Cinestesico (K)"
    finally:
        db.close()
