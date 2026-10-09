// Nombre del caché (cambiá el número para forzar actualización)
const CACHE_NAME = 'control-taller-cache-v3';

// Shell estable (no pongas archivos con hash)
const APP_SHELL = [
  '/',               // Nginx sirve index.html
  '/index.html',
  '/manifest.json',
  '/favicon.ico',
  '/icons/logo_192x192.png',
  '/icons/logo_512x512.png',
];

// Al instalar: cachear shell
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
});

// Al activar: limpiar cachés viejos
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.map((n) => (n !== CACHE_NAME ? caches.delete(n) : null)))
    ).then(() => self.clients.claim())
  );
});

// Helper: ¿es de nuestro mismo origen?
const isSameOrigin = (url) => url.origin === self.location.origin;

// Interceptar tráfico
self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Solo GET
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Estrategia para API => network-first con fallback a caché
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const resClone = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(req, resClone));
          return res;
        })
        .catch(async () => (await caches.match(req)) || new Response(JSON.stringify([]), {
          headers: { 'Content-Type': 'application/json' },
        }))
    );
    return;
  }

  // Estáticos del mismo origen => cache-first
  if (isSameOrigin(url)) {
    event.respondWith(
      caches.match(req).then((cached) => cached || fetch(req))
    );
  }
});
