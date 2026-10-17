"""Erzeugt die Druckmaterialien als HTML und druckt sie mit Chrome headless zu PDF."""
import subprocess, pathlib, sys

HERE = pathlib.Path(__file__).parent
OUT = pathlib.Path(sys.argv[1])
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

G = [  # Farbe, Symbol, Spot, Tipps (wie auf der Seite)
    ("#e5483b", "●", "McDonald's Happy Meal", [
        "Schaut auf das Ende vom Spot. Dort seht ihr die Box und das Logo.",
        "Schaut auf die Kinder und den Papa. Wie fühlen sie sich, als die Box aufgeht?",
        "Was passiert mit der Box und im Auto? Kann das wirklich passieren?",
        "Was ist wirklich in der Box drin?"]),
    ("#f08a1c", "▲", "Müllermilch", [
        "Schaut auf die Flaschen am Ende vom Spot.",
        "Was passiert, wenn der Mann die richtige Flasche findet? Was will er haben?",
        "Hört genau hin! Welches Geräusch macht die Flasche? Kann eine Flasche das?",
        "Was ist wirklich in der Flasche drin?"]),
    ("#b88600", "■", "hohes C", [
        "Schaut auf die Flaschen am Ende vom Spot. Hört auf den letzten Satz.",
        "Was sagt die Werbung über den Saft? Was soll er für euch tun?",
        "Schaut auf die Kuscheltiere und Puppen. Was machen sie? Können sie das wirklich?",
        "Was ist wirklich im Saft drin? Hört genau hin."]),
    ("#3a9a4b", "★", "nimm2 soft", [
        "Schaut auf die Tüte am Ende vom Spot.",
        "Lest die Wörter am Ende. Was sollen die Bonbons sein?",
        "Schaut auf die Gesichter der Kinder. Was passiert mit ihren Wangen?",
        "Was steht auf der Tüte? Was ist in den Bonbons drin?"]),
    ("#2f6fdf", "♥", "Skechers GOrun 2", [
        "Schaut auf die Schuhe am Ende vom Spot.",
        "Was können die Schuhe laut Werbung? Was schafft der Mann mit den Schuhen?",
        "Wer ist schneller, der Mann oder der Gepard? Kann ein Mensch so schnell laufen?",
        "Wofür sind Laufschuhe wirklich gut?"]),
    ("#8a4fd1", "◆", "Wrigley's Extra", [
        "Schaut auf die Packungen ganz am Ende vom Spot. Lest den Satz unten.",
        "Was soll der Kaugummi mit euren Zähnen machen?",
        "Was macht der Junge mit dem Teller? Könntest du das?",
        "Was kann Kaugummikauen für die Zähne wirklich tun?"]),
]
Q = [
    ("Was wird verkauft?", "Wie heißt die Marke? Gibt es einen Slogan?", ["Verkauft wird …", "Die Marke heißt …", "Der Slogan ist …"]),
    ("Was verspricht die Werbung?", "Was soll das Produkt für dich tun?", ["Die Werbung verspricht, dass …"]),
    ("Was ist übertrieben oder erfunden?", "Was kann es in echt nicht geben?", ["Erfunden ist, dass …"]),
    ("Was ist echt?", "Was stimmt wirklich?", ["Echt ist, dass …"]),
]
EH = [  # Erwartungshorizont der LiV
    ("Das Happy Meal macht Kinder glücklich und bringt Abenteuer und Magie.", "Die Box verwandelt sich in einen Dschungel, ein Regenbogen springt heraus.", "Im Happy Meal ist tatsächlich eine Spielfigur (Schleich).", "Fantasiewelt, Spielzeug bekannter Marken, Kinder als Darsteller, Jingle"),
    ("Die Milch ist so frisch, dass man die Kuh noch hört.", "Die Flasche muht.", "Müllermilch ist ein Milchgetränk.", "Humor, Tiergeräusch als Symbol für Frische, einprägsamer Slogan"),
    ("Der Saft gibt so viel Energie, dass sogar Spielzeug lebendig wird.", "Die Spielfiguren erwachen zum Leben.", "Orangensaft enthält Vitamin C.", "Gesundheitsversprechen im Slogan („Hauptsache gesund“), Kind als Darstellerin, Fantasie"),
    ("Naschen ist gesund und macht Spaß.", "Die Wangen ploppen übertrieben auf.", "Die Bonbons enthalten zugesetzte Vitamine.", "Lautmalerei („Plopp“), Humor, Gesundheitsargument („Vitamine“)"),
    ("Mit den Schuhen läuft man so schnell wie ein Gepard.", "Ein Mensch läuft durch Schuhe tierisch schnell.", "Laufschuhe können bequem sein und beim Laufen unterstützen.", "Tiere als Symbol für Eigenschaften (Schnelligkeit), Dynamik"),
    ("Der Kaugummi macht die Zähne stark.", "Der Junge zerbeißt einen Teller.", "Kaugummikauen kann die Zahnpflege unterstützen.", "Übertreibung, Gesundheitsargument („starke Zähne“)"),
]

BASE = """<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{title}</title><style>
@font-face {{ font-family: Andika; src: url(andika-400.woff2); font-weight: 400; }}
@font-face {{ font-family: Andika; src: url(andika-700.woff2); font-weight: 700; }}
@font-face {{ font-family: Fredoka; src: url(fredoka-600.woff2); font-weight: 600; }}
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
    star_line = '<div class="line">Wir glauben der Werbung (nicht), weil …</div>' if with_starts else '<div class="line"></div>'
    rows += f'<section class="q star"><div class="h"><span class="n">⭐</span><div><b>Expertenaufgabe: Glaubt ihr der Werbung?</b><br><small>Warum? Warum nicht? Würdet ihr das kaufen?</small></div></div>{star_line}<div class="line"></div></section>'
    syms = "".join(f'<span class="box sym" style="color:{c}">{s}</span>' for c, s, *_ in G)
    return f"""<div class="page"><header><img class="ed" src="eddie.svg" alt=""><div class="tt"><div class="badge">🔍 DETEKTIV-BOGEN</div><h1>Können wir Werbung immer glauben?</h1></div>
<div class="who">Gruppe: ______<br><span class="pick">Kreist euer Zeichen ein: {syms}</span></div></header>
<p class="names">Unsere Namen: ________________________________________________</p>{rows}</div>"""


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
"""


def schilder():
    pages = ""
    for i in range(0, 6, 2):
        cards = ""
        for j in (i, i + 1):
            c, s, *_ = G[j]
            cards += f'<div class="card" style="border-color:{c}"><img class="ed2" src="eddie.svg" alt=""><div class="sym big" style="background:{c}">{s}</div><div class="nm">Gruppe {j + 1}</div></div>'
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
            items = "".join(f'<li><b>Tipp zu Frage {k}:</b> {t}<br><i>{Q[k - 1][2][0]}</i></li>' for k, t in enumerate(tips, 1))
            items += '<li><b>Tipp zur Expertenaufgabe:</b> Denkt an die Super-Limo!<br><i>Wir glauben der Werbung (nicht), weil …</i></li>'
            cards += f'<div class="card" style="border-color:{c}"><div class="top"><span class="sym s" style="background:{c}">{s}</span> 💡 Tippkarte Gruppe {j + 1}<span class="spot">{spot}</span></div><ul>{items}</ul><div class="cut">Reservekarte, falls das iPad streikt</div></div>'
        pages += f'<div class="page">{cards}</div>'
    return pages


tipp_css = """
.page { display: flex; flex-direction: column; gap: 8mm; height: 272mm; }
.card { flex: 1; border: 3px dashed; border-radius: 6mm; padding: 6mm 8mm; display: flex; flex-direction: column; }
.top { font-size: 20pt; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.s { width: 34px; height: 34px; border-radius: 50%; color: #fff; display: inline-grid; place-items: center; font-size: 18pt; }
.spot { margin-left: auto; font-size: 10pt; font-weight: 400; color: #8a8273; }
ul { list-style: none; padding: 0; margin: 4mm 0 0; display: flex; flex-direction: column; gap: 3mm; font-size: 14pt; }
i { color: #6b645b; }
.cut { margin-top: auto; font-size: 9pt; color: #8a8273; text-align: right; }
"""

WORDS = [("Produkt", "Das wird verkauft."), ("Marke", "So heißt die Firma."), ("Logo", "Das Zeichen der Marke."),
         ("Slogan", "Ein kurzer Satz, den man sich merkt."), ("Versprechen", "Das soll das Produkt für dich tun."),
         ("übertrieben", "Viel mehr, als es wirklich ist."), ("erfunden", "Das gibt es in echt nicht."), ("echt", "Das stimmt wirklich.")]


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

DOCS = [
    ("Detektivbogen_mit_Satzanfaengen", "portrait", bogen_css, bogen(True)),
    ("Detektivbogen_ohne_Satzanfaenge", "portrait", bogen_css, bogen(False)),
    ("Gruppenschilder", "portrait", schild_css, schilder()),
    ("Tippkarten_Reserve", "portrait", tipp_css, tippkarten()),
    ("Leitfrage_und_Wortspeicher", "landscape", wort_css, wortspeicher()),
    ("Erwartungshorizont", "landscape", eh_css, erwartung()),
]

OUT.mkdir(parents=True, exist_ok=True)
for name, orient, css, body in DOCS:
    html = HERE / f"{name}.html"
    html.write_text(BASE.format(title=name, orient=orient, css=css, body=body), encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT / (name + '.pdf')}", html.as_uri()],
                   check=True, capture_output=True)
    print("ok", name)
