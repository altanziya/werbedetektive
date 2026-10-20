// Legt Seite, Schrift und verschlüsselte Spots beim ersten Öffnen ab, damit alles auch ohne WLAN läuft
const CACHE = 'wd-v10';
const FILES = [
  './', 'index.html', 'eddie.webp', 'fonts/andika-400.woff2', 'fonts/andika-700.woff2', 'fonts/fredoka-600.woff2', 'videos/meta.json',
  'audio/g1t1.mp3', 'audio/g1t2.mp3', 'audio/g1t3.mp3', 'audio/g1t4.mp3', 'audio/g2t1.mp3', 'audio/g2t2.mp3', 'audio/g2t3.mp3', 'audio/g2t4.mp3', 'audio/g3t1.mp3', 'audio/g3t2.mp3', 'audio/g3t3.mp3', 'audio/g3t4.mp3', 'audio/g4t1.mp3', 'audio/g4t2.mp3', 'audio/g4t3.mp3', 'audio/g4t4.mp3', 'audio/g5t1.mp3', 'audio/g5t2.mp3', 'audio/g5t3.mp3', 'audio/g5t4.mp3', 'audio/g6t1.mp3', 'audio/g6t2.mp3', 'audio/g6t3.mp3', 'audio/g6t4.mp3', 'audio/home.mp3', 'audio/intro.mp3', 'audio/w1.mp3', 'audio/w2.mp3', 'audio/w3.mp3', 'audio/w4.mp3', 'audio/w5.mp3',
  'videos/g1.bin', 'videos/g2.bin', 'videos/g3.bin', 'videos/g4.bin', 'videos/g5.bin', 'videos/g6.bin',
];

// Jede Version lädt ihre Dateien mit eigener Kennung (?v=) und am Browser-Zwischenspeicher vorbei.
// Sonst können alte Dateien aus dem Browser oder dem GitHub-CDN im neuen Cache landen.
const fresh = (f) => new Request(`${f}?v=${CACHE}`, { cache: 'reload' });

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES.map(fresh))).then(() => self.skipWaiting()));
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
