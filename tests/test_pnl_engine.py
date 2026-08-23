import pytest
from app.core.pnl_engine import PNLEngine
from app.core.models import VAKChannel, MetaModelCategory

def test_detect_vak_channel_visual():
    text = "Non vedo una prospettiva chiara per il mio futuro lavorativo."
    channel, keywords = PNLEngine.detect_vak_channel(text)
    assert channel == VAKChannel.VISUAL
    assert any("vedo" in kw or "chiara" in kw or "prospettiva" in kw for kw in keywords)

def test_detect_vak_channel_auditory():
    text = "Tutto questo rumore mi confonde, non riesco ad ascoltare la mia voce interiore."
    channel, keywords = PNLEngine.detect_vak_channel(text)
    assert channel == VAKChannel.AUDITORY
    assert any("rumore" in kw or "ascoltare" in kw or "voce" in kw for kw in keywords)

def test_detect_vak_channel_kinesthetic():
    text = "Sento un peso enorme sulle spalle e sono completamente bloccato."
    channel, keywords = PNLEngine.detect_vak_channel(text)
    assert channel == VAKChannel.KINESTHETIC
    assert any("peso" in kw or "bloccato" in kw for kw in keywords)

def test_analyze_meta_model_universal_quantifier():
    text = "Non riesco mai a terminare i miei progetti in tempo, sbaglio sempre tutto."
    meta = PNLEngine.analyze_meta_model(text)
    assert meta.category == MetaModelCategory.GENERALIZATION.value
    assert meta.subtype == "Quantificatore Universale"
    assert len(meta.detected_trigger_words) > 0

def test_analyze_meta_model_modal_operator():
    text = "Devo per forza fare tutto da solo, altrimenti è impossibile."
    meta = PNLEngine.analyze_meta_model(text)
    assert meta.category == MetaModelCategory.GENERALIZATION.value
    assert meta.subtype in ["Operatore Modale di Necessità", "Operatore Modale di Impossibilità", "Quantificatore Universale"]

def test_analyze_meta_model_missing_comparative():
    text = "Non sono abbastanza bravo per questo ruolo lavorativo."
    meta = PNLEngine.analyze_meta_model(text)
    assert meta.category == MetaModelCategory.DELETION.value
    assert meta.subtype == "Comparativa Mancante"

def test_generate_heuristic_reframes():
    text = "Non ho abbastanza tempo per completare il progetto."
    channel, _ = PNLEngine.detect_vak_channel(text)
    meta = PNLEngine.analyze_meta_model(text)
    response = PNLEngine.generate_heuristic_reframes(text, channel, meta)
    
    assert response.original_thought == text
    assert len(response.reframes) >= 3
    assert len(response.context_reframe) > 10
    assert len(response.meaning_reframe) > 10
    assert len(response.socratic_question) > 5
    assert len(response.empowering_micro_action) > 5
    assert response.anchoring_protocol is not None
    assert response.action_plan is not None
    assert len(response.anchoring_mantra) > 5
