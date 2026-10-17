"""Erzeugt die Druckmaterialien als HTML und druckt sie mit Chrome headless zu PDF."""
import subprocess, pathlib, sys, os, json, re

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
OUT = pathlib.Path(sys.argv[1])
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

TEXT = json.loads(re.search(r"/\*TEXT\*/(.*?)/\*TEXT\*/", (ROOT / "index.html").read_text(), re.S).group(1))
COLORS = ["#e5483b", "#f08a1c", "#b88600", "#3a9a4b", "#2f6fdf", "#8a4fd1"]
SPOTS = ["McDonald's Happy Meal", "Müllermilch", "hohes C", "nimm2 soft", "Skechers GOrun 2", "Wrigley's Extra"]
G = [(c, g["sym"], s, g["tips"]) for c, g, s in zip(COLORS, TEXT["groups"], SPOTS)]  # Farbe, Symbol, Spot, Tipp 1 und 2 (wie auf der Seite)
Q = [
    ("Was wird verkauft?", "Wie heißt die Marke? Gibt es einen Slogan?", ["Verkauft wird …", "Die Marke heißt …", "Der Slogan ist …"]),
    ("Was verspricht die Werbung?", "Was soll das Produkt für dich tun?", ["Die Werbung verspricht, dass …"]),
    ("Was ist übertrieben oder erfunden?", "Was kann es in echt nicht geben?", ["Erfunden ist, dass …"]),
    ("Was ist echt?", "Was stimmt wirklich?", ["Echt ist, dass …"]),
]
EH = [  # Erwartungshorizont der LiV
    ("Das Happy Meal macht Kinder glücklich und bringt Abenteuer und Magie.", "Das Happy Meal verwandelt sich in einen Dschungel, ein Regenbogen springt heraus.", "Im Happy Meal ist tatsächlich eine Spielfigur (Schleich).", "Fantasiewelt, Spielzeug bekannter Marken, Kinder als Darsteller, Jingle"),
    ("Wer Müllermilch kauft, kann ganz leicht 50.000 Euro gewinnen.", "Die Verkäuferin findet die Gewinnerflasche sofort und jubelt. Der Gewinn wirkt kinderleicht.", "In fünf Flaschen steckt wirklich ein „Muuh“. Wer eine davon findet, gewinnt 50.000 Euro. Müllermilch ist ein Milchgetränk.", "Gewinnspiel, Humor, Tiergeräusch („Muuh“) als Erkennungszeichen, Slogan „Alles Müller, oder was?“"),
    ("Der Saft gibt so viel Energie, dass sogar Spielzeug lebendig wird.", "Die Spielfiguren erwachen zum Leben.", "Orangensaft enthält Vitamin C.", "Gesundheitsversprechen im Slogan („Hauptsache gesund“), Kind als Darstellerin, Fantasie"),
    ("Naschen ist gesund und macht Spaß.", "Die Wangen ploppen übertrieben auf.", "Die Bonbons enthalten zugesetzte Vitamine.", "Lautmalerei („Plopp“), Humor, Gesundheitsargument („Vitamine“)"),
    ("Mit den Schuhen läuft man so schnell wie ein Gepard.", "Ein Mensch läuft durch Schuhe tierisch schnell.", "Laufschuhe können bequem sein und beim Laufen unterstützen.", "Tiere als Symbol für Eigenschaften (Schnelligkeit), Dynamik"),
    ("Der Kaugummi macht die Zähne stark.", "Der Junge zerbeißt einen Teller.", "Kaugummikauen kann die Zahnpflege unterstützen.", "Übertreibung, Gesundheitsargument („starke Zähne“)"),
]

BASE = """<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{title}</title><style>
@font-face {{ font-family: Andika; src: url({root}/fonts/andika-400.woff2); font-weight: 400; }}
@font-face {{ font-family: Andika; src: url({root}/fonts/andika-700.woff2); font-weight: 700; }}
@font-face {{ font-family: Fredoka; src: url({root}/fonts/fredoka-600.woff2); font-weight: 600; }}
@page {{ size: A4 {orient}; margin: 12mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: Andika, sans-serif; color: #23201c; font-size: 15pt; line-height: 1.35; }}
.page {{ page-break-after: always; break-after: page; }}
.page:last-child {{ page-break-after: auto; }}
.sym {{ font-family: -apple-system, 'Helvetica Neue', sans-serif; }}
{css}
</style></head><body>{body}</body></html>"""


def bogen(with_starts):
    rows = ""
    for i, (q, sub, starts) in enumerate(Q, 1):
        lines = "".join(f'<div class="line">{s if with_starts else ""}</div>' for s in (starts if with_starts else ["", ""]))
        if with_starts and len(starts) == 1:
            lines += '<div class="line"></div>'
        rows += f'<section class="q"><div class="h"><span class="n">{i}</span><div><b>{q}</b><br><small>{sub}</small></div></div>{lines}</section>'
    syms = "".join(f'<span class="box sym" style="color:{c}">{s}</span>' for c, s, *_ in G)
    help_ = '<p class="help">📖 Ihr kennt ein Wort nicht? Eddie erklärt es auf dem iPad. &nbsp; 💡 Ihr kommt nicht weiter? Tippt auf dem iPad auf den Tipp.</p>'
    front = f"""<div class="page"><header><img class="ed" src="{ROOT.as_uri()}/eddie.webp" alt=""><div class="tt"><div class="badge">🔍 DETEKTIV-BOGEN</div><h1>Können wir Werbung immer glauben?</h1></div>
<div class="who">Gruppe: ______<br><span class="pick">Kreist euer Zeichen ein: {syms}</span></div></header>
<p class="names">Unsere Namen: ________________________________________________</p>{rows}{help_}<p class="turn">Fertig? Dreht das Blatt um. 🚀</p></div>"""
    s = lambda t: t if with_starts else ""
    back = f"""<div class="page"><header class="rk"><span class="rocket">🚀</span><div class="tt"><div class="badge">RAKETENAUFGABE</div><h1>Glaubt ihr der Werbung?</h1></div></header>
<section class="q star"><div class="h"><span class="n">A</span><div><b>Glaubt ihr dem Versprechen der Werbung?</b><br><small>Warum? Warum nicht? Denkt an die Super-Limo.</small></div></div>
<div class="line">{s("Wir glauben der Werbung (nicht), weil …")}</div><div class="line"></div><div class="line"></div></section>
<section class="q star"><div class="h"><span class="n">B</span><div><b>Würdet ihr das Produkt kaufen?</b><br><small>Erklärt, warum.</small></div></div>
<div class="line">{s("Wir würden es (nicht) kaufen, weil …")}</div><div class="line"></div></section>
<section class="q star draw"><div class="h"><span class="n">⭐</span><div><b>Raketen-Plus: Wie sähe die Werbung aus, wenn sie nur die Wahrheit sagt?</b><br><small>Malt oder schreibt.</small></div></div><div class="canvas"></div></section></div>"""
    return front + back


bogen_css = """
header { display: flex; gap: 10px; align-items: flex-end; border-bottom: 3px solid #23201c; padding-bottom: 6px; }
.badge { display: inline-block; background: #23201c; color: #fff; border-radius: 99px; padding: 1px 12px; font-size: 11pt; }
h1 { margin: 4px 0 0; font-size: 22pt; }
.who { margin-left: auto; text-align: right; font-size: 14pt; }
.ed { height: 30mm; }
h1, .nm, .lead, .w b, .top { font-family: Fredoka, Andika, sans-serif; font-weight: 600; }
.pick { font-size: 11pt; }
.box { font-size: 16pt; margin-left: 4px; }
.names { margin: 8px 0 4px; }
.q { border: 2px solid #d9cdb6; border-radius: 12px; padding: 8px 12px 4px; margin-top: 8px; }
.q.star { border-color: #e8b80c; }
.h { display: flex; gap: 10px; align-items: flex-start; }
.n { flex: none; width: 30px; height: 30px; border-radius: 50%; background: #23201c; color: #fff; display: grid; place-items: center; font-weight: 700; }
.star .n { background: #e8b80c; }
small { color: #6b645b; font-size: 12pt; }
.line { border-bottom: 1.5px solid #9b917f; height: 40px; padding-top: 14px; color: #8a8273; font-style: italic; font-size: 13pt; }
.help { margin: 8px 0 0; font-size: 11pt; color: #6b645b; }
.turn { margin: 4px 0 0; text-align: right; font-weight: 700; }
.rk { align-items: center; }
.rocket { font-size: 46pt; line-height: 1; }
.star { background: #fffbea; }
.canvas { height: 95mm; border: 1.5px dashed #c9b98f; border-radius: 8px; margin: 8px 0 8px; background: #fff; }
"""


def schilder():
    pages = ""
    for i in range(0, 6, 2):
        cards = ""
        for j in (i, i + 1):
            c, s, *_ = G[j]
            cards += f'<div class="card" style="border-color:{c}"><img class="ed2" src="{ROOT.as_uri()}/eddie.webp" alt=""><div class="sym big" style="background:{c}">{s}</div><div class="nm">Gruppe {j + 1}</div></div>'
        pages += f'<div class="page">{cards}</div>'
    return pages


schild_css = """
.page { display: flex; flex-direction: column; gap: 10mm; height: 272mm; }
.card { flex: 1; border: 6mm solid; border-radius: 10mm; display: flex; align-items: center; justify-content: center; gap: 14mm; }
.big { width: 62mm; height: 62mm; flex: none; border-radius: 50%; color: #fff; display: grid; place-items: center; font-size: 110pt; }
.nm { font-size: 58pt; white-space: nowrap; }
.card { position: relative; }
.ed2 { position: absolute; right: 6mm; bottom: 4mm; height: 42mm; }
"""


def tippkarten():
    pages = ""
    for i in range(0, 6, 2):
        cards = ""
        for j in (i, i + 1):
            c, s, spot, tips = G[j]
            items = "".join(f'<li><b>Tipp {k}: {TEXT["tipHeads"][k - 1]}</b><br>{t}</li>' for k, t in enumerate(tips, 1))
            cards += f'<div class="card" style="border-color:{c}"><div class="top"><span class="sym s" style="background:{c}">{s}</span> 💡 Tippkarte Gruppe {j + 1}<span class="spot">{spot}</span></div><ul>{items}</ul><div class="cut">Reservekarte, falls das iPad streikt</div></div>'
        pages += f'<div class="page">{cards}</div>'
    return pages


tipp_css = """
.page { display: flex; flex-direction: column; gap: 8mm; height: 272mm; }
.card { flex: 1; border: 3px dashed; border-radius: 6mm; padding: 6mm 8mm; display: flex; flex-direction: column; }
.top { font-size: 20pt; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.s { width: 34px; height: 34px; border-radius: 50%; color: #fff; display: inline-grid; place-items: center; font-size: 18pt; }
.spot { margin-left: auto; font-size: 10pt; font-weight: 400; color: #8a8273; }
ul { list-style: none; padding: 0; margin: 6mm 0 0; display: flex; flex-direction: column; gap: 7mm; font-size: 16pt; }
i { color: #6b645b; }
.cut { margin-top: auto; font-size: 9pt; color: #8a8273; text-align: right; }
"""

WORDS = [("Produkt", "Eine Sache, die man kaufen kann."), ("Marke", "Der Name, den eine Firma ihren Sachen gibt."), ("Logo", "Das Zeichen der Marke."),
         ("Slogan", "Ein kurzer Satz aus der Werbung, den man sich merkt."), ("Versprechen", "Das soll das Produkt für dich tun."),
         ("übertrieben", "Viel größer, schneller oder besser, als es in echt ist."), ("erfunden", "Das gibt es in echt nicht."), ("echt", "Das stimmt wirklich.")]


def wortspeicher():
    cards = "".join(f'<div class="w"><b>{w}</b><span>{d}</span></div>' for w, d in WORDS)
    lead = '<div class="lead">Können wir Werbung immer glauben?</div>'
    return f'<div class="page">{lead}</div><div class="page grid">{cards}</div>'


wort_css = """
.lead { height: 180mm; display: grid; place-items: center; text-align: center; font-size: 64pt; font-weight: 700; line-height: 1.15; border: 4mm solid #23201c; border-radius: 10mm; padding: 10mm; }
.grid { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: repeat(4, 1fr); gap: 6mm; height: 180mm; }
.w { border: 3px solid #23201c; border-radius: 6mm; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 4mm; }
.w b { font-size: 40pt; line-height: 1.1; }
.w span { font-size: 14pt; color: #6b645b; }
"""


def erwartung():
    rows = "".join(
        f'<tr><td><span class="sym d" style="background:{G[i][0]}">{G[i][1]}</span> <b>{i + 1}</b><br>{G[i][2]}</td><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>'
        for i, (a, b, c, d) in enumerate(EH))
    return f"""<div class="page"><h1>Erwartungshorizont: Analyse der sechs Werbespots</h1>
<table><thead><tr><th>Gruppe / Spot</th><th>Versprechen</th><th>Fiktiv (übertrieben/erfunden)</th><th>Wahrer Kern</th><th>Werbemittel</th></tr></thead><tbody>{rows}</tbody></table>
<p class="src">Spots: McDonald's Deutschland „Nur im Happy Meal: exklusive bayala und Eldrador Tiere von Schleich“ (YouTube fn0-rO3ru0Q), Müllermilch „Finde das Muuh 2025“ (KoSvg-8NfIs), hohes C „Hauptsache gesund“ (wZbj80t1rYU), nimm2 soft „Die mit dem Plopp“ (hXE1qriS9Z4), Skechers GOrun 2 (0ufcuVFMtzo), Wrigley's Extra für Kinder (C5770f4hlNU). Zugriff 17.10.2026.</p></div>"""


eh_css = """
h1 { font-size: 18pt; margin: 0 0 4mm; }
table { width: 100%; border-collapse: collapse; font-size: 11pt; line-height: 1.25; }
th, td { border: 1px solid #9b917f; padding: 2.5mm; vertical-align: top; text-align: left; }
th { background: #f3ecdf; }
.d { width: 22px; height: 22px; border-radius: 50%; color: #fff; display: inline-grid; place-items: center; font-size: 12pt; }
.src { font-size: 9pt; color: #6b645b; }
"""


TB = [("Glück und Abenteuer", "Happy Meal wird zum Dschungel", "Spielfigur ist drin"),
      ("50.000 Euro gewinnen ist leicht", "Gewinnerflasche sofort gefunden", "5 Flaschen muhen wirklich"),
      ("Saft macht stark und gesund", "Kuscheltiere werden lebendig", "Vitamin C ist drin"),
      ("Naschen ist gesund", "Wangen ploppen auf", "Vitamine sind zugesetzt"),
      ("Schnell wie ein Gepard", "Mann überholt Gepard", "Bequeme Laufschuhe"),
      ("Superstarke Zähne", "Junge beißt in Teller", "Kauen hilft den Zähnen")]


def tafelbild():
    rows = "".join(f'<tr><td><span class="sym d" style="background:{G[i][0]}">{G[i][1]}</span> {G[i][2]}</td><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for i, (a, b, c) in enumerate(TB))
    words = "".join(f"<li>{w}</li>" for w, _ in WORDS)
    return f"""<div class="page"><div class="board"><h2>Können wir Werbung immer glauben?</h2>
<div class="cols"><ul class="ws"><b>Wortspeicher</b>{words}</ul>
<table><thead><tr><th>Spot</th><th>Das verspricht die Werbung</th><th>Übertrieben oder erfunden</th><th>Echt</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="fazit">Werbung mischt Echtes mit Erfundenem. Sie will, dass wir kaufen.</p></div></div>"""


tb_css = """
.board { background: #2f4f3a; color: #fff; border: 5mm solid #8a5a2b; border-radius: 3mm; padding: 6mm 8mm; height: 170mm; font-family: Andika; }
h2 { font-family: Fredoka; text-align: center; font-size: 24pt; margin: 0 0 4mm; }
.cols { display: flex; gap: 6mm; }
.ws { list-style: none; margin: 0; padding: 3mm 4mm; border: 1.5px dashed #fff; border-radius: 3mm; font-size: 12pt; min-width: 32mm; }
.ws b { display: block; margin-bottom: 2mm; }
table { flex: 1; border-collapse: collapse; font-size: 12pt; }
th, td { border-bottom: 1.5px solid rgba(255,255,255,.6); padding: 2mm 3mm; text-align: left; }
th { font-family: Fredoka; font-weight: 600; }
.d { width: 20px; height: 20px; border-radius: 50%; color: #fff; display: inline-grid; place-items: center; font-size: 11pt; border: 1px solid #fff; }
.fazit { margin: 6mm 0 0; text-align: center; font-size: 18pt; font-family: Fredoka; background: #fff3; border-radius: 3mm; padding: 3mm; }
"""


def lernumgebung():
    return """<div class="page"><h1>Lernumgebung „Werbedetektive“</h1>
<figure><img src="shot_home.png"><figcaption>Startseite mit Klassentier Eddie und Gruppenauswahl</figcaption></figure>
<figure><img src="shot_gruppe.png"><figcaption>Gruppenansicht mit Spot, Arbeitsauftrag von Eddie, Wortspeicher zum Antippen und Vorlesen, Tipp-Feld</figcaption></figure>
<figure><img src="shot_tipp.png"><figcaption>Tippseite der Gruppe mit zwei gestuften Denkanstößen zum Aufdecken und Vorlesen</figcaption></figure></div>"""


lu_css = """
h1 { font-family: Fredoka; font-size: 18pt; margin: 0 0 4mm; }
figure { margin: 0 0 6mm; text-align: center; }
img { width: 100mm; border: 1px solid #ccc; border-radius: 2mm; }
figure { margin-bottom: 3mm !important; }
figcaption { font-size: 10pt; color: #6b645b; margin-top: 1mm; }
"""

DOCS = [
    ("Detektivbogen_mit_Satzanfaengen", "portrait", bogen_css, bogen(True)),
    ("Detektivbogen_ohne_Satzanfaenge", "portrait", bogen_css, bogen(False)),
    ("Gruppenschilder", "portrait", schild_css, schilder()),
    ("Tippkarten_Reserve", "portrait", tipp_css, tippkarten()),
    ("Leitfrage_und_Wortspeicher", "landscape", wort_css, wortspeicher()),
    ("Erwartungshorizont", "landscape", eh_css, erwartung()),
    ("Tafelbild", "landscape", tb_css, tafelbild()),
    ("Lernumgebung_Screenshots", "portrait", lu_css, lernumgebung()),
]
LABEL = {"Detektivbogen_mit_Satzanfaengen": "Anhang 3: Detektivbogen mit Satzanfängen", "Detektivbogen_ohne_Satzanfaenge": "Anhang 4: Detektivbogen ohne Satzanfänge",
         "Lernumgebung_Screenshots": "Anhang 5", "Tippkarten_Reserve": "Anhang 6: Tippkarten (Auszug, Gruppen 1 und 2)", "Erwartungshorizont": "Anhang 7",
         "Tafelbild": "Anhang 8: Tafelbild (geplanter Endzustand)", "Leitfrage_und_Wortspeicher": "Anhang 9: Leitfrage und Wortspeicher"}
ANH = os.environ.get("ANHANG") == "1"
if ANH:
    DOCS = [d for d in DOCS if d[0] in LABEL]

OUT.mkdir(parents=True, exist_ok=True)
for name, orient, css, body in DOCS:
    html = HERE / f"{name}.html"
    if ANH:
        body = f'<div class="anh">{LABEL[name]}</div>' + body
        css += ".anh { font-family: 'Times New Roman', serif; font-size: 12pt; margin-bottom: 3mm; } .lead { height: 160mm !important; } .board { height: 160mm !important; } .grid { height: 165mm !important; } .line { height: 36px !important; padding-top: 12px !important; } .q { margin-top: 6px !important; } table { font-size: 10pt !important; } th, td { padding: 1.8mm !important; }"
        if name == "Tippkarten_Reserve": css += ".page { height: 258mm !important; }"
    html.write_text(BASE.format(root=ROOT.as_uri(), title=name, orient=orient, css=css, body=body), encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={HERE / ".chrome"}", "--no-first-run",
                    f"--print-to-pdf={OUT / (name + '.pdf')}", html.as_uri()],
                   check=True, capture_output=True, timeout=60)
    print("ok", name)
