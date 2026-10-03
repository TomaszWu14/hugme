"""Nagranie przeklikania do filmu (bez dźwięku) wg docs/SCENARIUSZ_FILMU.md – Playwright, 1920×1080, ~3 min.

Uruchom:  python scripts/film.py [katalog_wyjściowy]
Wynik:    <katalog>/hugme-przeklikanie.webm (+ .mp4, jeśli ffmpeg Playwrighta ma kodek H.264).
Nagrywa na lokalnym serwerze ze świeżą bazą (nic nie trafia na produkcję); kursor rysowany nakładką."""
import glob
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import axe_audit as A  # noqa: E402  (serve() – świeża baza na :5077)
from playwright.sync_api import sync_playwright  # noqa: E402

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "docs" / "film")
W, H, ZOOM = 1920, 1080, 1.25  # wideo 1920×1080; 125% powiększenia przez CSS zoom (Playwright nie skaluje wideo w górę)

CURSOR_JS = """
(() => {
  const dot = document.createElement('div');
  dot.id = 'film-cursor';
  Object.assign(dot.style, {position: 'fixed', left: '-40px', top: '-40px', width: '22px', height: '22px',
    borderRadius: '50%', background: 'rgba(184,67,47,.85)', border: '3px solid #fff', boxShadow: '0 0 0 3px rgba(27,37,64,.35)',
    pointerEvents: 'none', zIndex: '2147483647', transform: 'translate(-50%,-50%)', transition: 'width .15s, height .15s'});
  const add = () => { document.documentElement.style.zoom = '1.25'; document.body && document.body.appendChild(dot); };
  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', add) : add();
  document.addEventListener('mousemove', e => { dot.style.left = e.clientX + 'px'; dot.style.top = e.clientY + 'px'; }, true);
  document.addEventListener('mousedown', () => { dot.style.width = '34px'; dot.style.height = '34px'; }, true);
  document.addEventListener('mouseup', () => { dot.style.width = '22px'; dot.style.height = '22px'; }, true);
})();
"""

T0 = time.time()


def clock():
    return time.time() - T0


def until(sec):
    """Czeka do danej sekundy filmu (rytm scen jak w scenariuszu)."""
    time.sleep(max(0.0, sec - clock()))


class Film:
    def __init__(self, page):
        self.page = page
        self.mouse = (W / 2, H / 2)

    def move(self, x, y, steps=30):
        self.page.mouse.move(x, y, steps=steps)
        self.mouse = (x, y)

    def click(self, selector, pause=0.6, nav=False, edge=False):
        """Klik „ludzką” myszą; nav=True czeka na nawigację; edge=True klika przy początku (linki wielowierszowe)."""
        el = self.page.locator(selector).first
        el.scroll_into_view_if_needed()
        time.sleep(0.3)
        box = el.bounding_box()
        if edge:
            x, y = box["x"] + min(24, box["width"] / 2), box["y"] + min(14, box["height"] / 2)
        else:
            x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        self.move(x, y)
        time.sleep(pause)
        if nav:
            with self.page.expect_navigation(timeout=15000):
                self.page.mouse.click(x, y)
            self.page.wait_for_load_state()
        else:
            self.page.mouse.down()
            time.sleep(0.12)
            self.page.mouse.up()
        time.sleep(0.4)

    def type(self, selector, text, delay=55):
        self.click(selector)
        self.page.keyboard.press("End")
        self.page.keyboard.type(text, delay=delay)

    def scroll(self, px, secs=2.0):
        steps = max(1, int(secs * 20))
        for _ in range(steps):
            self.page.mouse.wheel(0, px / steps)
            time.sleep(secs / steps)

    def goto(self, path):
        self.page.goto(A.BASE + path)
        self.page.wait_for_load_state()
        time.sleep(0.6)

    def role(self, label_part):
        """Przełącza konto w pasku „Tryb demo” (widoczne dla widza)."""
        sel = self.page.locator("#role-switch")
        sel.scroll_into_view_if_needed()
        value = self.page.evaluate("(part) => [...document.querySelectorAll('#role-switch option')].find(o => o.textContent.includes(part)).value",
                                   label_part)
        self.click("#role-switch", pause=0.3)
        sel.select_option(value)
        time.sleep(0.4)
        self.click("form.role-switch button", nav=True)
        self.page.wait_for_load_state()
        time.sleep(0.6)


def record(page):
    f = Film(page)
    # 0:00 Start – powolne przewinięcie
    f.goto("/")
    f.move(700, 300)
    time.sleep(1.5)
    f.scroll(700, 4.0)
    time.sleep(1.0)
    f.scroll(-700, 2.5)
    until(14)
    # 0:15 Pole „Co jest trudne?”
    f.type("#f-opis", " Mój syn Kacper, tel. 600 123 456.")
    time.sleep(1.0)
    f.click("button:has-text('Znajdź rozwiązania')", nav=True)
    page.wait_for_url("**/wyniki")
    until(34)
    # 0:35 Wyniki
    time.sleep(2.0)
    f.scroll(350, 3.0)
    time.sleep(2.5)
    f.scroll(400, 3.0)
    first = page.locator("article.match").first
    box = first.bounding_box()
    if box:
        f.move(box["x"] + 200, box["y"] + 80)
    time.sleep(3.0)
    f.scroll(-750, 2.0)
    until(58)
    # 1:00 Zapis zgłoszenia
    f.click("button:has-text('Zapisz zgłoszenie')", nav=True)
    page.wait_for_url(lambda u: "/konto" in u or "/zgloszenie/" in u)
    if "/konto" in page.url:  # gość: wybór konta, szkic czeka w sesji
        f.click("form button[type=submit].btn--primary", nav=True)
        page.wait_for_load_state()
        time.sleep(0.8)
    if "/zgloszenie/" not in page.url:
        if not page.url.rstrip("/").endswith("/wyniki"):
            f.goto("/wyniki")
        f.click("button:has-text('Zapisz zgłoszenie')", nav=True)
        page.wait_for_url("**/zgloszenie/*")
    time.sleep(1.5)
    f.scroll(500, 2.0)
    f.click("button[value=pomocne]", nav=True)
    page.wait_for_load_state()
    until(74)
    # 1:15 Panel Hubu – koordynatorka
    f.role("Koordynatorka")
    f.goto("/admin")
    time.sleep(1.5)
    f.scroll(600, 2.0)
    f.click("table tbody tr:has(td:text-is('Zgłoszenie')) a", nav=True, edge=True)
    page.wait_for_load_state()
    time.sleep(1.0)
    page.locator("#f-status").select_option("polaczone")
    time.sleep(0.6)
    f.click("button:has-text('Zapisz i powiadom autora')", nav=True)
    page.wait_for_load_state()
    time.sleep(0.8)
    f.type("#f-tresc", "Dziękujemy! Łączymy Państwa z Asystentem zdrowia rodziny z powiatu wadowickiego – zadzwonię w tym tygodniu.", delay=28)
    f.click("form[action^='/watek'] button:has-text('Wyślij')", nav=True)
    page.wait_for_load_state()
    until(99)
    # 1:40 Razem z ZD – plan
    f.goto("/razem")
    time.sleep(1.2)
    f.click("button.stage-btn:has-text('Przedszkole')", nav=True)
    page.wait_for_load_state()
    time.sleep(1.5)
    f.scroll(500, 3.0)
    until(114)
    # 1:55 Jestem potrzebny – zgłoszenie w łatwym tekście (mieszkanka), para i misja (koordynatorka), dzienniczek
    f.role("Mieszkanka")
    f.goto("/razem/jestem-potrzebny/latwy")
    time.sleep(1.0)
    f.click("label.picto-choice:has(input[name=interests][value=psy])")
    f.click("label.picto-choice:has(input[name=days][value=sb])")
    f.click("label.picto-choice:has(input[name=companion][value=rodzic])")
    f.type("#f-alias", "Zosia")
    page.locator("#f-powiat").select_option("wadowicki")
    f.click("#f-consent")
    f.click("button:has-text('Wyślij')", nav=True)
    page.wait_for_load_state()
    time.sleep(2.0)
    f.role("Koordynatorka")
    f.goto("/admin/potrzebny")
    time.sleep(1.0)
    f.click("li.actions:has-text('Zosia') button:has-text('Połącz')", nav=True)
    page.wait_for_load_state()
    time.sleep(1.2)
    f.click("li:has-text('Zosia') button:has-text('Misja odbyła się')", nav=True)
    page.wait_for_load_state()
    time.sleep(1.0)
    f.role("Mieszkanka")
    f.goto("/razem/jestem-potrzebny/dzienniczek")
    page.locator("section:has-text('Zosia')").first.scroll_into_view_if_needed()
    time.sleep(0.5)
    f.scroll(120, 1.0)
    until(144)
    # 2:25 Praca – mapa
    f.goto("/razem/praca#mapa-pl-h")
    time.sleep(1.5)
    f.click("a[aria-label^='małopolskie']", nav=True)
    page.wait_for_load_state()
    page.locator("#lista-h").scroll_into_view_if_needed()
    time.sleep(0.5)
    f.scroll(200, 1.5)
    until(152)
    # 2:33 Pośrednik – gmina
    f.role("Gmina")
    f.goto("/posrednik")
    page.check("input[name=institution][value=gmina]")
    page.select_option("#f-audience", "seniorzy")
    page.select_option("#f-scale", "srednia")
    page.select_option("#f-budget", "maly")
    f.type("#f-problem", "Starsi mieszkańcy pięciu sołectw nie mają jak dojechać do przychodni.", delay=20)
    f.click("button:has-text('Przygotuj kartę usługi')", nav=True)
    page.wait_for_load_state()
    time.sleep(1.0)
    f.scroll(400, 2.0)
    until(160)
    # 2:41 Trendy i luki – koordynatorka
    f.role("Koordynatorka")
    f.goto("/admin/trendy")
    f.scroll(500, 2.5)
    time.sleep(0.5)
    f.goto("/admin/luki")
    time.sleep(2.0)
    until(168)
    # 2:49 Dostępność
    f.click("form:has(input[value=duzy-tekst]) button", nav=True)
    page.wait_for_load_state()
    time.sleep(1.2)
    f.click("form:has(input[value=kontrast]) button", nav=True)
    page.wait_for_load_state()
    time.sleep(1.5)
    until(173)
    # 2:54 Strona startowa (kontrast wyłączony)
    f.click("form:has(input[value=kontrast]) button", nav=True)
    page.wait_for_load_state()
    f.click("form:has(input[value=duzy-tekst]) button", nav=True)
    page.wait_for_load_state()
    f.goto("/")
    f.move(760, 420, steps=40)
    until(180)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in glob.glob(str(OUT / "*.webm")):
        os.remove(old)
    server = A.serve()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": W, "height": H}, locale="pl-PL",
                                  bypass_csp=True, record_video_dir=str(OUT), record_video_size={"width": 1920, "height": 1080})
        ctx.add_init_script(CURSOR_JS)
        page = ctx.new_page()
        page.set_default_timeout(15000)
        global T0
        T0 = time.time()  # zegar scen od pierwszej sceny, nie od startu serwera
        try:
            record(page)
        except Exception:
            page.screenshot(path=str(OUT / "blad.png"))
            print("BŁĄD przy", page.url, "po", round(clock()), "s – zrzut:", OUT / "blad.png")
            raise
        finally:
            ctx.close()
            browser.close()
    server.shutdown()
    webm = Path(glob.glob(str(OUT / "*.webm"))[0])
    final = OUT / "hugme-przeklikanie.webm"
    shutil.move(webm, final)
    print("webm:", final, final.stat().st_size // 1024, "KB,", round(clock()), "s")
    try:  # ffmpeg Playwrighta ma tylko VP8 – do MP4 (H.264) potrzebny pełny ffmpeg: pip install imageio-ffmpeg
        import imageio_ffmpeg
        ff = [imageio_ffmpeg.get_ffmpeg_exe()]
    except ImportError:
        ff = [shutil.which("ffmpeg")]
    if ff and ff[0]:
        mp4 = OUT / "hugme-przeklikanie.mp4"
        r = subprocess.run([ff[0], "-y", "-loglevel", "error", "-i", str(final), "-c:v", "libx264", "-preset", "medium",
                            "-crf", "22", "-pix_fmt", "yuv420p", "-r", "25", "-movflags", "+faststart", str(mp4)])
        print("mp4:", mp4 if r.returncode == 0 else f"ffmpeg bez H.264 (kod {r.returncode}) – zostaje webm")


if __name__ == "__main__":
    main()
