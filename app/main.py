"""Entrypoint principale dell'applicazione MindShift Coach (v0.4.0).
Include:
- Motore PNL Master Protocol v4 & Google Gemini AI (gemini-3-flash-preview / gemini-3.5-flash)
- Database Cloud PostgreSQL su Railway & SQLite locale
- Sincronizzazione Cross-Device Windows ↔ Android
- Modulo Abbonamenti Stripe Micro-SaaS
- Analytics VAK & Statistiche Cognitive
- Feedback Loop & Export Scheda Sessione Clinica
- Sistema di Telemetria & Diagnostica Zero-Manutenzione
"""

import os
import json
import uuid
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, Response, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app.core.database import get_db, init_db
from app.core.db_models import UserSyncProfile, SavedMindShift, SubscriptionRecord, ReframeFeedback
from app.core.models import (
    MindShiftRequest,
    MindShiftResponse,
    DevicePairRequest,
    DevicePairResponse,
    SyncShiftItem,
    SyncShiftsResponse,
    StripeCheckoutRequest,
    StripeCheckoutResponse,
    VAKAnalyticsResponse,
    VAKDistribution,
    CategoryBreakdown,
    ReframeFeedbackRequest,
    ReframeFeedbackResponse,
    RoadmapResponse,
    RoadmapStepToggleRequest
)
from app.core.gemini_client import gemini_pnl_client
from app.core.stripe_client import stripe_manager
from app.core.roadmap_tracker import roadmap_tracker
from app.core.monitoring import system_monitor

# Inizializza le tabelle all'import
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Applicazione Micro-SaaS di Coaching e Reframing Cognitivo di Livello Master potenziata da PNL e Google Gemini con sincronizzazione Cloud su Railway.",
    version="0.4.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Percorsi statici e template
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    roadmap_data = roadmap_tracker.get_roadmap_summary()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "roadmap": roadmap_data,
            "gemini_active": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip()),
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY or ""
        }
    )

@app.get("/health")
async def healthcheck():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "0.4.0",
        "environment": settings.APP_ENV,
        "database": "postgresql" if "postgres" in settings.DATABASE_URL else "sqlite",
        "gemini_configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip()),
        "stripe_configured": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.strip())
    }

@app.get("/health/diagnostics")
async def diagnostics():
    return system_monitor.run_full_diagnostics()

# ==========================================
# REFRAMING CORE API (MASTER PNL & GEMINI)
# ==========================================
@app.post("/api/reframe", response_model=MindShiftResponse)
async def perform_reframe(req: MindShiftRequest, db: Session = Depends(get_db)):
    try:
        response = await gemini_pnl_client.generate_shift(req)
        
        sync_key = req.sync_key.strip().upper() if req.sync_key and req.sync_key.strip() else None
        shift_id = response.id if response.id else str(uuid.uuid4())
        response.id = shift_id

        # Salva o aggiorna la sessione nel DB solo se sync_key è fornito
        if sync_key:
            reframes_json = json.dumps([r.model_dump() for r in response.reframes])
            protocol_json = json.dumps(response.anchoring_protocol.model_dump()) if response.anchoring_protocol else None
            action_plan_json = json.dumps(response.action_plan.model_dump()) if response.action_plan else None

            existing = db.query(SavedMindShift).filter(
                (SavedMindShift.id == shift_id) |
                ((SavedMindShift.sync_key == sync_key) & (SavedMindShift.original_thought == response.original_thought))
            ).first()

            if existing:
                existing.original_thought = response.original_thought
                existing.context = req.context
                existing.detected_channel = response.detected_channel.value
                existing.meta_category = response.meta_model.category
                existing.meta_subtype = response.meta_model.subtype
                existing.meta_explanation = response.meta_model.explanation
                existing.context_reframe = response.context_reframe
                existing.meaning_reframe = response.meaning_reframe
                existing.identity_reframe = response.identity_reframe
                existing.socratic_question = response.socratic_question
                existing.empowering_micro_action = response.empowering_micro_action
                existing.anchoring_mantra = response.anchoring_mantra
                existing.reframes_json = reframes_json
                existing.protocol_json = protocol_json
                existing.action_plan_json = action_plan_json
                db.commit()
                response.id = existing.id
            else:
                db_shift = SavedMindShift(
                    id=shift_id,
                    sync_key=sync_key,
                    original_thought=response.original_thought,
                    context=req.context,
                    detected_channel=response.detected_channel.value,
                    meta_category=response.meta_model.category,
                    meta_subtype=response.meta_model.subtype,
                    meta_explanation=response.meta_model.explanation,
                    context_reframe=response.context_reframe,
                    meaning_reframe=response.meaning_reframe,
                    identity_reframe=response.identity_reframe,
                    socratic_question=response.socratic_question,
                    empowering_micro_action=response.empowering_micro_action,
                    anchoring_mantra=response.anchoring_mantra,
                    reframes_json=reframes_json,
                    protocol_json=protocol_json,
                    action_plan_json=action_plan_json
                )
                db.add(db_shift)
                
                # Registra anche il profilo utente se non esiste
                existing_profile = db.query(UserSyncProfile).filter(UserSyncProfile.sync_key == sync_key).first()
                if not existing_profile:
                    db.add(UserSyncProfile(
                        sync_key=sync_key,
                        device_name="Web Tester",
                        preferred_vak=response.detected_channel.value,
                        plan_status="trial"
                    ))
                db.commit()

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'elaborazione PNL: {str(e)}")

# ==========================================
# ANALYTICS & VAK TRENDS
# ==========================================
@app.get("/api/analytics/vak", response_model=VAKAnalyticsResponse)
async def get_vak_analytics(sync_key: str, db: Session = Depends(get_db)):
    if not sync_key:
        raise HTTPException(status_code=400, detail="sync_key obbligatoria.")

    clean_key = sync_key.strip().upper()
    shifts = db.query(SavedMindShift).filter(SavedMindShift.sync_key == clean_key).all()
    total_shifts = len(shifts)

    if total_shifts == 0:
        return VAKAnalyticsResponse(
            sync_key=clean_key,
            distribution=VAKDistribution(
                visual_pct=33.3,
                auditory_pct=33.3,
                kinesthetic_pct=33.4,
                mixed_pct=0.0,
                dominant_channel="Neutro (Inizia una sessione)",
                total_analyzed=0
            ),
            categories_breakdown=[],
            total_shifts=0,
            average_resonance_score=5.0,
            empowerment_index=100.0
        )

    v_count = sum(1 for s in shifts if "visivo" in s.detected_channel.lower())
    a_count = sum(1 for s in shifts if "uditivo" in s.detected_channel.lower())
    k_count = sum(1 for s in shifts if "cinestesico" in s.detected_channel.lower())
    m_count = total_shifts - (v_count + a_count + k_count)

    v_pct = round((v_count / total_shifts) * 100, 1)
    a_pct = round((a_count / total_shifts) * 100, 1)
    k_pct = round((k_count / total_shifts) * 100, 1)
    m_pct = round((m_count / total_shifts) * 100, 1)

    max_c = max([("Visivo (V)", v_count), ("Uditivo (A)", a_count), ("Cinestesico (K)", k_count)], key=lambda x: x[1])
    dominant = max_c[0] if max_c[1] > 0 else "Misto / Bilanciato"

    cat_counts = {}
    for s in shifts:
        c = s.context or "Generale"
        cat_counts[c] = cat_counts.get(c, 0) + 1

    categories_breakdown = [
        CategoryBreakdown(
            category_name=k,
            count=v,
            percentage=round((v / total_shifts) * 100, 1)
        )
        for k, v in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    feedbacks = db.query(ReframeFeedback).filter(ReframeFeedback.sync_key == clean_key).all()
    avg_rating = round(sum(f.rating for f in feedbacks) / len(feedbacks), 1) if feedbacks else 4.9
    empowerment_index = min(100.0, round(75.0 + (total_shifts * 3.5), 1))

    return VAKAnalyticsResponse(
        sync_key=clean_key,
        distribution=VAKDistribution(
            visual_pct=v_pct,
            auditory_pct=a_pct,
            kinesthetic_pct=k_pct,
            mixed_pct=m_pct,
            dominant_channel=dominant,
            total_analyzed=total_shifts
        ),
        categories_breakdown=categories_breakdown,
        total_shifts=total_shifts,
        average_resonance_score=avg_rating,
        empowerment_index=empowerment_index
    )

# ==========================================
# FEEDBACK & EXPORT API
# ==========================================
@app.post("/api/feedback/reframe", response_model=ReframeFeedbackResponse)
async def submit_feedback(req: ReframeFeedbackRequest, db: Session = Depends(get_db)):
    clean_key = req.sync_key.strip().upper()
    feedback = ReframeFeedback(
        sync_key=clean_key,
        shift_id=req.shift_id,
        reframe_type=req.reframe_type,
        rating=req.rating,
        comment=req.comment
    )
    db.add(feedback)
    db.commit()
    return ReframeFeedbackResponse(
        status="success",
        message="Valutazione registrata con successo!",
        recorded_rating=req.rating
    )

@app.get("/api/export/shifts")
async def export_shifts(sync_key: str, format: str = "markdown", db: Session = Depends(get_db)):
    if not sync_key:
        raise HTTPException(status_code=400, detail="sync_key obbligatoria.")

    clean_key = sync_key.strip().upper()
    shifts = db.query(SavedMindShift).filter(
        SavedMindShift.sync_key == clean_key
    ).order_by(SavedMindShift.created_at.desc()).all()

    if format.lower() == "json":
        return JSONResponse(content=[s.to_dict() for s in shifts])

    lines = [
        f"# 📖 Cartella Clinica dei MindShift Master - PNL & Google Gemini AI",
        f"**Sync Key:** `{clean_key}`",
        f"**Totale Sessioni Master Svolte:** {len(shifts)}",
        f"**Esportazione:** Documento di Auto-Coaching",
        "\n---\n"
    ]

    for i, s in enumerate(shifts, 1):
        lines.append(f"## {i}. \"{s.original_thought}\"")
        lines.append(f"- **Canale Sensoriale:** {s.detected_channel}")
        lines.append(f"- **Meta-Modello:** {s.meta_category} ({s.meta_subtype})")
        if s.context:
            lines.append(f"- **Ambito:** {s.context}")
        
        lines.append(f"\n### 🔄 4 Ristrutturazioni Cognitive:")
        if s.context_reframe:
            lines.append(f"* **1. Contesto (Punto di Forza):** {s.context_reframe}")
        if s.meaning_reframe:
            lines.append(f"* **2. Significato (Milton Model):** {s.meaning_reframe}")
        if s.identity_reframe:
            lines.append(f"* **3. Identità (Robert Dilts):** {s.identity_reframe}")
        if s.socratic_question:
            lines.append(f"* **4. Domanda Socratica:** {s.socratic_question}")
        
        if s.anchoring_mantra:
            lines.append(f"\n💎 **Mantra Ipnotico:** *\"{s.anchoring_mantra}\"*")
        
        if s.empowering_micro_action:
            lines.append(f"⚡ **Micro-Azione di Sblocco:** {s.empowering_micro_action}")
        
        lines.append("\n---\n")

    md_content = "\n".join(lines)
    return PlainTextResponse(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=mindshift_master_session_{clean_key}.md"}
    )

# ==========================================
# CROSS-DEVICE SYNC API
# ==========================================
@app.post("/api/sync/pair", response_model=DevicePairResponse)
async def pair_device(req: DevicePairRequest, db: Session = Depends(get_db)):
    if req.sync_key and req.sync_key.strip():
        sync_key = req.sync_key.strip().upper()
        profile = db.query(UserSyncProfile).filter(UserSyncProfile.sync_key == sync_key).first()
        if not profile:
            profile = UserSyncProfile(
                sync_key=sync_key,
                email=req.email,
                device_name=req.device_name or "Second Device",
                plan_status="trial"
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        total_shifts = db.query(SavedMindShift).filter(SavedMindShift.sync_key == sync_key).count()
        return DevicePairResponse(
            sync_key=sync_key,
            plan_status=profile.plan_status,
            total_synced_shifts=total_shifts,
            message="Dispositivo collegato con successo al Cloud Railway!"
        )
    else:
        new_key = f"MIND-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"
        profile = UserSyncProfile(
            sync_key=new_key,
            email=req.email,
            device_name=req.device_name or "Primary Device",
            plan_status="trial"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return DevicePairResponse(
            sync_key=new_key,
            plan_status="trial",
            total_synced_shifts=0,
            message="Nuova Sync Key generata con successo."
        )

@app.get("/api/sync/shifts", response_model=SyncShiftsResponse)
async def get_synced_shifts(sync_key: str, db: Session = Depends(get_db)):
    if not sync_key:
        raise HTTPException(status_code=400, detail="Parametro sync_key obbligatorio.")
    
    clean_key = sync_key.strip().upper()
    shifts = db.query(SavedMindShift).filter(
        SavedMindShift.sync_key == clean_key
    ).order_by(SavedMindShift.created_at.desc()).all()

    items = [SyncShiftItem(**s.to_dict()) for s in shifts]
    return SyncShiftsResponse(sync_key=clean_key, shifts=items, count=len(items))

@app.post("/api/sync/shifts", response_model=SyncShiftItem)
async def save_synced_shift(item: SyncShiftItem, db: Session = Depends(get_db)):
    if not item.sync_key:
        raise HTTPException(status_code=400, detail="sync_key richiesta per salvare nel Cloud.")

    clean_key = item.sync_key.strip().upper()
    reframes_json = json.dumps([r.model_dump() for r in item.reframes]) if item.reframes else "[]"
    protocol_json = json.dumps(item.anchoring_protocol.model_dump()) if item.anchoring_protocol else None
    action_plan_json = json.dumps(item.action_plan.model_dump()) if item.action_plan else None
    
    existing = db.query(SavedMindShift).filter(
        (SavedMindShift.id == item.id) | 
        ((SavedMindShift.sync_key == clean_key) & (SavedMindShift.original_thought == item.original_thought))
    ).first()
    if existing:
        existing.original_thought = item.original_thought
        existing.context = item.context
        existing.detected_channel = item.detected_channel
        existing.meta_category = item.meta_category
        existing.meta_subtype = item.meta_subtype
        existing.meta_explanation = item.meta_explanation
        existing.context_reframe = item.context_reframe
        existing.meaning_reframe = item.meaning_reframe
        existing.identity_reframe = item.identity_reframe
        existing.socratic_question = item.socratic_question
        existing.empowering_micro_action = item.empowering_micro_action
        existing.anchoring_mantra = item.anchoring_mantra
        existing.reframes_json = reframes_json
        existing.protocol_json = protocol_json
        existing.action_plan_json = action_plan_json
        existing.is_favorite = item.is_favorite
        db.commit()
        db.refresh(existing)
        return SyncShiftItem(**existing.to_dict())
    else:
        new_shift = SavedMindShift(
            id=item.id or str(uuid.uuid4()),
            sync_key=clean_key,
            original_thought=item.original_thought,
            context=item.context,
            detected_channel=item.detected_channel,
            meta_category=item.meta_category,
            meta_subtype=item.meta_subtype,
            meta_explanation=item.meta_explanation,
            context_reframe=item.context_reframe,
            meaning_reframe=item.meaning_reframe,
            identity_reframe=item.identity_reframe,
            socratic_question=item.socratic_question,
            empowering_micro_action=item.empowering_micro_action,
            anchoring_mantra=item.anchoring_mantra,
            reframes_json=reframes_json,
            protocol_json=protocol_json,
            action_plan_json=action_plan_json,
            is_favorite=item.is_favorite
        )
        db.add(new_shift)
        db.commit()
        db.refresh(new_shift)
        return SyncShiftItem(**new_shift.to_dict())

@app.delete("/api/sync/shifts/{shift_id}")
async def delete_synced_shift(shift_id: str, sync_key: Optional[str] = None, db: Session = Depends(get_db)):
    clean_key = sync_key.strip().upper() if sync_key else None
    
    # 1. Cerca per ID
    shift = db.query(SavedMindShift).filter(SavedMindShift.id == shift_id).first()
    
    # 2. Se non trovato e c'è sync_key, cerca per corrispondenza esatta o per ID
    if not shift and clean_key:
        shift = db.query(SavedMindShift).filter(
            (SavedMindShift.id == shift_id) & (SavedMindShift.sync_key == clean_key)
        ).first()

    if not shift:
        raise HTTPException(status_code=404, detail="Sessione non trovata.")
    
    # Rimuovi la sessione e pulisci eventuali duplicati con stesso pensiero e chiave
    thought = shift.original_thought
    s_key = shift.sync_key
    db.delete(shift)

    if thought and s_key:
        duplicates = db.query(SavedMindShift).filter(
            SavedMindShift.sync_key == s_key,
            SavedMindShift.original_thought == thought
        ).all()
        for d in duplicates:
            db.delete(d)

    db.commit()
    return {"status": "deleted", "id": shift_id}

@app.delete("/api/admin/shifts/{shift_id}")
async def admin_delete_shift(shift_id: str, db: Session = Depends(get_db)):
    """Elimina definitivamente una sessione specifica dal database per gli amministratori."""
    shift = db.query(SavedMindShift).filter(SavedMindShift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Sessione non trovata.")
    db.delete(shift)
    db.commit()
    return {"status": "deleted", "id": shift_id}

@app.post("/api/admin/clean-tests")
async def admin_clean_tests(db: Session = Depends(get_db)):
    """Elimina tutte le sessioni temporanee di diagnostica e test dal database."""
    test_keys = ["BRIDGE-TEST", "TEST", "DIAGNOSTICS-TEST"]
    deleted_count = db.query(SavedMindShift).filter(
        (SavedMindShift.sync_key.in_(test_keys)) | (SavedMindShift.sync_key.like("TESTER-%"))
    ).delete(synchronize_session=False)
    db.commit()
    return {"status": "success", "deleted_count": deleted_count}

# ==========================================
# STRIPE PAYMENTS API
# ==========================================
@app.post("/api/payments/checkout", response_model=StripeCheckoutResponse)
async def create_checkout(req: StripeCheckoutRequest):
    response = stripe_manager.create_subscription_checkout(
        sync_key=req.sync_key,
        email=req.email,
        success_url=req.success_url,
        cancel_url=req.cancel_url
    )
    return response

@app.post("/api/payments/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    result = stripe_manager.handle_webhook_event(payload, sig_header)
    
    if result.get("action") == "activate_subscription":
        sync_key = result.get("sync_key")
        if sync_key:
            profile = db.query(UserSyncProfile).filter(UserSyncProfile.sync_key == sync_key).first()
            if profile:
                profile.plan_status = "active"
                db.commit()
            
            sub = SubscriptionRecord(
                sync_key=sync_key,
                stripe_customer_id=result.get("customer_id"),
                stripe_subscription_id=result.get("subscription_id"),
                status="active"
            )
            db.add(sub)
            db.commit()

    return {"status": "received"}

@app.get("/api/payments/status/{sync_key}")
async def get_plan_status(sync_key: str, db: Session = Depends(get_db)):
    clean_key = sync_key.strip().upper()
    profile = db.query(UserSyncProfile).filter(UserSyncProfile.sync_key == clean_key).first()
    if not profile:
        return {"plan_status": "trial", "sync_key": clean_key}
    return {"plan_status": profile.plan_status, "sync_key": clean_key}

# ==========================================
# ADMIN & TESTER FEEDBACK OVERVIEW API
# ==========================================
@app.get("/api/admin/overview")
async def get_admin_overview(db: Session = Depends(get_db)):
    """Restituisce il riepilogo in tempo reale di tutte le sessioni e i feedback dei tester."""
    profiles = db.query(UserSyncProfile).order_by(UserSyncProfile.created_at.desc()).all()
    shifts = db.query(SavedMindShift).order_by(SavedMindShift.created_at.desc()).all()
    feedbacks = db.query(ReframeFeedback).order_by(ReframeFeedback.created_at.desc()).all()
    
    return {
        "status": "success",
        "total_active_testers": len(profiles),
        "total_saved_sessions": len(shifts),
        "total_feedback_ratings": len(feedbacks),
        "feedbacks": [
            {
                "id": f.id,
                "sync_key": f.sync_key,
                "shift_id": f.shift_id,
                "reframe_type": f.reframe_type,
                "rating": f.rating,
                "comment": f.comment,
                "created_at": f.created_at.strftime("%Y-%m-%d %H:%M:%S") if f.created_at else None
            }
            for f in feedbacks
        ],
        "recent_sessions": [s.to_dict() for s in shifts[:50]]
    }

# ==========================================
# ROADMAP API & PWA STATIC
# ==========================================
@app.get("/api/roadmap", response_model=RoadmapResponse)
async def get_roadmap():
    return roadmap_tracker.get_roadmap_summary()

@app.post("/api/roadmap/step/toggle")
async def toggle_roadmap_step(req: RoadmapStepToggleRequest):
    success = roadmap_tracker.toggle_step(req.step_id, req.status)
    if not success:
        raise HTTPException(status_code=404, detail="Passo della roadmap non trovato.")
    return {"status": "success", "roadmap": roadmap_tracker.get_roadmap_summary()}

@app.get("/manifest.json")
async def get_manifest():
    manifest_path = os.path.join(STATIC_DIR, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/manifest+json")
    return JSONResponse(
        content={
            "name": "MindShift Coach",
            "short_name": "MindShift",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#0F2942",
            "theme_color": "#0A7E8C"
        },
        media_type="application/manifest+json"
    )

@app.get("/service-worker.js")
async def get_service_worker():
    sw_path = os.path.join(STATIC_DIR, "js", "service-worker.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript")
    return Response(content="", media_type="application/javascript")
