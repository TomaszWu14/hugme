"""Nagranie GIF do README: opis z telefonem -> Znajdź -> wyniki. Screencast CDP + Pillow."""
import base64, io, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "docs" / "screenshots" / "demo.gif"
PORT = 5091
OPIS = "Seniorzy z kilku sołectw nie mają jak dojechać do lekarza. Autobus jeździ rzadko. Dzwońcie: 600 123 456"

env = dict(os.environ, DEMO_ACCOUNTS="1", AI_DISABLED="1", SECRET_KEY="gif",
           DATABASE=str(Path(tempfile.mkdtemp()) / "gif.db"))
srv = subprocess.Popen([sys.executable, "-m", "flask", "--app", "app:create_app", "run", "--port", str(PORT)],
                       cwd=REPO, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
B = f"http://127.0.0.1:{PORT}"
for _ in range(50):
    try:
        urllib.request.urlopen(B + "/zdrowie"); break
    except Exception:
        time.sleep(0.3)

frames = []
try:
    with sync_playwright() as p:
        br = p.chromium.launch()
        page = br.new_page(viewport={"width": 1280, "height": 800})
        page.goto(B + "/")
        page.evaluate("document.getElementById('ask-title').scrollIntoView({block: 'start'}); window.scrollBy(0, -24)")
        page.wait_for_timeout(500)
        cdp = page.context.new_cdp_session(page)

        def on_frame(ev):
            frames.append((ev["metadata"]["timestamp"], ev["data"]))
            cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})

        cdp.on("Page.screencastFrame", on_frame)
        cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 85, "everyNthFrame": 1})
        page.wait_for_timeout(1500)
        box = page.locator("#f-opis")
        box.click()
        box.fill("")
        page.keyboard.type(OPIS, delay=45)
        page.wait_for_timeout(900)
        page.get_by_role("button", name="Znajdź rozwiązania").click()
        page.wait_for_url("**/wyniki")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        page.evaluate("document.getElementById('inn-h').scrollIntoView({behavior: 'smooth', block: 'start'})")
        page.wait_for_timeout(1200)
        page.evaluate("window.scrollBy({top: -150, behavior: 'smooth'})")
        page.wait_for_timeout(4500)
        cdp.send("Page.stopScreencast")
        page.wait_for_timeout(300)
        br.close()
finally:
    srv.terminate()

# Klatki o stałym kroku 1/10 s: bierzemy ostatnią klatkę przed każdym punktem czasu.
frames.sort()
t0, t_end, step = frames[0][0], frames[-1][0], 0.1
imgs, i, t = [], 0, frames[0][0]
while t <= t_end:
    while i + 1 < len(frames) and frames[i + 1][0] <= t:
        i += 1
    imgs.append(frames[i][1])
    t += step
pics = [Image.open(io.BytesIO(base64.b64decode(d))).convert("RGB").resize((960, 600), Image.LANCZOS) for d in imgs]
pal = pics[len(pics) // 2].quantize(colors=128, method=Image.MEDIANCUT)
pics = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in pics]
durs = [100] * len(pics)
durs[-1] = 2500
OUT.parent.mkdir(parents=True, exist_ok=True)
pics[0].save(OUT, save_all=True, append_images=pics[1:], duration=durs, loop=0, optimize=True)
print(len(frames), "klatek CDP ->", len(pics), "klatek GIF,", round(t_end - t0, 1), "s,", OUT.stat().st_size // 1024, "KB")
