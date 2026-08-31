"""Configurazione Database SQLAlchemy per MindShift Coach.
Supporta nativamente sia SQLite (in locale) che PostgreSQL (su Railway Cloud).
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("mindshift.database")

db_url = settings.DATABASE_URL
# Fix per compatibilità Railway PostgreSQL (postgres:// -> postgresql://)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

is_sqlite = db_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

try:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True
    )
except Exception as e:
    logger.warning(f"Errore creazione engine per {db_url}: {e}. Fallback su SQLite.")
    engine = create_engine("sqlite:///./mindshift.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency injection per le route FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Crea le tabelle del database se non esistono già e applica migrazioni automatiche."""
    try:
        from app.core import db_models  # Importa i modelli prima del create_all
        Base.metadata.create_all(bind=engine)

        # Migrazione automatica colonne per compatibilità con database esistenti
        migrations = [
            "ALTER TABLE user_sync_profiles ADD COLUMN experiential_profile_json TEXT",
            "ALTER TABLE user_sync_profiles ADD COLUMN memory_updated_at TIMESTAMP",
            "ALTER TABLE user_sync_profiles ADD COLUMN visit_count INTEGER DEFAULT 1",
            "ALTER TABLE user_sync_profiles ADD COLUMN last_visit_at TIMESTAMP"
        ]
        for stmt in migrations:
            try:
                with engine.begin() as conn:
                    conn.execute(text(stmt))
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Attenzione: init_db ritardato o fallback: {e}")
