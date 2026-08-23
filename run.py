"""Script di avvio per MindShift Coach."""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"==================================================")
    print(f"🧠 {settings.APP_NAME} - PNL & Google Gemini")
    print(f"🌍 Ambiente: {settings.APP_ENV}")
    print(f"🚀 Server in avvio su: http://localhost:{settings.PORT}")
    print(f"📱 Accesso da Android (stessa rete Wi-Fi): http://<TUO-IP-LOCALE>:{settings.PORT}")
    print(f"==================================================")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
