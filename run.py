"""Script di avvio universale per MindShift Coach (Locale & Railway Cloud)."""
import os
import uvicorn
from app.config import settings

if __name__ == "__main__":
    port_str = os.getenv("PORT", str(settings.PORT or 8080))
    port = int(port_str)
    host = "0.0.0.0"

    print(f"==================================================")
    print(f"🧠 {settings.APP_NAME} - PNL Master Coaching & Google Gemini")
    print(f"🌍 Ambiente: {settings.APP_ENV}")
    print(f"🚀 Server in ascolto su: http://{host}:{port}")
    print(f"==================================================")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
