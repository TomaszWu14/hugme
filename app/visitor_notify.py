"""Powiadomienie push (ntfy) dla właściciela o nowym odwiedzającym demo. Bez NTFY_URL – nic (zero ruchu sieciowego).
Wysyłka w wątku w tle, żeby nie opóźniać odpowiedzi dla gościa; każdy błąd to tylko ostrzeżenie w logu.
Firma z listy NTFY_WATCH_COMPANIES (frazy po przecinku, tylko w env) daje push pilny."""
import logging
import os
import threading
import unicodedata
import urllib.request

APP = "hugme"
TIMEOUT = 5
MAX_BODY = 300
MIN_PHRASE = 2
log = logging.getLogger(__name__)


def _send(url, body, token, title="", tags="bell", priority="high"):
    headers = {"Content-Type": "text/plain; charset=utf-8", "Title": title or f"Nowy gosc: {APP}", "Tags": tags,
               "Priority": priority}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
    try:
        # schemat ograniczony do http(s) w _push; URL z konfiguracji operatora
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # nosec B310
            resp.read()
    except Exception as exc:  # noqa: BLE001 – powiadomienie jest dodatkiem, nigdy nie psuje wejścia gościa
        log.warning("Powiadomienie ntfy nie wysłane: %s", exc)


def normalize(text):
    """Do porównań: bez wielkości liter i znaków diakrytycznych (NFKD; „ł” → „l”), pojedyncze spacje."""
    text = unicodedata.normalize("NFKD", (text or "").casefold().replace("ł", "l"))
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


def watched(company):
    """Czy firma gościa zawiera którąś z fraz NTFY_WATCH_COMPANIES (po normalizacji, frazy min. 2 znaki)."""
    name = normalize(company)
    phrases = (normalize(p) for p in os.environ.get("NTFY_WATCH_COMPANIES", "").split(","))
    return any(len(p) >= MIN_PHRASE and p in name for p in phrases)


def _push(body, title, tags, priority):
    url = os.environ.get("NTFY_URL", "").strip()
    if not url:
        return
    if not url.lower().startswith(("https://", "http://")):
        log.warning("NTFY_URL pominięty: dozwolone tylko adresy http(s)")
        return
    args = (url, body[:MAX_BODY], os.environ.get("NTFY_TOKEN", "").strip(), title, tags, priority)
    try:
        threading.Thread(target=_send, args=args, daemon=True).start()
    except RuntimeError as exc:  # np. brak możliwości uruchomienia wątku
        log.warning("Powiadomienie ntfy nie wysłane: %s", exc)


def notify_visitor(first_name, last_name, company):
    """Wysyła w tle „{imię} {nazwisko} ({firma}) wszedł do hugme” na NTFY_URL; bez NTFY_URL nic nie robi."""
    body = f"{first_name} {last_name} ({company}) wszedł do {APP}"
    if watched(company):
        _push(f"⚠️ {body}", f"UWAGA firma z listy: {APP}", "rotating_light", "urgent")
    else:
        _push(body, f"Nowy gosc: {APP}", "bell", "high")


def notify_engaged(first_name, last_name, company, views):
    """Jeden push, gdy gość obejrzał NTFY_ENGAGED_VIEWS ekranów; firma z listy – priorytet pilny."""
    body = f"{first_name} {last_name} ({company}) obejrzał już {views} ekranów w {APP}"
    _push(body, f"Gosc oglada demo: {APP}", "eyes", "urgent" if watched(company) else "default")
