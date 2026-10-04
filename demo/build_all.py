"""Odtwarza wszystkie materiały jedną komendą: python demo/build_all.py [--root <kopia repo>]

zrzuty.py → pdf.py (prezentacja_hugme.pdf) → nagraj.py → montaz.py (demo_hugme.mp4, bez dźwięku)
→ lektor.py (demo_hugme_lektor.mp4 z głosem ElevenLabs; pomijany bez klucza i nagrań w cache). Przerywa przy błędzie.
--root ustawia HUGME_ROOT: kod aplikacji do zrzutów i nagrań (domyślnie bieżące repo)."""
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

for script in ("zrzuty.py", "pdf.py", "nagraj.py", "montaz.py"):
    print(f"== {script}", flush=True)
    if subprocess.run([sys.executable, str(HERE / script)], env=env).returncode:
        sys.exit(f"Błąd w {script} – przerywam.")
print("== lektor.py", flush=True)
if subprocess.run([sys.executable, str(HERE / "lektor.py")], env=env).returncode:
    print("Lektor pominięty – film bez głosu: demo/out/demo_hugme.mp4")
print("Gotowe:", HERE / "out" / "prezentacja_hugme.pdf", "i", HERE / "out" / "demo_hugme_lektor.mp4")
