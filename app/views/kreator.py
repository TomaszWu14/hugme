"""Kreator pomysłów: fiszka (4 pola) → Kanwa Innowacji Społecznych → asystent (AI lub reguły)
→ generator wniosków (tylko w trakcie otwartego naboru), szkic, złożenie, wydruk z przeglądarki."""
import json

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.auth import login_required
from app.views.komunikacja import thread_view
from core import ai, catalog, db, notify
from core.domain import AREAS, AUDIENCES, STAGES
from core.privacy import mask

bp = Blueprint("kreator", __name__)

# (klucz, etykieta, pytanie pomocnicze, przykład)
CANVAS = [
    ("problem", "Problem", "Jaki problem rozwiązujesz i skąd wiesz, że istnieje?", "rodzice dzieci z zespołem Downa nie mają chwili odpoczynku"),
    ("odbiorcy", "Odbiorcy", "Dla kogo dokładnie jest rozwiązanie? Ile to osób?", "ok. 40 rodzin z powiatu krakowskiego"),
    ("rozwiazanie", "Rozwiązanie", "Na czym polega Twój pomysł – krok po kroku?", "sobotni klub 10–14 z animatorem i wolontariuszami"),
    ("wartosc", "Wartość i zmiana", "Co się zmieni w życiu odbiorców?", "4 godziny wolnego dla rodziców, przyjaźnie dla młodzieży"),
    ("nowosc", "Co jest nowe", "Czym różni się od tego, co już jest?", "łączy integrację młodzieży z odciążeniem rodziców"),
    ("partnerzy", "Partnerzy", "Kto pomoże? Gmina, szkoła, firma, organizacja?", "szkoła specjalna, dom kultury, harcerze"),
    ("zasoby", "Zasoby", "Czego potrzebujesz: ludzie, miejsce, sprzęt?", "sala, animator, 6 wolontariuszy"),
    ("koszty", "Koszty", "Jakie są główne rodzaje kosztów? (bez kwot)", "wynagrodzenie animatora, materiały, ubezpieczenie"),
    ("mierniki", "Mierniki", "Po czym poznasz, że działa?", "frekwencja, ocena rodziców po 3 miesiącach"),
    ("ryzyka", "Ryzyka", "Co może pójść nie tak i jak temu zaradzisz?", "brak wolontariuszy – współpraca z liceum"),
]
APPLICATION_FIELDS = [
    ("tytul", "Tytuł projektu", "Weekendowy klub dla nastolatków"),
    ("problem", "Problem i potrzeba", "opisz, kogo dotyczy problem i dlaczego jest ważny"),
    ("grupa", "Grupa odbiorców", "40 rodzin z powiatu krakowskiego"),
    ("dzialania", "Planowane działania", "rekrutacja, 20 spotkań, wyjścia do miasta"),
    ("rezultaty", "Rezultaty i mierniki", "frekwencja 70%, ocena rodziców ≥ 4/5"),
    ("budzet", "Budżet – opis kosztów (bez kwot w szkicu)", "animator, materiały, ubezpieczenie"),
    ("partnerzy", "Partnerzy", "szkoła specjalna, dom kultury"),
]


def _idea_or_404(iid):
    idea = db.one("SELECT * FROM ideas WHERE id = ?", (iid,))
    if idea is None:
        abort(404)
    return idea


def _own(idea):
    if g.user["id"] != idea["user_id"]:
        abort(403)


def _clean(value, limit):
    return mask(value.strip()[:limit])[0]


@bp.route("/pomysly")
def index():
    ideas = db.query("SELECT i.*, u.name AS author FROM ideas i JOIN users u ON u.id = i.user_id ORDER BY i.created_at DESC")
    calls = db.query("SELECT * FROM calls ORDER BY is_open DESC, deadline")
    return render_template("pomysly.html", ideas=ideas, calls=calls)


@bp.route("/pomysly/nowy", methods=["GET", "POST"])
@login_required
def new():
    form, errors = {"title": "", "essence": "", "audience": "", "stage": "", "area": ""}, {}
    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() for k in form}
        if len(form["title"]) < 3:
            errors["title"] = "Wpisz tytuł – wystarczy kilka słów."
        if len(form["essence"]) < 20:
            errors["essence"] = "Opisz istotę pomysłu w 1–2 zdaniach (co najmniej 20 znaków)."
        if form["audience"] not in AUDIENCES:
            errors["audience"] = "Wybierz, dla kogo jest pomysł."
        if form["stage"] not in STAGES:
            errors["stage"] = "Wybierz etap."
        if not errors:
            iid = db.execute(
                "INSERT INTO ideas (user_id, title, essence, audience, stage, area, created_at) VALUES (?,?,?,?,?,?,?)",
                (g.user["id"], _clean(form["title"], 120), _clean(form["essence"], 1000), form["audience"],
                 form["stage"], form["area"] if form["area"] in AREAS else None, db.now()))
            notify.notify_admins(f"Nowy pomysł: „{form['title'][:60]}”", f"/pomysly/{iid}", exclude=g.user["id"])
            flash("Fiszka zapisana i opublikowana. Teraz możesz uzupełnić kanwę albo zapytać asystenta.", "success")
            return redirect(url_for("kreator.detail", iid=iid))
    return render_template("pomysl_nowy.html", form=form, errors=errors, audiences=AUDIENCES, stages=STAGES), \
        (422 if errors else 200)


@bp.route("/pomysly/<int:iid>")
def detail(iid, assistant=None):
    idea = _idea_or_404(iid)
    author = db.one("SELECT name, role FROM users WHERE id = ?", (idea["user_id"],))
    open_calls = db.query("SELECT * FROM calls WHERE is_open = 1 ORDER BY deadline")
    apps = db.query("SELECT a.*, c.title AS call_title FROM applications a JOIN calls c ON c.id = a.call_id "
                    "WHERE a.idea_id = ?", (iid,))
    return render_template("pomysl.html", idea=idea, author=author, canvas=json.loads(idea["canvas"]),
                           fields=CANVAS, open_calls=open_calls, apps=apps, assistant=assistant,
                           thread=thread_view("pomysl", iid))


@bp.route("/pomysly/<int:iid>/kanwa", methods=["GET", "POST"])
@login_required
def canvas(iid):
    idea = _idea_or_404(iid)
    _own(idea)
    data = json.loads(idea["canvas"])
    if request.method == "POST":
        data = {k: _clean(request.form.get(k, ""), 800) for k, *_ in CANVAS}
        db.execute("UPDATE ideas SET canvas = ? WHERE id = ?",
                   (json.dumps({k: v for k, v in data.items() if v}, ensure_ascii=False), iid))
        flash("Kanwa zapisana.", "success")
        return redirect(url_for("kreator.detail", iid=iid) + "#kanwa")
    return render_template("kanwa.html", idea=idea, data=data, fields=CANVAS)


def rule_assistant(idea, canvas):
    """Asystent bez AI: wnioski z wypełnionych i pustych pól + podobne innowacje z Biblioteki."""
    labels = {k: label for k, label, *_ in CANVAS}
    filled = [labels[k] for k in labels if canvas.get(k)]
    strengths = ["Masz jasno nazwaną grupę odbiorców: " + idea["audience"] + "."]
    if filled:
        strengths.append("Przemyślane elementy kanwy: " + ", ".join(filled) + ".")
    if idea["stage"] in ("test", "wdrożenie"):
        strengths.append("Pomysł jest już sprawdzany w praktyce – to duży atut przy naborach.")
    questions = [q for k, _, q, _ in CANVAS if not canvas.get(k)][:4]
    questions += {"pomysł": ["Z kim możesz porozmawiać w tym tygodniu, żeby sprawdzić, czy problem jest realny?"],
                  "prototyp": ["Jak najtaniej przetestować pomysł z 5–10 osobami?"],
                  "test": ["Co zmienisz po pierwszych opiniach testujących?"],
                  "wdrożenie": ["Kto przejmie usługę, gdy skończy się grant?"]}[idea["stage"]]
    similar = catalog.match_innovations(f"{idea['title']} {idea['essence']} {canvas.get('problem', '')}", k=3)
    directions = [f"Zobacz, jak działa „{inn['title']}” ({inn['powiat']}) – może warto połączyć siły." for inn, _ in similar]
    directions.append("Pomyśl, czy usługę mogą współtworzyć sami odbiorcy – np. jako wolontariusze lub ambasadorzy.")
    prototype = (f"Szkic prototypu: „{idea['title']}”. Przez 6 tygodni testujesz rozwiązanie z małą grupą "
                 f"({idea['audience']}). Na start: {canvas.get('zasoby') or 'ustal minimalne zasoby'}. "
                 f"Po teście sprawdzasz: {canvas.get('mierniki') or 'frekwencję i opinię uczestników'}.")
    return {"strengths": strengths, "questions": questions, "directions": directions, "prototype": prototype,
            "by_ai": False}


def ai_assistant(idea, canvas):
    data = ai.ask_json(
        "Pomóż rozwinąć pomysł na innowację społeczną w Małopolsce.\n"
        f"Tytuł: {idea['title']}\nIstota: {idea['essence']}\nDla kogo: {idea['audience']}\nEtap: {idea['stage']}\n"
        f"Kanwa: {json.dumps(canvas, ensure_ascii=False)}\n\n"
        "Zwróć JSON: {\"mocne_strony\": [3 punkty], \"pytania\": [4 pytania rozwijające], "
        "\"kierunki\": [3 nieoczywiste kierunki rozwoju], \"prototyp\": \"opis szkicu prototypu w 3–4 zdaniach\"}",
        max_tokens=900)
    if not data:
        return None
    lst = lambda k: [str(x)[:300] for x in data.get(k, []) if x][:5]
    out = {"strengths": lst("mocne_strony"), "questions": lst("pytania"), "directions": lst("kierunki"),
           "prototype": str(data.get("prototyp", ""))[:900], "by_ai": True}
    return out if out["strengths"] or out["questions"] else None


@bp.post("/pomysly/<int:iid>/asystent")
@login_required
def assistant(iid):
    idea = _idea_or_404(iid)
    canvas = json.loads(idea["canvas"])
    return detail(iid, assistant=ai_assistant(idea, canvas) or rule_assistant(idea, canvas))


def _prefill(idea):
    c = json.loads(idea["canvas"])
    return {"tytul": idea["title"], "problem": c.get("problem") or idea["essence"],
            "grupa": c.get("odbiorcy") or idea["audience"], "dzialania": c.get("rozwiazanie", ""),
            "rezultaty": " ".join(x for x in (c.get("wartosc"), c.get("mierniki")) if x),
            "budzet": c.get("koszty", ""), "partnerzy": c.get("partnerzy", "")}


@bp.route("/pomysly/<int:iid>/wniosek/<int:cid>", methods=["GET", "POST"])
@login_required
def application(iid, cid):
    idea = _idea_or_404(iid)
    _own(idea)
    call = db.one("SELECT * FROM calls WHERE id = ?", (cid,))
    if call is None:
        abort(404)
    existing = db.one("SELECT * FROM applications WHERE idea_id = ? AND call_id = ?", (iid, cid))
    if existing and existing["status"] == "zlozony":
        return redirect(url_for("kreator.print_application", aid=existing["id"]))
    if not call["is_open"]:
        flash("Ten nabór jest zamknięty – generator wniosków działa tylko w trakcie naboru.", "error")
        return redirect(url_for("kreator.detail", iid=iid))
    fields = json.loads(existing["fields"]) if existing else _prefill(idea)
    suggestion, errors = None, {}
    if request.method == "POST":
        fields = {k: _clean(request.form.get(k, ""), 2000) for k, *_ in APPLICATION_FIELDS}
        action = request.form.get("akcja")
        if action == "ai":
            suggestion = ai.ask_json(
                "Na podstawie pól wniosku zaproponuj lepsze, konkretne opisy pól 'dzialania' i 'rezultaty' "
                "(bez kwot pieniędzy, prostym językiem).\n" + json.dumps(fields, ensure_ascii=False) +
                "\nZwróć JSON: {\"dzialania\": \"...\", \"rezultaty\": \"...\"}", max_tokens=700)
            if not suggestion:
                flash("Asystent AI jest teraz niedostępny – wniosek możesz dokończyć samodzielnie.", "info")
        else:
            if action == "zloz":
                errors = {k: "To pole jest potrzebne do złożenia wniosku." for k, *_ in APPLICATION_FIELDS if not fields[k]}
            if not errors:
                status = "zlozony" if action == "zloz" else "szkic"
                payload = json.dumps(fields, ensure_ascii=False)
                if existing:
                    db.execute("UPDATE applications SET fields = ?, status = ? WHERE id = ?", (payload, status, existing["id"]))
                    aid = existing["id"]
                else:
                    aid = db.execute("INSERT INTO applications (idea_id, call_id, user_id, fields, status, created_at) "
                                     "VALUES (?,?,?,?,?,?)", (iid, cid, g.user["id"], payload, status, db.now()))
                if status == "zlozony":
                    notify.notify_admins(f"Złożono wniosek „{fields['tytul'][:50]}” w naborze „{call['title'][:40]}”",
                                         url_for("kreator.print_application", aid=aid))
                    flash("Wniosek złożony. Hub potwierdzi przyjęcie w powiadomieniu.", "success")
                    return redirect(url_for("kreator.print_application", aid=aid))
                flash("Szkic zapisany. Możesz do niego wrócić w każdej chwili.", "success")
                return redirect(url_for("kreator.application", iid=iid, cid=cid))
    return render_template("wniosek.html", idea=idea, call=call, fields=fields, spec=APPLICATION_FIELDS,
                           suggestion=suggestion, errors=errors, ai_enabled=ai.enabled()), (422 if errors else 200)


@bp.route("/wnioski/<int:aid>")
@login_required
def print_application(aid):
    a = db.one("SELECT a.*, c.title AS call_title, c.deadline, i.title AS idea_title FROM applications a "
               "JOIN calls c ON c.id = a.call_id JOIN ideas i ON i.id = a.idea_id WHERE a.id = ?", (aid,))
    if a is None:
        abort(404)
    if g.user["id"] != a["user_id"] and g.user["role"] != "admin":
        abort(403)
    return render_template("wniosek_druk.html", a=a, fields=json.loads(a["fields"]), spec=APPLICATION_FIELDS)
