"""Lektor do filmu scenariuszy: ElevenLabs (eleven_multilingual_v2, polski) → ścieżka dźwiękowa → demo_hugme_lektor.mp4.

Klucz: ELEVENLABS_API_KEY w środowisku albo w pliku .env w katalogu repo (nie trafia do repo – .env jest w .gitignore).
Głos: ELEVENLABS_VOICE_ID (opcjonalnie); bez niego skrypt wybiera z Twoich głosów polski, a jeśli go nie ma – pierwszy.
Nagrania trafiają do demo/out/lektor/ (cache po treści) – ponowne uruchomienie bez zmian w tekście nie zużywa znaków.

Uruchom po montaz.py:  python demo/lektor.py"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "demo" / "out"
CACHE = OUT / "lektor"
SRC = OUT / "demo_hugme.mp4"
DST = OUT / "demo_hugme_lektor.mp4"
COPY = ROOT / "docs" / "film" / "hugme-scenariusze.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()
MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
API = "https://api.elevenlabs.io/v1"

# (kotwica, tekst): kotwica = "tytul" | "s2" | "koniec" | ("scenariusz1", nr podpisu) – lektor zaczyna razem z podpisem,
# a gdy poprzednia kwestia jeszcze trwa – zaraz po niej.
LINIE = [
    ("tytul", "HugMe. Twój problem nie zostaje sam."),
    (("scenariusz1", 0), "Mama zgłasza syna z zespołem Downa do programu „Jestem potrzebny”: lubi psy i ma czas w weekend rano."),
    (("scenariusz1", 1), "Formularz nie pyta o diagnozę ani o datę urodzenia – tylko o to, co lubi i kiedy może."),
    (("scenariusz1", 2), "Zgłoszenie trafia do Hubu."),
    (("scenariusz1", 3), "Koordynatorka widzi gotową parę: Franek i schronisko w Wadowicach. Jedno kliknięcie – połącz."),
    (("scenariusz1", 5), "Mama od razu dostaje powiadomienie, a w dzienniczku czeka pierwsza misja."),
    (("scenariusz1", 7), "Dalej – mapa miejsc pracy dla osób z zespołem Downa."),
    ("s2", "Scenariusz drugi: gmina."),
    (("scenariusz2", 0), "Urzędnik gminy opisuje problem własnymi słowami: seniorzy z pięciu sołectw nie mają jak dojechać do lekarza."),
    (("scenariusz2", 1), "Bus na Telefon – bardzo pasuje. Widać też, dlaczego."),
    (("scenariusz2", 4), "Pośrednik od razu przygotowuje kartę usługi dla gminy – gotową do wydruku."),
    (("scenariusz2", 6), "Koordynatorka Hubu widzi zgłoszenie w skrzynce, a w trendach – gdzie brakuje rozwiązań."),
    ("koniec", "HugMe. Mieszkaniec, gmina i Hub – w jednym miejscu."),
]


def klucz():
    k = os.environ.get("ELEVENLABS_API_KEY")
    env = ROOT / ".env"
    if not k and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*ELEVENLABS_API_KEY\s*=\s*['\"]?([^'\"\s]+)", line)
            if m:
                k = m.group(1)
    return k


def zapytanie(path, key, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body else None,
                                 headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "*/*"},
                                 method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def glos(key):
    if os.environ.get("ELEVENLABS_VOICE_ID"):
        return os.environ["ELEVENLABS_VOICE_ID"], "z ELEVENLABS_VOICE_ID"
    voices = json.loads(zapytanie("/voices", key))["voices"]
    pl = [v for v in voices if "pol" in json.dumps(v.get("labels", {})).lower()
          or any(x.get("language") == "pl" for x in v.get("verified_languages") or [])]
    v = (pl or voices)[0]
    return v["voice_id"], v["name"]


def sekundy(path):
    err = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def main():
    os_czasu = json.loads((OUT / "os_czasu.json").read_text(encoding="utf-8"))
    CACHE.mkdir(parents=True, exist_ok=True)
    key, plik_glosu = klucz(), CACHE / "glos.txt"
    voice = os.environ.get("ELEVENLABS_VOICE_ID") or (plik_glosu.read_text().strip() if plik_glosu.exists() else "")
    plan, kon = [], 0.0
    for kotwica, tekst in LINIE:
        t = (0.3 if kotwica == "tytul" else os_czasu[kotwica] + 0.2) if isinstance(kotwica, str)             else os_czasu[kotwica[0]][kotwica[1]][0]
        if not voice:
            if not key:
                sys.exit("Brak ELEVENLABS_API_KEY (środowisko albo .env) – dopisz klucz do .env.")
            voice, name = glos(key)
            plik_glosu.write_text(voice)
            print(f"głos: {name} ({voice})")
        plik = CACHE / f"{hashlib.sha1(f'{voice}|{MODEL}|{tekst}'.encode()).hexdigest()[:16]}.mp3"
        if not plik.exists():
            if not key:
                sys.exit(f"Brak nagrania w cache i brak ELEVENLABS_API_KEY: {tekst[:40]}…")
            plik.write_bytes(zapytanie(f"/text-to-speech/{voice}?output_format=mp3_44100_128", key, {
                "text": tekst, "model_id": MODEL, "language_code": "pl",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.15, "speed": 1.0}}))
        start = max(t, kon + 0.25)
        kon = start + sekundy(plik)
        plan.append((start, plik, tekst, start - t))
    for start, _, tekst, przes in plan:
        print(f"{start:6.2f} s{'' if przes < 0.05 else f'  (+{przes:.1f} s)'}  {tekst}")
    film = sekundy(SRC)
    dogrywka = max(0.0, kon + 0.4 - film)  # ostatnia plansza trwa, dopóki lektor nie skończy
    wej = ["-i", str(SRC)] + [x for _, p, _, _ in plan for x in ("-i", str(p))]
    f = [f"[0:v]tpad=stop_mode=clone:stop_duration={dogrywka:.2f}[v]"]
    f += [f"[{i + 1}:a]adelay={int(s * 1000)}|{int(s * 1000)},volume=1.0[a{i}]" for i, (s, *_) in enumerate(plan)]
    f.append("".join(f"[a{i}]" for i in range(len(plan))) + f"amix=inputs={len(plan)}:normalize=0,apad[a]")
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", *wej, "-filter_complex", ";".join(f),
                    "-map", "[v]", "-map", "[a]", "-t", f"{film + dogrywka:.2f}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(DST)], check=True)
    total = sekundy(DST)
    assert total <= 120, f"film za długi: {total:.1f} s"
    COPY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DST, COPY)
    print(f"gotowe: {DST.name} – {total:.2f} s, {DST.stat().st_size / 1e6:.1f} MB (kopia: docs/film/{COPY.name})")


if __name__ == "__main__":
    main()
