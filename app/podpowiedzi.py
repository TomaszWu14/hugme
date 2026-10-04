"""Tryb „Podpowiedzi”: chmurki „i” przy polach, filtrach i wskaźnikach oraz „Przewodnik po tej stronie”.

Wszystkie teksty są w app/podpowiedzi.json (klucze „ekran.element”). Preferencja to ciasteczko jak A+ i kontrast,
ale odwrócone: domyślnie włączone, `hints_off=1` wyłącza. Makra w templates/_podpowiedzi.html korzystają
z globalnych funkcji (działają też w makrach importowanych bez kontekstu)."""
import json
from functools import lru_cache
from pathlib import Path

from flask import current_app, request

PATH = Path(__file__).with_name("podpowiedzi.json")
COOKIE = "hints_off"


@lru_cache(maxsize=1)
def data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def hints_on():
    return request.cookies.get(COOKIE) != "1"


def entry(key):
    """Treść chmurki albo None, gdy podpowiedzi są wyłączone. W testach brak klucza = błąd (łapie literówki)."""
    item = data()["pola"].get(key)
    if item is None and current_app.testing:
        raise KeyError(f"Brak podpowiedzi „{key}” w app/podpowiedzi.json")
    return item if hints_on() else None


def steps():
    """Kroki przewodnika dla bieżącego widoku (endpoint Flask) – tylko przy włączonych podpowiedziach."""
    return data()["przewodnik"].get(request.endpoint or "", []) if hints_on() else []


def init(app):
    app.jinja_env.globals.update(podpowiedz=entry, podpowiedzi_wl=hints_on, przewodnik=steps)
