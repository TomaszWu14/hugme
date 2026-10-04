"""Demo prowadzące jury krok po kroku: dwa scenariusze, stan w sesji (session["scen"] = [sid, n]).

Krok: uid konta demo (None = gość), ścieżka prawdziwego ekranu, tytuł, tekst (co zrobić i co zobaczysz)
i opcjonalny `cel` – selektor CSS elementu, który JS podświetla; `akcja=True` – krok wymaga kliknięcia na stronie
(dalsze kroki pokazują jego skutek), więc „Dalej” jest mały, żeby nie kusił do pominięcia. Widok: app/views/demo.py, pasek: _scenariusz.html."""
from urllib.parse import urlsplit

from flask import g, request, session

from data.seed_data import INNOVATIONS

BUS = 1 + [i[0] for i in INNOVATIONS].index("Bus na Telefon")  # id z kolejności w seedzie (autoincrement od 1)

# Zgłoszenie z kroku 2 rodzica – demo.go() wpisuje je samo, gdy jury pominie formularz (kroki 3–4 pokazują Bartka).
BARTEK = {"alias": "Bartek", "powiat": "wadowicki", "age_group": "dorosly", "interests": "psy",
          "days": ["sb", "rano"], "companion": "rodzic", "consent": "1"}

GMINA_OPIS = "Seniorzy z pięciu sołectw nie mają jak dojechać do lekarza – autobus nie jeździ, a przychodnia jest w mieście."

SCENARIUSZE = {
    "rodzic": {
        "tytul": "Rodzic osoby z zespołem Downa – „Jestem potrzebny”",
        "opis": "Mama zgłasza dorosłego syna z ZD, który chce wyprowadzać psy ze schroniska – Hub dobiera miejsce, a potem przychodzą propozycje pracy i zajęć.",
        "czas": "ok. 1,5 min",
        "kroki": [
            dict(uid=None, path="/razem/jestem-potrzebny", tytul="Czym jest „Jestem potrzebny”",
                 tekst="Osoby z zespołem Downa pomagają innym – wyprowadzają psy ze schroniska, odwiedzają seniorów – zawsze z opiekunem. "
                       "Hub dobiera miejsce i potwierdza każdą misję.", cel=".razem-hero"),
            dict(uid=1, path="/razem/jestem-potrzebny/zglos", tytul="Mama zgłasza syna",
                 tekst="Jesteś teraz mamą (konto mieszkanki). Wpisz pseudonim „Bartek”, powiat wadowicki, zaznacz: osoba dorosła, "
                       "psy, sobota i rano, towarzyszy rodzic, zgoda – i kliknij „Wyślij zgłoszenie” na dole (pasek sam przejdzie dalej).",
                 cel="form.card", akcja=True),
            dict(uid=1, path="/razem/jestem-potrzebny/dzienniczek", tytul="Zgłoszenie czeka na Hub",
                 tekst="W dzienniczku przy „Bartku” widać: „Hub szuka dla Ciebie miejsca”. Koordynatorka Hubu dostała już powiadomienie.",
                 cel=".etr-page > section.card:last-of-type"),
            dict(uid=5, path="/admin/potrzebny", tytul="Hub łączy Bartka ze schroniskiem",
                 tekst="Jesteś koordynatorką Hubu. Znajdź parę „Bartek ↔ Schronisko dla zwierząt w Wadowicach” (obwiedziona, nie Tomek) "
                       "i kliknij przy niej „Połącz”.", cel='li[data-alias="Bartek"]', akcja=True),
            dict(uid=1, path="/powiadomienia", tytul="Odpowiedź Hubu",
                 tekst="Wracasz jako mama. Kliknij wiadomość na górze – Hub połączył Bartka ze schroniskiem, a w dzienniczku czeka pierwsza misja.",
                 cel="main .list-plain > li:first-child"),
            dict(uid=1, path="/razem/praca", tytul="Praca i zajęcia dla osób z ZD",
                 tekst="Mapa prawdziwych miejsc pracy osób z zespołem Downa, każde ze źródłem – kliknij Kraków na mapie Małopolski. "
                       "Zajęcia i spotkania dla rodzin są w zakładce „Wydarzenia”.",
                 cel='section[aria-labelledby="mapa-mp-h"]'),
        ],
    },
    "gmina": {
        "tytul": "Gmina → Hub: od problemu do gotowej usługi",
        "opis": "Urzędnik gminy opisuje problem seniorów, dostaje sprawdzone rozwiązanie i kartę usługi, a Hub odpowiada i widzi trendy.",
        "czas": "ok. 1,5 min",
        "opis_problemu": GMINA_OPIS,
        "kroki": [
            dict(uid=3, path="/", tytul="Gmina opisuje problem",
                 tekst="Jesteś urzędnikiem gminy. Opis problemu już jest w polu – kliknij „Znajdź rozwiązania”.", cel=".ask"),
            dict(uid=3, path="/wyniki", tytul="Bus na Telefon – „Bardzo pasuje”",
                 tekst="Na górze „Bus na Telefon” z oceną dopasowania i wyjaśnieniem, dlaczego pasuje. "
                       "Zjedź niżej, kliknij „Zapisz zgłoszenie” (trafi do Hubu), potem „Dalej”.", cel=".match", akcja=True),
            dict(uid=3, path=f"/posrednik?inspiracja={BUS}", tytul="Pośrednik: karta usługi",
                 tekst="Formularz wypełniliśmy na podstawie „Bus na Telefon”. Kliknij „Przygotuj kartę usługi”, "
                       "a na karcie – „Drukuj / zapisz jako PDF”.", cel="form.card"),
            dict(uid=5, path="/admin", tytul="Hub: zgłoszenie gminy w skrzynce",
                 tekst="Jesteś koordynatorką Hubu. Otwórz zgłoszenie gminy (na górze tabeli), ustaw status „W analizie”, "
                       "kliknij „Zapisz i powiadom autora” i odpisz w rozmowie poniżej.", cel=".table-wrap", akcja=True),
            dict(uid=5, path="/admin/trendy", tytul="Trendy i luki",
                 tekst="Z jakich obszarów przybywa zgłoszeń i gdzie brakuje rozwiązań (luki). To podpowiedź, jakie konkursy ogłosić.",
                 cel=".table-wrap"),
            dict(uid=3, path="/powiadomienia", tytul="Gmina dostaje odpowiedź",
                 tekst="Wracasz jako gmina. Na górze: nowy status zgłoszenia i wiadomość od Hubu – kliknij, żeby przeczytać.",
                 cel="main .list-plain > li:first-child"),
        ],
    },
}


def step(sid, n):
    """Krok n (od 1) scenariusza sid albo None."""
    s = SCENARIUSZE.get(sid)
    return s["kroki"][n - 1] if s and 1 <= n <= len(s["kroki"]) else None


def current():
    """Dane paska dla aktywnego scenariusza albo None."""
    sid, n = (session.get("scen") or [None, 0])[:2]
    st = step(sid, n)
    if st is None:
        return None
    s = SCENARIUSZE[sid]
    kroki = s["kroki"]
    return {"sid": sid, "nr": list(SCENARIUSZE).index(sid) + 1, "ile_scen": len(SCENARIUSZE), "scen": s, "n": n,
            "N": len(kroki), "krok": st, "nastepny": kroki[n] if n < len(kroki) else None}


def advance():
    """Akcja z kroku prowadzi na ekran następnego kroku (np. „Znajdź rozwiązania” → /wyniki) – pasek sam przechodzi dalej.
    Tylko GET, tylko gdy to inny ekran niż bieżący krok i to samo konto co w następnym kroku."""
    s = current() if request.method == "GET" else None
    nxt = s and s["nastepny"]
    if (nxt and request.path == urlsplit(nxt["path"]).path != urlsplit(s["krok"]["path"]).path
            and (g.user["id"] if g.user else None) == nxt["uid"]):
        session["scen"] = [s["sid"], s["n"] + 1]


def init(app):
    app.before_request(advance)  # po auth.load_user (kolejność rejestracji w create_app)
    app.jinja_env.globals.update(scenariusz=current)
