"""prezentacja.html → out/prezentacja_hugme.pdf (1920×1080, 10 stron) + PNG każdej strony w out/strony/.

Liczby, które się zmieniają (widoki WCAG, liczba testów), podstawiamy z repo w chwili budowania.
Uruchom: python demo/pdf.py"""
import re
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfReader

DEMO = Path(__file__).resolve().parent
REPO = DEMO.parent
OUT = DEMO / "out"
PDF = OUT / "prezentacja_hugme.pdf"


def liczby():
    # Liczbę testów podajemy jako „300+” na slajdzie – zmienia się z każdym PR-em, a 300+ jest prawdą w każdej wersji.
    wcag = re.search(r"Sprawdzonych widoków:\*\* (\d+)", (REPO / "docs/WCAG_RAPORT.md").read_text("utf-8")).group(1)
    return {"{{WCAG}}": wcag}


def main():
    (OUT / "strony").mkdir(parents=True, exist_ok=True)
    html = (DEMO / "prezentacja.html").read_text("utf-8")
    for k, v in liczby().items():
        html = html.replace(k, v)
    tmp = DEMO / "_prezentacja_render.html"  # obok oryginału, żeby względne ścieżki (fonty, zrzuty) działały
    tmp.write_text(html, "utf-8")
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(tmp.as_uri())
            page.evaluate("document.fonts.ready")
            page.pdf(path=PDF, width="1920px", height="1080px", print_background=True, prefer_css_page_size=True)
            page.emulate_media(media="print")
            for i, s in enumerate(page.locator("section.s").all(), 1):
                s.screenshot(path=OUT / "strony" / f"strona-{i:02}.png")
            b.close()
    finally:
        tmp.unlink(missing_ok=True)
    n = len(PdfReader(PDF).pages)
    assert n == 10, f"PDF ma {n} stron zamiast 10"
    shutil.copy(PDF, REPO / "docs" / "HugMe_prezentacja.pdf")
    print(f"{PDF} – {n} stron; kopia: docs/HugMe_prezentacja.pdf")


if __name__ == "__main__":
    main()
