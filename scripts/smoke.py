"""Smoke po wdrożeniu: strony odpowiadają, konto demo działa, dopasowanie zwraca karty, układ się nie rozjeżdża.

Uruchom:  python scripts/smoke.py [https://hugme.twapp.pl]   (kod wyjścia 1 = coś nie działa)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from axe_audit import CHECKS_JS  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://hugme.twapp.pl").rstrip("/")


def main():
    fails = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in (1280, 320):
            page = browser.new_page(viewport={"width": width, "height": 800})
            for path in ("/", "/zdrowie", "/biblioteka", "/razem", "/razem/praca"):
                if page.goto(BASE + path).status != 200:
                    fails.append(f"{width}px {path}: status")
            page.goto(BASE + "/")
            page.click("button:has-text(\"Znajdź rozwiązania\")")
            page.wait_for_url("**/wyniki")
            if page.locator(".card--thread").count() < 3:
                fails.append(f"{width}px /wyniki: mniej niż 3 dopasowania")
            page.goto(BASE + "/konto")
            page.locator('form:has(input[name=user_id][value="1"]) button[type=submit]').first.click()  # mieszkanka-rodzic
            page.wait_for_load_state()
            page.goto(BASE + "/moje")
            link = page.locator("a[href^='/zgloszenie/']").first.get_attribute("href")
            page.goto(BASE + link)
            checks = page.evaluate(CHECKS_JS)
            if checks["hscroll"] or checks["clipped"]:
                fails.append(f"{width}px {link}: hscroll={checks['hscroll']} clipped={checks['clipped']}")
            page.goto(BASE + "/konto")
            page.locator('form:has(input[name=user_id][value="5"]) button[type=submit]').first.click()  # koordynatorka Hubu
            page.wait_for_load_state()
            for path in ("/admin", "/admin/uzytkownicy", "/admin/trendy"):
                if page.goto(BASE + path).status != 200:
                    fails.append(f"{width}px {path} (admin): status")
            page.close()
        browser.close()
    print("Smoke OK" if not fails else "Smoke: PROBLEMY\n  " + "\n  ".join(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
