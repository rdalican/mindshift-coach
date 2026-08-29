const CACHE_NAME = 'mindshift-cache-v3.1';
const STATIC_ASSETS = [
  '/',
  '/manifest.json'
];

// Installazione immediata del nuovo Service Worker
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

// Attivazione e pulizia immediata di tutte le vecchie cache obsolete
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => {
          console.log('[SW] Eliminazione vecchia cache:', key);
          return caches.delete(key);
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Gestione messaggi per forzare aggiornamento
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// Strategia Network-First: carica sempre la versione più recente dalla rete e usa la cache solo offline
self.addEventListener('fetch', (event) => {
  // Pass-through diretto per tutte le API
  if (event.request.url.includes('/api/')) {
    return;
  }

  // Per navigazione (HTML) e file JS/CSS: prova sempre la rete prima della cache
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && event.request.method === 'GET') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // Fallback offline su cache se la rete non è disponibile
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }
        });
      })
  );
});
