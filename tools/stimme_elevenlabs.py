"""Spricht alle Texte aus dem TEXT-Block in index.html mit ElevenLabs ein (audio/*.mp3).

Key aus der macOS-Keychain (security add-generic-password -s elevenlabs-api -a "$USER" -w).
Aufruf: python3 tools/stimme_elevenlabs.py [nur,diese,dateien]
Stimmen: Will (Eddie) und Jessica (Wortspeicher, Tipps), kostenlose Standardstimmen, Sprache fest auf Deutsch.
"""
import json, pathlib, re, subprocess, sys, urllib.request

ROOT = pathlib.Path(__file__).parent.parent
TEXT = json.loads(re.search(r"/\*TEXT\*/(.*?)/\*TEXT\*/", (ROOT / "index.html").read_text(), re.S).group(1))
KEY = subprocess.run(["security", "find-generic-password", "-s", "elevenlabs-api", "-w"], capture_output=True, text=True, check=True).stdout.strip()
EDDIE, ERZAEHL = "bIHbv24MWmeRgasZH58o", "cgSgspJ2msm6clMCkdW9"
MODEL = "eleven_v3"

# Nur für die Stimme: so geschrieben, wie es deutsch klingen soll (angezeigt wird der Originaltext)
SPRECH = {"„": "", "“": "", "Aufgabe 1.": "Aufgabe eins.", "Aufgabe 2.": "Aufgabe zwei.", "Aufgabe 3.": "Aufgabe drei.", "Aufgabe 4.": "Aufgabe vier."}
def sprech(t):
    for a, b in SPRECH.items():
        t = t.replace(a, b)
    return t

jobs = {"home": (EDDIE, " ".join(TEXT["home"])), "intro": (EDDIE, " ".join(TEXT["intro"]))}
for k, w in enumerate(TEXT["words"], 1):
    jobs[f"w{k}"] = (ERZAEHL, f"Was bedeutet {w['w']}? {w['d']}")
for i, g in enumerate(TEXT["groups"], 1):
    for k, t in enumerate(g["tips"], 1):
        jobs[f"g{i}t{k}"] = (ERZAEHL, f"Tipp zu Aufgabe {k}. {TEXT['tipHeads'][k - 1]} {t}")

only = set(sys.argv[1].split(",")) if len(sys.argv) > 1 else None
out = ROOT / "audio"
for name, (voice, text) in jobs.items():
    if only and name not in only:
        continue
    body = {"text": sprech(text), "model_id": MODEL, "voice_settings": {"stability": 0.55, "similarity_boost": 0.8, "speed": 0.92}}
    if MODEL != "eleven_multilingual_v2":
        body["language_code"] = "de"  # Sprache fest auf Deutsch
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_64",
                                 data=json.dumps(body).encode(), headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    (out / f"{name}.mp3").write_bytes(urllib.request.urlopen(req, timeout=120).read())
    print("ok", name)
