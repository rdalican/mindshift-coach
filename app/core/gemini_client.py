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
    ActionPlan,
    SessionStepRequest,
    SessionStepResponse
)
from app.core.pnl_engine import PNLEngine
from app.core.guardrails import SemanticTopicGuardrail

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

REGOLA D'ORO DELL'IPER-SPECIFICITÀ SUL TEMA DELL'UTENTE (DIVIETO DI GENERALIZZAZIONE E CONTAMINAZIONE):
1. ANCORAGGIO TOTALE AL LESSICO E CONTESTO ESATTO: Tutte le 4 ristrutturazioni, le spiegazioni, la domanda socratica, il mantra e i piani di azione DEVONO essere calati al 100% nella materia specifica di cui parla l'utente (es. se parla di Bridge usa termini di Bridge; se parla di guida/traffico usa termini di guida e strada; se parla di sport usa termini atletici).
2. DIVIETO ASSOLUTO DI CONTAMINAZIONE TEMATICA: È severamente vietato introdurre temi non citati dall'utente (come intimità/sessualità, giochi da tavolo, auto o sport) se l'utente non ne ha parlato esplicitamente. Ogni risposta non attinente viene respinta e scartata dai guardrail semantici.
3. DIVIETO ASSOLUTO DI META-GERGO PNL NEL CONTENUTO: Non usare MAI espressioni autoreferenziali come "il piano di ristrutturazione neurolinguistica", "questo esercizio di PNL", "il tempio della mente" o "livelli logici" all'interno delle ristrutturazioni o del mantra! La PNL è il tuo motore invisibile, non l'oggetto del discorso. Parla direttamente del problema pratico dell'utente.
4. PRAGMATISMO CHIRURGICO: Elimina frasi motivazionali generiche o spiritualeggianti. Sii un Master Coach strategico, concreto, lucido e brillante.

SPECIALIZZAZIONE CONDIZIONALE:
- SOLO SE il pensiero riguarda ansia da prestazione sessuale o disfunzione erettile psicogena: decostruisci lo Spectatoring, attiva il parasimpatico e riorienta sul piacere sensoriale privo di performance.
- In TUTTI gli altri casi: mantieni il focus rigidamente ed esclusivamente sulla situazione pratica descritta dall'utente.

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
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-flash-latest"
]

class GeminiPNLClient:
    """Client multi-protocollo per Google Gemini AI (Master Protocol v4.0)."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""
        self.preferred_model = settings.GEMINI_MODEL

    def _call_gemini_rest_sync(self, prompt: str, model_name: str, system_instruction: Optional[str] = None) -> dict:
        import time
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        if self.api_key.startswith("ya29."):
            headers["Authorization"] = f"Bearer {self.api_key}"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"

        full_text = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": full_text}]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.7
            }
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        # Retry con backoff per rate limit temporaneo
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
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
            except urllib.error.HTTPError as he:
                if he.code == 429 and attempt < max_attempts - 1:
                    time.sleep(2.0)
                    continue
                raise he

    async def generate_shift(self, request: MindShiftRequest) -> MindShiftResponse:
        target_text = request.thought
        match_thought = re.search(r'PENSIERO DI PARTENZA:\s*"([^"]+)"', request.thought)
        if match_thought:
            target_text = match_thought.group(1)

        channel, vak_kw = PNLEngine.detect_vak_channel(target_text)
        meta = PNLEngine.analyze_meta_model(target_text)

        if not self.api_key:
            resp = PNLEngine.generate_heuristic_reframes(target_text, channel, meta)
            resp.vak_keywords = vak_kw
            return resp

        prompt = f"PENSIERO LIMITANTE DELL'UTENTE: \"{request.thought}\"\n"
        if request.context:
            prompt += f"CONTESTO: {request.context}\n"
        if request.preferred_channel:
            prompt += f"CANALE PREFERITO FORZATO: {request.preferred_channel}\n"

        # Iniezione Memoria Esperienziale Evolutiva dell'Account
        if request.sync_key:
            try:
                from app.core.database import SessionLocal
                from app.core.experiential_memory import ExperientialMemoryEngine
                with SessionLocal() as db:
                    profile = ExperientialMemoryEngine.get_or_build_profile(request.sync_key, db)
                    if profile and profile.total_episodes_analyzed > 0:
                        profile_block = ExperientialMemoryEngine.format_profile_for_prompt(profile)
                        prompt += f"\n{profile_block}\n"
            except Exception as e:
                logger.warning(f"Impossibile iniettare profilo esperienziale: {e}")

        prompt += "\nDIRETTIVA CRUCIALE: Calati al 100% nella materia e nel lessico esatto dell'utente (es. se parla di Bridge usa termini come licita, atout, piano di gioco; se parla di guida/traffico usa termini come volante, strada, precedenza, calma regale; se parla di sessuologia/intimità usa termini precisi come 'Spectatoring', sistema parasimpatico; se parla di salute/sport usa termini come sarcopenia, allenamento). Focalizzati rigorosamente SOLO sul tema in esame. NON usare meta-gergo PNL nel contenuto: fornisci soluzioni mentali pratiche, specifiche e chirurgiche.\n"

        models_to_try = [self.preferred_model] + [m for m in CANDIDATE_MODELS if m != self.preferred_model]
        last_error = None

        for model in models_to_try:
            try:
                loop = asyncio.get_running_loop()
                data = await loop.run_in_executor(None, self._call_gemini_rest_sync, prompt, model, GEMINI_SYSTEM_INSTRUCTION_V4)

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

                shift_res = MindShiftResponse(
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

                # Controllo di sicurezza Guardrail Semantico
                is_valid, violation_msg = SemanticTopicGuardrail.validate_mindshift_response(shift_res, target_text)
                if not is_valid:
                    logger.warning(f"Modello {model} ha fallito la validazione Guardrail: {violation_msg}. Scarto e provo successivo...")
                    continue

                return shift_res

            except Exception as err:
                last_error = err
                logger.warning(f"Tentativo con modello {model} fallito: {err}. Provo successivo...")
                continue

        logger.error(f"Tutti i modelli Gemini hanno fallito ({last_error}). Attivo PNL Master Heuristic Protocol v4.0.")
        resp = PNLEngine.generate_heuristic_reframes(target_text, channel, meta)
        resp.vak_keywords = vak_kw
        resp.engine_used = "PNL Master Heuristic Protocol v4.0 (Multi-Domain Fallback)"
        return resp

    async def generate_session_step(self, req: SessionStepRequest) -> SessionStepResponse:
        """Esegue uno step della Seduta Interattiva di Psico-Coaching PNL (Fasi 1-4)."""
        session_id = req.session_id or f"SESS-{req.current_step}"
        req.session_id = session_id
        
        if not self.api_key:
            return PNLEngine.generate_heuristic_session_step(req)

        step = req.current_step

        # Iniezione Memoria Esperienziale Evolutiva per calibrare le domande della seduta
        profile_block = ""
        if req.sync_key:
            try:
                from app.core.database import SessionLocal
                from app.core.experiential_memory import ExperientialMemoryEngine
                with SessionLocal() as db:
                    profile = ExperientialMemoryEngine.get_or_build_profile(req.sync_key, db)
                    if profile and profile.total_episodes_analyzed > 0:
                        profile_block = f"\n{ExperientialMemoryEngine.format_profile_for_prompt(profile)}\n"
            except Exception as e:
                logger.warning(f"Impossibile caricare profilo esperienziale per session step: {e}")
        
        # Costruzione del prompt per la fase specifica
        if step == 1:
            instruction = """SEI: Un Master Coach PNL & Psicoterapeuta Ericksoniano empatico e caloroso.
L'utente sta iniziando una seduta e ha espresso questo pensiero/blocco iniziale:
"{initial_thought}" (Contesto: {context})
{profile_block}

OBIETTIVO FASE 1 (Accoglienza Empatica & Chiarimento del Contesto):
1. Formula una risposta empatica di ascolto attivo (in 'coach_message') per validare l'esperienza senza giudizio e senza dare soluzioni premature.
2. Poni esattamente 2 domande di chiarimento chirurgiche (in 'investigation_questions') per comprendere come il blocco si manifesta concretamente nel presente e nel corpo dell'utente (lessico specifico sul tema).
3. Fornisci un'osservazione clinica (in 'clinical_insight') sui meccanismi percettivi in gioco.

OUTPUT JSON OBBLIGATORIO (senza markdown o testo prima/dopo):
{
  "step_title": "Fase 1: Accoglienza Empatica & Chiarimento del Contesto",
  "coach_message": "...",
  "investigation_questions": ["domanda 1", "domanda 2"],
  "clinical_insight": "..."
}"""
            prompt = instruction.replace("{initial_thought}", req.initial_thought).replace("{context}", req.context or "Generale").replace("{profile_block}", profile_block)

        elif step == 2:
            history_text = "\n".join([f"- {m.role.upper()}: {m.content}" for m in req.history])
            instruction = """SEI: Un Master Coach PNL & Psicoterapeuta Ericksoniano.
Pensiero iniziale: "{initial_thought}"
{profile_block}
Cronologia seduta finora:
{history_text}
Ultima risposta dell'utente sul contesto: "{user_resp}"

OBIETTIVO FASE 2 (Esplorazione Storica & Cause Passate / Time-Line):
1. In 'coach_message', rifletti con calore su quanto emerso nel contesto e introduci l'importanza di comprendere l'origine passata dello schema.
2. In 'investigation_questions', poni esattamente 2 domande sulle origini storiche e sul primo imprinting emotivo ("Da quanto tempo porti con te questo schema?", "Qual è il primo ricordo o episodio del passato in cui hai provato la stessa sensazione?").
3. In 'clinical_insight', offri una riflessione clinica sulla Time-Line del pattern.

OUTPUT JSON OBBLIGATORIO:
{
  "step_title": "Fase 2: Esplorazione Storica & Radici Pregresse (Time-Line)",
  "coach_message": "...",
  "investigation_questions": ["domanda 1", "domanda 2"],
  "clinical_insight": "..."
}"""
            prompt = instruction.replace("{initial_thought}", req.initial_thought).replace("{history_text}", history_text).replace("{user_resp}", req.latest_user_response or "").replace("{profile_block}", profile_block)

        elif step == 3:
            history_text = "\n".join([f"- {m.role.upper()}: {m.content}" for m in req.history])
            instruction = """SEI: Un Master Coach PNL & Psicoterapeuta Ericksoniano.
Pensiero iniziale: "{initial_thought}"
{profile_block}
Cronologia seduta finora:
{history_text}
Ultima risposta dell'utente sulla storia passata: "{user_resp}"

OBIETTIVO FASE 3 (Influenze Esterne, Relazioni & Vantaggi Secondari):
1. In 'coach_message', integra le radici storiche emerse con empatia e sposta l'attenzione sull'ambiente relazionale attuale.
2. In 'investigation_questions', poni esattamente 2 domande sull'ambiente esterno, persone che mantengono vivo il blocco (partner, colleghi, famiglia) e sull'intenzione positiva inconscia (vantaggio secondario di autoprotezione).
3. In 'clinical_insight', fornisci una sintesi sistemica.

OUTPUT JSON OBBLIGATORIO:
{
  "step_title": "Fase 3: Influenze Esterne, Relazioni & Vantaggi Secondari",
  "coach_message": "...",
  "investigation_questions": ["domanda 1", "domanda 2"],
  "clinical_insight": "..."
}"""
            prompt = instruction.replace("{initial_thought}", req.initial_thought).replace("{history_text}", history_text).replace("{user_resp}", req.latest_user_response or "").replace("{profile_block}", profile_block)

        else:
            # Fase 4: Sintesi finale terapeutica completa
            history_text = "\n".join([f"- {m.role.upper()}: {m.content}" for m in req.history])
            full_thought_context = f"PENSIERO DI PARTENZA: \"{req.initial_thought}\"\nANAMNESI COMPLETA RACCOLTA DURANTE LA SEDUTA:\n{history_text}\nULTIMA CONDIVISIONE: \"{req.latest_user_response or ''}\""
            
            shift_req = MindShiftRequest(thought=full_thought_context, context=req.context, sync_key=req.sync_key)
            final_shift = await self.generate_shift(shift_req)
            final_shift.original_thought = req.initial_thought

            return SessionStepResponse(
                session_id=session_id,
                current_step=4,
                next_step=4,
                is_final_step=True,
                step_title="Fase 4: Sintesi Clinica & Ristrutturazione Profonda",
                coach_message="Abbiamo completato l'anamnesi approfondita. Avendo ora chiaro il contesto attuale, le radici storiche e le dinamiche relazionali, ecco la tua Scheda Clinica di Trasformazione personalizzata.",
                clinical_insight="Sintesi terapeutica completata con successo: transizione verso l'ancoraggio e il piano operativo in 3 fasi.",
                final_shift=final_shift
            )

        models_to_try = [self.preferred_model] + [m for m in CANDIDATE_MODELS if m != self.preferred_model]
        last_error = None

        for model in models_to_try:
            try:
                loop = asyncio.get_running_loop()
                data = await loop.run_in_executor(None, self._call_gemini_rest_sync, prompt, model)

                coach_msg = data.get("coach_message", "Grazie per aver approfondito.")
                questions = data.get("investigation_questions", [])
                insight = data.get("clinical_insight", "")

                # Validazione anti-contaminazione su step intermedio
                is_c_msg, _, _ = SemanticTopicGuardrail.check_text_contamination(coach_msg, req.initial_thought)
                is_c_ins, _, _ = SemanticTopicGuardrail.check_text_contamination(insight, req.initial_thought)
                is_c_q = any(SemanticTopicGuardrail.check_text_contamination(q, req.initial_thought)[0] for q in questions)

                if is_c_msg or is_c_ins or is_c_q:
                    logger.warning(f"Step intermedio del modello {model} scartato da Guardrail per contaminazione tematica.")
                    continue

                return SessionStepResponse(
                    session_id=session_id,
                    current_step=step,
                    next_step=step + 1,
                    is_final_step=False,
                    step_title=data.get("step_title", f"Fase {step}"),
                    coach_message=coach_msg,
                    investigation_questions=questions,
                    clinical_insight=insight
                )
            except Exception as err:
                last_error = err
                logger.warning(f"Tentativo sessione con modello {model} fallito: {err}. Provo successivo...")
                continue

        logger.error(f"Tutti i modelli Gemini hanno fallito per session step ({last_error}). Fallback euristico.")
        return PNLEngine.generate_heuristic_session_step(req)

gemini_pnl_client = GeminiPNLClient()

