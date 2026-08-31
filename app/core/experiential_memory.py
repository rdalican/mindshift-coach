"""Motore di Sintesi della Memoria Esperienziale Evolutiva dell'Account.
Raccoglie, aggrega e sintetizza gli episodi e le sessioni registrate nel diario
per costruire un Profilo Cognitivo e PNL longitudinale che rende il Coach sempre più
esperto, calibrato ed empatico sul singolo individuo.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.core.db_models import UserSyncProfile, SavedMindShift, ReframeFeedback
from app.core.models import ExperientialProfile

logger = logging.getLogger("mindshift.experiential_memory")

def utc_now():
    return datetime.now(timezone.utc)

class ExperientialMemoryEngine:
    """Sintetizzatore analitico e generatore della cartella esperienziale dell'account."""

    @classmethod
    def synthesize_profile(cls, sync_key: str, db: Session) -> Optional[ExperientialProfile]:
        """Analizza tutti i mindshift e feedback salvati per la sync_key e sintetizza il profilo esperienziale."""
        if not sync_key:
            return None

        # Recupera tutte le sessioni salvate per la sync_key
        shifts: List[SavedMindShift] = db.query(SavedMindShift).filter(
            SavedMindShift.sync_key == sync_key
        ).order_by(SavedMindShift.created_at.asc()).all()

        if not shifts:
            # Nessuna sessione salvata: profilo base iniziale
            base_profile = ExperientialProfile(
                sync_key=sync_key,
                total_episodes_analyzed=0,
                primary_vak_channel="Cinestesico (K)",
                vak_distribution={},
                core_limiting_structures=["In attesa della prima sessione registrata"],
                unlocked_mastery_archetypes=["Potenziale Inespresso"],
                high_resonance_mantras=[],
                clinical_synthesis_narrative="Account appena inizializzato. Il sistema calibra le sessioni iniziali esplorando i diversi canali percettivi per mappare lo stile cognitivo dell'utente.",
                preferred_reframe_style="Identità (Robert Dilts) & Milton Model",
                last_profile_update=utc_now().isoformat()
            )
            cls._save_profile_to_db(sync_key, base_profile, db)
            return base_profile

        # 1. Distribuzione dei canali VAK
        vak_counts: Dict[str, int] = {}
        for s in shifts:
            ch = s.detected_channel or "Misto / Neutro"
            vak_counts[ch] = vak_counts.get(ch, 0) + 1

        primary_vak = max(vak_counts.items(), key=lambda x: x[1])[0] if vak_counts else "Cinestesico (K)"

        # 2. Pattern del Meta-Modello ricorrenti
        meta_counts: Dict[str, int] = {}
        for s in shifts:
            key = f"{s.meta_category}: {s.meta_subtype}" if s.meta_category else "Generalizzazione"
            meta_counts[key] = meta_counts.get(key, 0) + 1

        top_meta = sorted(meta_counts.items(), key=lambda x: x[1], reverse=True)
        core_limiting = [f"{m[0]} ({m[1]} occorrenze)" for m in top_meta[:3]]

        # 3. Archetipi di Maestria sbloccati dalle Ristrutturazioni di Identità e Titoli
        unlocked_archetypes = []
        for s in shifts:
            if s.identity_reframe and len(s.identity_reframe) > 10:
                cleaned = s.identity_reframe.replace("Non sei", "").strip()
                first_clause = cleaned.split(":")[0] if ":" in cleaned else cleaned.split(".")[0]
                if len(first_clause) < 90 and first_clause not in unlocked_archetypes:
                    unlocked_archetypes.append(first_clause.strip())
            elif s.context:
                tag = f"Maestria nel contesto {s.context.capitalize()}"
                if tag not in unlocked_archetypes:
                    unlocked_archetypes.append(tag)

        if not unlocked_archetypes:
            unlocked_archetypes = ["Osservatore Consapevole", "Sovrano del Proprio Stato"]

        # 4. Mantra ad Alta Risonanza
        high_mantras = []
        for s in shifts:
            if s.is_favorite and s.anchoring_mantra and s.anchoring_mantra not in high_mantras:
                high_mantras.append(s.anchoring_mantra)
        for s in reversed(shifts):
            if s.anchoring_mantra and s.anchoring_mantra not in high_mantras:
                high_mantras.append(s.anchoring_mantra)
            if len(high_mantras) >= 4:
                break

        # 5. Sintesi Clinica Narrativa Longitudinale
        total = len(shifts)
        narrative_parts = []
        narrative_parts.append(
            f"L'utente ha all'attivo {total} sessioni nel Diario con canale percettivo prevalente {primary_vak}."
        )

        contexts = list(set([s.context for s in shifts if s.context]))
        if contexts:
            narrative_parts.append(f"Ha elaborato con successo blocchi nei contesti: {', '.join(contexts)}.")

        if "Cinestesico" in primary_vak:
            narrative_parts.append(
                "Presenta una fisiologia emotiva reattiva e profonda: risponde con straordinaria efficacia a tecniche somatiche di de-tensione, respirazione prolungata (espirazione a 8s) e ancore tattili."
            )
        elif "Visivo" in primary_vak:
            narrative_parts.append(
                "Elabora le sfide attraverso proiezioni visive e scenari futuri: beneficia enormemente di dissociazione visiva (schermo mentale) e submodalità spaziali."
            )
        else:
            narrative_parts.append(
                "Mostra un forte dialogo interno critico: risponde al massimo livello alle domande socratiche di Milton Model e alle ristrutturazioni di significato."
            )

        narrative_parts.append(
            "Stile di reframe d'elezione: Elevazione dei Livelli Logici di Robert Dilts (trasformazione da reazione comportamentale ad Archetipo Sovrano)."
        )

        clinical_narrative = " ".join(narrative_parts)

        profile = ExperientialProfile(
            sync_key=sync_key,
            total_episodes_analyzed=total,
            primary_vak_channel=primary_vak,
            vak_distribution=vak_counts,
            core_limiting_structures=core_limiting,
            unlocked_mastery_archetypes=unlocked_archetypes[:4],
            high_resonance_mantras=high_mantras[:3],
            clinical_synthesis_narrative=clinical_narrative,
            preferred_reframe_style="Identità (Robert Dilts) & Milton Model",
            last_profile_update=utc_now().isoformat()
        )

        cls._save_profile_to_db(sync_key, profile, db)
        return profile

    @classmethod
    def get_or_build_profile(cls, sync_key: str, db: Session) -> Optional[ExperientialProfile]:
        """Restituisce il profilo memorizzato o lo sintetizza se mancante."""
        if not sync_key:
            return None

        user_profile: Optional[UserSyncProfile] = db.query(UserSyncProfile).filter(
            UserSyncProfile.sync_key == sync_key
        ).first()

        if user_profile and user_profile.experiential_profile_json:
            try:
                data = json.loads(user_profile.experiential_profile_json)
                return ExperientialProfile(**data)
            except Exception as e:
                logger.warning(f"Errore parsing profilo esperienziale per {sync_key}: {e}. Rigenero...")

        return cls.synthesize_profile(sync_key, db)

    @classmethod
    def _save_profile_to_db(cls, sync_key: str, profile: ExperientialProfile, db: Session):
        """Salva il profilo serializzato nel database in UserSyncProfile."""
        try:
            user_profile: Optional[UserSyncProfile] = db.query(UserSyncProfile).filter(
                UserSyncProfile.sync_key == sync_key
            ).first()

            if not user_profile:
                user_profile = UserSyncProfile(
                    sync_key=sync_key,
                    device_name="Primary Device",
                    plan_status="trial"
                )
                db.add(user_profile)

            user_profile.experiential_profile_json = json.dumps(profile.model_dump(), ensure_ascii=False)
            user_profile.memory_updated_at = utc_now()
            user_profile.preferred_vak = profile.primary_vak_channel
            db.commit()
            logger.info(f"Profilo esperienziale aggiornato con successo per sync_key {sync_key}")
        except Exception as e:
            db.rollback()
            logger.error(f"Errore nel salvataggio del profilo esperienziale: {e}")

    @classmethod
    def format_profile_for_prompt(cls, profile: Optional[ExperientialProfile]) -> str:
        """Formatta il profilo esperienziale in un blocco di istruzioni ad alta densità informativa per Gemini."""
        if not profile or profile.total_episodes_analyzed == 0:
            return ""

        archetypes_str = ", ".join(profile.unlocked_mastery_archetypes[:3]) if profile.unlocked_mastery_archetypes else "In costruzione"
        limiting_str = ", ".join(profile.core_limiting_structures[:3]) if profile.core_limiting_structures else "Pattern iniziali"
        mantra_str = f"\"{profile.high_resonance_mantras[0]}\"" if profile.high_resonance_mantras else "N/A"

        return f"""
PROFILO ESPERIENZIALE & MEMORIA DI RISTRUTTURAZIONE DELL'ACCOUNT (Fattori Evolutivi Longitudinali):
- Storico Sessioni e Blocchi Integrati: {profile.total_episodes_analyzed} sessioni nel Diario.
- Canale Sensoriale Dominante: {profile.primary_vak_channel} (orienta metafore e verbi su questo canale).
- Pattern & Bias Ricorrenti Noti: {limiting_str}
- Risorse & Archetipi di Potere Sbloccati in passato: {archetypes_str}
- Mantra ad Alta Risonanza consolidato: {mantra_str}
- Sintesi Evolutiva dell'Individuo: {profile.clinical_synthesis_narrative}

DIRETTIVA DI PERSONALIZZAZIONE EVOLUTIVA:
Usa questa memoria per rendere la sessione straordinariamente empatica e cucita su misura per questo specifico individuo, capitalizzando sulle risorse già sbloccate ma mantenendo il focus di ristrutturazione RIGOROSAMENTE sul nuovo blocco espresso (rispetta i Guardrail anti-contaminazione).
"""
