"""Pośrednik innowacji: gmina, CUS albo NGO podaje kontekst i dostaje kartę usługi
(opis, odbiorcy, zespół, kroki, partnerzy, koszty BEZ kwot, finansowanie, mierniki, ryzyka).
AI wzbogaca kartę; bez klucza działa szablon oparty o najlepiej dopasowaną innowację."""
import json
import re

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.auth import login_required
from core import ai, catalog, db
from core.domain import AUDIENCES, POWIATY
from core.privacy import mask

bp = Blueprint("posrednik", __name__)

INSTITUTIONS = {"gmina": "Gmina / urząd", "cus": "CUS / OPS", "ngo": "Organizacja pozarządowa", "szkola": "Szkoła / placówka"}
SCALES = {"mala": "do 20 osób", "srednia": "20–100 osób", "duza": "100–500 osób", "bardzo-duza": "ponad 500 osób"}
BUDGETS = {"brak": "bez budżetu – zasoby własne i wolontariat", "maly": "mały – drobne zakupy, kilka tysięcy",
           "sredni": "średni – kilkadziesiąt tysięcy, część etatu", "duzy": "duży – etaty i stała usługa"}
CARD_KEYS = ["opis", "odbiorcy", "zespol", "kroki", "partnerzy", "koszty", "finansowanie", "mierniki", "ryzyka"]
CARD_LABELS = {"opis": "Opis usługi", "odbiorcy": "Odbiorcy", "zespol": "Zespół", "kroki": "Kroki wdrożenia",
               "partnerzy": "Partnerzy", "koszty": "Koszty (rodzaje, bez kwot)", "finansowanie": "Skąd finansowanie",
               "mierniki": "Mierniki – po czym poznasz, że działa", "ryzyka": "Ryzyka i jak im zaradzić"}

_MONEY = re.compile(r"\d[\d\s.,]*\s*(?:zł|złotych|pln|tys\.?|tysięcy|mln|euro|€)", re.I)


def no_amounts(value):
    """Karta nie może zawierać wymyślonych kwot – zastępujemy je neutralnym znacznikiem."""
    if isinstance(value, list):
        return [no_amounts(v) for v in value]
    return _MONEY.sub("[kwota do wyceny]", str(value))


FUNDING = {
    "gmina": ["Budżet gminy – zadania własne pomocy społecznej", "Fundusze Europejskie dla Małopolski 2021–2027 (EFS+)",
              "Konkursy i granty ROPS / Hubu Innowacji Społecznych", "Programy rządowe i PFRON (dla usług dla osób z niepełnosprawnością)"],
    "cus": ["Zadania zlecone i własne gminy realizowane przez CUS", "Fundusze Europejskie dla Małopolski 2021–2027 (EFS+)",
            "Granty Hubu Innowacji Społecznych na testowanie innowacji"],
    "ngo": ["Otwarte konkursy ofert gminy i powiatu", "Granty Hubu Innowacji Społecznych (ROPS)",
            "Programy NIW-CRSO (np. FIO)", "Fundacje korporacyjne i lokalne firmy"],
    "szkola": ["Budżet organu prowadzącego", "Programy edukacyjne kuratorium i ministerstwa", "Rada rodziców, lokalne firmy"],
}


def rule_card(ctx, best):
    team = {"mala": "koordynator (część etatu) i 2–3 wolontariuszy", "srednia": "koordynator, 1–2 specjalistów, wolontariusze",
            "duza": "koordynator na etat, zespół specjalistów, wolontariusze", "bardzo-duza": "zespół projektowy, partnerzy w kilku gminach"}
    inn = f"„{best['title']}” ({best['org']}, powiat {best['powiat']})" if best else "podobnych inicjatyw z Biblioteki"
    return {
        "opis": f"Usługa odpowiada na problem: {ctx['problem']} Wzorujemy się na innowacji {inn}"
                + (f" – {best['summary'].lower()}" if best else "."),
        "odbiorcy": f"{ctx['audience'].capitalize()}, skala: {SCALES[ctx['scale']]}"
                    + (f", powiat {ctx['powiat']}." if ctx["powiat"] else "."),
        "zespol": team[ctx["scale"]].capitalize() + ".",
        "kroki": ["Porozmawiaj z 8–10 odbiorcami i sprawdź, czego naprawdę potrzebują.",
                  f"Poproś Hub o kontakt z autorami {inn} – podzielą się doświadczeniem.",
                  "Zbierz partnerów i ustal, kto za co odpowiada.",
                  "Przeprowadź pilotaż przez 3 miesiące z małą grupą.",
                  "Oceń wyniki z odbiorcami i zdecyduj o skali i stałym finansowaniu."],
        "partnerzy": ["Hub Innowacji Społecznych ROPS – wsparcie i kontakty"]
                     + (["Organizacje pozarządowe z terenu"] if ctx["institution"] != "ngo" else ["Gmina i ośrodek pomocy społecznej"])
                     + ["Szkoły, biblioteki, parafie, koła gospodyń – miejsca i ludzie", "Lokalne firmy – wolontariat i sprzęt"],
        "koszty": ["Wynagrodzenie koordynatora", "Materiały i drobny sprzęt", "Dojazdy lub transport uczestników",
                   "Lokal (często użyczony)", "Szkolenie zespołu i wolontariuszy", "Ubezpieczenie"]
                  if ctx["budget"] != "brak" else ["Koszty minimalne: materiały i ubezpieczenie wolontariuszy",
                                                    "Lokal użyczony przez gminę lub partnera"],
        "finansowanie": FUNDING[ctx["institution"]] + ["Sprawdź aktualne nabory – terminy i zasady się zmieniają."],
        "mierniki": ["Liczba osób, które skorzystały z usługi", "Ocena odbiorców (ankieta 1–5) po 3 miesiącach",
                     "Zmiana, którą chcesz osiągnąć – np. mniej dojazdów, więcej godzin odpoczynku"],
        "ryzyka": ["Mało chętnych na start – rekrutuj przez OPS, szkoły i parafie",
                   "Odejście kluczowej osoby – opisz procedury, miej zastępcę",
                   "Brak pieniędzy po pilotażu – od początku planuj finansowanie ciągłe"],
    }


def ai_card(ctx, best):
    text_keys, list_keys = ("opis", "odbiorcy", "zespol"), ("kroki", "partnerzy", "koszty", "finansowanie", "mierniki", "ryzyka")
    data = ai.ask_json(
        "Przygotuj kartę usługi społecznej do wdrożenia w Małopolsce (kontekst instytucji jest w danych zewnętrznych).\n"
        "Zasady: NIE podawaj żadnych kwot pieniędzy (tylko rodzaje kosztów). Źródła finansowania podawaj ogólnie "
        "(np. Fundusze Europejskie dla Małopolski, konkursy ROPS) z dopiskiem, by sprawdzić aktualne nabory.\n"
        "Zwróć JSON z kluczami: opis (tekst), odbiorcy (tekst), zespol (tekst), kroki (lista 5), partnerzy (lista), "
        "koszty (lista), finansowanie (lista), mierniki (lista), ryzyka (lista).",
        data=f"Instytucja: {INSTITUTIONS[ctx['institution']]}\nGrupa: {ctx['audience']}\nSkala: {SCALES[ctx['scale']]}\n"
             f"Budżet: {BUDGETS[ctx['budget']]}\nPowiat: {ctx['powiat'] or 'nie podano'}\nProblem: {ctx['problem']}\n"
             + (f"Wzorcowa innowacja z Biblioteki: {best['title']} – {best['summary']} ({best['org']})" if best else ""),
        schema={**{k: ("str", 1200) for k in text_keys}, **{k: ("list", 12, 300) for k in list_keys}},
        required=CARD_KEYS, max_tokens=1400)
    if not data:
        return None
    # Kwoty wycinane także z odpowiedzi AI – decyzja o kosztach „bez kwot” jest w kodzie, nie w prompcie.
    return {k: [no_amounts(x) for x in data[k]] if k in list_keys else no_amounts(data[k]) for k in CARD_KEYS}


@bp.route("/posrednik", methods=["GET", "POST"])
def form():
    ctx = {"institution": "", "audience": "", "scale": "", "budget": "", "powiat": "", "problem": ""}
    errors = {}
    if request.method == "POST":
        if g.user is None:
            return redirect(url_for("auth.demo", next=url_for("posrednik.form")))
        ctx = {k: request.form.get(k, "").strip() for k in ctx}
        for key, allowed, msg in [("institution", INSTITUTIONS, "Wybierz typ instytucji."),
                                  ("audience", AUDIENCES, "Wybierz grupę odbiorców."),
                                  ("scale", SCALES, "Wybierz skalę."), ("budget", BUDGETS, "Wybierz budżet.")]:
            if ctx[key] not in allowed:
                errors[key] = msg
        if ctx["powiat"] and ctx["powiat"] not in POWIATY:
            errors["powiat"] = "Wybierz powiat z listy."
        if len(ctx["problem"]) < 15:
            errors["problem"] = "Opisz w 1–2 zdaniach, jaki problem chcesz rozwiązać."
        if not errors:
            ctx["problem"] = mask(ctx["problem"][:1000])[0]
            matches = catalog.match_innovations(f"{ctx['problem']} {ctx['audience']}", k=3)
            best = matches[0][0] if matches else None
            card = ai_card(ctx, best)
            by_ai = card is not None
            card = card or rule_card(ctx, best)
            card["_inspiracje"] = [{"id": i["id"], "title": i["title"]} for i, _ in matches]
            cid = db.execute("INSERT INTO broker_cards (user_id, context, card, by_ai, created_at) VALUES (?,?,?,?,?)",
                             (g.user["id"], json.dumps(ctx, ensure_ascii=False), json.dumps(card, ensure_ascii=False),
                              int(by_ai), db.now()))
            return redirect(url_for("posrednik.card", cid=cid))
    mine = db.query("SELECT id, context, created_at FROM broker_cards WHERE user_id = ? ORDER BY id DESC",
                    (g.user["id"],)) if g.user else []
    return render_template("posrednik.html", ctx=ctx, errors=errors, institutions=INSTITUTIONS, scales=SCALES,
                           budgets=BUDGETS, audiences=AUDIENCES, powiaty=POWIATY,
                           mine=[(m["id"], json.loads(m["context"]), m["created_at"]) for m in mine]), \
        (422 if errors else 200)


@bp.route("/posrednik/karta/<int:cid>")
@login_required
def card(cid):
    row = db.one("SELECT * FROM broker_cards WHERE id = ?", (cid,))
    if row is None:
        abort(404)
    if row["user_id"] != g.user["id"] and g.user["role"] != "admin":
        abort(403)
    return render_template("karta.html", row=row, ctx=json.loads(row["context"]), card=json.loads(row["card"]),
                           keys=CARD_KEYS, labels=CARD_LABELS, institutions=INSTITUTIONS, scales=SCALES, budgets=BUDGETS)
