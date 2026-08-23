# 🧠 MindShift Coach - PNL & Google Gemini AI

Applicazione Micro-SaaS di Reframing cognitivo, decostruzione dei blocchi mentali e trasformazione degli stati emotivi potenziata dal **Meta-Modello della Programmazione Neuro-Linguistica (PNL)** e da **Google Gemini Flash**.

Progettata per operare in ambiente **Cloud**, installabile nativamente su **Windows** e **Android** tramite architettura **Progressive Web App (PWA)**, e strutturata secondo la **Roadmap di Lancio in 4 Settimane per la Rendita Passiva** (Paragrafo 6 del report strategico).

---

## 👥 Architettura di Sviluppo Multi-Agentica

Lo sviluppo dell'applicazione è guidato da una squadra a 5 ruoli agentici integrati:
1. **Agente 1 (QA & Controllo Errori)**: Valida la robustezza del codice, le eccezioni e i test di regressione.
2. **Agente 2 (Suggerimento Modifiche & Feature)**: Propone ottimizzazioni di performance, riduzione dei costi token e migliorie UX.
3. **Agente 3 (Analisi di Impatto)**: Valuta l'impatto di ogni modifica sull'architettura e sulla retrocompatibilità.
4. **Agente 4 (Monitoraggio Roadmap & Progresso)**: Traccia millimetricamente l'avanzamento delle 4 settimane del report con feedback loop utente.
5. **Agente Supervisor / Lead (Antigravity)**: Coordina la sintesi, integra la **GEM Esperto PNL** e la **GEM Programmatore** e richiede l'approvazione utente.

---

## 🚀 Avvio Rapido

### 1. Requisiti
- Python 3.10+
- Connessione Internet (per CDN e Gemini API)

### 2. Installazione Dipendenze
```bash
pip install -r requirements.txt
```

### 3. Configurazione (.env)
Se desideri abilitare l'IA di Google Gemini, aggiungi la tua chiave in `.env`:
```env
GEMINI_API_KEY="tua-chiave-api"
GEMINI_MODEL="gemini-1.5-flash"
```
*Nota: Se la chiave non viene inserita, l'applicazione attiva automaticamente il Motore PNL Euristico Offline, rimanendo funzionante al 100%.*

### 4. Avvio Server
- **Su Windows**: Doppio click su `AVVIA_MINDSHIFT.bat` oppure esegui:
```bash
python run.py
```
- **Accesso Browser**: `http://localhost:8000`
- **Accesso da Smartphone Android**: Apri Chrome su Android all'indirizzo `http://<IP-DEL-TUO-PC>:8000` e tocca **"Installa App"** o **"Aggiungi a schermata Home"**.

---

## 🧪 Esecuzione Test Automatici
```bash
pytest
```

---

## 🗺️ Roadmap di Lancio in 4 Settimane (Paragrafo 6)
- **Settimana 1: Validazione & MVP** *(Completata)*: Prototipo funzionante, motore PNL (VAK + Meta-Modello), interfaccia PWA Windows/Android.
- **Settimana 2: Integrazione & Pagamenti**: Database SQLite/PostgreSQL, Stripe Checkout (9,99€/m) e deploy Cloud (Railway/Render).
- **Settimana 3: Beta Testing & UX PNL Avanzata**: Diario dei reframing, statistiche VAK nel tempo e onboarding in 2 minuti.
- **Settimana 4: Automazione & Lancio Passivo**: Sentry monitoring autonomo, funnel di traffico organico (TikTok/Reels) e lancio Micro-SaaS.
