// Verschlüsselt die Spots für die Seite: node tools/encrypt.mjs <spot-ordner> <passwort>
// Ausgabe: videos/g1.bin … g6.bin (12 Byte IV + AES-GCM) und videos/meta.json (Salt, Iterationen, Prüfwert)
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { webcrypto as crypto } from 'node:crypto';
import path from 'node:path';

const [src, password] = process.argv.slice(2);
if (!src || !password) {
  console.error('Aufruf: node tools/encrypt.mjs <spot-ordner> <passwort>');
  process.exit(1);
}

const FILES = [
  '1_McDonalds_HappyMeal.mp4',
  '2_Muellermilch.mp4',
  '3_hohesC.mp4',
  '4_nimm2soft.mp4',
  '5_Skechers_GoRun2.mp4',
  '6_Wrigleys_Extra.mp4',
];
const ITERATIONS = 150000;
const out = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'videos');
await mkdir(out, { recursive: true });

const salt = crypto.getRandomValues(new Uint8Array(16));
const base = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveKey']);
const key = await crypto.subtle.deriveKey(
  { name: 'PBKDF2', salt, iterations: ITERATIONS, hash: 'SHA-256' },
  base, { name: 'AES-GCM', length: 256 }, false, ['encrypt'],
);

async function seal(bytes) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, bytes));
  const res = new Uint8Array(12 + ct.length);
  res.set(iv);
  res.set(ct, 12);
  return res;
}

for (const [i, f] of FILES.entries()) {
  const sealed = await seal(await readFile(path.join(src, f)));
  await writeFile(path.join(out, `g${i + 1}.bin`), sealed);
  console.log(`g${i + 1}.bin  ${f}  ${(sealed.length / 1e6).toFixed(1)} MB`);
}

const check = await seal(new TextEncoder().encode('werbedetektive'));
await writeFile(path.join(out, 'meta.json'), JSON.stringify({
  salt: Buffer.from(salt).toString('base64'),
  iterations: ITERATIONS,
  check: Buffer.from(check).toString('base64'),
}));
console.log('meta.json geschrieben');
