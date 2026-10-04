"""Nagrywa dwa scenariusze HugMe (Playwright, 1920×1080) + znaczniki kroków do demo/out/kroki.json.

Każdy scenariusz w osobnym kontekście (osobny plik .webm). Widoczny kursor i kółko kliknięcia wstrzyknięte
add_init_script. Asercje po każdym kroku – scenariusz, który się wysypie, przerywa skrypt (nie nagrywamy błędu).
Uruchom: python demo/nagraj.py   (HUGME_ROOT=<kopia repo> opcjonalnie)."""
import json
import shutil
import sys
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _serwer  # noqa: E402

OUT = HERE / "out"
VID = OUT / "nagrania"
W, H = 1920, 1080

KURSOR = """
(() => {
  const pos = JSON.parse(sessionStorage.getItem('demoKursor') || '[960,540]');
  function put() {
    if (!document.body || document.getElementById('demo-kursor')) return;
    const c = document.createElement('div');
    c.id = 'demo-kursor';
    Object.assign(c.style, {position: 'fixed', left: '0', top: '0', width: '30px', height: '30px', marginLeft: '-15px',
      marginTop: '-15px', borderRadius: '50%', background: 'rgba(184,67,47,.35)', border: '3px solid #B8432F',
      zIndex: 2147483647, pointerEvents: 'none', transform: `translate(${pos[0]}px,${pos[1]}px)`});
    document.body.appendChild(c);
    document.addEventListener('mousemove', e => {
      c.style.transform = `translate(${e.clientX}px,${e.clientY}px)`;
      sessionStorage.setItem('demoKursor', JSON.stringify([e.clientX, e.clientY]));
    }, true);
    document.addEventListener('mousedown', e => {
      const r = document.createElement('div');
      Object.assign(r.style, {position: 'fixed', left: e.clientX - 30 + 'px', top: e.clientY - 30 + 'px', width: '60px',
        height: '60px', borderRadius: '50%', border: '5px solid #B8432F', zIndex: 2147483646, pointerEvents: 'none',
        transition: 'transform .5s ease-out, opacity .5s ease-out', transform: 'scale(.3)', opacity: '1'});
      document.body.appendChild(r);
      requestAnimationFrame(() => { r.style.transform = 'scale(1.6)'; r.style.opacity = '0'; });
      setTimeout(() => r.remove(), 700);
    }, true);
  }
  document.addEventListener('DOMContentLoaded', put);
  put();
})();
"""


class Rec:
    """Jeden scenariusz: strona, zegar od startu nagrania, podpisy kroków i fragmenty do wycięcia."""

    def __init__(self, browser, base, name):
        self.base, self.name = base, name
        self.ctx = browser.new_context(viewport={"width": W, "height": H}, record_video_dir=str(VID),
                                       record_video_size={"width": W, "height": H}, locale="pl-PL", bypass_csp=True)
        self.ctx.add_cookies([{"name": "hints_off", "value": "1", "url": base}])
        self.ctx.add_init_script(KURSOR)
        self.page = self.ctx.new_page()
        self.t0 = time.monotonic()
        self.steps, self.cuts, self.start = [], [], 0.0
        self.ekran = self.tklik = 0.0  # chwila pojawienia się nowej strony / kliknięcia (do podpisów i cięć)
        # czas z eventu, nie z powrotu goto/click – te wracają dopiero po slow_mo, gdy nowa strona już widać
        self.page.on("framenavigated", lambda f: f == self.page.main_frame and setattr(self, "ekran", self.t()))

    def t(self):
        return round(time.monotonic() - self.t0, 2)

    def krok(self, text, t=None):
        """Podpis kroku od chwili t (domyślnie teraz; r.ekran = od pojawienia się nowej strony, bez czekania na networkidle)."""
        self.steps.append([self.t() if t is None else t, text])

    def pauza(self, ms=1200):
        self.page.wait_for_timeout(ms)

    def go(self, path):
        self.page.goto(self.base + path, wait_until="commit")
        self.page.wait_for_load_state("networkidle")

    def login(self, uid, nxt):
        """Zmiana konta demo – fragment wycinany w montażu (ekran wyboru konta nic nie wnosi)."""
        a = self.t()
        self.go(f"/konto?next={nxt}")
        self.page.locator(f'form:has(input[name=user_id][value="{uid}"]) button').first.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(300)
        self.cuts.append([a, self.t()])

    def klik(self, loc, wait=True):
        loc = loc.first
        loc.scroll_into_view_if_needed()
        box = loc.bounding_box()
        self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=12)
        self.page.wait_for_timeout(150)
        self.tklik = self.t()
        if not wait:
            loc.click()
            return
        with self.page.expect_navigation(wait_until="commit"):
            loc.click()
        self.page.wait_for_load_state("networkidle")

    def wytnij_czekanie(self):
        """Wytnij ekran ładowania między kliknięciem (zostaw 0,7 s z kółkiem) a nową stroną."""
        print(f"  {self.name}: czekanie po kliknięciu {self.ekran - self.tklik:.2f} s")
        if self.ekran - self.tklik > 1.0:
            self.cuts.append([self.tklik + 0.7, self.ekran])

    def wskaz(self, loc):
        """Najedź kursorem na element (bez klikania)."""
        loc = loc.first
        loc.scroll_into_view_if_needed()
        box = loc.bounding_box()
        self.page.mouse.move(box["x"] + 120, box["y"] + box["height"] / 2, steps=12)

    def pisz(self, sel, text, delay=30):
        loc = self.page.locator(sel)
        self.klik(loc, wait=False)
        loc.fill("")
        loc.press_sequentially(text, delay=delay)

    def przewin(self, px):
        self.page.evaluate(f"window.scrollBy({{top: {px}, behavior: 'smooth'}})")
        self.page.wait_for_timeout(700)

    def pokaz(self, loc, od=None):
        """Płynnie przewiń do elementu (asercja to_be_visible nie sprawdza, czy jest w kadrze).
        od=czas: przewiń natychmiast i wytnij wszystko od tej chwili – widz od razu widzi element, nie górę strony."""
        if od is None:
            loc.first.evaluate("e => e.scrollIntoView({behavior: 'smooth', block: 'start'})")
            self.page.wait_for_timeout(800)
            return
        loc.first.evaluate("e => e.scrollIntoView({behavior: 'instant', block: 'start'})")
        self.page.wait_for_timeout(150)
        self.cuts.append([od, self.t()])

    def koniec(self):
        end = self.t()
        video = self.page.video
        self.ctx.close()
        dst = VID / f"{self.name}.webm"
        shutil.move(video.path(), dst)
        return {"video": str(dst), "start": self.start, "end": end, "cuts": self.cuts, "steps": self.steps}


def scenariusz_1(r):
    p = r.page
    r.login(1, "/razem/jestem-potrzebny/zglos")
    r.start = r.cuts.pop()[1]  # początek filmu = gotowy formularz (bez białej klatki i logowania)
    expect(p.get_by_role("heading", name="Zgłaszam uczestnika")).to_be_visible()
    r.krok("Anna – mama nastolatka z zespołem Downa – zgłasza syna")
    r.pauza(900)
    r.pisz("#f-alias", "Franek", delay=90)
    r.klik(p.locator("#f-powiat"), wait=False)
    p.select_option("#f-powiat", "wadowicki")
    r.klik(p.locator("label.choice:has(input[name=age_group][value=mlodziez])"), wait=False)
    r.krok("Co lubi i kiedy może – bez diagnozy i daty urodzenia")
    r.klik(p.locator("label.picto-choice:has(input[name=interests][value=psy])"), wait=False)
    for v in ("sb", "nd", "rano"):
        r.klik(p.locator(f"label.choice:has(input[name=days][value={v}])"), wait=False)
    r.klik(p.locator("label.choice:has(input[name=companion][value=rodzic])"), wait=False)
    r.klik(p.locator("#f-consent"), wait=False)
    expect(p.locator("input[name=interests][value=psy]")).to_be_checked()
    expect(p.locator("#f-consent")).to_be_checked()
    r.klik(p.get_by_role("button", name="Wyślij zgłoszenie"))
    expect(p.get_by_role("heading", name="Mój dzienniczek")).to_be_visible()
    franek = p.locator("section.card", has=p.get_by_role("heading", name="Franek", exact=True))
    expect(franek).to_contain_text("Hub szuka dla Ciebie miejsca")
    r.pokaz(franek, od=r.ekran)  # bez kadru z cudzą kartą („Ania”) na górze dzienniczka
    r.krok("Zgłoszenie wysłane – dzienniczek: „Hub szuka dla Ciebie miejsca”")
    r.pauza(2300)

    r.login(5, "/admin/potrzebny")
    r.krok("Koordynatorka Hubu widzi gotowe pary: Franek ↔ schronisko w Wadowicach")
    para = p.locator("li", has_text="Franek").filter(has_text="Schronisko dla zwierząt w Wadowicach")
    expect(para.first).to_be_visible()
    para.first.scroll_into_view_if_needed()
    r.pauza(1300)
    r.krok("Jedno kliknięcie „Połącz” – rodzina dostaje powiadomienie")
    r.klik(para.first.get_by_role("button", name="Połącz"))
    expect(p.get_by_text("Franek").first).to_be_visible()
    r.pauza(1800)

    r.login(1, "/powiadomienia")
    r.krok("Anna dostaje powiadomienie: Hub połączył Franka z miejscem")
    note = p.get_by_role("link", name="Hub połączył Cię z miejscem").first
    expect(note).to_be_visible()
    r.pauza(1300)
    r.klik(note)
    expect(p.get_by_role("heading", name="Mój dzienniczek")).to_be_visible()
    franek = p.locator("section.card", has=p.get_by_role("heading", name="Franek", exact=True))
    expect(franek).to_contain_text("Schronisko dla zwierząt w Wadowicach")
    expect(franek).not_to_contain_text("Hub szuka dla Ciebie miejsca")
    r.pokaz(franek, od=r.ekran)
    r.krok("W dzienniczku Franka: misja – spacery z psami w schronisku")
    r.pauza(1800)

    r.go("/razem/praca")
    expect(p.get_by_role("heading", name="Gdzie pracują osoby z zespołem Downa")).to_be_visible()
    r.krok("Dalej: mapa miejsc pracy i zajęć dla osób z ZD", r.ekran)
    r.pauza(900)
    mapa = p.locator("section[aria-labelledby=mapa-pl-h]")
    expect(mapa.locator("svg.map")).to_be_visible()
    r.pokaz(mapa)
    r.pauza(1800)


def scenariusz_2(r):
    p = r.page
    r.login(3, "/")
    r.start = r.cuts.pop()[1]
    expect(p.locator("#f-opis")).to_be_visible()
    r.krok("Urzędnik gminy opisuje problem własnymi słowami")
    r.pisz("#f-opis", "Seniorzy z pięciu sołectw nie mają jak dojechać do lekarza. Brakuje transportu.", delay=25)
    p.select_option("#f-powiat", "dąbrowski")
    r.pauza(500)
    r.klik(p.get_by_role("button", name="Znajdź rozwiązania"))
    r.wytnij_czekanie()  # „Szukam rozwiązań…” – martwy fragment
    bus = p.locator(".match", has_text="Bus na Telefon").first
    expect(bus).to_be_visible()
    expect(bus).to_contain_text("Bardzo pasuje")
    r.krok("Wynik: „Bus na Telefon” – Bardzo pasuje, z wyjaśnieniem dlaczego", r.ekran)
    bus.scroll_into_view_if_needed()
    r.pauza(2600)
    href = bus.locator("a[href^='/biblioteka/']").first.get_attribute("href")
    r.krok("Zgłoszenie trafia do skrzynki Hubu")  # od przewinięcia do formularza zapisu
    r.klik(p.get_by_role("button", name="Zapisz zgłoszenie"))
    expect(p.get_by_text("Zgłoszenie zapisane").first).to_be_visible()
    r.pauza(2000)

    r.go(href)
    expect(p.get_by_role("heading", name="Bus na Telefon").first).to_be_visible()
    r.krok("Karta innowacji → „Dopasuj do mojej gminy”", r.ekran)
    r.pauza(900)
    r.klik(p.get_by_role("link", name="Dopasuj do mojej gminy"))
    expect(p.get_by_role("button", name="Przygotuj kartę usługi")).to_be_visible()
    r.krok("Pośrednik: kim jesteś, dla kogo, skala, budżet", r.ekran)
    gmina = p.locator("input[name=institution][value=gmina]")
    if not gmina.is_checked():
        r.klik(p.locator("label.choice:has(input[name=institution][value=gmina])"), wait=False)
    p.select_option("#f-audience", "seniorzy")
    if not p.input_value("#f-problem").strip():
        r.pisz("#f-problem", "Seniorzy z pięciu sołectw nie mają jak dojechać do lekarza.")
    expect(gmina).to_be_checked()
    r.pauza(800)
    r.klik(p.get_by_role("button", name="Przygotuj kartę usługi"))
    expect(p.locator("button[data-druk]")).to_be_visible()
    r.krok("Gotowa karta usługi dla gminy – do druku lub PDF", r.ekran)
    r.pauza(1300)
    r.przewin(450)
    r.pauza(900)

    r.login(5, "/admin")
    expect(p.get_by_role("heading", name="Skrzynka")).to_be_visible()
    r.krok("Hub ROPS: zgłoszenie gminy w skrzynce")
    wiersz = p.locator("tr", has_text="Seniorzy z pięciu sołectw").first
    expect(wiersz).to_be_visible()
    r.wskaz(wiersz)
    r.pauza(1500)
    r.go("/admin/trendy")
    expect(p.get_by_role("heading", name="Trendy potrzeb i luki")).to_be_visible()
    r.krok("Trendy potrzeb i luki – gdzie brakuje rozwiązań w Małopolsce", r.ekran)
    r.pauza(900)
    luki = p.locator("section[aria-labelledby=luki]")
    expect(luki).to_be_visible()
    r.pokaz(luki)
    r.pauza(1800)


def main():
    if VID.exists():
        shutil.rmtree(VID)
    VID.mkdir(parents=True)
    srv, base = _serwer.start(5137)
    result = {}
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(slow_mo=300)
            for name, fn in (("scenariusz1", scenariusz_1), ("scenariusz2", scenariusz_2)):
                r = Rec(br, base, name)
                fn(r)
                result[name] = r.koniec()
                print(name, "OK", result[name]["end"], "s")
            br.close()
    finally:
        srv.shutdown()
    (OUT / "kroki.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
