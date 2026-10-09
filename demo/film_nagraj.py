"""Nagrywa sceny filmu HugMe (demo/film_sceny.py) na świeżej bazie – Playwright + zrzut ekranu przez CDP.

Okno 1920×1080 ze stroną powiększoną do 125% (CSS zoom) – klatka Full HD z czytelnym tekstem. Klatki (JPEG 92) z Page.startScreencast trafiają
do ffmpeg 30 razy na sekundę, ale tylko w trakcie sceny: przełączanie kont (POST /konto przez ctx.request – te same
ciasteczka, bez ekranu wyboru konta) i ładowanie stron między scenami w ogóle nie wchodzą do nagrania.
Rytm wyznacza lektor: akcje są przypięte do słów (r.na("łączy")), a scena trwa co najmniej tyle, ile jej kwestia
(film_czas.dlugosc_sceny). Asercje w każdym kroku – jeśli coś się nie wyświetli, skrypt przerywa (nie nagrywamy błędu).

Wynik: demo/out/film/nagranie.mp4 + sceny.json (klatka początku i końca każdej sceny).
Uruchom: python demo/film_nagraj.py   (HUGME_ROOT=<kopia repo> opcjonalnie)"""
import base64
import json
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _serwer  # noqa: E402
import logging  # noqa: E402
logging.getLogger("werkzeug").setLevel(logging.ERROR)
import film_czas as C  # noqa: E402
from data.seed_data import INNOVATIONS  # noqa: E402  (_serwer dodał katalog aplikacji do sys.path)

OUT = HERE / "out" / "film"
W, H, FPS = 1920, 1080, 30
ZOOM = 1.25  # jak przeglądarka ustawiona na 125%
BUS = 1 + [i[0] for i in INNOVATIONS].index("Bus na Telefon")  # id z kolejności w seedzie

KURSOR = """
(() => {
  const zoom = () => document.documentElement && (document.documentElement.style.zoom = '%ZOOM%');
  zoom();
  document.addEventListener('readystatechange', zoom);
  const pos = JSON.parse(sessionStorage.getItem('filmKursor') || '[1100,420]');
  function put() {
    if (!document.body || document.getElementById('film-kursor')) return;
    const c = document.createElement('div');
    c.id = 'film-kursor';
    Object.assign(c.style, {position: 'fixed', left: '0', top: '0', width: '28px', height: '28px', marginLeft: '-14px',
      marginTop: '-14px', zoom: 1 / %ZOOM%, borderRadius: '50%', background: 'rgba(184,67,47,.30)', border: '3px solid #B8432F',
      boxShadow: '0 0 0 2px rgba(255,255,255,.85)', zIndex: 2147483647, pointerEvents: 'none',
      transform: `translate(${pos[0]}px,${pos[1]}px)`});
    document.body.appendChild(c);
    document.addEventListener('mousemove', e => {
      c.style.transform = `translate(${e.clientX}px,${e.clientY}px)`;
      sessionStorage.setItem('filmKursor', JSON.stringify([e.clientX, e.clientY]));
    }, true);
    document.addEventListener('mousedown', e => {
      const r = document.createElement('div');
      Object.assign(r.style, {position: 'fixed', zoom: 1 / %ZOOM%, left: e.clientX - 28 + 'px', top: e.clientY - 28 + 'px', width: '56px',
        height: '56px', borderRadius: '50%', border: '4px solid #B8432F', zIndex: 2147483646, pointerEvents: 'none',
        transition: 'transform .45s ease-out, opacity .45s ease-out', transform: 'scale(.3)', opacity: '1'});
      document.body.appendChild(r);
      requestAnimationFrame(() => { r.style.transform = 'scale(1.5)'; r.style.opacity = '0'; });
      setTimeout(() => r.remove(), 600);
    }, true);
  }
  document.addEventListener('DOMContentLoaded', put);
  put();
})();
""".replace("%ZOOM%", str(ZOOM))

PRZEWIN = """async ([y, ms]) => {
  const s = window.scrollY, d = Math.max(0, Math.min(y, document.documentElement.scrollHeight - innerHeight)) - s;
  const t0 = performance.now();
  await new Promise(res => { (function f(now) {
    const p = Math.min(1, (now - t0) / ms), e = p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
    window.scrollTo(0, s + d * e); p < 1 ? requestAnimationFrame(f) : res();
  })(t0); });
}"""


class Kamera:
    """Klatki z CDP Page.startScreencast → ffmpeg (H.264, 30 kl./s). Wątek co 1/30 s dopisuje ostatnią klatkę, ale
    tylko gdy nagrywa=True, więc licznik klatek jest osią czasu nagrania (bez przerw między scenami)."""

    def __init__(self, page, path):
        self.jpeg, self.t_klatki, self.nagrywa, self.n, self.koniec = None, 0.0, False, 0, False
        self.ff = subprocess.Popen([C.FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "image2pipe", "-c:v", "mjpeg",
                                    "-framerate", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "12",
                                    "-pix_fmt", "yuv420p", str(path)], stdin=subprocess.PIPE)
        self.cdp = page.context.new_cdp_session(page)
        self.cdp.on("Page.screencastFrame", self._klatka)
        self.cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": W, "maxHeight": H})
        self.watek = threading.Thread(target=self._pisz, daemon=True)
        self.watek.start()

    def _klatka(self, ev):
        self.jpeg = base64.b64decode(ev["data"])
        self.t_klatki = time.monotonic()
        self.cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})

    def _pisz(self):
        nast = time.monotonic()
        while not self.koniec:
            nast += 1 / FPS
            if self.nagrywa and self.jpeg:
                self.ff.stdin.write(self.jpeg)
                self.n += 1
            time.sleep(max(0.0, nast - time.monotonic()))

    def zamknij(self):
        self.koniec = True
        self.watek.join()
        self.cdp.send("Page.stopScreencast")
        self.ff.stdin.close()
        self.ff.wait()


class Rezyser:
    def __init__(self, ctx, page, base):
        self.ctx, self.p, self.base = ctx, page, base
        self.kamera = Kamera(page, OUT / "nagranie.mp4")
        self.sceny, self.sid, self.t0, self.uid = [], None, 0.0, None
        self.mysz = (1100, 420)

    # --- konto i nawigacja (poza nagraniem) ---
    def konto(self, uid):
        if uid == self.uid:
            return
        html = self.ctx.request.get(self.base + "/konto").text()
        csrf = re.search(r'name="_csrf" value="([^"]+)"', html).group(1)
        r = self.ctx.request.post(self.base + "/konto", form={"user_id": str(uid), "next": "/", "_csrf": csrf})
        assert r.ok, f"logowanie {uid}: {r.status}"
        self.uid = uid

    def idz(self, path):
        self.p.goto(self.base + path, wait_until="networkidle")
        self.p.evaluate("document.fonts.ready")

    # --- scena ---
    def start(self, sid, ciagla=False):
        """Początek sceny. ciagla=True: obraz płynnie kontynuuje poprzednią scenę (montaż nie robi przenikania)."""
        if not ciagla:  # świeża klatka z nowej strony: drgnięcie kursora wymusza odmalowanie
            t = time.monotonic()
            self.p.wait_for_timeout(200)
            self.p.mouse.move(self.mysz[0] + 1, self.mysz[1])
            self.p.mouse.move(*self.mysz)
            while self.kamera.t_klatki < t and time.monotonic() - t < 3:
                self.p.wait_for_timeout(30)
        self.sid, self.t0 = sid, time.monotonic()
        self.n0 = self.kamera.n
        self.kamera.nagrywa = True
        self.ciagla = ciagla
        print(f"  {sid}: start", flush=True)

    def stop(self, zapas=0.0):
        """Koniec sceny – nie wcześniej niż po całej kwestii lektora (+ zapas, np. na kliknięcie z przejściem)."""
        self.do(C.dlugosc_sceny(self.sid) + zapas)
        self.kamera.nagrywa = False
        n1 = self.kamera.n
        self.sceny.append({"id": self.sid, "start": self.n0, "koniec": n1, "ciagla": self.ciagla})
        print(f"  {self.sid}: {(n1 - self.n0) / FPS:.2f} s (min {C.dlugosc_sceny(self.sid):.2f})", flush=True)

    def koniec_klikiem(self, loc, ms=500, przed=0.45):
        """Ostatnie kliknięcie sceny (przejście na nową stronę): klik tuż przed końcem kwestii, nagranie kończy się
        chwilę po nim, a ładowanie nowej strony dzieje się już poza kadrem."""
        loc = loc.first
        expect(loc).to_be_visible()
        self.do_el(loc, ms)
        self.do(C.dlugosc_sceny(self.sid) - przed)
        with self.p.expect_navigation(wait_until="networkidle"):
            self.p.mouse.down()
            self.p.wait_for_timeout(90)
            self.p.mouse.up()
            self.stop()
        self.p.evaluate("document.fonts.ready")

    def t(self):
        return time.monotonic() - self.t0

    def do(self, t):
        """Czekaj do sekundy t sceny (wait_for_timeout, żeby Playwright odbierał klatki)."""
        while self.t() < t - 0.005:
            self.p.wait_for_timeout(min(100, max(5, int((t - self.t()) * 1000))))

    def na(self, slowo, nr=0, przed=0.0):
        """Czekaj do chwili, gdy lektor zaczyna dane słowo."""
        self.do(C.slowo(self.sid, slowo, nr) - przed)

    # --- ruch ---
    def kursor(self, x, y, ms=650):
        x0, y0 = self.mysz
        kroki = max(8, ms // 16)
        for i in range(1, kroki + 1):
            p = i / kroki
            e = 1 - (1 - p) ** 3
            self.p.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
            self.p.wait_for_timeout(ms / kroki)
        self.mysz = (x, y)

    def do_el(self, loc, ms=650, fx=0.5, fy=0.5, dx=0):
        b = loc.first.bounding_box()
        assert b, f"{self.sid}: element poza stroną"
        self.kursor(b["x"] + b["width"] * fx + dx, b["y"] + b["height"] * fy, ms)

    def klik(self, loc, ms=650, nawigacja=False, fx=0.5, fy=0.5):
        loc = loc.first
        expect(loc).to_be_visible()
        self.do_el(loc, ms, fx=fx, fy=fy)
        self.p.wait_for_timeout(120)
        if nawigacja:
            with self.p.expect_navigation(wait_until="networkidle"):
                self.p.mouse.down()
                self.p.wait_for_timeout(90)
                self.p.mouse.up()
            self.p.evaluate("document.fonts.ready")
        else:
            self.p.mouse.down()
            self.p.wait_for_timeout(90)
            self.p.mouse.up()

    def pisz(self, loc, tekst, ms_znak=32):
        loc.first.press_sequentially(tekst, delay=ms_znak)

    def przewin(self, loc_lub_y, ms=900, gora=110):
        """Płynnie przewiń, aż element będzie `gora` px od górnej krawędzi okna (albo do y)."""
        if isinstance(loc_lub_y, (int, float)):
            y = loc_lub_y
        else:
            y = loc_lub_y.first.evaluate("e => e.getBoundingClientRect().top + window.scrollY") - gora
        self.p.evaluate(PRZEWIN, [y, ms])

    def od_razu(self, loc, gora=110):
        """Natychmiastowe przewinięcie (przed startem sceny)."""
        loc.first.evaluate(f"e => window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - {gora})")


def sceny(r):
    p = r.p

    # 01–04: Anna szuka pomocy – jedno ciągłe ujęcie strony startowej, wyników i zgłoszenia
    r.konto(1)
    r.idz("/")
    expect(p.get_by_role("heading", name="Twój problem nie zostaje sam")).to_be_visible()
    r.start("01-start")
    r.kursor(1150, 330, 900)
    r.na("bo")
    form = p.locator("form:has(#f-opis)")
    r.przewin(p.get_by_role("heading", name="Co jest trudne? Kogo to dotyczy?"), 1800, gora=90)
    r.do_el(p.locator("#f-opis"), 700, fx=0.3)
    r.stop()

    r.start("02-opis", ciagla=True)
    opis = p.locator("#f-opis")
    r.klik(opis, 400, fx=0.3)
    p.keyboard.press("Control+A")
    p.wait_for_timeout(150)
    p.keyboard.press("Backspace")
    r.pisz(opis, "Mój syn ma zespół Downa. Wizyty u kardiologa, logopedy i endokrynologa są w różnych "
                 "miastach – ciągle jeździmy i jesteśmy wykończeni.", 26)
    r.na("wpisuje", przed=0.3)
    r.pisz(opis, " Syn ma na imię Kacper, tel. 600 123 456.", 36)
    r.klik(form.locator("#f-powiat"), 450)
    p.select_option("#f-powiat", "wadowicki")
    expect(form.locator("#f-powiat")).to_have_value("wadowicki")
    r.koniec_klikiem(p.get_by_role("button", name="Znajdź rozwiązania"))

    p.wait_for_url("**/wyniki")
    expect(p.get_by_text("Dla Twojego bezpieczeństwa ukryliśmy")).to_be_visible()
    asystent = p.locator("article.match", has_text="Asystent zdrowia rodziny").first
    expect(asystent).to_be_visible()
    r.start("03-wyniki")
    r.na("platforma")
    r.do_el(p.get_by_text("[IMIĘ]").first, 700)
    r.na("telefon")
    r.do_el(p.get_by_text("Dla Twojego bezpieczeństwa ukryliśmy"), 700, fx=0.35)
    r.na("potem", przed=0.1)
    r.przewin(p.get_by_role("heading", name="Rozwiązania z Biblioteki Innowacji"), 1300, gora=60)
    r.na("asystenta")
    r.do_el(asystent.get_by_role("link", name="Asystent zdrowia rodziny"), 600)
    r.na("który")
    r.do_el(asystent.locator("p").filter(has_text="Jedna osoba umawia"), 700, fx=0.3)
    r.na("przy", przed=0.1)
    r.przewin(asystent, 900, gora=140)
    r.do_el(asystent.locator("p.why"), 700, fx=0.25)
    r.na("dopasowanie")
    drugi = p.locator("article.match").nth(1)
    r.przewin(drugi, 1400, gora=120)
    r.do_el(drugi.locator("p.why"), 800, fx=0.3)
    r.stop()

    r.start("04-zgloszenie", ciagla=True)
    r.przewin(p.get_by_role("heading", name="Zapisz zgłoszenie – Hub odpowie"), 1000, gora=120)
    r.na("zapisuje", przed=0.5)
    r.klik(p.locator('form[action="/zgloszenie"] button[type=submit]'), 600, nawigacja=True)
    expect(p.get_by_text("Zgłoszenie zapisane")).to_be_visible()
    r.na("ocena", przed=0.3)
    pomocne = p.locator("form.feedback").first.get_by_role("button", name="Pomocne")
    r.przewin(p.get_by_role("heading", name="Dopasowane rozwiązania"), 900, gora=100)
    r.na("trafne", przed=0.6)
    r.klik(pomocne, 500, nawigacja=True)
    expect(p.get_by_text("Twoja ocena: pomocne").first).to_be_visible()
    r.od_razu(p.get_by_role("heading", name="Dopasowane rozwiązania"), 100)
    r.stop()
    zgl = p.url.split("#")[0].split("?")[0]

    # 05: koordynatorka Hubu – skrzynka, decyzja, odpowiedź
    r.konto(5)
    r.idz("/admin")
    expect(p.get_by_role("heading", name="Panel Hubu Innowacji Społecznych")).to_be_visible()
    r.start("05-hub")
    wiersz = p.locator("table tbody tr", has_text="ma zespół Downa").first
    r.przewin(p.get_by_role("heading", name="Skrzynka"), 1100, gora=90)
    r.do_el(wiersz.locator("a").first, 700, fx=0.3, fy=0.2)
    r.na("otwiera", przed=0.3)
    r.klik(wiersz.locator("a").first, 400, nawigacja=True, fx=0.2, fy=0.2)
    assert p.url.startswith(zgl), p.url
    decyzja = p.locator("#f-status")
    r.przewin(decyzja, 700, gora=260)
    r.na("połączone", przed=0.4)
    r.klik(decyzja, 400)
    p.select_option("#f-status", "polaczone")
    r.klik(p.get_by_role("button", name="Zapisz i powiadom autora"), 450, nawigacja=True)
    tresc = p.locator("#f-tresc")
    r.przewin(tresc, 600, gora=330)
    r.klik(tresc, 300)
    r.pisz(tresc, "Dzień dobry! Łączę Panią z autorami Asystenta zdrowia rodziny.", 14)
    r.klik(p.locator("form[action^='/watek'] button[type=submit]"), 450, nawigacja=True)
    expect(p.get_by_text("Łączę Panią z autorami").first).to_be_visible()
    r.od_razu(p.get_by_text("Łączę Panią z autorami").first, 380)
    r.stop()

    # 06: Razem z ZD – plan na etap życia
    r.konto(1)
    r.idz("/razem")
    expect(p.get_by_role("heading", name="Wasza rodzina nie zostaje sama")).to_be_visible()
    r.start("06-razem")
    r.do_el(p.get_by_role("heading", name="Wasza rodzina nie zostaje sama"), 900, fx=0.6)
    r.na("po", przed=0.2)
    r.przewin(p.get_by_role("heading", name="Wybierz etap życia"), 900, gora=110)
    r.na("przedszkola", przed=0.5)
    r.klik(p.locator("button.stage-btn", has_text="Przedszkole"), 500, nawigacja=True)
    expect(p.get_by_role("heading", name="Co teraz ważne")).to_be_visible()
    r.na("widać", przed=0.2)
    r.przewin(p.get_by_role("heading", name="Co teraz ważne"), 900, gora=100)
    r.do_el(p.locator("ol.steps li").first, 600, fx=0.4)
    r.na("kto")
    r.przewin(p.get_by_role("heading", name="Kto pomoże"), 1100, gora=120)
    r.do_el(p.get_by_role("heading", name="Kto pomoże"), 600, fx=0.6)
    r.stop()

    # 07: „Jestem potrzebny” w łatwym tekście – Bartek wybiera obrazki
    r.idz("/razem/jestem-potrzebny/latwy")
    p.fill("#f-alias", "Bartek")  # pola pod obrazkami wypełnione przed startem, widz zobaczy je przy „Wyślij”
    p.select_option("#f-powiat", "wadowicki")
    p.check("#f-consent")
    p.evaluate("window.scrollTo(0, 0)")
    r.od_razu(p.get_by_role("heading", name="Ja chcę pomagać"), 100)
    r.start("07-potrzebny")
    pikto = lambda n, v: p.locator(f"label.picto-choice:has(input[name={n}][value={v}])")  # noqa: E731
    r.do_el(p.get_by_role("heading", name="Ja chcę pomagać"), 900, fx=0.7)
    r.na("wybiera")
    r.do_el(p.locator("#f-interests"), 700, fx=0.25, fy=0.3)
    r.na("psy", przed=0.5)
    r.klik(pikto("interests", "psy"), 450)
    r.przewin(p.locator("#f-days"), 700, gora=160)
    r.na("sobotę", przed=0.5)
    r.klik(pikto("days", "sb"), 400)
    r.na("rano", przed=0.3)
    r.klik(pikto("days", "rano"), 400)
    r.na("mama", przed=0.6)
    r.klik(pikto("companion", "rodzic"), 400)
    expect(p.locator("input[name=interests][value=psy]")).to_be_checked()
    wyslij = p.locator("form[action='/razem/jestem-potrzebny/latwy'] button[type=submit]")
    r.przewin(wyslij, 600, gora=520)
    r.koniec_klikiem(wyslij, 400)
    expect(p.get_by_role("heading", name="Mój dzienniczek")).to_be_visible()

    # 08: Hub łączy Bartka ze schroniskiem i potwierdza misję
    r.konto(5)
    r.idz("/admin/potrzebny")
    para = p.locator('li[data-alias="Bartek"]').filter(has_text="Schronisko dla zwierząt w Wadowicach").first
    expect(para).to_be_visible()
    r.start("08-para")
    r.przewin(p.get_by_role("heading", name=re.compile("Propozycje par")), 1000, gora=90)
    r.do_el(para, 800, fx=0.3, fy=0.25)
    r.na("łączy", przed=0.5)
    r.klik(para.get_by_role("button", name=re.compile("Połącz")), 450, nawigacja=True)
    misja = p.locator("li", has_text="Bartek").filter(has=p.get_by_role("button", name=re.compile("Misja odbyła się"))).first
    expect(misja).to_be_visible()
    r.przewin(p.get_by_role("heading", name=re.compile("Pary połączone")), 1000, gora=110)
    r.do_el(misja, 600, fx=0.3, fy=0.3)
    r.na("potwierdza", przed=0.4)
    r.klik(misja.get_by_role("button", name=re.compile("Misja odbyła się")), 450, nawigacja=True)
    r.od_razu(p.get_by_role("heading", name=re.compile("Pary połączone")), 110)
    r.stop()

    # 09: dzienniczek Bartka – pierwsza odznaka
    r.konto(1)
    r.idz("/razem/jestem-potrzebny/dzienniczek")
    bartek = p.locator("section.card", has=p.get_by_role("heading", name="Bartek", exact=True)).first
    expect(bartek).to_contain_text("Pierwsza misja")
    r.od_razu(bartek, 90)
    r.start("09-dzienniczek")
    r.na("pierwsza", przed=0.6)
    r.do_el(bartek.locator(".badge-card").first, 700)
    r.na("po", przed=0.2)
    r.do_el(bartek.get_by_text(re.compile("misjach pokażemy tu umiejętności")), 800, fx=0.3)
    r.stop()

    # 10: Praca – mapa miejsc pracy osób z ZD
    r.idz("/razem/praca")
    expect(p.get_by_role("heading", name="Gdzie pracują osoby z zespołem Downa")).to_be_visible()
    r.start("10-praca")
    r.na("pokazuje")
    mapa = p.locator("section[aria-labelledby=mapa-pl-h]")
    r.przewin(mapa, 1300, gora=70)
    mp = mapa.locator("a[aria-label^='małopolskie']")
    r.do_el(mp, 800)
    r.na("kawiarnie", przed=0.3)
    r.klik(mp, 300, nawigacja=True)
    lista = p.locator("section[aria-labelledby=lista-h]")
    expect(lista).to_be_visible()
    r.od_razu(lista, 90)
    r.na("źródłem", przed=1.2)
    r.do_el(lista.get_by_role("link", name=re.compile("^Źródło")).first, 700)
    r.stop()

    # 11: gmina – Biblioteka → Pośrednik → karta usługi
    r.konto(3)
    r.idz(f"/biblioteka/{BUS}")
    expect(p.get_by_role("heading", name="Bus na Telefon").first).to_be_visible()
    r.start("11-gmina")
    r.do_el(p.get_by_role("heading", name="Bus na Telefon").first, 900, fx=0.6)
    r.na("pośrednik", przed=0.8)
    r.klik(p.get_by_role("link", name="Dopasuj do mojej gminy"), 600, nawigacja=True)
    expect(p.locator("#f-problem")).to_have_value(re.compile("Bus na Telefon"))
    p.select_option("#f-powiat", "dąbrowski")
    r.przewin(p.locator("#f-problem"), 800, gora=300)
    r.do_el(p.locator("#f-problem"), 600, fx=0.4)
    r.na("przygotowuje", przed=0.4)
    r.klik(p.get_by_role("button", name="Przygotuj kartę usługi"), 500, nawigacja=True)
    druk = p.locator("button[data-druk]")
    expect(druk).to_be_visible()
    r.na("zespół", przed=0.3)
    r.przewin(p.locator("dt", has_text="Zespół").first, 1600, gora=100)
    r.na("finansowanie", przed=0.4)
    r.przewin(p.locator("dt", has_text="Skąd finansowanie").first, 1500, gora=160)
    r.na("gotową", przed=0.3)
    r.przewin(0, 900)
    r.do_el(druk, 600)
    r.stop()

    # 12: Hub – trendy potrzeb i luki
    r.konto(5)
    r.idz("/admin/trendy")
    expect(p.get_by_role("heading", name="Trendy potrzeb i luki")).to_be_visible()
    r.start("12-trendy")
    r.do_el(p.locator("table").first.locator("tbody tr").first, 900, fx=0.45)
    r.na("powiatach", przed=0.3)
    mapa = p.locator("table:has(caption:has-text('Mapa potrzeb'))")
    r.przewin(mapa, 1300, gora=80)
    r.do_el(mapa.locator("tbody tr", has_text="wadowicki").locator("td").nth(1), 700)
    r.na("problemy", przed=0.2)
    r.przewin(p.get_by_role("heading", name="Luki – gdzie brakuje rozwiązań"), 1300, gora=90)
    r.na("konkursów", przed=0.9)
    r.do_el(p.get_by_text("Kandydat na konkurs").first, 700)
    r.stop()

    # 13: dostępność – większy tekst, wysoki kontrast, klawiatura
    r.konto(1)
    r.idz("/")
    r.start("13-dostepnosc")
    r.na("większy", przed=0.6)
    r.klik(p.locator("form:has(input[value=duzy-tekst]) button"), 500, nawigacja=True)
    r.na("wysoki", przed=0.5)
    r.klik(p.locator("form:has(input[value=kontrast]) button"), 500, nawigacja=True)
    r.na("klawiaturą", przed=0.7)
    r.kursor(1250, 650, 500)
    for _ in range(9):
        p.keyboard.press("Tab")
        p.wait_for_timeout(420)
    r.stop()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    srv, base = _serwer.start(5139)
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch()
            ctx = br.new_context(viewport={"width": W, "height": H}, locale="pl-PL")
            ctx.add_cookies([{"name": "hints_off", "value": "1", "url": base}])
            ctx.add_init_script(KURSOR)
            page = ctx.new_page()
            page.set_default_timeout(15000)
            r = Rezyser(ctx, page, base)
            try:
                sceny(r)
            except Exception:
                page.screenshot(path=str(OUT / "blad.png"))
                print("BŁĄD w scenie", r.sid, "przy", page.url, "– zrzut:", OUT / "blad.png")
                raise
            finally:
                r.kamera.zamknij()
                br.close()
    finally:
        srv.shutdown()
    (OUT / "sceny.json").write_text(json.dumps({"fps": FPS, "sceny": r.sceny}, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
    print("nagranie:", OUT / "nagranie.mp4", f"{r.kamera.n / FPS:.1f} s")


if __name__ == "__main__":
    main()
