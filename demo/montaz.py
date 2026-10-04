"""Montaż filmu demo: plansze + 2 scenariusze z podpisami kroków → demo/out/demo_hugme.mp4 (H.264, 1920×1080, 30 fps).

Czyta demo/out/kroki.json z nagraj.py. Napisy i plansze to PNG z HTML (Playwright, Atkinson Hyperlegible – polskie
znaki bez kombinowania z drawtext), nakładane ffmpeg overlay z enable='between(t,a,b)'. Bez dźwięku."""
import html
import json
import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "out"
TMP = OUT / "montaz"
FINAL = OUT / "demo_hugme.mp4"
COPY = ROOT / "docs" / "film" / "hugme-scenariusze.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()
LIMIT = 90.0  # właściciel: max 1:30 (twardy limit zadania 120 s)
CARD = {"tytul": 3.0, "s2": 2.0, "koniec": 3.0}
SCEN = {"scenariusz1": "Scenariusz 1 · Rodzic osoby z zespołem Downa – „Jestem potrzebny”",
        "scenariusz2": "Scenariusz 2 · Gmina → Hub ROPS: od problemu do karty usługi"}

FONTS = (ROOT / "app" / "static" / "fonts").as_uri()
LOGO = (ROOT / "app" / "static" / "img" / "logo.svg").as_uri()
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
.card {{ background: #FBF6EE; color: #1B2540; height: 100%; display: flex; flex-direction: column;
        justify-content: center; padding: 0 180px; gap: 28px; }}
.card img {{ width: 120px; }}
.k {{ color: #B8432F; font-weight: 700; font-size: 34px; letter-spacing: .06em; text-transform: uppercase; }}
.t {{ font-size: 104px; font-weight: 700; line-height: 1.05; }}
.s {{ font-size: 44px; color: #3d4660; max-width: 1400px; line-height: 1.3; white-space: pre-line; }}
.m {{ font-size: 34px; color: #1D6B52; font-weight: 700; }}
.bar {{ position: absolute; left: 0; right: 0; bottom: 0; background: rgba(27,37,64,.94); color: #fff;
       padding: 22px 64px 28px; border-top: 6px solid #B8432F; }}
.bar .k {{ font-size: 24px; color: #F2B8A8; margin-bottom: 6px; }}
.bar .x {{ font-size: 44px; font-weight: 700; line-height: 1.2; }}
"""


def esc(s):
    return html.escape(s)


def plansza(kicker, title, sub, meta=""):
    return (f'<div class="card"><img src="{LOGO}" alt=""><p class="k">{esc(kicker)}</p><p class="t">{esc(title)}</p>'
            f'<p class="s">{esc(sub)}</p>{f"<p class=m>{esc(meta)}</p>" if meta else ""}</div>')


def renderuj(jobs):
    """jobs: [(plik.png, body_html, przezroczyste)] → PNG 1920×1080."""
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page(viewport={"width": 1920, "height": 1080})
        for path, body, transparent in jobs:
            bg = "transparent" if transparent else "#FBF6EE"
            src = TMP / "_render.html"  # plik, nie set_content: z about:blank Chromium nie wczyta fontów i logo z file://
            src.write_text(f"<html><head><meta charset=utf-8><style>{CSS} body{{background:{bg}}}</style></head>"
                           f"<body>{body}</body></html>", encoding="utf-8")
            page.goto(src.as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(100)
            page.screenshot(path=str(path), omit_background=transparent)
        br.close()


def keep_segments(s):
    """Fragmenty nagrania do zostawienia: [start, end] minus wycięte logowania."""
    segs, cur = [], s["start"]
    for a, b in sorted(s["cuts"]):
        if b <= cur:
            continue
        if a > cur:
            segs.append((cur, a))
        cur = max(cur, b)
    segs.append((cur, s["end"]))
    return [(a, b) for a, b in segs if b - a > 0.1]


def remap(t, segs):
    """Czas w nagraniu → czas w zmontowanym klipie."""
    out = 0.0
    for a, b in segs:
        if t <= a:
            return out
        if t < b:
            return out + t - a
        out += b - a
    return out


def run(args):
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "24", "-pix_fmt", "yuv420p", "-r", "30"]


def klip(name, s, speed):
    segs = keep_segments(s)
    dur = sum(b - a for a, b in segs)
    steps = [(remap(t, segs), txt) for t, txt in s["steps"]]
    pngs = []
    for i, (t, txt) in enumerate(steps):
        a = 0.0 if i == 0 else t
        b = steps[i + 1][0] if i + 1 < len(steps) else dur + 1
        pngs.append((TMP / f"{name}-{i}.png", a / speed, b / speed,
                     f'<div class="bar"><p class="k">{esc(SCEN[name])}</p><p class="x">{esc(txt)}</p></div>'))
    renderuj([(p, body, True) for p, _, _, body in pngs])
    f = [f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]" for i, (a, b) in enumerate(segs)]
    f.append("".join(f"[v{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0,"
             f"setpts=PTS/{speed},fps=30,scale=1920:1080,setsar=1[b0]")
    for i, (_, a, b, _) in enumerate(pngs):
        f.append(f"[b{i}][{i + 1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[b{i + 1}]")
    inputs = ["-i", s["video"]]
    for p, *_ in pngs:
        inputs += ["-i", str(p)]
    dst = TMP / f"{name}.mp4"
    run([*inputs, "-filter_complex", ";".join(f), "-map", f"[b{len(pngs)}]", "-an", *ENC, str(dst)])
    return dst, dur / speed, [(round(a, 1), txt) for (_, a, _, _), (_, txt) in zip(pngs, steps)]


def sekundy(path):
    return imageio_ffmpeg.count_frames_and_secs(str(path))[1]


def main():
    data = json.loads((OUT / "kroki.json").read_text(encoding="utf-8"))
    for s in data.values():
        # webm zaczyna się od pierwszej klatki, chwilę po zegarze nagraj.py – przesuń znaczniki o zmierzoną różnicę
        off = max(0.0, s["end"] - sekundy(s["video"]))
        s["start"], s["end"] = max(0.0, s["start"] - off), s["end"] - off
        s["cuts"] = [[a - off, b - off] for a, b in s["cuts"]]
        s["steps"] = [[max(0.0, t - off), txt] for t, txt in s["steps"]]
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    raw = sum(sum(b - a for a, b in keep_segments(s)) for s in data.values()) + sum(CARD.values())
    # ponytail: jedno globalne tempo dla obu scenariuszy; maks. 1,25× – dłuższe nagranie trzeba skrócić w nagraj.py
    speed = min(1.25, max(1.0, raw / (LIMIT - 0.5)))
    renderuj([
        (TMP / "tytul.png", plansza("HackYeah 2026 · HubMi.pl · ROPS Kraków", "HugMe – demo",
                                     "Twój problem nie zostaje sam: mieszkaniec, gmina i Hub w jednym miejscu.",
                                     "2 scenariusze · dane przykładowe"), False),
        (TMP / "s2.png", plansza("Scenariusz 2", "Gmina → Hub ROPS",
                                  "Od opisu problemu do karty usługi i trendów potrzeb."), False),
        (TMP / "koniec.png", plansza("Dziękujemy", "HugMe",
                                      "Demo: hugme.twapp.pl\nRepo: github.com/TomaszWu14/hugme",
                                      "Tomasz Wierzbowski · 4.10.2026"), False),
    ])
    s1, d1, k1 = klip("scenariusz1", data["scenariusz1"], speed)
    s2, d2, k2 = klip("scenariusz2", data["scenariusz2"], speed)
    parts = [("-loop", "1", "-t", str(CARD["tytul"]), "-i", str(TMP / "tytul.png")), ("-i", str(s1)),
             ("-loop", "1", "-t", str(CARD["s2"]), "-i", str(TMP / "s2.png")), ("-i", str(s2)),
             ("-loop", "1", "-t", str(CARD["koniec"]), "-i", str(TMP / "koniec.png"))]
    args = [x for p in parts for x in p]
    norm = ";".join(f"[{i}:v]fps=30,scale=1920:1080,setsar=1,format=yuv420p[n{i}]" for i in range(5))
    args += ["-filter_complex", norm + ";" + "".join(f"[n{i}]" for i in range(5)) + "concat=n=5:v=1:a=0[v]",
             "-map", "[v]", "-an", *ENC, "-movflags", "+faststart", str(FINAL)]
    run(args)
    total = sekundy(FINAL)
    assert total <= 120, f"film za długi: {total:.1f} s"
    COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FINAL, COPY)
    print(f"tempo {speed:.2f}x | scenariusz 1: {d1:.1f} s | scenariusz 2: {d2:.1f} s | razem {total:.2f} s | "
          f"{FINAL.stat().st_size / 1e6:.1f} MB")
    t1, t2 = CARD["tytul"], CARD["tytul"] + d1 + CARD["s2"]
    for off, ks in ((t1, k1), (t2, k2)):
        for a, txt in ks:
            print(f"  {off + a:5.1f} s  {txt}")
    # oś czasu dla lektora (demo/lektor.py): kiedy w gotowym filmie pojawia się każdy podpis i plansza
    (OUT / "os_czasu.json").write_text(json.dumps({
        "razem": total, "s2": t1 + d1, "koniec": t2 + d2,
        "scenariusz1": [[round(t1 + a, 2), txt] for a, txt in k1],
        "scenariusz2": [[round(t2 + a, 2), txt] for a, txt in k2],
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    if total > LIMIT:
        print(f"UWAGA: {total:.1f} s > {LIMIT} s – skróć pauzy w nagraj.py")


if __name__ == "__main__":
    main()
