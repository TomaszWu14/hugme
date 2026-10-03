"""Wyszukiwanie w katalogu: innowacje, podobne zgłoszenia, materiały, eksperci.

Indeks budowany jest przy każdym zapytaniu z aktualnej bazy, więc edycja Biblioteki działa od razu.
ponytail: przebudowa O(n) na zapytanie – przy >5 tys. innowacji cache z unieważnianiem po edycji."""
from core import ai, db
from core.domain import AREAS
from core.match import Index, detect_area, innovation_text, topics_of
from data.slownik import TOPICS


def _pair(rows, results):
    by_id = {r["id"]: r for r in rows}
    return [(by_id[res.doc_id], res) for res in results]


def match_innovations(text, k=5):
    rows = db.query("SELECT * FROM innovations")
    return _pair(rows, Index([(r["id"], innovation_text(r)) for r in rows]).search(text, k))


def similar_reports(text, exclude_id=None, k=3):
    rows = db.query("SELECT * FROM reports WHERE approved = 1")
    idx = Index([(r["id"], r["body"]) for r in rows])
    return _pair(rows, idx.search(text, k, exclude={exclude_id}))


def match_materials(text, k=3):
    rows = db.query("SELECT * FROM materials")
    return _pair(rows, Index([(r["id"], f"{r['title']} {r['summary']} {r['body']}") for r in rows]).search(text, k))


def match_experts(text, k=3):
    rows = db.query("SELECT * FROM users WHERE role = 'ekspert'")
    docs = [(r["id"], " ".join([r["bio"]] + [AREAS[a]["name"] for a in r["areas"].split(",") if a in AREAS]))
            for r in rows]
    return _pair(rows, Index(docs).search(text, k))


def analyze(text):
    """Analiza opisu: obszar, tematy, ewentualnie streszczenie i dodatkowe słowa od AI.
    Zwraca dict z kluczem by_ai – UI zawsze oznacza treści od AI."""
    topics = [TOPICS[t][0] for t, _ in topics_of(text).most_common(4)]
    result = {"area": detect_area(text), "topics": topics, "summary": None, "keywords": [], "by_ai": False}
    data = ai.ask_json(
        "Mieszkaniec opisał problem społeczny (dane osobowe są już ukryte):\n"
        f"<opis>{text}</opis>\n\n"
        "Zwróć JSON: {\"podsumowanie\": \"1–2 zdania, czego potrzebuje ta grupa\", "
        "\"slowa\": [\"do 8 słów kluczowych, także synonimów, które pomogą znaleźć rozwiązania\"], "
        f"\"obszar\": \"jeden z: {', '.join(AREAS)}\"}}",
        max_tokens=400,
    )
    if data:
        result["summary"] = str(data.get("podsumowanie", ""))[:400] or None
        result["keywords"] = [str(w)[:40] for w in data.get("slowa", [])][:8]
        if data.get("obszar") in AREAS and not result["area"]:
            result["area"] = data["obszar"]
        result["by_ai"] = bool(result["summary"] or result["keywords"])
    return result


def expanded_query(text, analysis):
    return text + " " + " ".join(analysis["keywords"]) if analysis["keywords"] else text
