"""Agente 4: Monitoraggio Roadmap & Progresso (4 Settimane dal Paragrafo 6).
Traccia millimetricamente lo stato di avanzamento e i deliverable per la rendita passiva.
"""

from typing import List
from app.core.models import (
    RoadmapStep,
    RoadmapStepStatus,
    RoadmapWeek,
    RoadmapResponse
)

INITIAL_ROADMAP: List[RoadmapWeek] = [
    RoadmapWeek(
        week_number=1,
        title="Settimana 1: Validazione & MVP",
        objective="Sviluppo del prototipo funzionante con motore PNL e interfaccia responsive Windows/Android.",
        status="Completata",
        steps=[
            RoadmapStep(
                id="s1_step1",
                week=1,
                title="Architettura di Progetto & Squadra Multi-Agente",
                description="Setup ambiente Python, configurazione FastAPI, GEM Programmatore e GEM PNL.",
                deliverable="Struttura di cartelle, config.py, models.py e requirements.txt",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s1_step2",
                week=1,
                title="Motore PNL Core (Meta-Modello, VAK & Gemini Flash)",
                description="Algoritmo di estrazione canale sensoriale VAK, decostruzione del Meta-Modello e 3 carte di Reframing.",
                deliverable="app/core/pnl_engine.py e app/core/gemini_client.py",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s1_step3",
                week=1,
                title="Interfaccia Responsive Web & PWA (Windows/Android)",
                description="Frontend moderno in HTML5 + Tailwind con supporto installazione desktop (Windows) e mobile (Android).",
                deliverable="app/templates/index.html, static/css, static/js e manifest.json",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s1_step4",
                week=1,
                title="Test di Validazione Automatica & Checkpoint Feedback Utente",
                description="Esecuzione suite di test su pattern linguistici e approvazione formale dell'utente per l'MVP.",
                deliverable="Report QA, pytest completato e checkpoint di fine Settimana 1",
                status=RoadmapStepStatus.DONE
            )
        ]
    ),
    RoadmapWeek(
        week_number=2,
        title="Settimana 2: Integrazione & Pagamenti",
        objective="Database condiviso Cloud su Railway, sincronizzazione Windows-Android e abbonamenti Stripe.",
        status="Completata",
        steps=[
            RoadmapStep(
                id="s2_step1",
                week=2,
                title="Database Condiviso Cloud (PostgreSQL / Railway)",
                description="Persistenza sessioni, profili di sincronizzazione e storico reframing con SQLAlchemy.",
                deliverable="app/core/database.py e app/core/db_models.py",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s2_step2",
                week=2,
                title="Sincronizzazione Cross-Device Windows ↔ Android",
                description="Accoppiamento dispositivo con Sync Key univoca e sincronizzazione in tempo reale.",
                deliverable="Endpoint /api/sync/pair e /api/sync/shifts",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s2_step3",
                week=2,
                title="Integrazione Stripe / Paywall Micro-SaaS (9.99€/m)",
                description="Checkout session ricorrente con 3 giorni di prova gratuita e gestione webhook.",
                deliverable="app/core/stripe_client.py e /api/payments/checkout",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s2_step4",
                week=2,
                title="Configurazione Deploy Railway & Feedback Utente",
                description="Setup railway.json, Procfile, Dockerfile e verifica su istanza Cloud Railway.",
                deliverable="railway.json, Procfile, GUIDA_DEPLOY_RAILWAY.md",
                status=RoadmapStepStatus.DONE
            )
        ]
    ),
    RoadmapWeek(
        week_number=3,
        title="Settimana 3: Beta Testing & UX PNL Avanzata",
        objective="Analytics canali VAK, Wizard di Onboarding in 2 minuti, Rating risonanza e PNL Master Protocol v4.",
        status="Completata",
        steps=[
            RoadmapStep(
                id="s3_step1",
                week=3,
                title="Diario Cognitivo & Tracciamento VAK nel Tempo",
                description="Statistiche visive sui canali sensoriali predominanti dell'utente ed esportazione diario.",
                deliverable="Endpoint /api/analytics/vak e /api/export/shifts",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s3_step2",
                week=3,
                title="Onboarding Guidato 'MindShift in 2 Minuti'",
                description="Wizard interattivo a 4 passaggi per calibrare VAK e massimizzare la retention.",
                deliverable="Modal Onboarding interattivo in index.html",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s3_step3",
                week=3,
                title="Beta Testing & Calibrazione Prompt Master v4 (Milton & Dilts)",
                description="Rating di risonanza (1-5 stelle), identità di Robert Dilts e 4 ristrutturazioni profonde.",
                deliverable="app/core/pnl_engine.py v4 e /api/feedback/reframe",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s3_step4",
                week=3,
                title="Review & Feedback Utente Settimana 3",
                description="Validazione delle metriche di onboarding e potenziamento valore percepito.",
                deliverable="Approvazione checkpoint Settimana 3",
                status=RoadmapStepStatus.DONE
            )
        ]
    ),
    RoadmapWeek(
        week_number=4,
        title="Settimana 4: Automazione & Lancio Passivo",
        objective="Monitoraggio errori a zero manutenzione, asset di marketing organico e lancio ufficiale.",
        status="Completata",
        steps=[
            RoadmapStep(
                id="s4_step1",
                week=4,
                title="Monitoraggio Errori Autonomo & Diagnostica Realtime",
                description="Setup telemetria e allarmi automatici per garantire il 99.9% uptime senza manutenzione manuale.",
                deliverable="app/core/monitoring.py e /health/diagnostics",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s4_step2",
                week=4,
                title="Asset & Script Funnel Organico (TikTok/Reels)",
                description="Pacchetto di 10 script video virali basati su PNL ed ipnosi conversazionale per traffico passivo a costo zero.",
                deliverable="docs/10_SCRIPT_VIDEO_TIKTOK_REELS.md",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s4_step3",
                week=4,
                title="Launch Kit Product Hunt & Top 15 Directory AI",
                description="Strategia di lancio, copy maker e sottomissione alle principali directory di SaaS per backlink e SEO.",
                deliverable="docs/PRODUCT_HUNT_LAUNCH_KIT.md",
                status=RoadmapStepStatus.DONE
            ),
            RoadmapStep(
                id="s4_step4",
                week=4,
                title="Consuntivo Finale & Manuale Gestione Zero",
                description="Guida operativa per la gestione del Micro-SaaS in 10 minuti a settimana.",
                deliverable="docs/MANUALE_GESTIONE_PASSIVA.md e Consegna Finale",
                status=RoadmapStepStatus.DONE
            )
        ]
    )
]

class RoadmapTracker:
    def __init__(self):
        self.weeks = INITIAL_ROADMAP

    def get_roadmap_summary(self) -> RoadmapResponse:
        total_steps = sum(len(w.steps) for w in self.weeks)
        completed_steps = sum(
            1 for w in self.weeks for s in w.steps if s.status == RoadmapStepStatus.DONE
        )
        percentage = round((completed_steps / total_steps) * 100, 1) if total_steps > 0 else 0.0

        current_week = 4
        for w in self.weeks:
            if any(s.status == RoadmapStepStatus.IN_PROGRESS for s in w.steps):
                current_week = w.week_number
                break

        return RoadmapResponse(
            current_week=current_week,
            completion_percentage=percentage,
            weeks=self.weeks
        )

    def toggle_step(self, step_id: str, new_status: RoadmapStepStatus) -> bool:
        for w in self.weeks:
            for s in w.steps:
                if s.id == step_id:
                    s.status = new_status
                    if all(step.status == RoadmapStepStatus.DONE for step in w.steps):
                        w.status = "Completata"
                    elif any(step.status in (RoadmapStepStatus.DONE, RoadmapStepStatus.IN_PROGRESS) for step in w.steps):
                        w.status = "In Corso"
                    else:
                        w.status = "Pianificata"
                    return True
        return False

roadmap_tracker = RoadmapTracker()
