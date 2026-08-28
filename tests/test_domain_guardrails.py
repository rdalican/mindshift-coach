import pytest
from app.core.guardrails import SemanticTopicGuardrail
from app.core.models import (
    MindShiftResponse, 
    VAKChannel, 
    MetaModelAnalysis, 
    ReframeOption, 
    AnchoringProtocol, 
    ActionPlan
)
from app.core.pnl_engine import PNLEngine

def test_guardrail_detects_intimacy_contamination_in_driving_topic():
    user_thought = "Quando sono al volante perdo la pazienza se qualcuno mi taglia la strada"
    bad_text = "L'erezione non è un problema di performance ma di ansia da prestazione."
    is_contam, domain, kw = SemanticTopicGuardrail.check_text_contamination(bad_text, user_thought)
    assert is_contam is True
    assert domain == "intimita_sessualita"
    assert kw == "erezione"

def test_guardrail_allows_intimacy_terms_when_user_explicitly_mentions_it():
    user_thought = "Soffro di disfunzione erettile e ansia da prestazione a letto"
    valid_text = "L'erezione riflette il sistema nervoso parasimpatico e la serenità."
    is_contam, domain, kw = SemanticTopicGuardrail.check_text_contamination(valid_text, user_thought)
    assert is_contam is False
    assert domain is None

def test_guardrail_detects_bridge_contamination_in_sport_topic():
    user_thought = "Devo fare più esercizio fisico per combattere la sarcopenia"
    bad_text = "Al tavolo verde prima di fare la licita osserva il morto."
    is_contam, domain, kw = SemanticTopicGuardrail.check_text_contamination(bad_text, user_thought)
    assert is_contam is True
    assert domain == "bridge_carte"

def test_guardrail_full_mindshift_response_validation():
    user_thought = "Ho paura di parlare in pubblico durante le riunioni di lavoro"
    
    # Valid response
    ch, vkw = PNLEngine.detect_vak_channel(user_thought)
    meta = PNLEngine.analyze_meta_model(user_thought)
    clean_shift = PNLEngine.generate_heuristic_reframes(user_thought, ch, meta)
    
    is_valid, violation = SemanticTopicGuardrail.validate_mindshift_response(clean_shift, user_thought)
    assert is_valid is True
    assert violation is None

def test_guardrail_catches_contaminated_mindshift_response():
    user_thought = "Non riesco a studiare per l'esame universitario"
    
    contaminated_shift = MindShiftResponse(
        original_thought=user_thought,
        detected_channel=VAKChannel.VISUAL,
        meta_model=MetaModelAnalysis(category="Cancellazione", subtype="Semplice", explanation="", detected_trigger_words=[]),
        context_reframe="La risposta del tuo corpo con la prostata è normale.",
        meaning_reframe="L'erezione non è un dovere.",
        identity_reframe="Sei un uomo saggio.",
        socratic_question="Cosa faresti?",
        reframes=[
            ReframeOption(type="Contesto", title="", content="Disinnesca lo spectatoring intimo.", pnl_explanation="", icon="")
        ],
        anchoring_protocol=AnchoringProtocol(title="", technique_name="", steps=["Respira"], duration_seconds=90, target_state=""),
        action_plan=ActionPlan(phase_immediate_2min="Azione", phase_24h_task="Task", phase_7days_habit="Habit"),
        empowering_micro_action="Azione",
        anchoring_mantra="Mantra di potere"
    )
    
    is_valid, violation = SemanticTopicGuardrail.validate_mindshift_response(contaminated_shift, user_thought)
    assert is_valid is False
    assert "intimita_sessualita" in violation or "prostata" in violation or "erezione" in violation

@pytest.mark.parametrize("scenario_thought", [
    "Ho paura di chiedere un aumento al mio capo",
    "Non riesco a svegliarmi presto la mattina per correre",
    "Mi sento in colpa quando spendo soldi per me stesso",
    "Quando cucino per gli ospiti ho l'ansia che il cibo non piaccia",
    "Ho un blocco creativo quando devo scrivere un articolo di lavoro",
    "Quando guido in tangenziale mi arrabbio con chi non mette le frecce",
    "Procrastino sempre la compilazione della dichiarazione dei redditi",
    "Non riesco a dire di no agli amici quando mi chiedono favori"
])
def test_ten_diverse_domains_produce_zero_contamination(scenario_thought):
    ch, vkw = PNLEngine.detect_vak_channel(scenario_thought)
    meta = PNLEngine.analyze_meta_model(scenario_thought)
    response = PNLEngine.generate_heuristic_reframes(scenario_thought, ch, meta)
    
    is_valid, violation = SemanticTopicGuardrail.validate_mindshift_response(response, scenario_thought)
    assert is_valid is True, f"Fallimento per scenario '{scenario_thought}': {violation}"
