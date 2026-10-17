// Legt Seite, Schrift und verschlüsselte Spots beim ersten Öffnen ab, damit alles auch ohne WLAN läuft
const CACHE = 'wd-v7';
const FILES = [
  './', 'index.html', 'eddie.webp', 'fonts/andika-400.woff2', 'fonts/andika-700.woff2', 'fonts/fredoka-600.woff2', 'videos/meta.json',
  'audio/g1t1.mp3', 'audio/g1t2.mp3', 'audio/g2t1.mp3', 'audio/g2t2.mp3', 'audio/g3t1.mp3', 'audio/g3t2.mp3', 'audio/g4t1.mp3', 'audio/g4t2.mp3', 'audio/g5t1.mp3', 'audio/g5t2.mp3', 'audio/g6t1.mp3', 'audio/g6t2.mp3', 'audio/home.mp3', 'audio/intro.mp3', 'audio/w1.mp3', 'audio/w2.mp3', 'audio/w3.mp3', 'audio/w4.mp3', 'audio/w5.mp3',
  'videos/g1.bin', 'videos/g2.bin', 'videos/g3.bin', 'videos/g4.bin', 'videos/g5.bin', 'videos/g6.bin',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES.map((f) => new Request(f, { cache: 'reload' })))  // am Browser-Zwischenspeicher vorbei, sonst landen alte Dateien im neuen Cache).then(() => self.skipWaiting()));
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
