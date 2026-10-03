"""Opcjonalne AI (Claude). Działa tylko z kluczem ANTHROPIC_API_KEY; przy braku klucza, błędzie
albo przekroczeniu czasu zwraca None, a wywołujący używa wersji regułowej / szablonu.
Tekst trafia tu WYŁĄCZNIE po zamaskowaniu danych osobowych (core.privacy)."""
import json
import logging
import os
import re
from functools import lru_cache

log = logging.getLogger(__name__)

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")
TIMEOUT = 8.0

SYSTEM = (
    "Jesteś asystentem Małopolskiego Hubu Innowacji Społecznych (platforma HugMe). "
    "Piszesz po polsku, prostym językiem, ciepło i konkretnie – do mieszkańca, nie urzędowo. "
    "Nie wymyślasz kwot, nazwisk, adresów ani faktów, których nie znasz. "
    "Nie stawiasz diagnoz medycznych. Gdy czegoś nie wiesz – mówisz, gdzie zapytać."
)


def enabled():
    return bool(os.environ.get("ANTHROPIC_API_KEY")) and os.environ.get("AI_DISABLED") != "1"


@lru_cache(maxsize=1)
def _client():
    import anthropic
    return anthropic.Anthropic(timeout=TIMEOUT, max_retries=0)


@lru_cache(maxsize=256)  # ponytail: cache w pamięci procesu – oszczędza budżet przy powtórkach w demo
def ask(prompt, max_tokens=900):
    if not enabled():
        return None
    import anthropic
    try:
        resp = _client().messages.create(
            model=MODEL, max_tokens=max_tokens, system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIStatusError as e:
        log.warning("AI: błąd API %s", e.status_code)
        return None
    except anthropic.APIConnectionError:  # obejmuje też przekroczenie czasu
        log.warning("AI: brak połączenia / timeout")
        return None
    if resp.stop_reason == "refusal":
        return None
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    return text or None


def ask_json(prompt, max_tokens=900):
    """Prosi o JSON i parsuje pierwszy obiekt z odpowiedzi; None przy jakimkolwiek problemie."""
    text = ask(prompt + "\n\nOdpowiedz WYŁĄCZNIE poprawnym obiektem JSON, bez komentarzy.", max_tokens)
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    try:
        data = json.loads(m.group()) if m else None
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def easy_text(text):
    """Wersja w tekście łatwym do czytania (ETR): krótkie zdania, bez skrótów. None bez klucza/awarii."""
    prompt = ("Przepisz poniższy opis na tekst łatwy do czytania dla dorosłej osoby z niepełnosprawnością intelektualną: "
              "zdania do 8 słów, jedna myśl w zdaniu, czas teraźniejszy, forma „Ty”, bez skrótów i trudnych słów, "
              "maksymalnie 5 zdań. Odpowiedz samym tekstem.")
    return ask(prompt + chr(10) + chr(10) + text[:1500], max_tokens=300)
