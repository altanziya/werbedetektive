# Werbedetektive

Lernumgebung für eine Sachunterrichtsstunde (Klasse 3): Jede Gruppe sieht genau einen Werbespot und daneben ihren Arbeitsauftrag.

- Keine Eingaben, keine Cookies, keine Drittanbieter, Schrift lokal.
- Spots liegen nur verschlüsselt (AES-GCM, Schlüssel aus Passwort per PBKDF2) im Repo und werden im Browser entschlüsselt.
- Nach dem ersten Öffnen offline nutzbar (Service Worker).

Spots neu verschlüsseln: `node tools/encrypt.mjs <ordner-mit-mp4s> <passwort>`, danach `CACHE` in `sw.js` hochzählen.

Texte stehen im `TEXT`-Block in `index.html`. Nach jeder Textänderung die Stimme neu einsprechen mit `python3 tools/stimme_elevenlabs.py [w4,g1t1,…]` (ElevenLabs-Key in der Keychain unter `elevenlabs-api`, Ausweichlösung ohne Key ist `tools/stimme.py`) und `CACHE` in `sw.js` hochzählen.

Vor jedem Push `tools/check.sh` laufen lassen. Ein Syntaxfehler in `sw.js` fällt im Browser nicht auf, lässt aber alle Geräte dauerhaft auf dem alten Stand hängen.
