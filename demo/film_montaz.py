"""Montaż filmu HugMe: plansze + nagranie scen (film_nagraj.py) + lektor + napisy → docs/film/hugme-film.mp4 (do 3:00).

Każda scena trwa tyle, ile nagranie (a ono co najmniej tyle, ile kwestia lektora), więc dźwięk nie jest przyspieszany
ani ucinany. Między scenami z różnych ekranów krótkie przenikanie; sceny „ciągłe” (to samo ujęcie) bez przejścia.
Lektor: film_lektor/<scena>.mp3 (ElevenLabs, głos „Arleta”), TEMPO z film_czas. Napisy wtopione w obraz (PNG z HTML,
czcionka Atkinson Hyperlegible jak w aplikacji) i osobno docs/film/hugme-film.srt. Na końcu powstaje
docs/SCENARIUSZ_FILMU.md z rzeczywistymi czasami scen. Uruchom: python demo/film_montaz.py"""
import html
import json
import shutil
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

import film_czas as C
from film_sceny import SCENY

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "out" / "film"
TMP = OUT / "montaz"
FINAL = ROOT / "docs" / "film" / "hugme-film.mp4"
SRT = ROOT / "docs" / "film" / "hugme-film.srt"
DOC = ROOT / "docs" / "SCENARIUSZ_FILMU.md"
FPS = 30
LIMIT = 180.0       # wymóg konkursu: do 3 minut
PRZENIKANIE = 0.4   # s między scenami z różnych ekranów
PLANSZA = {"00-tytul": 0.6, "14-koniec": 2.6}  # dodatkowy czas planszy po kwestii (zatrzymanie kadru)

FONTS = (ROOT / "app" / "static" / "fonts").as_uri()
LOGO = (ROOT / "app" / "static" / "img" / "logo.svg").as_uri()
QR = (ROOT / "docs" / "slajdy" / "qr-demo.svg").as_uri()
# jak w app/static/css/hugme.css: podstawowa łacina i polskie znaki w osobnych plikach
LAT = "U+0000-00FF, U+2000-206F, U+20AC, U+2122, U+2190-2199, U+25A0-25FF, U+2600-27BF"
EXT = "U+0100-024F, U+1E00-1EFF"
CSS = f"""
@font-face {{ font-family: A; font-weight: 400; src: url({FONTS}/atkinson-latin-400.woff2); unicode-range: {LAT}; }}
@font-face {{ font-family: A; font-weight: 400; src: url({FONTS}/atkinson-400.woff2); unicode-range: {EXT}; }}
@font-face {{ font-family: A; font-weight: 700; src: url({FONTS}/atkinson-latin-700.woff2); unicode-range: {LAT}; }}
@font-face {{ font-family: A; font-weight: 700; src: url({FONTS}/atkinson-700.woff2); unicode-range: {EXT}; }}
* {{ margin: 0; box-sizing: border-box; }}
html, body {{ width: 1920px; height: 1080px; font-family: A, sans-serif; }}
.card {{ background: #FBF6EE; color: #1B2540; height: 100%; display: flex; flex-direction: column; justify-content: center;
        padding: 0 200px; gap: 26px; position: relative; overflow: hidden; }}
.card::before {{ content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 22px; background: #B8432F; }}
.logo {{ width: 150px; }}
.k {{ color: #B8432F; font-weight: 700; font-size: 32px; letter-spacing: .08em; text-transform: uppercase; }}
.t {{ font-size: 150px; font-weight: 700; line-height: 1; letter-spacing: -2px; }}
.s {{ font-size: 56px; font-weight: 700; color: #1B2540; }}
.m {{ font-size: 36px; color: #3d4660; line-height: 1.35; max-width: 1300px; }}
.chips {{ display: flex; gap: 18px; margin-top: 10px; }}
.chip {{ font-size: 28px; font-weight: 700; padding: 12px 24px; border-radius: 999px; border: 3px solid #1B2540; }}
.end {{ display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 80px; }}
.links {{ font-size: 40px; line-height: 1.55; }}
.links b {{ color: #B8432F; }}
.qr {{ width: 300px; height: 300px; background: #fff; padding: 18px; border-radius: 18px; border: 3px solid #1B2540; }}
.qr img {{ width: 100%; height: 100%; }}
.note {{ font-size: 26px; color: #5a6178; }}
.bar {{ position: absolute; left: 50%; bottom: 46px; transform: translateX(-50%); width: max-content; max-width: 1680px;
       background: rgba(27, 37, 64, .93); color: #fff; padding: 14px 34px 18px; border-radius: 16px; text-align: center;
       box-shadow: 0 6px 24px rgba(0, 0, 0, .25); }}
.bar .k {{ font-size: 22px; color: #F2B8A8; margin-bottom: 4px; }}
.bar .x {{ font-size: 40px; font-weight: 700; line-height: 1.25; }}
"""


def esc(s):
    return html.escape(s)


def tytul_html():
    return (f'<div class="card"><img class="logo" src="{LOGO}" alt=""><p class="k">HackYeah 2026 · HubMi.pl · ROPS Kraków</p>'
            '<p class="t">HugMe</p><p class="s">Twój problem nie zostaje sam</p>'
            '<p class="m">Platforma dla Małopolskiego Hubu Innowacji Społecznych: mieszkańcy, gminy i Hub w jednym miejscu.</p>'
            '<div class="chips"><span class="chip">Mieszkanka</span><span class="chip">Koordynatorka Hubu</span>'
            '<span class="chip">Gmina</span></div></div>')


def koniec_html():
    return (f'<div class="card"><div class="end"><div style="display:flex;flex-direction:column;gap:24px">'
            f'<img class="logo" src="{LOGO}" alt=""><p class="t">HugMe</p><p class="s">Twój problem nie zostaje sam.</p>'
            '<p class="links">Demo: <b>hugme.twapp.pl</b><br>Kod: <b>github.com/TomaszWu14/hugme</b></p>'
            '<p class="note">Wszystkie osoby, organizacje i zgłoszenia w filmie są przykładowe (fikcyjne).</p></div>'
            f'<div class="qr"><img src="{QR}" alt=""></div></div></div>')


def napis_html(kicker, tekst):
    k = f'<p class="k">{esc(kicker)}</p>' if kicker else ""
    return f'<div class="bar">{k}<p class="x">{esc(tekst)}</p></div>'


def renderuj(jobs):
    """jobs: [(plik.png, body_html, przezroczyste)] → PNG 1920×1080."""
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page(viewport={"width": 1920, "height": 1080})
        src = TMP / "_render.html"  # plik, nie set_content: z about:blank Chromium nie wczyta fontów i logo z file://
        for path, body, transparent in jobs:
            bg = "transparent" if transparent else "#FBF6EE"
            src.write_text(f"<html><head><meta charset=utf-8><style>{CSS} body{{background:{bg}}}</style></head>"
                           f"<body>{body}</body></html>", encoding="utf-8")
            page.goto(src.as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(60)
            page.screenshot(path=str(path), omit_background=transparent)
        br.close()


def run(args):
    subprocess.run([C.FF, "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def sekundy(path):
    out = subprocess.run([C.FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    h, m, s = out.split("Duration: ")[1].split(",")[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def ts(sec, sep=","):
    ms = int(round(sec * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}"


def os_czasu(nagr):
    """Kolejność, długości i przejścia → [(scena, start w filmie, długość, przejście przed)]."""
    po_id = {s["id"]: s for s in nagr["sceny"]}
    plan, t = [], 0.0
    for i, s in enumerate(SCENY):
        sid = s["id"]
        if sid in PLANSZA:
            dl = C.dlugosc_sceny(sid) + PLANSZA[sid]
            ciagla = False
        else:
            n = po_id[sid]
            dl = (n["koniec"] - n["start"]) / FPS
            ciagla = n["ciagla"]
        d = 0.0 if i == 0 or ciagla else (0.6 if sid in PLANSZA or SCENY[i - 1]["id"] in PLANSZA else PRZENIKANIE)
        start = t - d
        plan.append({"id": sid, "start": round(start, 3), "dl": round(dl, 3), "przejscie": d})
        t = start + dl
    return plan, t


def main():
    nagr = json.loads((OUT / "sceny.json").read_text(encoding="utf-8"))
    assert nagr["fps"] == FPS
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    plan, total = os_czasu(nagr)
    assert total <= LIMIT, f"film za długi: {total:.1f} s"

    # napisy: (początek, koniec, kicker, tekst) w czasie filmu; na planszach bez paska (tekst jest na planszy)
    napisy = []
    for p in plan:
        s = C.PO_ID[p["id"]]
        for tekst, a, b in C.napisy(p["id"]):
            napisy.append((p["start"] + a, p["start"] + b, s["podpis"], tekst, p["id"] in PLANSZA))
    jobs = [(TMP / "tytul.png", tytul_html(), False), (TMP / "koniec.png", koniec_html(), False),
            (TMP / "pusty.png", "", True)]
    jobs += [(TMP / f"napis-{i:02d}.png", napis_html(k, x), True) for i, (_, _, k, x, plansza) in enumerate(napisy)
             if not plansza]
    renderuj(jobs)

    # ścieżka napisów: lista PNG z czasami (concat demuxer) – jedna nakładka zamiast kilkudziesięciu
    lista, t = [], 0.0
    for i, (a, b, _, _, plansza) in enumerate(napisy):
        if plansza:
            continue
        if a > t:
            lista += [f"file '{TMP / 'pusty.png'}'", f"duration {a - t:.3f}"]
        lista += [f"file '{TMP / f'napis-{i:02d}.png'}'", f"duration {b - a:.3f}"]
        t = b
    lista += [f"file '{TMP / 'pusty.png'}'", f"duration {max(0.1, total - t):.3f}", f"file '{TMP / 'pusty.png'}'"]
    (TMP / "napisy.txt").write_text("\n".join(lista) + "\n", encoding="utf-8")

    # obraz: sceny z nagrania (trim po klatkach) i plansze, łączone przenikaniem albo wprost
    nagranie = str(OUT / "nagranie.mp4")
    wej = ["-i", nagranie,
           "-loop", "1", "-framerate", str(FPS), "-t", f"{plan[0]['dl']:.3f}", "-i", str(TMP / "tytul.png"),
           "-loop", "1", "-framerate", str(FPS), "-t", f"{plan[-1]['dl']:.3f}", "-i", str(TMP / "koniec.png"),
           "-f", "concat", "-safe", "0", "-i", str(TMP / "napisy.txt")]
    po_id = {s["id"]: s for s in nagr["sceny"]}
    nagrane = [p for p in plan if p["id"] not in PLANSZA]
    f = [f"[0:v]split={len(nagrane)}" + "".join(f"[r{i}]" for i in range(len(nagrane)))]
    klipy = []
    for i, p in enumerate(nagrane):
        n = po_id[p["id"]]
        f.append(f"[r{i}]trim=start_frame={n['start']}:end_frame={n['koniec']},setpts=PTS-STARTPTS,"
                 f"fps={FPS},format=yuv420p,settb=AVTB[c{i}]")
    f.append(f"[1:v]fps={FPS},format=yuv420p,settb=AVTB[tytul]")
    f.append(f"[2:v]fps={FPS},format=yuv420p,settb=AVTB[koniec]")
    nr = 0
    for p in plan:
        klipy.append("tytul" if p["id"] == "00-tytul" else "koniec" if p["id"] == "14-koniec" else f"c{nr}")
        nr += p["id"] not in PLANSZA
    cur, dl = klipy[0], plan[0]["dl"]
    for i in range(1, len(plan)):
        p, nxt, out = plan[i], klipy[i], f"v{i}"
        if p["przejscie"] > 0:
            f.append(f"[{cur}][{nxt}]xfade=transition=fade:duration={p['przejscie']}:offset={dl - p['przejscie']:.3f}[{out}]")
            dl += p["dl"] - p["przejscie"]
        else:
            f.append(f"[{cur}][{nxt}]concat=n=2:v=1:a=0[{out}]")
            dl += p["dl"]
        cur = out
    f.append(f"[3:v]fps={FPS},format=rgba[sub]")
    f.append(f"[{cur}][sub]overlay=0:0:shortest=0:eof_action=pass,format=yuv420p,"
             f"fade=t=in:st=0:d=0.5,fade=t=out:st={total - 0.8:.3f}:d=0.8[v]")

    # dźwięk: każda kwestia na swoim miejscu (start sceny + wejście), lekko przyspieszona TEMPO, głośność –16 LUFS
    for i, p in enumerate(plan):
        wej += ["-i", str(C.LEKTOR / f"{p['id']}.mp3")]
        ms = int(round((p["start"] + C.WEJSCIE) * 1000))
        f.append(f"[{4 + i}:a]aresample=48000,atempo={C.TEMPO},adelay=delays={ms}:all=1,aformat=channel_layouts=stereo[a{i}]")
    f.append("".join(f"[a{i}]" for i in range(len(plan))) + f"amix=inputs={len(plan)}:normalize=0,"
             f"loudnorm=I=-16:TP=-1.5:LRA=11,apad,atrim=0:{total:.3f}[a]")
    run([*wej, "-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart",
         "-metadata", "title=HugMe – film demo (3 min)", "-metadata:s:a:0", "language=pol", str(FINAL)])

    dlugosc = sekundy(FINAL)
    assert dlugosc <= LIMIT + 0.05, f"film za długi: {dlugosc:.2f} s"
    SRT.write_text("\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{x}\n" for i, (a, b, _, x, _) in enumerate(napisy, 1)),
                   encoding="utf-8")
    (OUT / "os_czasu.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    scenariusz(plan, dlugosc)
    print(f"gotowe: {FINAL.relative_to(ROOT)} – {dlugosc:.2f} s, {FINAL.stat().st_size / 1e6:.1f} MB")
    for p in plan:
        print(f"  {ts(p['start'], '.')[3:10]}  {p['id']:15} {p['dl']:5.1f} s")


def scenariusz(plan, dlugosc):
    """docs/SCENARIUSZ_FILMU.md – tabela z rzeczywistymi czasami z montażu, tekst lektora = napisy."""
    m, s = divmod(round(dlugosc), 60)
    w = ["# Scenariusz filmu HugMe (3 minuty)", "",
         f"**Film:** [docs/film/hugme-film.mp4](film/hugme-film.mp4) – {m}:{s:02d}, 1920×1080, 30 kl./s, polski lektor "
         "i wtopione napisy; osobno napisy [hugme-film.srt](film/hugme-film.srt). "
         "Do pobrania z GitHuba: otwórz plik i kliknij „Download raw file” (ikona strzałki).", "",
         "**Historia w jednym ciągu:** Anna, mama chłopca z zespołem Downa, opisuje problem → platforma ukrywa dane "
         "osobowe i dobiera sprawdzone rozwiązania z wyjaśnieniem → zgłoszenie trafia do koordynatorki Hubu ROPS, która "
         "łączy rodzinę z rozwiązaniem i odpowiada → moduł Razem z ZD i program „Jestem potrzebny” (Bartek pomaga "
         "w schronisku, dostaje odznakę) → mapa miejsc pracy → gmina dostaje kartę usługi z Pośrednika innowacji → "
         "Hub widzi trendy i luki → dostępność → plansza z linkami.", "",
         "| Czas | Scena | Co widać | Lektor (= napisy) |", "|---|---|---|---|"]
    for i, p in enumerate(plan):
        sc = C.PO_ID[p["id"]]
        koniec = plan[i + 1]["start"] if i + 1 < len(plan) else dlugosc
        czas = f"{ts(p['start'], '.')[4:8]}–{ts(koniec, '.')[4:8]}"
        nazwa = sc["podpis"] or ("Plansza tytułowa" if p["id"] == "00-tytul" else "Plansza końcowa")
        w.append(f"| {czas} | {nazwa} | {sc['ekran']} | „{sc['lektor']}” |")
    w += ["",
          "## Jak powstaje film",
          "",
          "Wszystko jest w repo i odtwarza się jedną komendą: `python demo/build_all.py` (albo krokami poniżej).",
          "",
          "1. **Scenariusz** – `demo/film_sceny.py`: dla każdej sceny konto demo, podpis, opis ekranu, tekst lektora "
          "i jego zapis fonetyczny dla syntezatora („HugMe” czytamy po angielsku: „hag‑mi”).",
          "2. **Lektor** – `demo/film_lektor/*.mp3`: ElevenLabs (model eleven_multilingual_v2, głos „Arleta – Calm "
          "Instructor”), jedna kwestia na scenę. `slowa.json` to czasy każdego słowa z transkrypcji (ElevenLabs Scribe) – "
          "z nich liczone są napisy i chwile kliknięć.",
          "3. **Nagranie** – `python demo/film_nagraj.py`: Playwright na świeżej bazie, okno 1920×1080 z powiększeniem "
          "125%, zapis klatek przez CDP (ostry tekst). Akcje są przypięte do słów lektora (np. klik „Połącz” na słowie "
          "„łączy”), a scena trwa co najmniej tyle, ile jej kwestia – dlatego nic nie jest ucięte ani przyspieszone. "
          "Konta przełączamy w tle, więc w filmie nie ma ekranu wyboru konta.",
          "4. **Montaż** – `python demo/film_montaz.py`: plansze, przenikania 0,4 s między ekranami, lektor "
          f"(tempo ×{C.TEMPO}, głośność −16 LUFS), napisy co do słowa; sprawdza limit 3:00 i zapisuje ten plik.",
          "",
          "**Dlaczego nowa wersja:** poprzednie filmy powstawały w pośpiechu – nagranie było przyspieszane do "
          "zadanej długości, a lektor dopasowywany do scen „na sztywno”, przez co kwestie się urywały, w ścieżce były "
          "kilkunastosekundowe dziury, a napisy nie pasowały do obrazu. Teraz to lektor wyznacza rytm obrazu.",
          ""]
    DOC.write_text("\n".join(w), encoding="utf-8")


if __name__ == "__main__":
    main()
