import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App General Settings
    APP_NAME: str = "MindShift Coach"
    APP_ENV: str = "production"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    APP_BASE_URL: str = "http://localhost:8000"

    # Database Configuration (PostgreSQL Railway / SQLite Fallback)
    DATABASE_URL: str = "sqlite:///./mindshift.db"

    # Google Gemini AI Key & Models (Supporta chiavi AQ. e AIzaSy)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Monetizzazione & Stripe Micro-SaaS
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID: str = "price_mock_mindshift_monthly"
    STRIPE_PRICE_ID_MONTHLY: str = ""
    DEFAULT_PRICING_MONTHLY: str = "9.99"
    FREE_TRIAL_DAYS: int = 3

    # Monitoraggio & Zero Manutenzione
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Auto-fix per Railway PostgreSQL URL se formattato con postgres://
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
