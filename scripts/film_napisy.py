"""Obróbka nagrania z scripts/film.py: przyspieszenie do <= 3 min, napisy PL z tekstu lektora, plansza końcowa.

Czasy napisów liczone z rzeczywistych startów scen (sceny.txt z film.py), tekst z docs/SCENARIUSZ_FILMU.md.
Uruchom:  python scripts/film_napisy.py <katalog_z_nagraniem> [audio.mp3|wav]
Wynik:    docs/film/lektor.srt, <katalog>/hugme-film.mp4 (z napisami; z głosem, gdy podasz plik audio)"""
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
TARGET = 179.0   # s – wymóg konkursu: do 3 minut
CARD = 4.0       # s planszy końcowej
MAX_CUE = 84     # znaków na napis (2 wiersze)
FF = imageio_ffmpeg.get_ffmpeg_exe()


def lektor_lines():
    rows = [r for r in (ROOT / "docs" / "SCENARIUSZ_FILMU.md").read_text(encoding="utf-8").splitlines()
            if re.match(r"\| \d:\d\d–", r)]
    return [r.split("|")[4].strip().strip("„”").replace("*", "") for r in rows]


def chunks(text):
    """Dzieli tekst sceny na napisy: najpierw po zdaniach, długie zdania po myślnikach i przecinkach."""
    out = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        parts, cur = re.split(r"(?<=[–,])\s+", sent), ""
        for part in parts:
            if cur and len(cur) + len(part) + 1 > MAX_CUE:
                out.append(cur)
                cur = part
            else:
                cur = f"{cur} {part}".strip()
        out.append(cur)
    return out


def ts(sec):
    ms = int(round(sec * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def build_srt(starts, end, factor):
    cues = []
    texts = lektor_lines()
    bounds = [s / factor for s in starts] + [end / factor]
    for i, text in enumerate(texts):
        a, b = bounds[i], bounds[i + 1] - 0.15
        parts = chunks(text)
        total = sum(len(p) for p in parts)
        t = a
        for p in parts:
            d = (b - a) * len(p) / total
            cues.append((t, t + d, p))
            t += d
    return "\n".join(f"{n}\n{ts(a)} --> {ts(b)}\n{t}\n" for n, (a, b, t) in enumerate(cues, 1))


def end_card(path):
    logo = (ROOT / "app" / "static" / "img" / "logo.svg").read_text(encoding="utf-8")
    html = f"""<html><body style="margin:0;width:1920px;height:1080px;background:#FBF6EE;color:#1B2540;
      font-family:'Segoe UI',Arial,sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px">
      <div style="width:220px;height:220px">{logo}</div>
      <div style="font-size:120px;font-weight:700;letter-spacing:-2px">HugMe</div>
      <div style="font-size:44px">Twój problem nie zostaje sam</div>
      <div style="font-size:52px;font-weight:700;color:#B8432F;margin-top:24px">hugme.twapp.pl</div>
      <div style="font-size:34px">github.com/TomaszWu14/hugme · platforma dla HubMi.pl</div></body></html>"""
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1920, "height": 1080})
        page.set_content(html)
        page.locator("svg").first.evaluate("e => { e.setAttribute('width', 220); e.setAttribute('height', 220); }")
        page.screenshot(path=str(path))
        b.close()


def duration(path):
    out = subprocess.run([FF, "-i", str(path)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def main(folder, audio=None):
    folder = Path(folder)
    raw = folder / "hugme-przeklikanie.mp4"
    marks = [float(line.split("\t")[1]) for line in (folder / "sceny.txt").read_text().splitlines() if line]
    raw_len = duration(raw)
    factor = raw_len / TARGET
    starts = [0.0] + marks[:-1]          # 12 scen: start 0 i znaczniki until() przed kolejnymi scenami
    srt = build_srt(starts, raw_len, factor)
    (ROOT / "docs" / "film" / "lektor.srt").write_text(srt, encoding="utf-8")
    (folder / "lektor.srt").write_text(srt, encoding="utf-8")
    end_card(folder / "plansza.png")
    style = ("FontName=Arial,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H10402519,BorderStyle=3,"
             "Outline=6,Shadow=0,MarginV=24")  # biały na granatowej ramce – czytelny na każdym tle
    graph = (f"[0:v]setpts=PTS/{factor:.5f},fps=25[v];[1:v]format=yuv420p[c];"
             f"[v][c]overlay=enable='gte(t,{TARGET - CARD})'[o];[o]subtitles=lektor.srt:force_style='{style}'[out]")
    cmd = [FF, "-y", "-loglevel", "error", "-i", raw.name, "-loop", "1", "-t", str(TARGET), "-i", "plansza.png"]
    if audio:
        cmd += ["-i", str(Path(audio).resolve())]
    cmd += ["-filter_complex", graph, "-map", "[out]"]
    cmd += ["-map", "2:a", "-c:a", "aac", "-b:a", "128k"] if audio else ["-an"]
    cmd += ["-t", str(TARGET), "-c:v", "libx264", "-preset", "medium", "-crf", "26", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "hugme-film.mp4"]
    subprocess.run(cmd, cwd=folder, check=True)
    print(f"factor {factor:.3f}, film: {folder / 'hugme-film.mp4'}, {duration(folder / 'hugme-film.mp4'):.1f} s")


if __name__ == "__main__":
    main(*sys.argv[1:])
