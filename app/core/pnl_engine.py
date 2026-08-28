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
    MindShiftResponse,
    SessionStepRequest,
    SessionStepResponse
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
        "keywords": ["non ho tempo", "manca il tempo", "senza tempo", "scadenza", "scadenze", "fretta", "ritardo", "procrastinazione", "giornata corta", "troppe cose da fare", "agenda piena"],
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
    },
    {
        "domain": "intimita_sessualita",
        "keywords": [
            "sesso", "sessuale", "sessualità", "intimità", "erezione", "erettile", "disfunzione erettile",
            "insufficienza erettile", "ansia da prestazione", "prostata", "prostatica", "ipertrofia prostatica",
            "tadalafil", "serenoa repens", "urologo", "spectatoring", "vaginismo", "eiaculazione precoce",
            "penetrazione", "coito", "calo del desiderio"
        ],
        "context_reframe": "La risposta del tuo corpo non è un guasto meccanico, ma il riflesso di un sistema nervoso che è andato in allarme (iperattivazione simpatica) per proteggerti da antichi timori di giudizio. Riconoscere la componente psicogena e medica insieme permette di disinnescare la pressione e ristabilire la normale risposta fisiologica.",
        "meaning_reframe": "L'intimità non è un test di valore o un dovere esecutivo a comando, ma un processo involontario regolato dal sistema parasimpatico che fiorisce solo quando c'è assenza di giudizio, calma e piacere sensoriale puro. Disinnescare la 'Mente Spettatore' apre la via alla vera serenità.",
        "identity_reframe": "Non sei un 'uomo con un problema di prestazione': sei un uomo con una ricca storia emotiva, degno di intimità autentica, piacere e accoglienza, capace di vivere la propria sensualità senza dover dimostrare nulla a nessuno.",
        "socratic_question": "Cosa accadrebbe se durante l'intimità smettessi di monitorare la tua risposta fisica dall'esterno e ti concedessi di essere semplicemente presente nel contatto, nel respiro e nel piacere condiviso?",
        "action_2min": "Esegui 4 cicli di respirazione 4-8 (inspira 4 secondi dal naso espandendo l'addome, espira 8 secondi a labbra socchiuse): questo attiva istantaneamente il nervo vago e riduce l'adrenalina nel sangue.",
        "action_24h": "Condividi un momento di intimità non orientato alla prestazione (es. carezze, massaggio, contatto pelle a pelle), concordando preventivamente che l'unico scopo è il rilassamento e la sintonia sensoriale.",
        "action_7days": "Installa il protocollo di 'Defusione dello Spectatoring': ogni volta che ti accorgi di osservarti dall'alto o giudicarti, di' mentalmente 'Stop' e sposta il 100% dell'attenzione su 3 sensazioni tattili fisiche (il calore della pelle, il battito, il respiro).",
        "mantra": "Io lascio andare ogni controllo e pretesa: il mio corpo è al sicuro e risponde con naturalezza alla calma e al piacere.",
        "anchor_title": "Ancoraggio di Presenza Sensoriale e Calma Parasimpatica",
        "anchor_technique": "Ri-associazione Cinestesica & Respirazione Vago-Mediata",
        "anchor_steps": [
            "Fai un respiro diaframmatico profondo espirando lentamente a labbra socchiuse.",
            "Porta tutta la tua attenzione sensoriale sul contatto del tuo corpo e sul calore delle mani.",
            "Chiudi gli occhi e visualizza un'onda calda di sicurezza che rilassa il bacino e il plesso solare.",
            "Ripeti dentro di te: 'Il mio corpo sa come rilassarsi. Io sono al sicuro nel piacere'."
        ]
    },
    {
        "domain": "guida_rabbia_traffico",
        "keywords": [
            "volante", "guidare", "guida", "traffico", "macchina", "auto", "strada", "furbo", "furbi",
            "sorpasso", "precedenza", "rabbia", "furie", "monto su tutte le furie", "clacson", "litigare",
            "ingiustizia", "stradale", "furia", "arrabbio", "arrabbiare", "incazzo", "incazzare", "corsia"
        ],
        "context_reframe": "La tua reazione di rabbia al volante non è cattivo carattere, ma un riflesso protettivo di alto senso di giustizia e prontezza di riflessi che entra in allarme quando percepisci un pericolo o una scorrettezza. Incanalare questa energia ti dà il potere della totale padronanza e lucidità sulla strada.",
        "meaning_reframe": "Il comportamento scorretto o aggressivo degli altri guidatori è solo la proiezione della loro fretta, distrazione o stress personale: non ha nulla a che fare con te. Non concedere a uno sconosciuto il potere di determinare il tuo battito cardiaco o il tuo stato d'animo.",
        "identity_reframe": "Non sei un guidatore reattivo che si fa trascinare nelle provocazioni: sei il Sovrano Lucido e Imperturbabile del tuo Spazio al volante, capace di viaggiare in una bolla di totale sicurezza e calma strategica.",
        "socratic_question": "Se considerassi ogni auto che fa il furbo semplicemente come un ostacolo naturale mobile (come una pozzanghera o una foglia al vento), quale profonda calma proveresti nel lasciarla sfilare via senza alterare la tua serenità?",
        "action_2min": "Mentre sei seduto o al volante, posiziona le mani rilassate a ore 9:15, rilascia completamente la mandibola e le spalle, e fai 3 respiri profondi prolungando l'espirazione per 8 secondi.",
        "action_24h": "Durante il prossimo tragitto in auto, adotta la 'Regola del Distacco Regale': se qualcuno commette un'infrazione o cerca di fare il furbo, fai un sorriso interiore, pronuncia a mente 'Ti lascio andare alla tua fretta' e mantieni la tua traiettoria in totale calma.",
        "action_7days": "Installa il rituale di bordo: appena entri in auto e chiudi la portiera, tocca il volante con consapevolezza, fai un respiro profondo e ripeti il mantra prima di avviare il motore.",
        "mantra": "Al volante domino il mio spazio interiore: lascio scorrere la fretta altrui e mantengo la mia calma regale.",
        "anchor_title": "Ancoraggio del Volante e della Calma Regale",
        "anchor_technique": "Ancoraggio Tattile alle Mani & Dissociazione Strategica",
        "anchor_steps": [
            "Afferra il volante con una presa morbida ma presente a ore 9:15.",
            "Espira lentamente rilasciando ogni tensione dal collo, dalla fronte e dalle spalle.",
            "Visualizza l'abitacolo della tua auto come una fortezza di serenità e lucidità inviolabile.",
            "Ripeti mentalmente: 'Io sono il padrone della mia calma: nulla dall'esterno può turbare il mio viaggio'."
        ]
    },
    {
        "domain": "bridge_giochi_strategici",
        "keywords": ["bridge", "licita", "licite", "atout", "smazzata", "prese", "carta", "carte", "morto", "dichiarazione", "torneo", "compagno", "tavolo", "avversari", "contratto", "fiori", "quadri", "cuori", "picche"],
        "context_reframe": "La tua precisione e l'esigenza di calcolo nel Bridge dimostrano profonda intelligenza strategica e rispetto per il gioco della carta. L'imprevisto al tavolo non è un errore, ma il momento esatto in cui inizia la vera partita di deduzione probabilistica.",
        "meaning_reframe": "Una carta inaspettata o una licita complessa non distruggono il tuo piano di gioco: ti forniscono nuove informazioni preziose sulla distribuzione delle mani avversarie. Adattare la linea di gioco alla realtà del tavolo è il massimo livello di maestria del bridgista.",
        "identity_reframe": "Non sei un calcolatore rigido legato a uno schema fisso: sei un Navigatore Strategico delle Probabilità, capace di leggere la smazzata, valorizzare le atout e mantenere la lucidità tattica presa dopo presa.",
        "socratic_question": "Cosa accadrebbe se accogliessi ogni carta imprevista come un indizio prezioso sulla distribuzione avversaria, trasformando l'adattamento nel tuo vantaggio competitivo?",
        "action_2min": "Chiudi gli occhi per 60 secondi: visualizza il tavolo verde, fai un respiro profondo e immagina il tuo piano di gioco che diventa fluido come l'acqua, pronto ad aggirare qualsiasi mossa avversaria.",
        "action_24h": "Gioca o analizza 3 mani di Bridge applicando la regola del 'Piano Liquido': al terzo giro di atout, fai un check-point consapevole e aggiorna la stima della distribuzione senza alcun giudizio.",
        "action_7days": "Adotta il rituale di centratura al tavolo: prima di ogni attacco o licita cruciale, tocca il dorso delle carte con calma ed espira per mantenere il focus sulla singola presa presente.",
        "mantra": "Ogni carta rivelata è la mappa che si compone: io domino il tavolo con lucidità, calma e strategia fluida.",
        "anchor_title": "Ancoraggio del Tavolo Verde e della Mente Fluida",
        "anchor_technique": "Ri-centratura Visivo-Spaziale e Respirazione Tattica",
        "anchor_steps": [
            "Poggia le mani piatte sul tavolo sentendo il contatto solido.",
            "Fai un respiro lento rilasciando le tensioni delle spalle e della mandibola.",
            "Visualizza il tuo compagno e il morto con occhi di fiducia e cooperazione.",
            "Pronuncia dentro di te: 'Una carta alla volta, con totale presenza strategica'."
        ]
    },
    {
        "domain": "attivita_fisica_salute",
        "keywords": ["sarcopenia", "fisica", "fisico", "esercizi", "allenamento", "palestra", "muscoli", "sport", "movimento", "pigrizia", "pesi", "camminata", "corsa", "salute", "invecchiare", "età", "pensione", "corpo"],
        "context_reframe": "La resistenza iniziale ad allenarti non è pigrizia: è il naturale meccanismo di risparmio energetico del cervello. Riconoscerlo ti permette di aggirare l'attrito con micro-abitudini senza dover fare affidamento sulla sola forza di volontà.",
        "meaning_reframe": "Il movimento fisico e il mantenimento muscolare non sono un dovere punitivo, ma il carburante che preserva la tua autonomia, la tua forza e la tua lucidità mentale. Ogni singola serie di esercizi è un deposito diretto nel tuo conto della longevità.",
        "identity_reframe": "Non sei una persona che combatte contro il proprio corpo: sei il Custode Consapevole della tua Vitalità, capace di onorare la tua salute attraverso scelte quotidiane di eccellenza e rispetto per te stesso.",
        "socratic_question": "Qual è il più piccolo movimento o esercizio di 2 minuti che puoi compiere adesso, sapendo che una volta iniziato il corpo troverà il piacere naturale dell'energia in movimento?",
        "action_2min": "Alzati subito in piedi, fai 5 circonduzioni delle spalle, distendi le braccia verso l'alto e fai 3 respiri profondi sentendo il sangue che riprende a circolare nei muscoli.",
        "action_24h": "Applica la 'Regola dei 5 Minuti': prima di iniziare qualsiasi commissione della giornata, completa esattamente 5 minuti di riscaldamento o esercizi a corpo libero.",
        "action_7days": "Installa il trigger 'Prima la Salute': associa l'attività fisica al caffè del mattino, completando 15 minuti di routine di mobilità e forza prima di uscire di casa.",
        "mantra": "Mentre il mio corpo si muove, la mia energia si moltiplica: la mia forza è la mia libertà quotidiana.",
        "anchor_title": "Ancoraggio di Vitalità Corporea e Potenza Muscolare",
        "anchor_technique": "Attivazione Posturale e Fisiologia Dinamica",
        "anchor_steps": [
            "Mettiti in piedi a schiena dritta con i piedi ben saldi a terra.",
            "Contrai i muscoli delle gambe e dell'addome per 3 secondi e poi rilascia con un'espirazione potente.",
            "Senti il calore e la vitalità che si diffondono in tutto il corpo.",
            "Ripeti dentro di te: 'Il mio corpo è forte, vitale e pronto ad agire'."
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
        best_domain = None
        max_matches = 0
        for domain_data in THEMATIC_DOMAINS:
            count = sum(1 for kw in domain_data["keywords"] if re.search(rf"\b{re.escape(kw)}\b", t_low))
            if count > max_matches:
                max_matches = count
                best_domain = domain_data
        return best_domain if max_matches > 0 else None

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

    @classmethod
    def generate_heuristic_session_step(cls, req: SessionStepRequest) -> SessionStepResponse:
        """Eroga lo step maieutico euristico corrispondente alla fase della seduta."""
        step = req.current_step
        session_id = req.session_id or "SESSION-HEURISTIC"
        text = req.initial_thought
        matched = cls.match_thematic_domain(text)

        if step == 1:
            # Fase 1: Chiarimento del Contesto & Calibrazione
            if matched and matched["domain"] == "intimita_sessualita":
                q1 = "Nel momento in cui ti avvicini all'intimità, in che modo la tua attenzione si sposta dal piacere dei sensi e dalla complicità alla paura del giudizio o del monitoraggio della risposta fisica (Mente Spettatore)?"
                q2 = "Cosa noti a livello corporeo (respiro, tensione pelvica, battito cardiaco) nei minuti precedenti all'incontro intimo?"
                insight = "Identificazione dell'iperattivazione simpatica e dello Spectatoring che blocca la naturale risposta erettile."
            elif matched and matched["domain"] == "bridge_giochi_strategici":
                q1 = "In quale momento esatto della partita o del torneo si manifesta questo blocco (es. durante la licita o al gioco della carta)?"
                q2 = "Cosa noti nel tuo stato d'animo al tavolo non appena si verifica un imprevisto o un errore del compagno?"
                insight = "Stiamo focalizzando la dinamica percettiva al tavolo da Bridge."
            elif matched and matched["domain"] == "guida_rabbia_traffico":
                q1 = "Cosa provi fisicamente al volante (tensione alle braccia, battito accelerato, calore) subito prima che la rabbia prenda il sopravvento?"
                q2 = "Qual è la specifica mossa dell'altro guidatore che scatena in te la reazione più incontrollabile?"
                insight = "Indagine sull'iperattivazione adrenergica e sul riflesso di reattività automatica al volante."
            elif matched and matched["domain"] == "attivita_fisica_salute":
                q1 = "Cosa fai concretamente nei minuti precedenti al momento in cui dovresti iniziare gli esercizi fisici?"
                q2 = "Qual è la conversazione interna che fai con te stesso quando scegli di dare priorità ad altre commissioni?"
                insight = "Stiamo mappando i rituali di innesco e l'attrito iniziale del corpo."
            else:
                q1 = "In quali situazioni o momenti specifici della giornata si presenta con maggiore intensità questa sensazione?"
                q2 = "Cosa noti nel tuo corpo o nel tuo dialogo interno subito prima che questo blocco si attivi?"
                insight = "Calibrazione del contesto operativo e dei trigger primari."

            return SessionStepResponse(
                session_id=session_id,
                current_step=1,
                next_step=2,
                is_final_step=False,
                step_title="Fase 1: Accoglienza Empatica & Chiarimento del Contesto",
                coach_message="Ti ringrazio per la fiducia e sincerità nel condividere questa situazione. Nella nostra seduta esploreremo insieme come la tua mente e le tue reazioni interagiscono in questo momento, senza alcun giudizio.",
                investigation_questions=[q1, q2],
                clinical_insight=insight
            )

        elif step == 2:
            # Fase 2: Esplorazione Storica & Radici Pregresse (Time-Line & Imprinting)
            if matched and matched["domain"] == "intimita_sessualita":
                q1 = "In che modo lo shock emotivo vissuto a 23 anni ha installato nell'inconscio la convinzione che lasciarsi andare all'intimità comporti una perdita di controllo o conseguenze gravose?"
                q2 = "Come si è strutturata nel tempo la ricerca di forti emozioni o di situazioni esterne come tentativo di aggirare questa paura profonda e forzare l'eccitazione?"
                insight = "Indagine della Time-Line sull'evento di primo imprinting e sull'ancoraggio negativo tra sesso e perdita di controllo."
            elif matched and matched["domain"] == "guida_rabbia_traffico":
                q1 = "Ricordi qual è stato il primo episodio al volante o nella tua storia in cui hai provato questo forte senso di ingiustizia verso chi si comporta in modo scorretto?"
                q2 = "Da quanto tempo noti che l'auto è diventata un catalizzatore di tensione emotiva o di sfida con gli altri?"
                insight = "Esplorazione della Time-Line sui primi episodi di rabbia reattiva al volante."
            else:
                q1 = "Da quanto tempo porti con te questo schema o questa specifica preoccupazione?"
                q2 = "Se guardi indietro lungo la tua storia personale, qual è il primo episodio (anche anni fa o in gioventù) in cui ricordi di aver provato esattamente la stessa sensazione?"
                insight = "Tracciamento della Time-Line per individuare l'evento di primo imprinting emotivo e la convinzione radice."

            return SessionStepResponse(
                session_id=session_id,
                current_step=2,
                next_step=3,
                is_final_step=False,
                step_title="Fase 2: Esplorazione Storica & Radici Pregresse (Time-Line)",
                coach_message="Questo chiarimento è cruciale. I nostri schemi emotivi e fisici raramente nascono per caso: spesso sono risposte biologiche di allarme apprese in un momento di forte impatto emotivo del passato.",
                investigation_questions=[q1, q2],
                clinical_insight=insight
            )

        elif step == 3:
            # Fase 3: Influenze Esterne, Relazioni & Vantaggi Secondari
            if matched and matched["domain"] == "intimita_sessualita":
                q1 = "Quali aspettative (reali o immaginate) senti gravare su di te durante un incontro intimo, e cosa temi accada se ti mostri vulnerabile senza dover per forza 'performare'?"
                q2 = "A livello inconscio, in che modo la defaillance o l'ansia sta cercando di 'proteggerti' dal rischio di un coinvolgimento emotivo profondo o dal timore di un nuovo fallimento?"
                insight = "Mappatura dei vantaggi secondari inconsci e delle dinamiche relazionali sistemiche."
            elif matched and matched["domain"] == "guida_rabbia_traffico":
                q1 = "Quando guidi da solo rispetto a quando hai passeggeri a bordo con te, noti se il bisogno di farti rispettare o la rabbia cambiano di intensità?"
                q2 = "A livello profondo e inconscio, quale sensazione di potere o di protezione ti dà il rifiutarti di lasciar passare chi fa il furbo?"
                insight = "Analisi del bisogno di controllo del territorio e dell'intenzione positiva di protezione."
            else:
                q1 = "Ci sono persone, aspettative esterne o dinamiche relazionali attorno a te che alimentano o mantengono viva questa tensione?"
                q2 = "A livello profondo e inconscio, da quale rischio, fallimento o sofferenza questa parte di te sta cercando di proteggerti?"
                insight = "Mappatura dei fattori sistemici ambientali e dell'intenzione positiva inconscia di protezione."

            return SessionStepResponse(
                session_id=session_id,
                current_step=3,
                next_step=4,
                is_final_step=False,
                step_title="Fase 3: Influenze Esterne, Relazioni & Vantaggi Secondari",
                coach_message="Riconoscere l'origine storica di questo vissuto permette di iniziare a separare chi eri allora da chi sei oggi. Ora allarghiamo lo sguardo al tuo ambiente, alle aspettative e alle tue relazioni.",
                investigation_questions=[q1, q2],
                clinical_insight=insight
            )

        else:
            # Fase 4: Sintesi Clinica & Master PNL Protocol Finale
            channel, vak_kw = cls.detect_vak_channel(text)
            meta = cls.analyze_meta_model(text)
            shift = cls.generate_heuristic_reframes(text, channel, meta)
            shift.vak_keywords = vak_kw

            return SessionStepResponse(
                session_id=session_id,
                current_step=4,
                next_step=4,
                is_final_step=True,
                step_title="Fase 4: Sintesi Clinica & Ristrutturazione Profonda",
                coach_message="Abbiamo completato l'anamnesi approfondita. Avendo ora chiaro il contesto attuale, le radici storiche e le dinamiche relazionali, ecco la tua Scheda Clinica di Trasformazione personalizzata.",
                clinical_insight="Sintesi maieutica completata con successo: transizione verso l'ancoraggio e il piano operativo in 3 fasi.",
                final_shift=shift
            )
