# Werbedetektive

Lernumgebung für eine Sachunterrichtsstunde (Klasse 3): Jede Gruppe sieht genau einen Werbespot und daneben ihren Arbeitsauftrag.

- Keine Eingaben, keine Cookies, keine Drittanbieter, Schrift lokal.
- Spots liegen nur verschlüsselt (AES-GCM, Schlüssel aus Passwort per PBKDF2) im Repo und werden im Browser entschlüsselt.
- Nach dem ersten Öffnen offline nutzbar (Service Worker).

Spots neu verschlüsseln: `node tools/encrypt.mjs <ordner-mit-mp4s> <passwort>`, danach `CACHE` in `sw.js` hochzählen.
