"""Zrzuty 1920×1080 do prezentacji: świeża baza z seedem, AI wyłączone, Podpowiedzi wyłączone.

Uruchom: python demo/zrzuty.py   (opcjonalnie HUGME_ROOT=<czysta kopia main>)."""
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from _serwer import start

OUT = Path(__file__).resolve().parent / "zrzuty"
OPIS = "Syn z zespołem Downa po szkole chce pracować, ale nie wiemy, gdzie szukać pracy."


def zaloguj(page, base, uid):
    page.goto(f"{base}/konto")
    page.locator(f'form:has(input[name=user_id][value="{uid}"]) button').first.click()
    page.wait_for_load_state()


def main():
    OUT.mkdir(exist_ok=True)
    srv, base = start(5077)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            ctx = b.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
            ctx.add_cookies([{"name": "hints_off", "value": "1", "url": base}])
            page = ctx.new_page()

            page.goto(base + "/")
            page.screenshot(path=OUT / "01-start.png")

            zaloguj(page, base, 1)  # Anna, mieszkanka-rodzic
            page.goto(base + "/")
            page.fill("textarea[name=opis]", OPIS)
            page.locator("form:has(textarea[name=opis]) button[type=submit]").first.click()
            page.wait_for_url("**/wyniki")
            expect(page.locator("main")).to_contain_text("pasuje")
            page.eval_on_selector("aside details", "e => e.open = true")  # „Inni mieli podobnie” rozwinięte
            page.screenshot(path=OUT / "02-wyniki.png", full_page=True)
            # Panel Hubu nie może świecić zerami: Anna zapisuje zgłoszenie (wątek) i jedną fiszkę pomysłu.
            page.locator('form[action="/zgloszenie"] button[type=submit]').click()
            page.wait_for_load_state()
            page.goto(base + "/pomysly/nowy")
            page.fill("[name=title]", "Kawiarnia z praktykami dla dorosłych z ZD (PRZYKŁAD)")
            page.fill("[name=essence]", "Praktyki w lokalnej kawiarni z trenerem pracy, potem zatrudnienie u pracodawców z powiatu.")
            for sel in ("audience", "stage"):
                page.select_option(f"select[name={sel}]", index=1)
            page.locator("form.card button[type=submit]").click()
            page.wait_for_load_state()

            zaloguj(page, base, 5)  # Joanna, koordynatorka Hubu
            page.goto(base + "/admin")
            page.screenshot(path=OUT / "03-panel-hubu.png", full_page=True)
            page.goto(base + "/admin/trendy")
            page.screenshot(path=OUT / "04-trendy.png")
            b.close()
    finally:
        srv.shutdown()
    print("zrzuty:", sorted(x.name for x in OUT.glob("*.png")))


if __name__ == "__main__":
    main()
