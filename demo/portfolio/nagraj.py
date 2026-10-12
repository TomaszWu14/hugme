"""Nagranie scen filmu portfolio HugMe (screencast CDP) i montaż z lektorem (ffmpeg).

Lektor: s1–s6.mp3 (ElevenLabs); napisy pisane ręcznie: docs/film/hugme-portfolio.srt.
Wynik: demo/portfolio/hugme-portfolio.mp4 – opublikowany w wydaniu GitHub filmy-2026-10.
Uruchom: python demo/portfolio/nagraj.py  (wymaga: playwright, imageio-ffmpeg)."""
import base64, os, shutil, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

HERE = Path(__file__).parent
REPO = Path(__file__).resolve().parents[2]
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 25
PORT = 5093
B = f"http://127.0.0.1:{PORT}"
GH = "https://github.com/TomaszWu14/hugme"
AUDIO = {1: 14.40, 2: 11.70, 3: 12.96, 4: 11.28, 5: 22.52, 6: 27.54}
LEAD, TAIL = 0.3, 0.6
GMINA, ADMIN = 3, 5
BUS = "Seniorzy z kilku sołectw nie mają jak dojechać do lekarza. Autobus jeździ rzadko. Dzwońcie: 600 123 456"
DACH = "Dach zabytkowego kościoła przecieka, a parafia nie ma pieniędzy na remont."

env = dict(os.environ, DEMO_ACCOUNTS="1", AI_DISABLED="1", SECRET_KEY="film",
           DATABASE=str(Path(tempfile.mkdtemp()) / "film.db"))
srv = subprocess.Popen([sys.executable, "-m", "flask", "--app", "app:create_app", "run", "--port", str(PORT)],
                       cwd=REPO, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    try:
        urllib.request.urlopen(B + "/zdrowie"); break
    except Exception:
        time.sleep(0.3)

scenes = {n: [] for n in AUDIO}   # scena -> lista klipów (lista (ts, jpeg_b64))


def run():
    with sync_playwright() as p:
        br = p.chromium.launch()
        ctx = br.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5, locale="pl-PL")
        page = ctx.new_page()
        cdp = ctx.new_cdp_session(page)
        cur = []

        def on_frame(ev):
            cur.append((ev["metadata"]["timestamp"], ev["data"]))
            try:
                cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
            except Exception:
                pass
        cdp.on("Page.screencastFrame", on_frame)

        def rec(scene, action):
            cur.clear()
            t0 = time.time()
            cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 82, "maxWidth": 1920, "maxHeight": 1080,
                                              "everyNthFrame": 1})
            page.wait_for_timeout(150)
            action()
            t1 = time.time()
            cdp.send("Page.stopScreencast")
            page.wait_for_timeout(150)
            scenes[scene].append((t0, t1, list(cur)))

        def go(path, top=None, off=-20):
            if path.startswith("http"):
                page.goto(path, wait_until="load"); page.wait_for_timeout(2000)
            else:
                page.goto(B + path); page.wait_for_load_state("networkidle")
            if top:
                page.evaluate(f"document.querySelector({top!r}).scrollIntoView({{block:'start'}}); window.scrollBy(0,{off})")
            page.wait_for_timeout(300)

        def login(uid):
            page.goto(B + "/konto")
            tok = page.locator("input[name=_csrf]").first.get_attribute("value")
            ctx.request.post(B + "/konto", form={"_csrf": tok, "user_id": str(uid), "next": "/"})

        def smooth(sel=None, by=None, wait=1200):
            if sel:
                page.evaluate(f"document.querySelector({sel!r}).scrollIntoView({{behavior:'smooth', block:'start'}})")
            else:
                page.evaluate(f"window.scrollBy({{top:{by}, behavior:'smooth'}})")
            page.wait_for_timeout(wait)

        def search(text):
            go("/", "#ask-title", -10)
            box = page.locator("#f-opis")
            box.click(); box.fill("")
            return box

        # ── Scena 1: problem – Biblioteka, potem pusty dla Huba obraz trendów
        login(ADMIN)
        go("/biblioteka")
        rec(1, lambda: (page.wait_for_timeout(800), smooth(by=900, wait=2600), smooth(by=900, wait=2600),
                        smooth(by=900, wait=2000)))
        go("/admin/trendy")
        rec(1, lambda: (page.wait_for_timeout(2500), smooth(by=500, wait=3500)))

        # ── Scena 2: gmina opisuje problem
        login(GMINA)
        search("")
        def s2():
            page.wait_for_timeout(700)
            page.keyboard.type(BUS, delay=38)
            page.wait_for_timeout(600)
            page.get_by_role("button", name="Znajdź rozwiązania").click()
            page.wait_for_url("**/wyniki"); page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2600)
        rec(2, s2)

        # ── Scena 3: wyniki z powodem; potem opis bez dobrego dopasowania
        rec(3, lambda: (smooth("#inn-h", wait=1300), smooth(by=-130, wait=5200)))
        search("")
        page.keyboard.type(DACH)
        page.get_by_role("button", name="Znajdź rozwiązania").click()
        page.wait_for_url("**/wyniki"); page.wait_for_load_state("networkidle")
        rec(3, lambda: (page.wait_for_timeout(600), smooth("#inn-h", wait=1200), smooth(by=-120, wait=3600)))

        # ── Scena 4: zapis zgłoszenia, odpowiedź Hubu, luka w trendach
        def s4a():
            smooth("#save-h", wait=1400)
            page.get_by_role("button", name="Zapisz zgłoszenie").last.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1800)
        rec(4, s4a)
        report = page.url
        login(ADMIN)
        go(report, "#watek-h", -10)
        def s4b():
            page.locator("#f-tresc").click()
            page.keyboard.type("Szukamy partnerów w regionie. Odezwiemy się do piątku.", delay=30)
            page.wait_for_timeout(300)
            page.locator("#f-tresc").evaluate("t => t.form.querySelector('button[type=submit]').click()")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1300)
        rec(4, s4b)
        go("/admin/trendy", "#luki", -10)
        rec(4, lambda: page.wait_for_timeout(3600))

        # ── Scena 5: decyzja – wynik z regułami i „i”, potem D-01 w dzienniku decyzji
        login(GMINA)
        search("")
        page.keyboard.type(BUS)
        page.get_by_role("button", name="Znajdź rozwiązania").click()
        page.wait_for_url("**/wyniki"); page.wait_for_load_state("networkidle")
        go(page.url, "#inn-h", -10)
        def s5a():
            page.wait_for_timeout(1500)
            page.locator('details[data-help-for="dopasowanie.trafnosc"] summary').first.click()
            page.wait_for_timeout(8500)
        rec(5, s5a)
        go(GH + "/blob/main/docs/06-decyzje.md")
        page.wait_for_timeout(1500)
        page.evaluate("[...document.querySelectorAll('h2')].find(h => h.textContent.includes('D-01')).scrollIntoView({block:'start'}); window.scrollBy(0,-90)")
        page.wait_for_timeout(500)
        rec(5, lambda: (page.wait_for_timeout(5000), smooth(by=280, wait=6500)))

        # ── Scena 6: czego nie ma
        go("/")
        rec(6, lambda: page.wait_for_timeout(3300))           # pasek „Tryb demo” – konta bez haseł
        login(ADMIN)
        go("/admin/poczta")
        rec(6, lambda: page.wait_for_timeout(3600))           # kolejka e-mail
        go("/razem/wizyty")
        rec(6, lambda: (page.wait_for_timeout(1500), smooth(by=300, wait=2400)))  # wizyty w przeglądarce
        login(GMINA)
        go("/posrednik")
        page.check("input[name=institution][value=gmina]")
        page.select_option("select[name=audience]", "seniorzy")
        page.locator("textarea[name=problem]").fill("Seniorzy z małych wsi nie mają jak dojechać do lekarza i urzędu.")
        page.locator("textarea[name=problem]").evaluate("t => t.form.querySelector('button[type=submit]').click()")
        page.wait_for_url("**/posrednik/karta/**"); page.wait_for_load_state("networkidle")
        page.evaluate("[...document.querySelectorAll('h2,h3,dt,strong')].find(e => e.textContent.includes('Koszty')).scrollIntoView({block:'center'})")
        page.wait_for_timeout(400)
        rec(6, lambda: page.wait_for_timeout(4800))           # karta usługi: koszty bez kwot
        go(GH + "/blob/main/README.md")
        page.mouse.move(640, 400)
        def s6end():
            page.wait_for_timeout(3000)
            for _ in range(3):
                page.mouse.wheel(0, 90); page.wait_for_timeout(120)
            page.wait_for_timeout(4200)
        rec(6, s6end)  # README na GitHubie
        br.close()


try:
    run()
finally:
    srv.terminate()

# ── Montaż: klatki co 1/25 s, scena = długość lektora + zapas; brakujące klatki = ostatnia klatka.
work = HERE / "klatki"
shutil.rmtree(work, ignore_errors=True); work.mkdir()
idx, wavs = 0, []
for n, dur in AUDIO.items():
    target = round((LEAD + dur + TAIL) * FPS)
    seq = []
    for t0, end, frames in scenes[n]:
        frames = sorted(frames)
        if not frames:
            continue
        t, i = t0 + 0.2, 0
        while t <= end + 1e-9:
            while i + 1 < len(frames) and frames[i + 1][0] <= t:
                i += 1
            seq.append(frames[i][1]); t += 1 / FPS
    print(f"scena {n}: nagrane {len(seq) / FPS:.1f} s, potrzebne {target / FPS:.1f} s")
    seq = (seq + [seq[-1]] * target)[:target]
    for d in seq:
        (work / f"{idx:06d}.jpg").write_bytes(base64.b64decode(d)); idx += 1
    wav = HERE / f"a{n}.wav"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(HERE / f"s{n}.mp3"), "-af",
                    f"adelay={int(LEAD * 1000)}:all=1,apad=whole_dur={target / FPS}", "-ar", "44100", "-ac", "2",
                    str(wav)], check=True)
    wavs.append(wav)
(HERE / "audio.txt").write_text("".join(f"file '{w.name}'\n" for w in wavs), encoding="utf-8")
subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(HERE / "audio.txt"),
                str(HERE / "lektor.wav")], check=True)
out = HERE / "hugme-portfolio.mp4"
subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(work / "%06d.jpg"),
                "-i", str(HERE / "lektor.wav"), "-vf", "scale=1920:1080:flags=lanczos,format=yuv420p",
                "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart", "-shortest", str(out)], check=True)
print("gotowe:", out, round(idx / FPS, 1), "s,", out.stat().st_size // 1024, "KB")
