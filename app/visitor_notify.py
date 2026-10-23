"""Powiadomienie push (ntfy) dla właściciela o nowym odwiedzającym demo. Bez NTFY_URL – nic (zero ruchu sieciowego).
Wysyłka w wątku w tle, żeby nie opóźniać odpowiedzi dla gościa; każdy błąd to tylko ostrzeżenie w logu."""
import logging
import os
import threading
import urllib.request

APP = "hugme"
TIMEOUT = 5
MAX_BODY = 300
log = logging.getLogger(__name__)


def _send(url, body, token):
    headers = {"Content-Type": "text/plain; charset=utf-8", "Title": f"Nowy gosc: {APP}", "Tags": "bell",
               "Priority": "high"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310 – adres z konfiguracji właściciela
            resp.read()
    except Exception as exc:  # powiadomienie jest dodatkiem – nigdy nie psuje wejścia gościa
        log.warning("Powiadomienie ntfy nie wysłane: %s", exc)


def notify_visitor(first_name, last_name, company):
    """Wysyła w tle „{imię} {nazwisko} ({firma}) wszedł do hugme” na NTFY_URL; bez NTFY_URL nic nie robi."""
    url = os.environ.get("NTFY_URL", "").strip()
    if not url:
        return
    body = f"{first_name} {last_name} ({company}) wszedł do {APP}"[:MAX_BODY]
    try:
        threading.Thread(target=_send, args=(url, body, os.environ.get("NTFY_TOKEN", "").strip()), daemon=True).start()
    except Exception as exc:
        log.warning("Powiadomienie ntfy nie wysłane: %s", exc)
