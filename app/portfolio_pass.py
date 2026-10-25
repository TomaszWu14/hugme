"""Przepustka z portfolio: rekruter przedstawił się raz na portfolio (ciasteczko `gosc` na .twapp.pl), więc demo
nie pokazuje własnej bramki. Backend pyta portfolio (GET {PORTFOLIO_URL}/api/gosc, tylko kod statusu: 200 = ok).
PORTFOLIO_PASS=0 wyłącza; PORTFOLIO_URL musi zaczynać się od https://. Błąd, timeout, inny kod = brak przepustki."""
import hashlib
import logging
import os
import threading
import time
import urllib.error
import urllib.request

COOKIE = "gosc"
MAX_TOKEN = 200
TIMEOUT = 2
CACHE_SECONDS = 600
DEFAULT_URL = "https://portfolio.twapp.pl"
log = logging.getLogger(__name__)
_cache: dict[str, float] = {}  # sha256(token) -> kiedy wygasa (tylko wyniki pozytywne)
_lock = threading.Lock()


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def _base_url():
    """Adres portfolio albo None, gdy sprawdzanie wyłączone (PORTFOLIO_PASS=0 lub adres bez https://)."""
    if os.environ.get("PORTFOLIO_PASS") == "0":
        return None
    url = (os.environ.get("PORTFOLIO_URL") or DEFAULT_URL).rstrip("/")
    if not url.startswith("https://"):
        log.warning("PORTFOLIO_URL musi zaczynać się od https:// – sprawdzanie przepustki wyłączone.")
        return None
    return url


def _status(base, token):
    """Kod statusu odpowiedzi portfolio (bez przekierowań) albo None przy błędzie sieci. Wysyła tylko ciasteczko gosc."""
    req = urllib.request.Request(f"{base}/api/gosc", headers={"Cookie": f"{COOKIE}={token}"}, method="GET")
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=TIMEOUT) as resp:  # nosec B310 – https wymuszone w _base_url
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception as exc:  # noqa: BLE001 – przepustka jest dodatkiem, nigdy nie psuje żądania
        log.warning("Sprawdzenie przepustki portfolio nieudane: %s", type(exc).__name__)  # bez tokenu w logu
        return None


def valid(token):
    """True, gdy portfolio potwierdza token (200). Pusty/za długi token i wyłączona funkcja: bez ruchu sieciowego."""
    if not token or len(token) > MAX_TOKEN:
        return False
    base = _base_url()
    if base is None:
        return False
    key = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = time.monotonic()
    with _lock:
        if _cache.get(key, 0) > now:
            return True
    if _status(base, token) != 200:
        return False
    with _lock:
        _cache[key] = now + CACHE_SECONDS
        for k in [k for k, exp in _cache.items() if exp <= now]:
            del _cache[k]
    return True
