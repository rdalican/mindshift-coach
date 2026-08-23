# ☁️ Guida Ufficiale al Deploy su Railway.com
## MindShift Coach (Database Condiviso Windows ↔ Android)

Questa guida ti accompagna passo-passo nella pubblicazione di **MindShift Coach** sul tuo account **Railway.com** (sfruttando il tuo piano esistente da 5€/mese) per avere l'app attiva in Cloud 24/7 e accessibile da qualunque dispositivo.

---

## 🛠️ METODO A: Deploy da GitHub (Consigliato e Automatico)

Se hai un repository GitHub per il progetto:

1. **Collega il Repository**:
   - Accedi a [railway.com](https://railway.com) ed entra nella tua Dashboard.
   - Clicca su **"+ New Project"** -> **"Deploy from GitHub repo"**.
   - Seleziona il repository `MindShift Coach`.

2. **Aggiungi il Database PostgreSQL**:
   - Nella schermata del progetto su Railway, clicca su **"+ New"** -> **"Database"** -> **"Add PostgreSQL"**.
   - Railway creerà il database ed esporrà automaticamente la variabile `DATABASE_URL`.
   - L'applicazione creerà in automatico tutte le tabelle al primo avvio.

3. **Imposta le Variabili d'Ambiente (Variables)**:
   - Clicca sulla scheda del servizio MindShift Coach e vai su **"Variables"**.
   - Clicca su **"New Variable"** (o "Raw Editor") e inserisci:

```env
APP_ENV=production
GEMINI_API_KEY=La_Tua_Chiave_AQ_xxx
GEMINI_MODEL=gemini-3-flash-preview
DEFAULT_PRICING_MONTHLY=9.99
FREE_TRIAL_DAYS=3
```
*(Se utilizzi Stripe per i pagamenti reali, aggiungi anche `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` e `STRIPE_WEBHOOK_SECRET`).*

4. **Genera il Dominio Pubblico HTTPS**:
   - Vai nella scheda **"Settings"** del servizio MindShift Coach.
   - Nella sezione **"Networking"**, clicca su **"Generate Domain"**.
   - Railway ti assegnerà un indirizzo pubblico HTTPS del tipo:  
     `https://mindshift-coach-production.up.railway.app`

---

## 💻 METODO B: Deploy Diretto da Terminale (con Railway CLI)

Se preferisci pubblicare direttamente dal tuo PC senza passare per GitHub:

1. **Installa la CLI di Railway** (da PowerShell come amministratore):
   ```powershell
   npm i -g @railway/cli
   ```
2. **Effettua il Login**:
   ```powershell
   railway login
   ```
3. **Inizializza e Collega il Progetto**:
   ```powershell
   railway init
   railway add --database postgres
   ```
4. **Carica il Codice in Cloud**:
   ```powershell
   railway up
   ```

---

## 📱 Come installare e sincronizzare l'App:

1. **Su PC Windows**:
   - Apri l'indirizzo generato da Railway (es. `https://tuo-nome.up.railway.app`) con Chrome o Edge.
   - Clicca sull'icona **"Installa"** nella barra degli indirizzi del browser.

2. **Su Smartphone Android**:
   - Apri lo stesso indirizzo nel browser Chrome del tuo smartphone.
   - Tocca i tre puntini in alto a destra e seleziona **"Aggiungi a schermata Home"** / **"Installa applicazione"**.

3. **Sincronizzazione Dati Realtime**:
   - Apri la scheda **"Sync Windows ↔ Android"** su PC e copia la tua **Sync Key** (es. `MIND-A8F2-491C`).
   - Incollala nella versione smartphone.
   - Da questo momento tutte le sessioni Master PNL, le cartelle cliniche e gli analytics saranno sincronizzati in tempo reale nel database cloud di Railway!
