"""Configurazione Database SQLAlchemy per MindShift Coach.
Supporta nativamente sia SQLite (in locale) che PostgreSQL (su Railway Cloud).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

db_url = settings.DATABASE_URL
# Fix per compatibilità Railway PostgreSQL (postgres:// -> postgresql://)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

is_sqlite = db_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

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
    """Crea le tabelle del database se non esistono già."""
    from app.core import db_models  # Importa i modelli prima del create_all
    Base.metadata.create_all(bind=engine)
