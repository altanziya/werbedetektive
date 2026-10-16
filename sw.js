// Legt Seite, Schrift und verschlüsselte Spots beim ersten Öffnen ab, damit alles auch ohne WLAN läuft
const CACHE = 'wd-v1';
const FILES = [
  './', 'index.html', 'fonts/andika-400.woff2', 'fonts/andika-700.woff2', 'videos/meta.json',
  'videos/g1.bin', 'videos/g2.bin', 'videos/g3.bin', 'videos/g4.bin', 'videos/g5.bin', 'videos/g6.bin',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then((hit) => hit || fetch(e.request)));
});
