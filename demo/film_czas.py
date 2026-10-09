"""Czasy lektora filmu: długości nagrań, słowa z czasami i napisy – wspólne dla film_nagraj.py i film_montaz.py.

Słowa z czasami są w film_lektor/slowa.json (transkrypcja ElevenLabs Scribe nagrań z film_lektor/*.mp3, tokeny
z tekstu „wymowa”). Wszystkie czasy zwracane tu są w sekundach od początku sceny i już po przyspieszeniu TEMPO:
scena = WEJSCIE (cisza na wejście obrazu) + mowa + ODDECH (cisza przed następną sceną)."""
import difflib
import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path

import imageio_ffmpeg

from film_sceny import SCENY

HERE = Path(__file__).resolve().parent
LEKTOR = HERE / "film_lektor"
FF = imageio_ffmpeg.get_ffmpeg_exe()

TEMPO = 1.04     # lektor odrobinę szybciej (atempo, bez zmiany barwy), żeby film zmieścił się w 3:00
WEJSCIE = 0.5    # s od początku sceny do pierwszego słowa
ODDECH = 0.8     # s ciszy po ostatnim słowie sceny
MAKS_NAPIS = 84  # znaków w jednym napisie (1–2 wiersze)

PO_ID = {s["id"]: s for s in SCENY}


@lru_cache(None)
def _slowa_json():
    return json.loads((LEKTOR / "slowa.json").read_text(encoding="utf-8"))


@lru_cache(None)
def dlugosc_pliku(sid):
    """Długość nagrania lektora w sekundach (dekodowana, bez przyspieszenia)."""
    err = subprocess.run([FF, "-hide_banner", "-i", str(LEKTOR / f"{sid}.mp3"), "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    h, m, s = re.findall(r"time=(\d+):(\d+):([\d.]+)", err)[-1]
    return int(h) * 3600 + int(m) * 60 + float(s)


def slowa(sid):
    """[(słowo, początek, koniec)] względem początku sceny."""
    return [(t, WEJSCIE + a / TEMPO, WEJSCIE + b / TEMPO) for t, a, b in _slowa_json()[sid]]


def koniec_mowy(sid):
    return slowa(sid)[-1][2]


def dlugosc_sceny(sid):
    """Najkrótsza długość sceny: wejście + cała kwestia + oddech."""
    return WEJSCIE + dlugosc_pliku(sid) / TEMPO + ODDECH


def _norm(t):
    return re.sub(r"[^\wąćęłńóśźż]", "", t.lower())


def slowo(sid, tekst, nr=0):
    """Początek nr-tego wystąpienia słowa (bez wielkości liter i interpunkcji) – do zgrania akcji z lektorem."""
    hits = [a for t, a, _ in slowa(sid) if _norm(t) == _norm(tekst)]
    if len(hits) <= nr:
        raise KeyError(f"{sid}: brak słowa „{tekst}” w lektorze")
    return hits[nr]


def _kawalki(zdanie):
    """Dzieli zdanie na napisy do MAKS_NAPIS znaków – po myślniku, dwukropku albo przecinku najbliżej środka."""
    if len(zdanie) <= MAKS_NAPIS:
        return [zdanie]
    ciecia = [m.end() for m in re.finditer(r"(?: –|:|,) ", zdanie)]
    if not ciecia:
        return [zdanie]
    srodek = len(zdanie) / 2
    c = min(ciecia, key=lambda x: abs(x - srodek))
    return _kawalki(zdanie[:c].strip()) + _kawalki(zdanie[c:].strip())


def napisy(sid):
    """[(tekst, początek, koniec)] względem początku sceny: tekst z „lektor”, czasy ze słów transkrypcji."""
    tekst = PO_ID[sid]["lektor"]
    kaw = [k for z in re.split(r"(?<=[.!?])\s+", tekst) for k in _kawalki(z)]
    sl = slowa(sid)
    # tokeny napisu ↔ tokeny wymowy (różnią się np. „HugMe” ↔ „Hag mi”, „138” ↔ „stu trzydziestu ośmiu”)
    tok = [t for t in tekst.split() if _norm(t)]
    mapa = {}
    sm = difflib.SequenceMatcher(None, [_norm(t) for t in tok], [_norm(t) for t, _, _ in sl], autojunk=False)
    for _, i1, i2, j1, j2 in sm.get_opcodes():
        for k in range(i1, i2):
            mapa[k] = min(j1 + (k - i1), j2 - 1) if j2 > j1 else j1
    out, i = [], 0
    for k in kaw:
        n = len([t for t in k.split() if _norm(t)])
        out.append([k, sl[min(mapa.get(i, 0), len(sl) - 1)][1]])
        i += n
    wynik = []
    for j, (k, a) in enumerate(out):
        b = out[j + 1][1] if j + 1 < len(out) else koniec_mowy(sid) + 0.4
        wynik.append((k, round(a - 0.08, 2), round(b - 0.08, 2)))
    return wynik


if __name__ == "__main__":
    razem = 0.0
    for s in SCENY:
        d = dlugosc_sceny(s["id"])
        razem += d
        print(f"{s['id']:16} scena ≥ {d:5.2f} s")
        for k, a, b in napisy(s["id"]):
            print(f"    {a:5.2f}–{b:5.2f}  {k}")
    print(f"razem (bez nadwyżek akcji i przenikań): {razem:.1f} s")
