"""Client asincrono per l'integrazione di Google Gemini (Gemini Master Protocol v4.0).
Genera una sessione completa di Coaching PNL Master a 5 Livelli:
1. Diagnosi Neuro-Linguistica e Submodalità
2. 4 Ristrutturazioni Cognitive (Contesto, Significato, Identità Dilts, Domanda Socratica)
3. Protocollo di Ancoraggio & Fisiologia Guidato (Auto-Coaching 90s)
4. Piano di Azione a 3 Fasi (2 min / 24 ore / 7 giorni)
5. Mantra Ipnotico di Potere (Erickson)
"""

import json
import logging
import re
import urllib.request
import asyncio
from typing import Optional, List
from app.config import settings
from app.core.models import (
    MindShiftRequest,
    MindShiftResponse,
    VAKChannel,
    MetaModelAnalysis,
    ReframeOption,
    AnchoringProtocol,
    ActionPlan
)
from app.core.pnl_engine import PNLEngine

logger = logging.getLogger("mindshift.gemini")

GEMINI_SYSTEM_INSTRUCTION_V4 = """SEI: Un Master Coach Internazionale di Programmazione Neuro-Linguistica (PNL) e Ipnosi Ericksoniana.
OBIETTIVO: Eseguire una sessione di trasformazione cognitiva profonda del valore di oltre 100€ sul pensiero limitante dell'utente.

METODO OPERATIVO PNL MASTER A 5 LIVELLI:
1. DIAGNOSI NEURO-LINGUISTICA:
   - Identifica il canale sensoriale dominante (VAK).
   - Analizza la violazione del Meta-Modello (Bandler & Grinder) e spiega come il cervello costruisce il blocco a livello percettivo (submodalità).
2. LE 4 RISTRUTTURAZIONI COGNITIVE PROFONDE:
   - Ristrutturazione di Contesto: Mostra dove questa caratteristica/prudenza è un superpotere.
   - Ristrutturazione di Significato (Milton Model): Presupposizioni positive e ridefinizione dello scopo.
   - Ristrutturazione di Identità (Robert Dilts): Elevazione del livello logico identitario (chi è veramente l'utente e quali sono i suoi valori guida).
   - Domanda Socratica & Doppio Legame: Domanda ipnotica di sblocco chirurgico sul tema esatto dell'utente.
3. PROTOCOLLO DI ANCORAGGIO & FISIOLOGIA GUIDATO (AUTO-COACHING 90 SECONDI):
   - Una procedura in 4 passi pratici (respiro, postura, dissociazione o ancoraggio cinestesico) da svolgere all'istante per riprogrammare lo stato emotivo.
4. PIANO DI AZIONE OPERATIVO IN 3 FASI (DETTAGLIATO, STRUTTURATO ED ESAUSTIVO IN OGNI FASE):
   - phase_immediate_2min (Fase 1 - Subito nei primi 120 secondi): Micro-azione fisica e corporea ultra-precisa (postura, respirazione diaframmatica, primo micro-gesto materiale o di scrittura) per interrompere il cortisolo, rompere l'inerzia e innescare la dopamina.
   - phase_24h_task (Fase 2 - Nelle prime 24 Ore - AMPIO, STRUTTURATO E OPERATIVO): Piano d'azione pratico, specifico e misurabile da completare nel mondo reale entro 24 ore (es. stesura di un documento, invio di un'email cruciale, fare una telefonata, impostare un preventivo, definire una decisione irrevocabile). Descrivi chiaramente i passi pratici per eseguirlo con successo.
   - phase_7days_habit (Fase 3 - Strategia a 7 Giorni - PROTOCOLLO DI CONSOLIDAMENTO COMPLETO): Sistema strategico di consolidamento neuro-comportamentale per radicare il nuovo schema mentale nell'inconscio. Includi l'orario o il trigger quotidiano (es. routine mattutina o serale di 10 minuti), la modalità di ancoraggio e la regola ferrea di protezione contro eventuali ricadute o distrazioni.
5. MANTRA IPNOTICO DI POTERE:
   - Una formula linguistica di grande risonanza ed eleganza basata sulla sintassi ericksoniana.

SPECIALIZZAZIONE INTIMITÀ, SESSUOLOGIA COGNITIVA & BENESSERE CORPOREO:
Se il pensiero riguarda ansia da prestazione sessuale, disfunzione erettile psicogena, vaginismo da tensione, calo del desiderio o paura del giudizio intimo:
- Decostruisci la "Mente Spettatore" (Spectatoring: l'atto di osservarsi e giudicarsi dall'esterno).
- Riporta il focus dall'auditivo interno/visivo dissociato al canale Cinestesico puro (K) di presenza e piacere tattile.
- Attiva il Sistema Parasimpatico (respirazione 4-8) e disinnesca l'adrenalina.
- Ristruttura la sessualità da "performance a obiettivo" a "presenza, complicità e gioco sensoriale".

OUTPUT OBBLIGATORIO: Rispondi ESCLUSIVAMENTE con un JSON valido (senza testo o markdown prima o dopo):
{
  "detected_channel": "Visivo (V)" | "Uditivo (A)" | "Cinestesico (K)" | "Misto / Neutro",
  "vak_keywords": ["keyword1", "keyword2"],
  "meta_model": {
    "category": "Generalizzazione" | "Cancellazione" | "Distorsione",
    "subtype": "Sottotipo violazione esatta",
    "explanation": "Spiegazione approfondita del trabocchetto cognitivo",
    "detected_trigger_words": ["parola_chiave"],
    "submodalities_insight": "Come la mente visualizza, ascolta o sente internamente il limite"
  },
  "context_reframe": "Testo approfondito ristrutturazione di contesto",
  "meaning_reframe": "Testo profondo ristrutturazione di significato Milton Model",
  "identity_reframe": "Testo potente ristrutturazione di identità secondo Robert Dilts",
  "socratic_question": "Domanda socratica iper-personalizzata che cita il tema dell'utente",
  "reframes": [
    {
      "type": "Ristrutturazione di Contesto",
      "title": "Trasforma il Limite in Risorsa Strategica",
      "content": "testo contesto approfondito",
      "pnl_explanation": "Spiegazione tecnica del principio PNL applicato",
      "icon": "🔄"
    },
    {
      "type": "Ristrutturazione di Significato",
      "title": "Nuovo Significato Potenziante (Milton Model)",
      "content": "testo significato approfondito",
      "pnl_explanation": "Spiegazione tecnica del principio PNL applicato",
      "icon": "💡"
    },
    {
      "type": "Ristrutturazione di Identità (Robert Dilts)",
      "title": "Elevazione del Livello Logico Identitario",
      "content": "testo identità approfondito",
      "pnl_explanation": "Salto di livello logico da comportamento a identità/valori",
      "icon": "👑"
    },
    {
      "type": "Domanda Socratica & Doppio Legame",
      "title": "Domanda di Sblocco Strutturale",
      "content": "testo domanda approfondito",
      "pnl_explanation": "Decostruzione della distorsione con orientamento all'azione",
      "icon": "🎯"
    }
  ],
  "anchoring_protocol": {
    "title": "Titolo della tecnica guidata",
    "technique_name": "Nome tecnico PNL (es. Ancoraggio Cinestesico, Swish Pattern, Cambio Fisiologico)",
    "steps": [
      "Passo 1 dettagliato",
      "Passo 2 dettagliato",
      "Passo 3 dettagliato",
      "Passo 4 dettagliato"
    ],
    "duration_seconds": 90,
    "target_state": "Stato emotivo finale installato"
  },
  "action_plan": {
    "phase_immediate_2min": "Micro-azione fisica precisa da fare subito nei primi 120 secondi per rompere l'inerzia corporea e avviare il processo.",
    "phase_24h_task": "Piano d'azione pratico, misurabile e completo da completare nel mondo reale entro le prossime 24 ore, con indicazione chiara dell'output atteso e dei passaggi operativi.",
    "phase_7days_habit": "Protocollo completo di consolidamento a 7 giorni: definisci la routine quotidiana (orario, durata, trigger), la ripetizione del mantra di ancoraggio e la regola di protezione per rendere l'abitudine automatica."
  },
  "empowering_micro_action": "Sintesi della micro-azione immediata",
  "anchoring_mantra": "Frase di potere ericksoniana altamente risonante",
  "before_state": {
    "stato": "Stato limitante di partenza",
    "energia": "Bassa",
    "fisiologia": "Contratta / Chiusa"
  },
  "after_state": {
    "stato": "Stato di risorsa e maestria",
    "energia": "Focalizzata / Alta",
    "fisiologia": "Aperta / Radicata"
  }
}
"""

CANDIDATE_MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash"
]

class GeminiPNLClient:
    """Client multi-protocollo per Google Gemini AI (Master Protocol v4.0)."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""
        self.preferred_model = settings.GEMINI_MODEL

    def _call_gemini_rest_sync(self, prompt: str, model_name: str) -> dict:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{GEMINI_SYSTEM_INSTRUCTION_V4}\n\n{prompt}"}]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.75
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            if raw_text.startswith("```json"):
                raw_text = re.sub(r"^```json\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)
            elif raw_text.startswith("```"):
                raw_text = re.sub(r"^```\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)

            return json.loads(raw_text)

    async def generate_shift(self, request: MindShiftRequest) -> MindShiftResponse:
        channel, vak_kw = PNLEngine.detect_vak_channel(request.thought)
        meta = PNLEngine.analyze_meta_model(request.thought)

        if not self.api_key:
            resp = PNLEngine.generate_heuristic_reframes(request.thought, channel, meta)
            resp.vak_keywords = vak_kw
            return resp

        prompt = f"PENSIERO LIMITANTE DELL'UTENTE: \"{request.thought}\"\n"
        if request.context:
            prompt += f"CONTESTO: {request.context}\n"
        if request.preferred_channel:
            prompt += f"CANALE PREFERITO FORZATO: {request.preferred_channel}\n"

        models_to_try = [self.preferred_model] + [m for m in CANDIDATE_MODELS if m != self.preferred_model]
        last_error = None

        for model in models_to_try:
            try:
                loop = asyncio.get_running_loop()
                data = await loop.run_in_executor(None, self._call_gemini_rest_sync, prompt, model)

                raw_ch = data.get("detected_channel", "")
                if "visivo" in raw_ch.lower():
                    final_channel = VAKChannel.VISUAL
                elif "uditivo" in raw_ch.lower():
                    final_channel = VAKChannel.AUDITORY
                elif "cinestesico" in raw_ch.lower():
                    final_channel = VAKChannel.KINESTHETIC
                else:
                    final_channel = channel

                meta_data = data.get("meta_model", {})
                meta_obj = MetaModelAnalysis(
                    category=meta_data.get("category", meta.category),
                    subtype=meta_data.get("subtype", meta.subtype),
                    explanation=meta_data.get("explanation", meta.explanation),
                    detected_trigger_words=meta_data.get("detected_trigger_words", meta.detected_trigger_words),
                    submodalities_insight=meta_data.get("submodalities_insight", "Riorganizzazione percettiva delle submodalità sensoriali.")
                )

                reframes_list = []
                for r in data.get("reframes", []):
                    reframes_list.append(ReframeOption(
                        type=r.get("type", "Ristrutturazione"),
                        title=r.get("title", "Nuova Prospettiva"),
                        content=r.get("content", ""),
                        pnl_explanation=r.get("pnl_explanation", ""),
                        icon=r.get("icon", "💡")
                    ))

                if not reframes_list:
                    reframes_list = PNLEngine.generate_heuristic_reframes(request.thought, final_channel, meta_obj).reframes

                # Anchoring protocol
                proto_data = data.get("anchoring_protocol", {})
                anchoring_proto = AnchoringProtocol(
                    title=proto_data.get("title", "Ancoraggio di Risorsa"),
                    technique_name=proto_data.get("technique_name", "Ancoraggio PNL"),
                    steps=proto_data.get("steps", [
                        "Fai un respiro diaframmatico profondo.",
                        "Visualizza l'obiettivo completato.",
                        "Senti la sicurezza nel corpo."
                    ]),
                    duration_seconds=proto_data.get("duration_seconds", 90),
                    target_state=proto_data.get("target_state", "Stato di Padronanza")
                )

                # Action Plan
                plan_data = data.get("action_plan", {})
                plan = ActionPlan(
                    phase_immediate_2min=plan_data.get("phase_immediate_2min", data.get("empowering_micro_action", "Compi la prima mossa.")),
                    phase_24h_task=plan_data.get("phase_24h_task", "Completa il primo micro-obiettivo entro domani."),
                    phase_7days_habit=plan_data.get("phase_7days_habit", "Consolida l'abitudine dedicandovi 15 minuti al giorno.")
                )

                return MindShiftResponse(
                    original_thought=request.thought,
                    detected_channel=final_channel,
                    vak_keywords=data.get("vak_keywords", vak_kw),
                    meta_model=meta_obj,
                    context_reframe=data.get("context_reframe", ""),
                    meaning_reframe=data.get("meaning_reframe", ""),
                    identity_reframe=data.get("identity_reframe", ""),
                    socratic_question=data.get("socratic_question", ""),
                    reframes=reframes_list,
                    anchoring_protocol=anchoring_proto,
                    action_plan=plan,
                    empowering_micro_action=plan.phase_immediate_2min,
                    anchoring_mantra=data.get("anchoring_mantra", "Io sono il creatore della mia esperienza e avanzo con chiarezza."),
                    before_state=data.get("before_state", {"stato": "Limitante", "energia": "Bassa"}),
                    after_state=data.get("after_state", {"stato": "Potenziante", "energia": "Alta"}),
                    engine_used=f"Google Gemini AI ({model} - Master Protocol)"
                )

            except Exception as err:
                last_error = err
                logger.warning(f"Tentativo con modello {model} fallito: {err}. Provo successivo...")
                continue

        logger.error(f"Tutti i modelli Gemini hanno fallito ({last_error}). Attivo PNL Master Heuristic Protocol v4.0.")
        resp = PNLEngine.generate_heuristic_reframes(request.thought, channel, meta)
        resp.vak_keywords = vak_kw
        resp.engine_used = "PNL Master Heuristic Protocol v4.0 (Multi-Domain Fallback)"
        return resp

gemini_pnl_client = GeminiPNLClient()
