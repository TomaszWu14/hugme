"""Miniatura YouTube 1280×720 i avatar kanału 800×800 (JPG) → docs/logo/.

HTML z osadzonymi fontami Atkinson, logo.svg i zrzutem z telefonu → zrzut Playwright.
Uruchom: python demo/portfolio/miniatura.py"""
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[2]
STATIC = REPO / "app" / "static"
OUT = REPO / "docs" / "logo"


def b64(p):
    return base64.b64encode(p.read_bytes()).decode()


# Jak w hugme.css: podstawowa łacina w atkinson-latin-*, polskie znaki w atkinson-*.
ZAKRESY = {"atkinson-latin": "U+0000-00FF,U+2000-206F", "atkinson": "U+0100-024F,U+1E00-1EFF"}
FONTS = "".join(
    f"@font-face{{font-family:A;font-weight:{w};unicode-range:{zakres};"
    f"src:url(data:font/woff2;base64,{b64(STATIC / 'fonts' / f'{plik}-{w}.woff2')})}}"
    for w in (400, 700) for plik, zakres in ZAKRESY.items())
LOGO = f"data:image/svg+xml;base64,{b64(STATIC / 'img' / 'logo.svg')}"
ZRZUT = f"data:image/png;base64,{b64(REPO / 'docs' / 'zrzuty' / '02-wyniki-telefon.png')}"
BASE = f"<style>{FONTS}*{{margin:0;box-sizing:border-box}}body{{font-family:A;color:#1B2540;background:#FBF6EE}}</style>"

MINIATURA = BASE + f"""<style>
body{{width:1280px;height:720px;position:relative;overflow:hidden}}
.lewa{{position:absolute;left:80px;top:70px;width:700px}}
.marka{{display:flex;align-items:center;gap:18px;font-size:54px;font-weight:700}}
.marka img{{width:76px}} .marka b{{color:#B8432F}}
h1{{font-size:84px;line-height:1.02;margin-top:44px;letter-spacing:-1px}}
h1 em{{font-style:normal;color:#B8432F}}
p{{font-size:34px;line-height:1.3;margin-top:26px;color:#46506B}}
.chip{{position:absolute;left:80px;bottom:64px;background:#1B2540;color:#fff;font-size:26px;font-weight:700;
padding:14px 26px;border-radius:999px}} .chip span{{color:#FFE7A3}}
.tel{{position:absolute;right:90px;top:46px;width:404px;height:720px;border-radius:52px;background:#1B2540;padding:14px;
transform:rotate(4deg);box-shadow:0 30px 60px rgba(27,37,64,.3)}}
.ekran{{width:100%;height:100%;border-radius:40px;background:url({ZRZUT}) 0 -470px/376px auto no-repeat #fff}}
</style>
<div class="lewa">
  <div class="marka"><img src="{LOGO}"><span>Hug<b>Me</b></span></div>
  <h1>Opisz problem.<br><em>Znajdź pomoc</em><br>z regionu.</h1>
  <p>Sprawdzone innowacje społeczne<br>z Małopolski w kilka sekund</p>
</div>
<div class="chip">HackYeah 2026 · ocena jury <span>7,30</span> (średnia 5,65)</div>
<div class="tel"><div class="ekran"></div></div>"""

# Ikona + nazwa mieszczą się w kole, które YouTube wycina z kwadratu.
AVATAR = BASE + f"""<style>body{{width:800px;height:800px;display:flex;flex-direction:column;
align-items:center;justify-content:center}} img{{width:400px}}
div{{font-size:128px;font-weight:700;line-height:1;margin-top:-6px}} b{{color:#B8432F}}</style>
<img src="{LOGO}"><div>Hug<b>Me</b></div>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for html, (w, h), nazwa in ((MINIATURA, (1280, 720), "hugme-miniatura-youtube.jpg"),
                                (AVATAR, (800, 800), "hugme-avatar-800.jpg")):
        page = b.new_page(viewport={"width": w, "height": h})
        page.set_content(html)
        page.evaluate("document.fonts.ready")
        page.screenshot(path=str(OUT / nazwa), type="jpeg", quality=92)
        print(OUT / nazwa)
    b.close()
