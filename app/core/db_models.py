"""Modelli Relazionali SQLAlchemy per MindShift Coach.
Gestisce profili di sincronizzazione cross-device, storico delle sessioni Master PNL, abbonamenti e feedback.
"""

from datetime import datetime, timezone
import json
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class UserSyncProfile(Base):
    """Profilo di accoppiamento per sincronizzazione cloud tra Windows e Android."""
    __tablename__ = "user_sync_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sync_key = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=True, index=True)
    device_name = Column(String(100), nullable=True, default="Primary Device")
    preferred_vak = Column(String(50), nullable=True)
    plan_status = Column(String(50), default="trial")
    trial_ends_at = Column(DateTime, nullable=True)
    experiential_profile_json = Column(Text, nullable=True)
    memory_updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    last_sync_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class SavedMindShift(Base):
    """Sessione di Coaching Master PNL salvata e sincronizzata sul Cloud."""
    __tablename__ = "saved_mindshifts"

    id = Column(String(64), primary_key=True, index=True)
    sync_key = Column(String(64), index=True, nullable=False)
    original_thought = Column(Text, nullable=False)
    context = Column(String(100), nullable=True)
    detected_channel = Column(String(50), nullable=False)
    meta_category = Column(String(50), nullable=False)
    meta_subtype = Column(String(100), nullable=False)
    meta_explanation = Column(Text, nullable=True)
    
    # 4 Ristrutturazioni
    context_reframe = Column(Text, nullable=True)
    meaning_reframe = Column(Text, nullable=True)
    identity_reframe = Column(Text, nullable=True)
    socratic_question = Column(Text, nullable=True)
    empowering_micro_action = Column(Text, nullable=True)
    anchoring_mantra = Column(Text, nullable=True)
    
    # JSON aggregati
    reframes_json = Column(Text, nullable=True)
    protocol_json = Column(Text, nullable=True)
    action_plan_json = Column(Text, nullable=True)
    
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    def to_dict(self):
        reframes = []
        if self.reframes_json:
            try:
                reframes = json.loads(self.reframes_json)
            except Exception:
                reframes = []

        anchoring_protocol = None
        if self.protocol_json:
            try:
                anchoring_protocol = json.loads(self.protocol_json)
            except Exception:
                anchoring_protocol = None

        action_plan = None
        if self.action_plan_json:
            try:
                action_plan = json.loads(self.action_plan_json)
            except Exception:
                action_plan = None

        return {
            "id": self.id,
            "sync_key": self.sync_key,
            "original_thought": self.original_thought,
            "context": self.context,
            "detected_channel": self.detected_channel,
            "meta_category": self.meta_category,
            "meta_subtype": self.meta_subtype,
            "meta_explanation": self.meta_explanation or "",
            "context_reframe": self.context_reframe,
            "meaning_reframe": self.meaning_reframe,
            "identity_reframe": self.identity_reframe or "",
            "socratic_question": self.socratic_question,
            "empowering_micro_action": self.empowering_micro_action,
            "anchoring_mantra": self.anchoring_mantra or "",
            "reframes": reframes,
            "anchoring_protocol": anchoring_protocol,
            "action_plan": action_plan,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class SubscriptionRecord(Base):
    """Storico abbonamenti e pagamenti Stripe per il Micro-SaaS."""
    __tablename__ = "subscription_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sync_key = Column(String(64), index=True, nullable=False)
    stripe_customer_id = Column(String(100), nullable=True)
    stripe_subscription_id = Column(String(100), nullable=True)
    plan = Column(String(50), default="monthly_9.99")
    status = Column(String(50), default="active")
    amount = Column(String(20), default="9.99")
    created_at = Column(DateTime, default=utc_now)

class ReframeFeedback(Base):
    """Feedback e gradimento dell'utente (1-5 stelle) sulle sessioni PNL."""
    __tablename__ = "reframe_feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sync_key = Column(String(64), index=True, nullable=False)
    shift_id = Column(String(64), index=True, nullable=False)
    reframe_type = Column(String(100), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
