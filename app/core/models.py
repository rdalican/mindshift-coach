from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class VAKChannel(str, Enum):
    VISUAL = "Visivo (V)"
    AUDITORY = "Uditivo (A)"
    KINESTHETIC = "Cinestesico (K)"
    MIXED = "Misto / Neutro"

class MetaModelCategory(str, Enum):
    GENERALIZATION = "Generalizzazione"
    DELETION = "Cancellazione"
    DISTORTION = "Distorsione"

class MetaModelAnalysis(BaseModel):
    category: str
    subtype: str
    explanation: str
    detected_trigger_words: List[str] = []
    submodalities_insight: Optional[str] = Field(None, description="Come il cervello costruisce il blocco a livello percettivo")

class ReframeOption(BaseModel):
    type: str # "Contesto", "Significato", "Identità (Dilts)", "Domanda Socratica"
    title: str
    content: str
    pnl_explanation: str
    icon: str

class AnchoringProtocol(BaseModel):
    title: str
    technique_name: str
    steps: List[str]
    duration_seconds: int = 90
    target_state: str

class ActionPlan(BaseModel):
    phase_immediate_2min: str
    phase_24h_task: str
    phase_7days_habit: str

class MindShiftRequest(BaseModel):
    thought: str = Field(..., min_length=3, max_length=1500, description="Il pensiero limitante o blocco emotivo da ristrutturare.")
    context: Optional[str] = Field(None, description="Contesto opzionale (business, lavoro, denaro, relazioni, salute).")
    preferred_channel: Optional[str] = Field(None, description="Canale sensoriale preferito opzionale.")
    sync_key: Optional[str] = Field(None, description="Sync Key per sincronizzare immediatamente il risultato nel Cloud.")

class MindShiftResponse(BaseModel):
    id: Optional[str] = None
    original_thought: str
    context: Optional[str] = None
    detected_channel: VAKChannel
    vak_keywords: List[str] = []
    meta_model: MetaModelAnalysis
    
    # 4 Ristrutturazioni Avanzate
    context_reframe: str
    meaning_reframe: str
    identity_reframe: str = ""
    socratic_question: str
    
    reframes: List[ReframeOption] = []
    
    # Protocollo di Ancoraggio & Auto-Coaching
    anchoring_protocol: AnchoringProtocol
    
    # Piano di Azione a 3 Fasi (2 min / 24 ore / 7 giorni)
    action_plan: ActionPlan
    empowering_micro_action: str
    
    # Mantra Ipnotico di Potere (Erickson)
    anchoring_mantra: str = ""
    
    before_state: Dict[str, str] = Field(default_factory=lambda: {"stato": "Bloccato/Limitante", "energia": "Bassa", "fisiologia": "Chiusa/Contratta"})
    after_state: Dict[str, str] = Field(default_factory=lambda: {"stato": "Risorsa/Potere", "energia": "Focalizzata/Alta", "fisiologia": "Aperta/Stabile"})
    engine_used: str = "Google Gemini AI (Master PNL Protocol)"

# --- MODELLI DI SINCRONIZZAZIONE CROSS-DEVICE ---
class DevicePairRequest(BaseModel):
    sync_key: Optional[str] = Field(None, description="Chiave esistente per collegare un secondo dispositivo. Se omessa, viene generata una nuova chiave.")
    email: Optional[str] = Field(None, description="Email opzionale.")
    device_name: Optional[str] = Field("Primary Device", description="Nome del dispositivo.")

class DevicePairResponse(BaseModel):
    sync_key: str
    plan_status: str
    total_synced_shifts: int
    message: str

class SyncShiftItem(BaseModel):
    id: str
    sync_key: Optional[str] = None
    original_thought: str
    context: Optional[str] = None
    detected_channel: str
    meta_category: str = "Generalizzazione"
    meta_subtype: str = "Pattern PNL"
    meta_explanation: Optional[str] = None
    context_reframe: Optional[str] = None
    meaning_reframe: Optional[str] = None
    identity_reframe: Optional[str] = None
    socratic_question: Optional[str] = None
    empowering_micro_action: Optional[str] = None
    anchoring_mantra: Optional[str] = None
    reframes: List[ReframeOption] = []
    anchoring_protocol: Optional[AnchoringProtocol] = None
    action_plan: Optional[ActionPlan] = None
    is_favorite: bool = False
    created_at: Optional[str] = None

class SyncShiftsResponse(BaseModel):
    sync_key: str
    shifts: List[SyncShiftItem]
    count: int

# --- MODELLI STRIPE & MONETIZZAZIONE ---
class StripeCheckoutRequest(BaseModel):
    sync_key: str
    email: Optional[str] = None
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class StripeCheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str
    is_mock: bool = False

# --- MODELLI ANALYTICS & FEEDBACK PNL ---
class VAKDistribution(BaseModel):
    visual_pct: float
    auditory_pct: float
    kinesthetic_pct: float
    mixed_pct: float
    dominant_channel: str
    total_analyzed: int

class CategoryBreakdown(BaseModel):
    category_name: str
    count: int
    percentage: float

class VAKAnalyticsResponse(BaseModel):
    sync_key: str
    distribution: VAKDistribution
    categories_breakdown: List[CategoryBreakdown]
    total_shifts: int
    average_resonance_score: float
    empowerment_index: float

class ReframeFeedbackRequest(BaseModel):
    sync_key: str
    shift_id: str
    reframe_type: str
    rating: int = Field(..., ge=1, le=5, description="Valutazione da 1 a 5 stelle")
    comment: Optional[str] = None

class ReframeFeedbackResponse(BaseModel):
    status: str
    message: str
    recorded_rating: int

# --- MODELLI ROADMAP ---
class RoadmapStepStatus(str, Enum):
    DONE = "completed"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"

class RoadmapStep(BaseModel):
    id: str
    week: int
    title: str
    description: str
    deliverable: str
    status: RoadmapStepStatus = RoadmapStepStatus.PENDING

class RoadmapWeek(BaseModel):
    week_number: int
    title: str
    objective: str
    status: str
    steps: List[RoadmapStep]

class RoadmapResponse(BaseModel):
    current_week: int
    completion_percentage: float
    weeks: List[RoadmapWeek]

class RoadmapStepToggleRequest(BaseModel):
    step_id: str
    status: RoadmapStepStatus
