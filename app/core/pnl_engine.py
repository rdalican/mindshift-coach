"""Motore di Programmazione Neuro-Linguistica (PNL Master Protocol v4.0).
Comprende:
1. Diagnosi Neuro-Linguistica e decodifica delle Submodalità
2. 4 Ristrutturazioni Cognitive di Livello Superiore (Contesto, Significato, Identità Dilts, Domanda Socratica)
3. Protocollo di Ancoraggio & Fisiologia Guidato (Auto-Coaching)
4. Piano di Azione Operativo a 3 Fasi (2 min / 24 ore / 7 giorni)
5. Mantra Ipnotico di Potere (Erickson)
"""

import re
from typing import List, Tuple, Dict, Optional
from app.core.models import (
    VAKChannel,
    MetaModelCategory,
    MetaModelAnalysis,
    ReframeOption,
    AnchoringProtocol,
    ActionPlan,
    MindShiftResponse
)

# DIZIONARI SENSORIALI VAK
VAK_DICTIONARY = {
    VAKChannel.VISUAL: [
        "vedere", "vedo", "chiaro", "limpido", "prospettiva", "orizzonte", "buio", "sfocato", 
        "immagine", "guardare", "osservare", "luce", "colore", "visualizzare", "apparenza", 
        "scorgere", "nebbia", "mostrare", "lucido", "quadro", "visibile", "brillante", "cieco",
        "visione", "panorama", "nero", "punto di vista", "flash", "trasparente", "intravedere"
    ],
    VAKChannel.AUDITORY: [
        "ascoltare", "ascolto", "suonare", "suona", "risuonare", "risuona", "stonato", "rumore", 
        "voce", "silenzio", "armonia", "grido", "sussurro", "ripetere", "tono", "eco", "discutere", 
        "accordo", "disaccordo", "gridare", "parlare", "udire", "volume", "melodia", "parole",
        "rumoroso", "chiacchierare", "dichiarare", "chiedere", "domandare", "frastuono"
    ],
    VAKChannel.KINESTHETIC: [
        "sentire", "sento", "peso", "pesante", "leggero", "schiacciato", "bloccato", "afferrare", 
        "toccare", "caldo", "freddo", "contatto", "tensione", "spinta", "crollo", "scivolare", 
        "solido", "duro", "morbido", "stretta", "nodo", "ansia", "pancia", "respiro", "affanno",
        "concreto", "urtare", "sprofondare", "morsa", "vibrazione", "brivido", "carico", "pressione"
    ]
}

META_MODEL_PATTERNS = [
    (
        MetaModelCategory.GENERALIZATION,
        "Quantificatore Universale",
        r"\b(sempre|mai|tutti|nessuno|niente|nulla|ovunque|chiunque|ogni volta|tutto)\b",
        "Estensione indebita di un singolo episodio a regola universale permanente.",
        "Il cervello sta eliminando selettivamente tutte le eccezioni positive passate per proteggerti dal rischio di delusioni future."
    ),
    (
        MetaModelCategory.GENERALIZATION,
        "Operatore Modale di Necessità",
        r"\b(devo|dovrei|bisogna|è necessario|tocca a me|sono costretto|non ho scelta)\b",
        "Sensazione di costrizione esterna e assenza di opzioni decisionali.",
        "La mente trasforma un desiderio o una scelta in un obbligo soffocante, attivando la resistenza inconscia."
    ),
    (
        MetaModelCategory.GENERALIZATION,
        "Operatore Modale di Impossibilità",
        r"\b(non posso|impossibile|non riesco|non sono capace|non ce la faccio|incapace|non sono all'altezza)\b",
        "Convinzione limitante sulle proprie capacità e risorse interiori.",
        "Stai scambiando una mancanza momentanea di strategia o abilità con un limite permanente della tua identità."
    ),
    (
        MetaModelCategory.DISTORTION,
        "Lettura del Pensiero (Mind Reading)",
        r"\b(pensano che|so già che|credono che|mi giudicano|mi considerano|pensa che io|diranno che|penseranno)\b",
        "Presunzione di conoscere i pensieri o le intenzioni altrui senza verifica sensoriale diretta.",
        "Stai proiettando le tue insicurezze personali nella mente degli altri, scambiando le tue fantasie per fatti oggettivi."
    ),
    (
        MetaModelCategory.DISTORTION,
        "Causa-Effetto / Equivalenza Complessa",
        r"\b(mi fa sentire|mi rende|se .* allora|significa che|vuol dire che|provoca|causa|genera)\b",
        "Attribuzione del proprio stato emotivo interno a un fattore esterno indipendente.",
        "Stai cedendo il telecomando del tuo stato d'animo a un evento esterno che in realtà non ha potere diretto sulla tua reazione."
    ),
    (
        MetaModelCategory.DELETION,
        "Comparativa Mancante",
        r"\b(non sono abbastanza|è troppo|troppo tardi|peggio|meglio|poco|insufficiente|inferiore|minore)\b",
        "Giudizio basato su uno standard di confronto implicito non specificato.",
        "Stai usando un metro di paragone invisibile e irraggiungibile per invalidare i progressi reali che stai compiendo."
    ),
    (
        MetaModelCategory.DELETION,
        "Indice Referenziale Mancante",
        r"\b(la gente|loro|il mondo|la società|tutti quanti|si dice|nessuno mi)\b",
        "Generalizzazione su un gruppo non specificato di persone o entità.",
        "La mente crea un'entità anonima astratta per giustificare l'esitazione senza affrontare individui specifici."
    )
]

THEMATIC_DOMAINS = [
    {
        "domain": "tempo",
        "keywords": ["tempo", "tardi", "orari", "giornata", "fretta", "ritardo", "scadenza", "anno", "mese", "ora", "anni"],
        "context_reframe": "La sensazione di non avere tempo è il miglior filtro naturale per eliminare il 80% delle distrazioni inutili e concentrarsi solo sull'azione essenziale che muove davvero l'ago.",
        "meaning_reframe": "Il tempo non è una misura che si subisce, ma una risorsa che si genera stabilendo priorità chiare. Un'ora di lavoro iper-focalizzato vale più di una settimana di dispersione.",
        "identity_reframe": "Non sei una persona 'sopraffatta dal tempo': sei un architetto strategico che impara a padroneggiare la concentrazione estrema.",
        "socratic_question": "Se avessi a disposizione soltanto 20 minuti al giorno da dedicare a questo progetto, quale singola azione compiresti che renderebbe tutto il resto più facile?",
        "action_2min": "Imposta il timer del telefono per 10 minuti in modalità 'zero notifiche' e scrivi la prima bozza della tua attività.",
        "action_24h": "Elimina dalla tua agenda di domani un'attività non fondamentale per liberare un blocco di 45 minuti inviolabili.",
        "action_7days": "Installa la routine 'Power Hour': ogni mattina alle 8:30 dedica i primi 30 minuti esclusivamente al tuo obiettivo primario prima di aprire email e social.",
        "mantra": "Io non cerco il tempo: io genero lo spazio per ciò che è sacro per la mia crescita.",
        "anchor_title": "Ancoraggio del Tempo Flessibile",
        "anchor_technique": "Riorganizzazione Visiva della Time-Line",
        "anchor_steps": [
            "Fai 2 respiri lenti e profondi, chiudendo gli occhi per un istante.",
            "Visualizza la tua linea del tempo davanti a te come un sentiero spazioso e luminoso.",
            "Prendi il compito di oggi e posizionalo esattamente nei primi 2 metri del sentiero, vedendolo nitido e leggero.",
            "Riapri gli occhi con la certezza che lo spazio necessario esiste già."
        ]
    },
    {
        "domain": "denaro",
        "keywords": ["soldi", "denaro", "costa", "prezzo", "economico", "pagare", "guadagnare", "stipendio", "vendita", "costoso", "euro", "clienti"],
        "context_reframe": "La prudenza sul denaro dimostra rispetto per il valore e maturità gestionale. In fase di crescita, è la forza che ti spinge a costruire offerte impeccabili e sostenibili.",
        "meaning_reframe": "Il denaro segue sempre il valore scambiato e la risoluzione di problemi reali. Chiedere il giusto prezzo è un atto di rispetto verso il cliente, che si impegnerà al massimo nel percorso.",
        "identity_reframe": "Non sei qualcuno che 'chiede soldi': sei un professionista generatore di soluzioni che merita di essere remunerato per il valore creato.",
        "socratic_question": "Quale problema specifico e urgente puoi risolvere per un cliente che renderebbe il prezzo della tua soluzione un investimento ovvio?",
        "action_2min": "Scrivi su un foglio la cifra esatta che intendi richiedere e pronunciala ad alta voce 3 volte con voce ferma.",
        "action_24h": "Elenca 3 testimonianze, casi studio o benefici tangibili che il tuo lavoro produce per chi si affida a te.",
        "action_7days": "Presenta la tua offerta a prezzo pieno a 2 nuovi potenziali clienti senza concedere sconti automatici.",
        "mantra": "Il mio valore è solido, la mia competenza è reale, la mia ricchezza è la conseguenza naturale del valore che porto al mondo.",
        "anchor_title": "Ancoraggio di Prosperità e Sicurezza",
        "anchor_technique": "Ancoraggio Cinestesico di Solidità",
        "anchor_steps": [
            "Mettiti in piedi, appoggia entrambi i piedi ben piantati a terra alla larghezza delle spalle.",
            "Stringi il pugno destro richiamando alla mente il momento in cui hai aiutato qualcuno con competenza.",
            "Respira sentendo la colonna vertebrale eretta e stabile.",
            "Pronuncia a mente: 'Il mio lavoro trasforma la vita delle persone'."
        ]
    },
    {
        "domain": "giudizio_sociale",
        "keywords": ["giudizio", "giudicano", "pensano", "parlano", "figuraccia", "vergogna", "ridere", "famiglia", "amici", "colleghi", "critica"],
        "context_reframe": "La tua attenzione verso le opinioni altrui è indice di spiccata sensibilità ed empatia. Incanalata a tuo favore, ti consente di comprendere i bisogni profondi delle persone prima degli altri.",
        "meaning_reframe": "Le persone giudicano sempre attraverso il filtro delle proprie paure e dei propri limiti. Chi sta davvero costruendo qualcosa non ha il tempo né l'interesse di criticare chi ci sta provando.",
        "identity_reframe": "Non sei un attore in cerca di applausi: sei un pioniere guidato dai propri valori autentici.",
        "socratic_question": "In base a quali prove sensoriali concrete e oggettive sai cosa pensano gli altri? Cosa cambierebbe se scoprissi che molti stanno semplicemente ammirando la tua iniziativa?",
        "action_2min": "Pronuncia ad alta voce: 'La mia autostima dipende dalla coerenza con i miei valori, non dall'approvazione temporanea di terzi' e fai un respiro profondo.",
        "action_24h": "Pubblica o condividi quell'idea o contenuto che stavi trattenendo per paura dei commenti.",
        "action_7days": "Pratica l'esercizio dell'esposizione graduale: esprimi un'opinione autentica e costruttiva in ogni riunione o discussione importante.",
        "mantra": "Accetto la mia unicità, cammino a testa alta e lascio che i miei risultati parlino per me.",
        "anchor_title": "Scudo Emotivo di Centratura",
        "anchor_technique": "Dissociazione Visiva Protettiva",
        "anchor_steps": [
            "Immagina una bolla trasparente e infrangibile di luce dorata che circonda tutto il tuo corpo a 360 gradi.",
            "Osserva le opinioni altrui rimbalzare sulla superficie della bolla senza toccare il tuo nucleo.",
            "Senti la calma interiore mentre mantieni il sorriso e il contatto visivo."
        ]
    }
]

class PNLEngine:
    """Motore euristico e analitico di Programmazione Neuro-Linguistica (v4.0)."""

    @staticmethod
    def detect_vak_channel(text: str) -> Tuple[VAKChannel, List[str]]:
        text_lower = text.lower()
        scores = {VAKChannel.VISUAL: 0, VAKChannel.AUDITORY: 0, VAKChannel.KINESTHETIC: 0}
        found_keywords = []

        for channel, words in VAK_DICTIONARY.items():
            for word in words:
                matches = re.findall(rf"\b{re.escape(word)}\b", text_lower)
                if matches:
                    count = len(matches)
                    scores[channel] += count
                    found_keywords.append(f"{word} ({channel.value.split()[0]})")

        max_score = max(scores.values())
        if max_score == 0:
            return VAKChannel.MIXED, []

        top_channels = [ch for ch, sc in scores.items() if sc == max_score]
        if len(top_channels) > 1:
            return VAKChannel.MIXED, found_keywords
        
        return top_channels[0], found_keywords

    @staticmethod
    def analyze_meta_model(text: str) -> MetaModelAnalysis:
        text_lower = text.lower()
        for category, subtype, pattern, explanation, submodalities in META_MODEL_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                return MetaModelAnalysis(
                    category=category.value,
                    subtype=subtype,
                    explanation=explanation,
                    detected_trigger_words=list(set(matches)),
                    submodalities_insight=submodalities
                )

        return MetaModelAnalysis(
            category=MetaModelCategory.DELETION.value,
            subtype="Cancellazione Semplice / Stato Emotivo",
            explanation="Espressione di un limite o blocco senza specificare il processo causale o le risorse disponibili.",
            detected_trigger_words=[],
            submodalities_insight="Il cervello sta riducendo l'orizzonte visivo per focalizzarsi solo sull'ostacolo immediato."
        )

    @classmethod
    def match_thematic_domain(cls, text: str) -> Optional[Dict[str, str]]:
        t_low = text.lower()
        for domain_data in THEMATIC_DOMAINS:
            for kw in domain_data["keywords"]:
                if re.search(rf"\b{re.escape(kw)}\b", t_low):
                    return domain_data
        return None

    @classmethod
    def generate_heuristic_reframes(cls, text: str, channel: VAKChannel, meta: MetaModelAnalysis) -> MindShiftResponse:
        matched = cls.match_thematic_domain(text)
        trigger = meta.detected_trigger_words[0] if meta.detected_trigger_words else "questo"

        if matched:
            ctx = matched["context_reframe"]
            mean = matched["meaning_reframe"]
            ident = matched["identity_reframe"]
            soc = matched["socratic_question"]
            act_2m = matched["action_2min"]
            act_24h = matched["action_24h"]
            act_7d = matched["action_7days"]
            mantra = matched["mantra"]
            anchor_title = matched["anchor_title"]
            anchor_tech = matched["anchor_technique"]
            anchor_steps = matched["anchor_steps"]
        else:
            ctx = f"Riconoscere l'intensità di questo pensiero dimostra che hai una forte carica emotiva pronta ad essere incanalata verso una strategia più funzionale."
            mean = f"Questo momento di frizione non è un blocco invalicabile, ma il segnale fisiologico che stai uscendo dalla tua vecchia zona di comfort."
            ident = f"Non sei definito dalle tue temporanee esitazioni: sei colui che osserva il pensiero e ha il potere di riprogrammarlo."
            soc = f"Se sapessi con certezza che ogni tentativo affina la tua maestria, quale singolo passo compiresti adesso?"
            act_2m = "Alzati in piedi, apri il torace e fai 3 respiri profondi con espirazione prolungata (4s dentro, 6s fuori). Scrivi subito su un foglio la prima azione concreta da compiere per rompere l'inerzia."
            act_24h = "Blocca uno slot di 30 minuti nel tuo calendario di oggi: esegui e completa il compito operativo principale (es. stesura bozza, invio messaggio/email chiave, definizione preventivo) senza accettare interruzioni."
            act_7d = "Protocollo di consolidamento a 7 giorni: ogni mattina alle 8:30 ripeti il mantra di potere per 60 secondi prima di aprire le notifiche e registra ogni sera sul diario i 3 micro-progressi reali conseguiti."
            mantra = "Io sono più grande di qualsiasi ostacolo temporaneo e avanzo con chiarezza e potere."
            anchor_title = "Ancoraggio di Risorsa Istantanea",
            anchor_tech = "Cambio di Fisiologia e Ancoraggio Circolare",
            anchor_steps = [
                "Porta le spalle indietro e in basso, aprendo il torace.",
                "Fai un respiro diaframmatico profondo espirando più lentamente di quanto hai inspirato.",
                "Scegli un punto fermo davanti a te e sorridi per 5 secondi attivando i muscoli zigomatici.",
                "Senti l'ondata di lucidità mentale che si diffonde nel corpo."
            ]

        reframes = [
            ReframeOption(
                type="Ristrutturazione di Contesto",
                title="Trasforma il Limite in Risorsa Strategica",
                content=ctx,
                pnl_explanation="Sposta il comportamento in un ambiente dove diventa un punto di forza e protezione.",
                icon="🔄"
            ),
            ReframeOption(
                type="Ristrutturazione di Significato",
                title="Nuovo Significato Potenziante (Milton Model)",
                content=mean,
                pnl_explanation="Applica presupposizioni ipnotiche di competenza, apprendimento e maestria.",
                icon="💡"
            ),
            ReframeOption(
                type="Ristrutturazione di Identità (Robert Dilts)",
                title="Elevazione del Livello Logico Identitario",
                content=ident,
                pnl_explanation="Disidentifica l'individuo dal comportamento temporaneo ancorandolo ai suoi valori guida.",
                icon="👑"
            ),
            ReframeOption(
                type="Domanda Socratica & Doppio Legame",
                title="Domanda di Sblocco Strutturale",
                content=soc,
                pnl_explanation="Decostruisce la trappola del Meta-Modello e costringe la mente a trovare una soluzione attiva.",
                icon="🎯"
            )
        ]

        anchoring_proto = AnchoringProtocol(
            title=anchor_title if isinstance(anchor_title, str) else anchor_title[0],
            technique_name=anchor_tech if isinstance(anchor_tech, str) else anchor_tech[0],
            steps=anchor_steps,
            duration_seconds=90,
            target_state="Lucidità, Sicurezza e Focalizzazione Immediata"
        )

        plan = ActionPlan(
            phase_immediate_2min=act_2m,
            phase_24h_task=act_24h,
            phase_7days_habit=act_7d
        )

        return MindShiftResponse(
            original_thought=text,
            detected_channel=channel,
            vak_keywords=[],
            meta_model=meta,
            context_reframe=ctx,
            meaning_reframe=mean,
            identity_reframe=ident,
            socratic_question=soc,
            reframes=reframes,
            anchoring_protocol=anchoring_proto,
            action_plan=plan,
            empowering_micro_action=act_2m,
            anchoring_mantra=mantra,
            engine_used="PNL Master Heuristic Protocol v4.0"
        )
