"""Audyt WCAG 2.1 AA: axe-core (Playwright) na wszystkich widokach, desktop 1280 px i telefon 320 px.
Dodatkowo: brak przewijania w poziomie, cele dotykowe >= 44 px, zrzuty ekranu do docs/zrzuty.

Uruchom:  python scripts/axe_audit.py [--zrzuty]
Wynik:    docs/WCAG_RAPORT.md (+ docs/zrzuty/*.png z flagą --zrzuty)"""
import os
import sys
import tempfile
import threading
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["AI_DISABLED"] = "1"

from playwright.sync_api import sync_playwright  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

from app import create_app  # noqa: E402

AXE = ROOT / "scripts" / ".cache" / "axe.min.js"
AXE_URL = "https://cdn.jsdelivr.net/npm/axe-core@4.10.2/axe.min.js"
PORT = 5077
BASE = f"http://127.0.0.1:{PORT}"
VIEWPORTS = {"desktop": {"width": 1280, "height": 800}, "telefon": {"width": 320, "height": 640}}
TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]

# (rola albo None, ścieżka, nazwa zrzutu albo None)
PAGES = [
    (None, "/", "01-start"), (None, "@wyniki", "02-wyniki"), (None, "/wiedza", "05-wiedza"),
    (None, "/wiedza/obszar/rodziny-zd", None), (None, "/wiedza/sciezka-rodziny", "06-sciezka-rodziny"),
    (None, "/wiedza/material/1", None), (None, "/biblioteka", "07-biblioteka"), (None, "/biblioteka/1", "08-innowacja-tester"),
    (None, "/tester", None),
    (None, "/pomysly", None), (None, "/pomysly/1", None), (None, "/posrednik", None), (None, "/konto", None),
    (None, "/dostepnosc", None), (None, "/prywatnosc", None), (None, "/nie-ma-takiej-strony", None),
    ("mieszkaniec", "/moje", None), ("mieszkaniec", "/powiadomienia", None), ("mieszkaniec", "/zgloszenie/1", "03-zgloszenie-watek"),
    ("ngo", "/pomysly/nowy", None), ("ngo", "/pomysly/1", "09-pomysl-asystent"), ("ngo", "/pomysly/1/kanwa", None),
    ("ngo", "/pomysly/1/wniosek/1", "10-generator-wniosku"), ("gmina", "@karta", "11-karta-uslugi"),
    ("ekspert", "/ekspert", None),
    (None, "/razem", "16-razem-start"), (None, "/razem/etap/przedszkole", "17-razem-plan"), (None, "/razem/wizyty", None),
    (None, "/razem/prawa?orzeczenie=nie&szkola=tak", None), (None, "/razem/szkoly", None), (None, "/razem/rodzenstwo", None),
    (None, "/razem/co-po-nas", None), (None, "/razem/miejsca", None), (None, "/razem/sprzet", None),
    (None, "/razem/wydarzenia", None), (None, "/razem/pisma", None), (None, "/razem/pisma/asystent", None),
    (None, "/razem/moje-sprawy", "18-razem-moje-sprawy"),
    (None, "/razem/jestem-potrzebny", "21-potrzebny-start"), (None, "/razem/jestem-potrzebny/latwy", "22-potrzebny-latwy"),
    (None, "/razem/jestem-potrzebny/zglos", None), (None, "/razem/jestem-potrzebny/oferta", None),
    (None, "/razem/jestem-potrzebny/buddy", None), (None, "/razem/jestem-potrzebny/zasady", None),
    (None, "/razem/praca#mapa-pl-h", "23-praca-mapa"), (None, "/razem/praca?woj=malopolskie", None),
    (None, "/demo", "28-demo"), (None, "@scen", "29-scenariusz-pasek"),  # @scen zostawia scenariusz w sesji – ostatni wpis gościa
    ("mieszkaniec", "/razem/przewodnik", "19-razem-przewodnik"),
    ("mieszkaniec", "/razem/jestem-potrzebny/dzienniczek", "24-potrzebny-dzienniczek"),
    ("mieszkaniec", "/razem/jestem-potrzebny/dzienniczek/dyplom/1", None), ("mieszkaniec", "/razem/wytchnienie", None),
    ("mieszkaniec", "/razem/wydarzenia", None),
    ("admin", "/admin", "12-panel-hubu"), ("admin", "/admin/watki", None), ("admin", "/admin/luki", "13-luki"),
    ("admin", "/admin/trendy", "14-trendy"), ("admin", "/admin/biblioteka", None), ("admin", "/admin/biblioteka/1", None),
    ("admin", "/admin/import", None), ("admin", "/admin/nabory", None), ("admin", "/admin/poczta", None),
    ("admin", "/zgloszenie/1", "04-decyzja-hubu"), ("admin", "/admin/razem", "20-razem-panel"),
    ("admin", "/admin/potrzebny", "25-potrzebny-panel"),
    ("admin", "/admin/uzytkownicy", "26-uzytkownicy"), ("admin", "/admin/uzytkownicy/2", None), ("admin", "/admin/uzytkownicy/nowy", None),
    ("admin", "/admin/role", "27-role"),
]
ROLE_UID = {"mieszkaniec": 1, "ngo": 2, "gmina": 3, "ekspert": 4, "admin": 5}  # id kont demo z seeda


def serve():
    db = Path(tempfile.mkdtemp()) / "audit.db"
    app = create_app({"DATABASE": str(db), "SECRET_KEY": "audit", "DEMO_ACCOUNTS": True})
    server = make_server("127.0.0.1", PORT, app, threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def login(page, role):
    page.goto(f"{BASE}/konto")
    page.locator(f'form:has(input[name=user_id][value="{ROLE_UID[role]}"]) button[type=submit]').first.click()
    page.wait_for_load_state()


def open_path(page, path):
    if path == "@wyniki":
        page.goto(BASE + "/")
        page.click("button:has-text(\"Znajdź rozwiązania\")")
    elif path == "@karta":
        page.goto(BASE + "/posrednik")
        page.check("input[name=institution][value=gmina]")
        page.select_option("#f-audience", "seniorzy")
        page.select_option("#f-scale", "srednia")
        page.select_option("#f-budget", "maly")
        page.fill("#f-problem", "Starsi mieszkańcy pięciu sołectw nie mają jak dojechać do przychodni.")
        page.click("text=Przygotuj kartę usługi")
    elif path == "@scen":  # pasek scenariusza demo: pierwszy krok pierwszego scenariusza
        page.goto(BASE + "/demo")
        page.locator("button:has-text(\"Rozpocznij\")").first.click()
    elif path == "/pomysly/1" :
        page.goto(BASE + path)
        if page.locator("text=Zapytaj asystenta").count():
            page.click("text=Zapytaj asystenta")
    else:
        page.goto(BASE + path)
    page.wait_for_load_state()


CHECKS_JS = """() => {
  const doc = document.documentElement;
  const small = [...document.querySelectorAll('a.btn, button, input[type=radio], input[type=checkbox], select, .nav a')]
    .filter(el => el.offsetParent !== null)
    .filter(el => { const r = el.getBoundingClientRect(); return r.height < 24 || (el.matches('.btn, button, .nav a') && r.height < 44); })
    .map(el => (el.textContent || el.name || el.tagName).trim().slice(0, 40));
  // tekst karty z paskiem obszaru nie może wchodzić pod pasek ani wychodzić poza kartę
  const clipped = [...document.querySelectorAll('.card--thread')].filter(c => c.offsetParent).flatMap(c => {
    const r = c.getBoundingClientRect(), left = r.left + 8;
    return [...c.querySelectorAll('h2, h3, p')].filter(e => e.offsetParent && e.textContent.trim() && !e.closest('.help__panel'))  // chmurka „i” to okienko, nie tekst karty
      .filter(e => { const q = e.getBoundingClientRect(); return q.left < left || q.right > r.right + 1; })
      .slice(0, 1).map(e => e.textContent.trim().slice(0, 40));
  });
  return {hscroll: doc.scrollWidth > doc.clientWidth + 1, small, clipped};
}"""


def main(screens=False):
    if not AXE.exists():
        AXE.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(AXE_URL, AXE)
    axe_src = AXE.read_text(encoding="utf-8")
    shots = ROOT / "docs" / "zrzuty"
    shots.mkdir(parents=True, exist_ok=True)
    server = serve()
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vp_name, vp in VIEWPORTS.items():
            ctx = browser.new_context(viewport=vp, bypass_csp=True, locale="pl-PL")  # bypass_csp tylko by wstrzyknąć axe
            page = ctx.new_page()
            current_role = "?"
            for role, path, shot in PAGES:
                if role != current_role:
                    ctx.clear_cookies()
                    if role:
                        login(page, role)
                    current_role = role
                open_path(page, path)
                page.evaluate(axe_src)
                axe = page.evaluate("async (tags) => await axe.run(document, {runOnly: {type: 'tag', values: tags}})", TAGS)
                extra = page.evaluate(CHECKS_JS)
                results.append({"vp": vp_name, "role": role or "gość", "path": path, "url": page.url.replace(BASE, ""),
                                "violations": [(v["id"], v["impact"], len(v["nodes"]), v["help"],
                                                [n["target"][0] for n in v["nodes"][:3]]) for v in axe["violations"]],
                                "passes": len(axe["passes"]), **extra})
                if screens and shot:
                    page.screenshot(path=str(shots / f"{shot}-{vp_name}.png"), full_page=vp_name == "telefon")
            # Tryb wysokiego kontrastu i większego tekstu – strona startowa
            for pref in ("kontrast", "duzy-tekst"):
                ctx.clear_cookies()
                page.goto(BASE + "/")
                page.locator(f"form:has(input[value={pref}]) button").click()
                page.wait_for_load_state()
                page.evaluate(axe_src)
                axe = page.evaluate("async (tags) => await axe.run(document, {runOnly: {type: 'tag', values: tags}})", TAGS)
                extra = page.evaluate(CHECKS_JS)
                results.append({"vp": vp_name, "role": f"gość ({pref})", "path": "/", "url": "/",
                                "violations": [(v["id"], v["impact"], len(v["nodes"]), v["help"],
                                                [n["target"][0] for n in v["nodes"][:3]]) for v in axe["violations"]],
                                "passes": len(axe["passes"]), **extra})
                if screens and vp_name == "telefon" and pref == "kontrast":
                    page.screenshot(path=str(shots / "15-wysoki-kontrast-telefon.png"))
            ctx.close()
        layout_bad = layout_big_text(browser) + keyboard_flows(browser)
        browser.close()
    server.shutdown()
    write_report(results, layout_bad)
    bad = [r for r in results if r["violations"] or r["hscroll"] or r["clipped"]]
    print(f"Widoków sprawdzonych: {len(results)}; z problemami: {len(bad)}; "
          f"układ telefon A+: {len(PAGES)} widoków, z problemami: {len(layout_bad)}")
    for r in bad:
        print(f"  [{r['vp']}] {r['role']} {r['url']}: {r['violations']} hscroll={r['hscroll']} clipped={r['clipped']}")
    for line in layout_bad:
        print("  " + line)
    return 1 if bad or layout_bad else 0


FOCUS_JS = """() => { const e = document.activeElement, cs = getComputedStyle(e);
  return {tag: e.tagName, text: (e.innerText || e.value || e.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').trim().slice(0, 40),
          visible: e !== document.body && (parseFloat(cs.outlineWidth) >= 2 && cs.outlineStyle !== 'none' || cs.boxShadow !== 'none')}; }"""


def tab_to(page, label, limit=80):
    """Naciska Tab, aż fokus trafi na element z tekstem `label`; po drodze każdy fokus musi być widoczny."""
    for _ in range(limit):
        page.keyboard.press("Tab")
        f = page.evaluate(FOCUS_JS)
        if not f["visible"]:
            return f"niewidoczny fokus na {f['tag']} „{f['text']}”"
        if label in f["text"]:
            return None
    return f"„{label}” nieosiągalne Tabem w {limit} krokach"


def keyboard_flows(browser):
    """Główne ścieżki tylko klawiaturą: skip link, wyszukiwanie, wybór konta demo (2.1.1, 2.4.1, 2.4.7)."""
    ctx = browser.new_context(viewport=VIEWPORTS["desktop"], locale="pl-PL")
    page, bad = ctx.new_page(), []
    page.goto(BASE + "/")
    page.keyboard.press("Tab")
    if "Przejdź do treści" not in page.evaluate(FOCUS_JS)["text"]:
        bad.append("[klawiatura] / : pierwszy Tab nie trafia w „Przejdź do treści”")
    page.keyboard.press("Enter")
    if page.evaluate("document.activeElement.id") != "tresc":
        bad.append("[klawiatura] / : skip link nie przenosi fokusu do treści")
    if err := tab_to(page, "Znajdź rozwiązania"):
        bad.append(f"[klawiatura] / : {err}")
    else:
        with page.expect_navigation():
            page.keyboard.press("Enter")
        if "/wyniki" not in page.url:
            bad.append("[klawiatura] / : Enter na „Znajdź rozwiązania” nie prowadzi do wyników")
    page.goto(BASE + "/konto")
    if err := tab_to(page, "Wejdź jako koordynatorka"):
        bad.append(f"[klawiatura] /konto: {err}")
    else:
        with page.expect_navigation():
            page.keyboard.press("Enter")
        page.goto(BASE + "/admin")
        if err := tab_to(page, "Skrzynka"):
            bad.append(f"[klawiatura] /admin: {err}")
    ctx.close()
    return bad


def layout_big_text(browser):
    """Telefon 320 px z A+ (137,5 %): tylko układ – przewijanie w bok i tekst poza kartą. Axe nie zależy od rozmiaru tekstu."""
    ctx = browser.new_context(viewport=VIEWPORTS["telefon"], locale="pl-PL")
    page, current_role, bad = ctx.new_page(), "?", []
    for role, path, _ in PAGES:
        if role != current_role:
            ctx.clear_cookies()
            ctx.add_cookies([{"name": "a11y_size", "value": "1", "url": BASE}])
            if role:
                login(page, role)
            current_role = role
        open_path(page, path)
        extra = page.evaluate(CHECKS_JS)
        if extra["hscroll"] or extra["clipped"]:
            bad.append(f"[telefon A+] {role or 'gość'} {page.url.replace(BASE, '')}: hscroll={extra['hscroll']} clipped={extra['clipped']}")
    ctx.close()
    return bad


def write_report(results, layout_bad=()):
    lines = ["# Raport audytu WCAG 2.1 AA (axe-core + Playwright)", "",
             "Wygenerowany przez `python scripts/axe_audit.py`. Reguły axe: " + ", ".join(TAGS) + ".",
             "Widoki: desktop 1280 px i telefon 320 px; dodatkowo tryb wysokiego kontrastu i A+.", "",
             f"**Sprawdzonych widoków:** {len(results)} · **z naruszeniami axe:** "
             f"{sum(1 for r in results if r['violations'])} · **z przewijaniem w poziomie:** "
             f"{sum(1 for r in results if r['hscroll'])} · **układ na telefonie z A+ (wszystkie widoki):** "
             f"{'bez problemów ✔' if not layout_bad else f'{len(layout_bad)} z problemami ⚠'}", "",
             "| Ekran | Rola | Ścieżka | Naruszenia axe | Reguły zaliczone | Przewijanie w bok | Małe cele dotykowe |",
             "|---|---|---|---|---|---|---|"]
    for r in results:
        v = ", ".join(f"{i} ({imp}, {n})" for i, imp, n, *_ in r["violations"]) or "brak ✔"
        lines.append(f"| {r['vp']} | {r['role']} | `{r['url']}` | {v} | {r['passes']} | "
                     f"{'TAK ⚠' if r['hscroll'] else 'nie ✔'} | {', '.join(r['small']) or 'brak ✔'} |")
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "WCAG_RAPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main(screens="--zrzuty" in sys.argv))
