const CACHE = 'getgrowline-v1';
const PRECACHE = [
  '/',
  '/offline',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/maskable-192.png',
  '/static/maskable-512.png',
  '/static/manifest.webmanifest'
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return; // never cache API POSTs
  const url = new URL(req.url);
  if (url.pathname.startsWith('/api/')) return; // always live data
  e.respondWith(
    fetch(req).catch(() =>
      caches.match(req).then((hit) => hit || caches.match('/offline'))
    )
  );
});
