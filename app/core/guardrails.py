"""Guardrail Semantico e Validatore Anti-Contaminazione Tematica.
Garantisce con certezza matematica che nessuna sessione o ristrutturazione
possa contenere concetti, termini o riferimenti estranei al tema espresso dall'utente.
"""

import re
import logging
from typing import Tuple, Optional, Dict, List, Any
from app.core.models import MindShiftResponse

logger = logging.getLogger("mindshift.guardrails")

# Firme lessicali ad alta specificità per domini tematici circoscritti
RESTRICTED_DOMAIN_SIGNATURES: Dict[str, Dict[str, List[str]]] = {
    "intimita_sessualita": {
        "signatures": [
            "erezione", "erettil", "disfunzione", "prostata", "prostat", "tadalafil", 
            "serenoa", "repens", "coito", "penetrazion", "vaginism", "spectatoring", 
            "eiaculazion", "sessual", "sesso", "intimità", "fallica"
        ],
        "allowed_triggers": [
            "sesso", "sessual", "intim", "erezione", "erettil", "disfunzione", "prostata",
            "prostat", "tadalafil", "serenoa", "urologo", "letto", "penetrazion", "vaginism",
            "eiaculaz", "orgasm", "desiderio sessuale"
        ]
    },
    "bridge_carte": {
        "signatures": [
            "licita", "licite", "atout", "smazzata", "smazzate", "prese al tavolo", 
            "tavolo verde", "morto al bridge", "gioco della carta", "dichiarazione di bridge"
        ],
        "allowed_triggers": [
            "bridge", "licit", "atout", "smazzat", "torneo di bridge"
        ]
    },
    "guida_traffico": {
        "signatures": [
            "volante", "guidatore", "traffico", "sorpasso", "precedenza", "carreggiata", 
            "autostrada", "al volante", "abitacolo", "clacson"
        ],
        "allowed_triggers": [
            "guid", "volant", "traffico", "macchina", "auto", "strad", "tangenzial", 
            "corsia", "clacson", "sorpasso", "precedenza"
        ]
    },
    "sarcopenia_sport": {
        "signatures": [
            "sarcopenia", "massa muscolare", "planck", "manubri", "allenamento fisico", "sarcopenic"
        ],
        "allowed_triggers": [
            "sarcopeni", "sport", "palestra", "allenament", "pesi", "muscol", 
            "attività fisica", "esercizi", "planck", "corsa", "correre"
        ]
    }
}


class SemanticTopicGuardrail:
    """Validatore deterministico di pertinenza semantica e barriera anti-allucinazione."""

    @classmethod
    def check_text_contamination(cls, text: str, user_thought: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Verifica se il testo generato contiene termini specifici di un dominio non menzionato dall'utente.
        
        Ritorna:
            (is_contaminated, domain_violated, trigger_word_found)
        """
        if not text or not user_thought:
            return False, None, None

        t_low = text.lower()
        u_low = user_thought.lower()

        for domain, rule in RESTRICTED_DOMAIN_SIGNATURES.items():
            signatures = rule["signatures"]
            allowed_triggers = rule["allowed_triggers"]

            # Controlla se l'input dell'utente menzionava questo dominio
            user_has_domain = any(re.search(rf"\b{re.escape(trig)}", u_low) for trig in allowed_triggers)

            if not user_has_domain:
                # Se l'utente NON parlava di questo dominio, NESSUNA firma di questo dominio deve comparire nell'output
                for sig in signatures:
                    match = re.search(rf"\b{re.escape(sig)}", t_low)
                    if match:
                        logger.warning(
                            f"[GUARDRAIL ALERT] Rilevata contaminazione nel testo per il dominio '{domain}'! "
                            f"Termine vietato trovato: '{sig}'. L'utente parlava di: '{user_thought[:80]}...'"
                        )
                        return True, domain, sig

        return False, None, None

    @classmethod
    def validate_mindshift_response(cls, response: MindShiftResponse, user_thought: str) -> Tuple[bool, Optional[str]]:
        """Esamina l'intera risposta MindShiftResponse (tutti i campi e ristrutturazioni) 
        per assicurare la totale assenza di contaminazione tematica."""
        fields_to_check = [
            ("context_reframe", response.context_reframe),
            ("meaning_reframe", response.meaning_reframe),
            ("identity_reframe", response.identity_reframe),
            ("socratic_question", response.socratic_question),
            ("anchoring_mantra", response.anchoring_mantra),
            ("empowering_micro_action", response.empowering_micro_action)
        ]

        if response.action_plan:
            fields_to_check.append(("action_plan_2min", response.action_plan.phase_immediate_2min))
            fields_to_check.append(("action_plan_24h", response.action_plan.phase_24h_task))
            fields_to_check.append(("action_plan_7d", response.action_plan.phase_7days_habit))

        if response.anchoring_protocol:
            fields_to_check.append(("anchoring_title", response.anchoring_protocol.title))
            for i, st in enumerate(response.anchoring_protocol.steps):
                fields_to_check.append((f"anchoring_step_{i}", st))

        for r in response.reframes:
            fields_to_check.append((f"reframe_{r.type}", r.content))

        for field_name, field_text in fields_to_check:
            if field_text:
                is_contam, domain, kw = cls.check_text_contamination(field_text, user_thought)
                if is_contam:
                    error_msg = f"Contaminazione nel campo '{field_name}': rilevato termine '{kw}' del dominio '{domain}'"
                    logger.error(f"[GUARDRAIL VIOLATION] {error_msg}")
                    return False, error_msg

        return True, None
