"""Sistema di Monitoraggio, Telemetria & Diagnostica per MindShift Coach.
Garantisce la resilienza a zero-manutenzione per il deployment in cloud (Railway).
"""

import time
import logging
from typing import Dict, Any
from app.config import settings
from app.core.database import SessionLocal
from sqlalchemy import text

logger = logging.getLogger("mindshift.monitoring")

class SystemMonitor:
    """Monitor autonomo di stato e salute dei servizi critici."""

    def __init__(self):
        self.start_time = time.time()

    def get_uptime_seconds(self) -> float:
        return round(time.time() - self.start_time, 2)

    def check_database_health(self) -> Dict[str, Any]:
        start = time.time()
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            latency_ms = round((time.time() - start) * 1000, 2)
            return {
                "status": "operational",
                "engine": "postgresql" if "postgres" in settings.DATABASE_URL else "sqlite",
                "latency_ms": latency_ms
            }
        except Exception as e:
            logger.error(f"Errore connessione database: {e}")
            return {
                "status": "degraded",
                "error": str(e),
                "latency_ms": round((time.time() - start) * 1000, 2)
            }

    def check_gemini_config(self) -> Dict[str, Any]:
        has_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
        return {
            "status": "configured" if has_key else "missing_key",
            "model_configured": settings.GEMINI_MODEL,
            "key_type": "AQ_Studio" if settings.GEMINI_API_KEY.startswith("AQ.") else "AIzaSy_Legacy" if settings.GEMINI_API_KEY.startswith("AIzaSy") else "Custom"
        }

    def check_stripe_config(self) -> Dict[str, Any]:
        has_secret = bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.strip())
        has_webhook = bool(settings.STRIPE_WEBHOOK_SECRET and settings.STRIPE_WEBHOOK_SECRET.strip())
        return {
            "status": "live" if has_secret else "mock_mode",
            "secret_key_present": has_secret,
            "webhook_configured": has_webhook,
            "monthly_price": f"€{settings.DEFAULT_PRICING_MONTHLY}/mese",
            "trial_days": settings.FREE_TRIAL_DAYS
        }

    def run_full_diagnostics(self) -> Dict[str, Any]:
        db_health = self.check_database_health()
        gemini_health = self.check_gemini_config()
        stripe_health = self.check_stripe_config()

        overall_status = "healthy"
        if db_health["status"] != "operational":
            overall_status = "unhealthy"

        return {
            "status": overall_status,
            "app_name": settings.APP_NAME,
            "version": "0.4.0",
            "uptime_seconds": self.get_uptime_seconds(),
            "environment": settings.APP_ENV,
            "components": {
                "database": db_health,
                "ai_engine": gemini_health,
                "monetization": stripe_health
            }
        }

system_monitor = SystemMonitor()
