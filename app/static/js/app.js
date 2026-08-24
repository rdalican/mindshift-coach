// MindShift Coach - Master Protocol Frontend Logic (v4.2)

let deferredPrompt = null;
let currentShiftData = null;
let currentSyncKey = localStorage.getItem('mindshift_sync_key') || null;
let cachedShifts = [];
let wizardState = { vak: null, thought: null };
let anchorTimerInterval = null;
let isAudioPlaying = false;

document.addEventListener('DOMContentLoaded', async () => {
  initPWA();
  initTabs();
  initForm();
  await initSyncKey();
  loadSavedShifts();
  loadAnalytics();
  loadRoadmap();
  checkPaymentStatus();
});

// --- PWA INSTALLATION LOGIC ---
function initPWA() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
      .then(() => console.log('Service Worker registrato.'))
      .catch((err) => console.log('Errore Service Worker:', err));
  }

  const installBtn = document.getElementById('pwa-install-btn');
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn) installBtn.classList.remove('hidden');
  });

  if (installBtn) {
    installBtn.addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`Install prompt: ${outcome}`);
        deferredPrompt = null;
        installBtn.classList.add('hidden');
      }
    });
  }
}

// --- SYNC KEY & DEVICE PAIRING (WINDOWS ↔ ANDROID) ---
async function initSyncKey() {
  const display = document.getElementById('sync-key-display');
  const statusText = document.getElementById('sync-status-text');

  if (!currentSyncKey) {
    try {
      const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
      const devName = isMobile ? "Android Device" : "Windows Desktop";

      const res = await fetch('/api/sync/pair', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_name: devName })
      });
      const data = await res.json();
      currentSyncKey = data.sync_key;
      localStorage.setItem('mindshift_sync_key', currentSyncKey);
    } catch (err) {
      currentSyncKey = 'MIND-LOCAL-' + Math.random().toString(36).substring(2, 6).toUpperCase();
      localStorage.setItem('mindshift_sync_key', currentSyncKey);
    }
  }

  if (display) display.value = currentSyncKey;
  if (statusText) statusText.textContent = `☁️ ${currentSyncKey}`;
}

async function pairDeviceWithInputKey() {
  const input = document.getElementById('sync-key-input');
  const key = input.value.trim().toUpperCase();
  if (!key) {
    alert('Inserisci una Sync Key valida.');
    return;
  }

  try {
    const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    const devName = isMobile ? "Android Device" : "Windows Desktop";

    const res = await fetch('/api/sync/pair', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sync_key: key, device_name: devName })
    });
    
    if (!res.ok) throw new Error('Chiave non valida');
    const data = await res.json();
    
    currentSyncKey = data.sync_key;
    localStorage.setItem('mindshift_sync_key', currentSyncKey);
    
    const display = document.getElementById('sync-key-display');
    const statusText = document.getElementById('sync-status-text');
    if (display) display.value = currentSyncKey;
    if (statusText) statusText.textContent = `☁️ ${currentSyncKey}`;
    
    alert(`Dispositivo collegato con successo! ${data.total_synced_shifts} Sessioni sincronizzate.`);
    loadSavedShifts();
    loadAnalytics();
  } catch (err) {
    alert(`Errore di collegamento: ${err.message}`);
  }
}

function copySyncKey() {
  if (!currentSyncKey) return;
  navigator.clipboard.writeText(currentSyncKey).then(() => {
    alert('Sync Key copiata! Incollala sul tuo smartphone Android o sul PC per condividere i dati.');
  });
}

function openSyncModal() {
  const targetBtn = document.querySelector('[data-target="cloud-sync-section"]');
  if (targetBtn) targetBtn.click();
}

// --- TAB SWITCHING ---
function initTabs() {
  const navBtns = document.querySelectorAll('.nav-tab-btn');
  const sections = document.querySelectorAll('.app-section');

  navBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-target');
      
      navBtns.forEach(b => {
        b.classList.remove('bg-teal-700', 'text-white');
        b.classList.add('text-slate-300', 'hover:bg-slate-800');
      });
      btn.classList.add('bg-teal-700', 'text-white');
      btn.classList.remove('text-slate-300', 'hover:bg-slate-800');

      sections.forEach(sec => {
        if (sec.id === target) {
          sec.classList.remove('hidden');
        } else {
          sec.classList.add('hidden');
        }
      });

      if (target === 'saved-shifts-section') {
        loadSavedShifts();
      } else if (target === 'analytics-section') {
        loadAnalytics();
      } else if (target === 'roadmap-section') {
        loadRoadmap();
      }
    });
  });
}

// --- FORM SUBMISSION & MASTER SESSION GENERATION ---
function initForm() {
  const form = document.getElementById('mindshift-form');
  const thoughtInput = document.getElementById('thought-input');
  const quickPills = document.querySelectorAll('.quick-thought-pill');
  const resultsContainer = document.getElementById('results-container');
  const loadingState = document.getElementById('loading-state');

  quickPills.forEach(pill => {
    pill.addEventListener('click', () => {
      thoughtInput.value = pill.getAttribute('data-text');
      thoughtInput.focus();
    });
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const thought = thoughtInput.value.trim();
    if (!thought) return;

    const context = document.getElementById('context-select').value;
    const preferredChannel = document.getElementById('channel-select').value;

    resultsContainer.classList.add('hidden');
    loadingState.classList.remove('hidden');
    loadingState.scrollIntoView({ behavior: 'smooth' });

    try {
      const response = await fetch('/api/reframe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thought: thought,
          context: context || null,
          preferred_channel: preferredChannel || null,
          sync_key: currentSyncKey
        })
      });

      if (!response.ok) throw new Error(`Errore HTTP: ${response.status}`);

      const data = await response.json();
      currentShiftData = data;
      renderMasterProtocol(data);

      resultsContainer.classList.remove('hidden');
      resultsContainer.scrollIntoView({ behavior: 'smooth' });
      
      loadSavedShifts();
      loadAnalytics();
    } catch (err) {
      alert(`Si è verificato un errore: ${err.message}`);
    } finally {
      loadingState.classList.add('hidden');
    }
  });
}

// --- RENDER COMPLETO DEL PROTOCOLLO MASTER PNL A 5 MODULI ---
function renderMasterProtocol(data) {
  // Engine Badge
  document.getElementById('res-engine-badge').textContent = data.engine_used;

  // QUADRO PRIMA VS DOPO
  if (data.before_state && data.before_state.stato) {
    document.getElementById('res-before-state').textContent = `${data.before_state.stato} (Fisiologia: ${data.before_state.fisiologia || 'Contratta'})`;
  }
  if (data.after_state && data.after_state.stato) {
    document.getElementById('res-after-state').textContent = `${data.after_state.stato} (Fisiologia: ${data.after_state.fisiologia || 'Aperta e Stabile'})`;
  }

  // MODULO 1: DIAGNOSI VAK & SUBMODALITÀ
  const vakBadge = document.getElementById('res-vak-badge');
  const vakKeywords = document.getElementById('res-vak-keywords');
  const ch = data.detected_channel;

  vakBadge.className = 'px-3 py-1 rounded-full text-xs font-bold';
  if (ch.includes('Visivo')) {
    vakBadge.classList.add('badge-visual');
    vakBadge.innerHTML = '👁️ ' + ch;
  } else if (ch.includes('Uditivo')) {
    vakBadge.classList.add('badge-auditory');
    vakBadge.innerHTML = '👂 ' + ch;
  } else if (ch.includes('Cinestesico')) {
    vakBadge.classList.add('badge-kinesthetic');
    vakBadge.innerHTML = '🖐️ ' + ch;
  } else {
    vakBadge.classList.add('badge-mixed');
    vakBadge.innerHTML = '⚖️ ' + ch;
  }

  if (data.vak_keywords && data.vak_keywords.length > 0) {
    vakKeywords.innerHTML = data.vak_keywords.map(kw => 
      `<span class="bg-slate-800 text-slate-200 text-xs px-2 py-0.5 rounded border border-slate-700 font-mono">${kw}</span>`
    ).join(' ');
  } else {
    vakKeywords.innerHTML = '<span class="text-slate-400 text-xs italic">Predicati integrati</span>';
  }

  document.getElementById('res-submodalities-insight').textContent = 
    data.meta_model.submodalities_insight || "Riorganizzazione delle submodalità sensoriali e spostamento del punto focale percettivo.";

  document.getElementById('res-meta-category').textContent = data.meta_model.category;
  document.getElementById('res-meta-subtype').textContent = data.meta_model.subtype;
  document.getElementById('res-meta-explanation').textContent = data.meta_model.explanation;
  
  const triggerContainer = document.getElementById('res-meta-triggers');
  if (data.meta_model.detected_trigger_words && data.meta_model.detected_trigger_words.length > 0) {
    triggerContainer.innerHTML = data.meta_model.detected_trigger_words.map(tw => 
      `<span class="bg-red-950/60 text-red-300 text-xs px-2 py-0.5 rounded border border-red-800/50">"${tw}"</span>`
    ).join(' ');
  } else {
    triggerContainer.innerHTML = '';
  }

  // MODULO 2: LE 4 RISTRUTTURAZIONI COGNITIVE PROFONDE
  const cardsContainer = document.getElementById('reframes-cards-container');
  cardsContainer.innerHTML = '';

  const reframesToRender = data.reframes && data.reframes.length > 0 ? data.reframes : [
    { type: "Ristrutturazione di Contesto", title: "Risorsa Strategica", content: data.context_reframe, pnl_explanation: "Sposta il comportamento in un contesto ad alto valore.", icon: "🔄" },
    { type: "Ristrutturazione di Significato", title: "Significato Milton Model", content: data.meaning_reframe, pnl_explanation: "Presupposizione di competenza e crescita.", icon: "💡" },
    { type: "Ristrutturazione di Identità (Robert Dilts)", title: "Livello Logico Identitario", content: data.identity_reframe || "Disidentificazione dal limite.", pnl_explanation: "Salto al livello di valori e identità autentica.", icon: "👑" },
    { type: "Domanda Socratica & Doppio Legame", title: "Domanda di Sblocco", content: data.socratic_question, pnl_explanation: "Decostruzione della trappola logica.", icon: "🎯" }
  ];

  reframesToRender.forEach((r, idx) => {
    const card = document.createElement('div');
    card.className = 'reframe-card bg-slate-800/90 rounded-2xl p-5 md:p-6 flex flex-col justify-between border border-slate-700 shadow-lg';
    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-3">
          <span class="text-2xl">${r.icon || '💡'}</span>
          <span class="text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded bg-teal-950 text-teal-300 border border-teal-800/60">
            ${r.type}
          </span>
        </div>
        <h4 class="text-base font-extrabold text-white mb-2">${r.title}</h4>
        <p class="text-slate-200 text-sm leading-relaxed mb-4">${r.content}</p>
        <p class="text-xs text-teal-400/90 italic mb-4 border-l-2 border-teal-500/60 pl-2.5">${r.pnl_explanation}</p>
      </div>
      <div>
        <div class="flex items-center justify-between py-2 border-t border-slate-700/60 text-xs text-slate-400">
          <span>Risonanza PNL:</span>
          <div class="flex gap-1 text-amber-400 cursor-pointer text-sm">
            <span onclick="submitRating('${escapeJs(r.type)}', 1)">★</span>
            <span onclick="submitRating('${escapeJs(r.type)}', 2)">★</span>
            <span onclick="submitRating('${escapeJs(r.type)}', 3)">★</span>
            <span onclick="submitRating('${escapeJs(r.type)}', 4)">★</span>
            <span onclick="submitRating('${escapeJs(r.type)}', 5)">★</span>
          </div>
        </div>
        <div class="flex items-center justify-between pt-2 border-t border-slate-700/60">
          <button onclick="copyToClipboard('${escapeJs(r.content)}')" class="text-xs text-slate-300 hover:text-white flex items-center gap-1 transition">
            📋 Copia
          </button>
          <span class="text-[10px] text-teal-400 font-mono">Master PNL v4</span>
        </div>
      </div>
    `;
    cardsContainer.appendChild(card);
  });

  // MODULO 3: PROTOCOLLO DI ANCORAGGIO GUIDATO (90s)
  const proto = data.anchoring_protocol || {
    title: "Ancoraggio di Risorsa e Sicurezza",
    technique_name: "Ancoraggio Cinestesico",
    steps: ["Fai 3 respiri profondi.", "Visualizza la riuscita.", "Ancora lo stato premendo il pollice."],
    target_state: "Padronanza Assoluta"
  };

  document.getElementById('res-anchor-title').textContent = proto.title;
  document.getElementById('res-anchor-tech').textContent = proto.technique_name;
  document.getElementById('res-anchor-target').textContent = proto.target_state;

  const stepsContainer = document.getElementById('res-anchor-steps');
  stepsContainer.innerHTML = (proto.steps || []).map((step, idx) => `
    <div class="flex items-start gap-3 p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
      <span class="w-6 h-6 rounded-full bg-teal-600 text-white font-black text-xs flex items-center justify-center shrink-0 mt-0.5 shadow">
        ${idx + 1}
      </span>
      <p class="text-xs md:text-sm text-slate-200 leading-relaxed font-medium">${step}</p>
    </div>
  `).join('');

  // MODULO 4: PIANO OPERATIVO IN 3 FASI
  const plan = data.action_plan || {
    phase_immediate_2min: data.empowering_micro_action,
    phase_24h_task: "Completa la prima azione concreta entro 24 ore.",
    phase_7days_habit: "Mantieni l'abitudine per 7 giorni consecutivi."
  };

  document.getElementById('res-action-2min').textContent = plan.phase_immediate_2min;
  document.getElementById('res-action-24h').textContent = plan.phase_24h_task;
  document.getElementById('res-action-7days').textContent = plan.phase_7days_habit;

  // MODULO 5: MANTRA IPNOTICO DI POTERE
  const mantra = data.anchoring_mantra || "Io genero lo spazio per ciò che è sacro per la mia crescita.";
  document.getElementById('res-mantra-text').textContent = `"${mantra}"`;
}

// --- GESTIONE VOCI NATURALI & NEURALI (AUDIO COACH GREVE, PROFONDO E FLUIDO) ---
let availableVoices = [];
window._activeSpeechUtterance = null; // Previene il Garbage Collector di Chrome/Windows (Causa dei glitch audio)

function loadVoices() {
  if ('speechSynthesis' in window) {
    availableVoices = window.speechSynthesis.getVoices();
  }
}

if ('speechSynthesis' in window) {
  loadVoices();
  window.speechSynthesis.onvoiceschanged = loadVoices;
}

function getBestGraveItalianVoice() {
  if (!availableVoices || availableVoices.length === 0) {
    loadVoices();
  }
  
  const italianVoices = availableVoices.filter(v => v.lang && v.lang.startsWith('it'));
  if (italianVoices.length === 0) return null;

  // 1. Cerca prioritariamente voci maschili / profonde (Diego, Cosimo, Luca)
  const maleVoice = italianVoices.find(v => {
    const n = (v.name || '').toLowerCase();
    return n.includes('diego') || n.includes('cosimo') || n.includes('luca') || n.includes('male') || n.includes('maschile');
  });
  if (maleVoice) return maleVoice;

  // 2. Cerca voci Neural / Natural / Premium (Elsa, Isabella, Google)
  const neuralVoice = italianVoices.find(v => {
    const n = (v.name || '').toLowerCase();
    return n.includes('natural') || n.includes('neural') || n.includes('online') || n.includes('google');
  });
  if (neuralVoice) return neuralVoice;

  return italianVoices[0];
}

let isSpeakingSequence = false;
let speechTimeoutId = null;

function stopAudioCoach() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  if (speechTimeoutId) {
    clearTimeout(speechTimeoutId);
    speechTimeoutId = null;
  }
  window._activeSpeechUtterance = null;
  isSpeakingSequence = false;
  isAudioPlaying = false;
  
  const btnText = document.getElementById('audio-btn-text');
  const icon = document.getElementById('audio-icon');
  if (btnText) btnText.textContent = "Ascolta Sessione Guidata";
  if (icon) icon.textContent = "🎧";
}

function playChunkedHypnoticSession(shiftData, onFinishCallback) {
  if (!('speechSynthesis' in window)) {
    alert('La sintesi vocale non è supportata dal tuo browser.');
    return;
  }

  stopAudioCoach();

  if (window.speechSynthesis.paused) {
    window.speechSynthesis.resume();
  }

  const voice = getBestGraveItalianVoice();
  const meaning = shiftData.meaning_reframe || shiftData.context_reframe || "";
  const identity = shiftData.identity_reframe || "";
  const mantra = shiftData.anchoring_mantra || "";
  const socratic = shiftData.socratic_question || "";

  // Frasi complete e naturali (senza spezzare le parole o la grammatica)
  const phrases = [
    { text: "Fai un respiro lento e profondo, e rilassa le spalle.", pauseAfter: 500 },
    { text: `Ascolta questa nuova prospettiva: ${meaning}`, pauseAfter: 600 },
    identity ? { text: `A livello della tua identità profonda, ricorda: ${identity}`, pauseAfter: 600 } : null,
    socratic ? { text: `Ora chiediti: ${socratic}`, pauseAfter: 500 } : null,
    { text: `Ripeti dentro di te la tua formula di potere: ${mantra}`, pauseAfter: 700 },
    { text: "Senti questa sicurezza e chiarezza stabilizzarsi in tutto il tuo corpo.", pauseAfter: 400 }
  ].filter(Boolean);

  isSpeakingSequence = true;
  isAudioPlaying = true;
  const btnText = document.getElementById('audio-btn-text');
  const icon = document.getElementById('audio-icon');
  if (btnText) btnText.textContent = "Pausa Audio Guida";
  if (icon) icon.textContent = "⏸️";

  function speakChunk(idx) {
    if (!isSpeakingSequence || idx >= phrases.length) {
      stopAudioCoach();
      if (onFinishCallback) onFinishCallback();
      return;
    }

    const chunk = phrases[idx];
    const utterance = new SpeechSynthesisUtterance(chunk.text);
    window._activeSpeechUtterance = utterance; // Mantiene attiva la referenza contro i bug di GC

    if (voice) utterance.voice = voice;
    utterance.lang = 'it-IT';
    utterance.rate = 0.84;  // Cadenza naturale, chiara e fluida (non trascinata)
    utterance.pitch = 0.80; // Tono basso/baritonale maschile profondo e naturale
    utterance.volume = 1.0;

    utterance.onend = () => {
      if (!isSpeakingSequence) return;
      speechTimeoutId = setTimeout(() => {
        speakChunk(idx + 1);
      }, chunk.pauseAfter || 500);
    };

    utterance.onerror = (err) => {
      console.warn("Audio error:", err);
      if (!isSpeakingSequence) return;
      speechTimeoutId = setTimeout(() => {
        speakChunk(idx + 1);
      }, 300);
    };

    window.speechSynthesis.speak(utterance);
  }

  speakChunk(0);
}

// --- AUDIO COACH VOCALE (SPEECH SYNTHESIS CALDO, MODULATO & FLUIDO) ---
function toggleAudioCoach() {
  if (isAudioPlaying) {
    stopAudioCoach();
    return;
  }

  if (!currentShiftData) return;

  playChunkedHypnoticSession(currentShiftData);
}

// --- TIMER ANCORAGGIO FISIOLOGICO 90 SECONDI ---
function startAnchorTimer() {
  const btn = document.getElementById('anchor-timer-btn');
  const timerText = document.getElementById('timer-btn-text');
  let timeLeft = 90;
  if (anchorTimerInterval) clearInterval(anchorTimerInterval);

  btn.classList.add('bg-amber-600');
  timerText.textContent = `⏱️ ${timeLeft}s (Inspira... Trattieni... Espira)`;

  anchorTimerInterval = setInterval(() => {
    timeLeft--;
    if (timeLeft <= 0) {
      clearInterval(anchorTimerInterval);
      btn.classList.remove('bg-amber-600');
      btn.classList.add('bg-emerald-600');
      timerText.textContent = `✅ Stato Ancorato nel Corpo!`;
    } else {
      const phase = (timeLeft % 8 >= 4) ? "Inspira profondamente..." : "Espira rilasciando...";
      timerText.textContent = `⏱️ ${timeLeft}s (${phase})`;
    }
  }, 1000);
}

// --- FEEDBACK RATING SUBMISSION ---
async function submitRating(reframeType, rating) {
  try {
    await fetch('/api/feedback/reframe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sync_key: currentSyncKey,
        shift_id: Date.now().toString(),
        reframe_type: reframeType,
        rating: rating
      })
    });
    alert(`Grazie per la valutazione (${rating}⭐)! Calibrazione PNL registrata.`);
    loadAnalytics();
  } catch (e) {
    alert('Voto registrato.');
  }
}

// --- COPIA MANTRA ---
function copyMantra() {
  const mantraText = document.getElementById('res-mantra-text').textContent;
  navigator.clipboard.writeText(mantraText).then(() => {
    alert('Mantra di ancoraggio copiato! Impostalo come promemoria o notifica.');
  });
}

// --- SALVATAGGIO & SINCRONIZZAZIONE CLOUD ---
async function saveCurrentFullShift() {
  if (!currentShiftData) return;
  const shiftId = (currentShiftData && currentShiftData.id) ? currentShiftData.id : Date.now().toString();
  const payload = {
    id: shiftId,
    sync_key: currentSyncKey,
    original_thought: currentShiftData.original_thought,
    detected_channel: currentShiftData.detected_channel,
    meta_category: currentShiftData.meta_model.category,
    meta_subtype: currentShiftData.meta_model.subtype,
    meta_explanation: currentShiftData.meta_model.explanation,
    context_reframe: currentShiftData.context_reframe,
    meaning_reframe: currentShiftData.meaning_reframe,
    identity_reframe: currentShiftData.identity_reframe,
    socratic_question: currentShiftData.socratic_question,
    empowering_micro_action: currentShiftData.empowering_micro_action,
    anchoring_mantra: currentShiftData.anchoring_mantra,
    reframes: currentShiftData.reframes,
    anchoring_protocol: currentShiftData.anchoring_protocol,
    action_plan: currentShiftData.action_plan
  };

  try {
    await fetch('/api/sync/shifts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    alert('Sessione Master PNL salvata e sincronizzata nel Cloud di Railway!');
    loadSavedShifts();
    loadAnalytics();
  } catch (err) {
    alert('Salvata localmente.');
  }
}

async function loadSavedShifts() {
  const container = document.getElementById('saved-shifts-list');
  const countBadge = document.getElementById('saved-shifts-count');
  if (!container) return;

  try {
    if (currentSyncKey) {
      const res = await fetch(`/api/sync/shifts?sync_key=${encodeURIComponent(currentSyncKey)}`);
      if (res.ok) {
        const data = await res.json();
        cachedShifts = data.shifts || [];
        if (countBadge) countBadge.textContent = data.count;
        renderFilteredShifts(cachedShifts);
      }
    }
  } catch (e) {
    console.warn('Errore fetch cloud shifts:', e);
  }
}

function renderFilteredShifts(shifts) {
  const container = document.getElementById('saved-shifts-list');
  if (!container) return;

  if (shifts.length === 0) {
    container.innerHTML = `
      <div class="text-center py-12 text-slate-400">
        <span class="text-4xl block mb-2">☁️</span>
        <p class="text-base font-medium">Nessuna Sessione Master salvata.</p>
        <p class="text-xs text-slate-500 mt-1">Esegui una sessione per vederla apparire qui.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = shifts.map((item, idx) => `
    <div class="glass-panel rounded-2xl p-6 mb-6 border border-slate-700/80 shadow-xl relative">
      <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
        <span class="text-xs text-teal-400 font-mono font-bold">☁️ Sessione Master #${idx + 1} (${item.created_at ? new Date(item.created_at).toLocaleDateString('it-IT') : 'Recente'})</span>
        <div class="flex items-center gap-2">
          <span class="text-xs px-2.5 py-0.5 rounded bg-slate-800 text-teal-300 border border-teal-800/40 font-bold">${item.detected_channel}</span>
          <span class="text-xs px-2.5 py-0.5 rounded bg-slate-800 text-amber-300 border border-amber-800/40 font-bold">${item.meta_subtype}</span>
          <button onclick="reloadSavedShiftIntoMainView('${item.id}')" title="Riapri nel Protocollo Interattivo" class="text-xs px-2.5 py-1 rounded bg-teal-900/60 hover:bg-teal-800 text-teal-300 border border-teal-700 font-bold ml-1 transition">🔍 Riapri</button>
          <button onclick="deleteShift('${item.id}')" title="Elimina" class="text-xs text-red-400 hover:text-red-300 ml-2">🗑️</button>
        </div>
      </div>
      
      <div class="mb-4 bg-slate-900/80 p-4 rounded-xl border-l-4 border-amber-500">
        <span class="text-xs text-slate-400 font-bold block mb-1">Pensiero di partenza:</span>
        <p class="text-base text-slate-100 font-medium italic">"${item.original_thought}"</p>
      </div>

      <!-- 4 RISTRUTTURAZIONI -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
        ${(item.reframes || []).map(r => `
          <div class="bg-slate-800/80 p-3.5 rounded-xl border border-slate-700/50">
            <span class="text-xs font-extrabold text-teal-300 block mb-1">${r.icon || '💡'} ${r.type}</span>
            <p class="text-xs text-slate-200 leading-relaxed">${r.content}</p>
          </div>
        `).join('')}
      </div>

      <!-- MANTRA DI ANCORAGGIO -->
      ${item.anchoring_mantra ? `
        <div class="p-3.5 rounded-xl bg-amber-950/30 border border-amber-800/40 text-center text-sm text-amber-300 font-bold mb-4 shadow-inner">
          💎 Mantra di Ancoraggio: "${item.anchoring_mantra}"
        </div>
      ` : ''}

      <!-- AUDIO COACH VOCALE PLAYER & ANCORAGGIO -->
      <div class="p-3.5 rounded-xl bg-slate-800/60 border border-teal-800/30 mb-4 flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <button onclick="playSavedAudioCoach('${item.id}')" class="px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs flex items-center gap-1.5 transition">
            <span>🎧</span> <span>Ascolta Audio Coach</span>
          </button>
          <span class="text-xs text-slate-400">Guida vocale e riprogrammazione ipnotica</span>
        </div>
        ${item.anchoring_protocol && item.anchoring_protocol.breath_pace ? `
          <div class="text-xs text-teal-300 font-mono bg-slate-900/80 px-2.5 py-1 rounded border border-teal-900">
            Respiro: ${item.anchoring_protocol.breath_pace}
          </div>
        ` : ''}
      </div>

      <!-- PIANO DI AZIONE 3 FASI -->
      ${item.action_plan ? `
        <div class="pt-3 border-t border-slate-700/60">
          <span class="text-xs font-bold text-slate-300 block mb-2">📋 Piano Operativo di Sblocco in 3 Fasi:</span>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div class="p-3 rounded-xl bg-slate-900/80 border border-emerald-900/50 flex flex-col justify-between">
              <div>
                <span class="text-emerald-400 text-xs font-black uppercase tracking-wider block mb-1">⚡ 1. Subito (2 Minuti):</span>
                <p class="text-xs text-slate-200 leading-relaxed">${item.action_plan.phase_immediate_2min || item.action_plan.micro_action_2min || item.empowering_micro_action || 'Micro-azione corporea immediata'}</p>
              </div>
            </div>
            <div class="p-3 rounded-xl bg-slate-900/80 border border-teal-900/50 flex flex-col justify-between">
              <div>
                <span class="text-teal-400 text-xs font-black uppercase tracking-wider block mb-1">📅 2. Entro 24 Ore:</span>
                <p class="text-xs text-slate-200 leading-relaxed">${item.action_plan.phase_24h_task || item.action_plan.task_24h || 'Compito operativo nel mondo reale'}</p>
              </div>
            </div>
            <div class="p-3 rounded-xl bg-slate-900/80 border border-indigo-900/50 flex flex-col justify-between">
              <div>
                <span class="text-indigo-400 text-xs font-black uppercase tracking-wider block mb-1">🔄 3. Strategia a 7 Giorni:</span>
                <p class="text-xs text-slate-200 leading-relaxed">${item.action_plan.phase_7days_habit || item.action_plan.habit_7days || 'Abitudine di consolidamento'}</p>
              </div>
            </div>
          </div>
        </div>
      ` : (item.empowering_micro_action ? `
        <div class="pt-2 border-t border-slate-700/50 flex items-center gap-2 text-xs text-emerald-300 font-medium">
          <span>⚡ Micro-Azione:</span>
          <span>${item.empowering_micro_action}</span>
        </div>
      ` : '')}
    </div>
  `).join('');
}

function reloadSavedShiftIntoMainView(shiftId) {
  const shift = cachedShifts.find(s => s.id === shiftId);
  if (!shift) return;

  currentShiftData = shift;
  renderMasterProtocol(shift);

  // Switch to Protocol Tab
  const mainTabBtn = document.querySelector('[data-tab="reframe"]');
  if (mainTabBtn) mainTabBtn.click();

  const resultsContainer = document.getElementById('results-container');
  if (resultsContainer) {
    resultsContainer.classList.remove('hidden');
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
  }
}

function playSavedAudioCoach(shiftId) {
  const shift = cachedShifts.find(s => s.id === shiftId);
  if (!shift) return;

  playChunkedHypnoticSession(shift);
}

function filterJournalEntries() {
  const query = (document.getElementById('journal-search-input')?.value || '').toLowerCase();
  const vakFilter = document.getElementById('journal-filter-vak')?.value || '';

  const filtered = cachedShifts.filter(s => {
    const matchQuery = !query || s.original_thought.toLowerCase().includes(query) || (s.context && s.context.toLowerCase().includes(query));
    const matchVak = !vakFilter || s.detected_channel.includes(vakFilter);
    return matchQuery && matchVak;
  });

  renderFilteredShifts(filtered);
}

function downloadJournalMarkdown() {
  if (!currentSyncKey) return;
  window.open(`/api/export/shifts?sync_key=${encodeURIComponent(currentSyncKey)}&format=markdown`, '_blank');
}

async function deleteShift(id) {
  if (!confirm('Vuoi eliminare questa sessione dal Cloud?')) return;
  try {
    await fetch(`/api/sync/shifts/${id}?sync_key=${encodeURIComponent(currentSyncKey)}`, {
      method: 'DELETE'
    });
    loadSavedShifts();
    loadAnalytics();
  } catch (err) {
    alert('Errore eliminazione.');
  }
}

function manualCloudSync() {
  loadSavedShifts();
  loadAnalytics();
  alert('Diario e statistiche aggiornate con Railway Cloud!');
}

// --- ANALYTICS DASHBOARD ---
async function loadAnalytics() {
  if (!currentSyncKey) return;
  try {
    const res = await fetch(`/api/analytics/vak?sync_key=${encodeURIComponent(currentSyncKey)}`);
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById('stat-total-shifts').textContent = data.total_shifts;
    document.getElementById('stat-dominant-channel').textContent = data.distribution.dominant_channel;
    document.getElementById('stat-avg-rating').textContent = `${data.average_resonance_score} / 5`;
    document.getElementById('stat-empowerment-score').textContent = `${data.empowerment_index}%`;

    document.getElementById('vak-visual-pct').textContent = `${data.distribution.visual_pct}%`;
    document.getElementById('vak-visual-bar').style.width = `${data.distribution.visual_pct}%`;

    document.getElementById('vak-auditory-pct').textContent = `${data.distribution.auditory_pct}%`;
    document.getElementById('vak-auditory-bar').style.width = `${data.distribution.auditory_pct}%`;

    document.getElementById('vak-kinesthetic-pct').textContent = `${data.distribution.kinesthetic_pct}%`;
    document.getElementById('vak-kinesthetic-bar').style.width = `${data.distribution.kinesthetic_pct}%`;
  } catch (e) {
    console.warn('Errore analytics:', e);
  }
}

// --- ONBOARDING WIZARD ---
function openOnboardingModal() {
  wizardState = { vak: null, thought: null };
  document.getElementById('wizard-step-1').classList.remove('hidden');
  document.getElementById('wizard-step-2').classList.add('hidden');
  document.getElementById('wizard-step-3').classList.add('hidden');
  document.getElementById('wizard-progress-bar').style.width = '33%';
  document.getElementById('wizard-step-num').textContent = '33%';
  document.getElementById('wizard-step-label').textContent = 'Passo 1 di 3: Scegli il tuo stile sensoriale';
  document.getElementById('onboarding-modal').classList.remove('hidden');
}

function closeOnboardingModal() {
  document.getElementById('onboarding-modal').classList.add('hidden');
}

function selectWizardVak(channel) {
  wizardState.vak = channel;
  document.getElementById('wizard-step-1').classList.add('hidden');
  document.getElementById('wizard-step-2').classList.remove('hidden');
  document.getElementById('wizard-progress-bar').style.width = '66%';
  document.getElementById('wizard-step-num').textContent = '66%';
  document.getElementById('wizard-step-label').textContent = 'Passo 2 di 3: Scegli o inserisci il pensiero';
}

function selectWizardThought(thought) {
  wizardState.thought = thought;
  document.getElementById('wizard-step-2').classList.add('hidden');
  document.getElementById('wizard-step-3').classList.remove('hidden');
  document.getElementById('wizard-progress-bar').style.width = '100%';
  document.getElementById('wizard-step-num').textContent = '100%';
  document.getElementById('wizard-step-label').textContent = 'Passo 3 di 3: Genera Sessione Master';
}

async function executeWizardShift() {
  closeOnboardingModal();
  const liveTab = document.querySelector('[data-target="live-shift-section"]');
  if (liveTab) liveTab.click();

  const thoughtInput = document.getElementById('thought-input');
  const channelSelect = document.getElementById('channel-select');

  if (thoughtInput) thoughtInput.value = wizardState.thought || "Non ho abbastanza tempo per lanciare questo progetto.";
  if (channelSelect && wizardState.vak) channelSelect.value = wizardState.vak;

  const form = document.getElementById('mindshift-form');
  if (form) form.dispatchEvent(new Event('submit'));
}

// --- ROADMAP TRACKER ---
async function loadRoadmap() {
  const container = document.getElementById('roadmap-weeks-container');
  const progressText = document.getElementById('roadmap-progress-text');
  const progressBar = document.getElementById('roadmap-progress-bar');
  if (!container) return;

  try {
    const res = await fetch('/api/roadmap');
    const data = await res.json();

    if (progressText) progressText.textContent = `${data.completion_percentage}%`;
    if (progressBar) progressBar.style.width = `${data.completion_percentage}%`;

    container.innerHTML = data.weeks.map(week => `
      <div class="glass-panel rounded-xl p-5 mb-6 border border-slate-700/80">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-700/60">
          <div>
            <h3 class="text-lg font-bold text-white flex items-center gap-2">
              <span>${week.week_number === 1 ? '🎯' : week.week_number === 2 ? '💳' : week.week_number === 3 ? '🧠' : '🚀'}</span>
              ${week.title}
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">${week.objective}</p>
          </div>
          <span class="text-xs font-semibold px-2.5 py-1 rounded ${
            week.status === 'Completata' ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' :
            week.status === 'In Corso' ? 'bg-teal-950 text-teal-300 border border-teal-800' :
            'bg-slate-800 text-slate-400 border border-slate-700'
          }">
            ${week.status}
          </span>
        </div>
        <div class="space-y-3">
          ${week.steps.map(step => `
            <div class="flex items-start justify-between gap-3 p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <div class="flex items-start gap-3">
                <input 
                  type="checkbox" 
                  id="chk-${step.id}" 
                  ${step.status === 'completed' ? 'checked' : ''} 
                  onchange="toggleStepStatus('${step.id}', this.checked)"
                  class="mt-1 w-4 h-4 rounded text-teal-600 bg-slate-800 border-slate-600 focus:ring-teal-500 cursor-pointer"
                />
                <div>
                  <label for="chk-${step.id}" class="text-sm font-semibold text-white cursor-pointer ${step.status === 'completed' ? 'line-through text-slate-400' : ''}">
                    ${step.title}
                  </label>
                  <p class="text-xs text-slate-400 mt-0.5">${step.description}</p>
                  <div class="mt-1.5 flex items-center gap-1.5 text-xs text-teal-400/90">
                    <span class="font-mono">📦 Deliverable:</span>
                    <span class="font-mono text-slate-300">${step.deliverable}</span>
                  </div>
                </div>
              </div>
              <span class="text-xs px-2 py-0.5 rounded font-mono ${
                step.status === 'completed' ? 'bg-emerald-900/40 text-emerald-300' :
                step.status === 'in_progress' ? 'bg-amber-900/40 text-amber-300' :
                'bg-slate-800 text-slate-400'
              }">
                ${step.status === 'completed' ? 'Fatto' : step.status === 'in_progress' ? 'In corso' : 'Pianificato'}
              </span>
            </div>
          `).join('')}
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Errore caricamento roadmap:', err);
  }
}

async function toggleStepStatus(stepId, isChecked) {
  const newStatus = isChecked ? 'completed' : 'pending';
  try {
    await fetch('/api/roadmap/step/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ step_id: stepId, status: newStatus })
    });
    loadRoadmap();
  } catch (err) {
    alert('Errore aggiornamento');
  }
}

// --- STRIPE PAYMENTS MODAL ---
function openPricingModal() {
  const modal = document.getElementById('pricing-modal');
  if (modal) modal.classList.remove('hidden');
}

function closePricingModal() {
  const modal = document.getElementById('pricing-modal');
  if (modal) modal.classList.add('hidden');
}

async function startStripeCheckout() {
  try {
    const res = await fetch('/api/payments/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sync_key: currentSyncKey })
    });
    const data = await res.json();
    if (data.checkout_url) window.location.href = data.checkout_url;
  } catch (err) {
    alert('Errore avvio checkout.');
  }
}

function checkPaymentStatus() {
  const params = new URLSearchParams(window.location.search);
  if (params.get('payment') === 'success' || params.get('payment') === 'mock_success') {
    alert('🎉 Congratulazioni! Il tuo abbonamento MindShift Coach Pro è attivo con 3 giorni di prova gratuita.');
  }
}

// --- UTILS ---
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    alert('Testo copiato negli appunti!');
  }).catch(() => {
    alert('Impossibile copiare.');
  });
}

function escapeJs(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, ' ');
}
