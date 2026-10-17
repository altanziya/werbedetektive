"""Spricht alle Texte aus dem TEXT-Block in index.html mit einer Neuralstimme ein (audio/*.mp3).

Braucht edge-tts (pip install edge-tts). Aufruf: python3 tools/stimme.py
"""
import asyncio, json, pathlib, re
import edge_tts

ROOT = pathlib.Path(__file__).parent.parent
TEXT = json.loads(re.search(r"/\*TEXT\*/(.*?)/\*TEXT\*/", (ROOT / "index.html").read_text(), re.S).group(1))
EDDIE, ERZAEHL = "de-DE-FlorianMultilingualNeural", "de-DE-SeraphinaMultilingualNeural"

jobs = {"home": (EDDIE, " ".join(TEXT["home"])), "intro": (EDDIE, " ".join(TEXT["intro"]))}
for k, w in enumerate(TEXT["words"], 1):
    jobs[f"w{k}"] = (ERZAEHL, f"{w['w']}. {w['d']}")
for i, g in enumerate(TEXT["groups"], 1):
    for k, t in enumerate(g["tips"], 1):
        jobs[f"g{i}t{k}"] = (ERZAEHL, f"Tipp {k}. {TEXT['tipHeads'][k - 1]} {t}")


async def main():
    out = ROOT / "audio"
    out.mkdir(exist_ok=True)
    for name, (voice, text) in jobs.items():
        await edge_tts.Communicate(text, voice, rate="-10%").save(str(out / f"{name}.mp3"))
        print("ok", name)

asyncio.run(main())
