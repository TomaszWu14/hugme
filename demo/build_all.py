"""Odtwarza wszystkie materiały jedną komendą: python demo/build_all.py [--root <kopia repo>]

zrzuty.py → pdf.py (prezentacja_hugme.pdf) → film_nagraj.py (nagranie scen) → film_montaz.py
(docs/film/hugme-film.mp4 z lektorem i napisami, docs/film/hugme-film.srt, docs/SCENARIUSZ_FILMU.md).
Lektor jest już w repo (demo/film_lektor/) – film powstaje bez klucza ElevenLabs. Wymaga: pip install imageio-ffmpeg.
Przerywa przy błędzie. --root ustawia HUGME_ROOT: kod aplikacji do zrzutów i nagrań (domyślnie bieżące repo)."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

parser = argparse.ArgumentParser()
parser.add_argument("--root", help="katalog z kodem aplikacji (HUGME_ROOT)")
args = parser.parse_args()
env = dict(os.environ)
if args.root:
    env["HUGME_ROOT"] = str(Path(args.root).resolve())

for script in ("zrzuty.py", "pdf.py", "film_nagraj.py", "film_montaz.py"):
    print(f"== {script}", flush=True)
    if subprocess.run([sys.executable, str(HERE / script)], env=env, cwd=HERE).returncode:
        sys.exit(f"Błąd w {script} – przerywam.")
print("Gotowe:", HERE / "out" / "prezentacja_hugme.pdf", "i", HERE.parent / "docs" / "film" / "hugme-film.mp4")
