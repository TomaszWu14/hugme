"""Jednorazowo: GeoJSON województw i powiatów → uproszczone ścieżki SVG w data/mapa.py (mapa pracy bez JS).

Źródło: https://github.com/ppatrzyk/polska-geojson (dane OSM/GUGiK, licencja ODbL / domena publiczna).
Uruchom:  python scripts/mapa_svg.py [katalog z woj.json i pow.json]   (domyślnie pobiera z GitHuba)"""
import json
import math
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core.domain import POWIATY  # noqa: E402

BASE = "https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/"
URLS = {"woj": BASE + "wojewodztwa/wojewodztwa-min.geojson", "pow": BASE + "powiaty/powiaty-min.geojson"}
PL = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
TOL_PL, TOL_MP = 1.2, 0.9  # tolerancja uproszczenia (px w viewBox)


def slug(name):
    return name.translate(PL).lower().replace(" ", "-")


def load(key, folder):
    if folder:
        return json.loads((Path(folder) / f"{key}.json").read_text(encoding="utf-8"))
    return json.loads(urllib.request.urlopen(URLS[key], timeout=60).read())


def rings(geom):
    """Wszystkie pierścienie zewnętrzne (bez dziur) – lista list [lon, lat]."""
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    return [poly[0] for poly in geom["coordinates"]]


def project(lon, lat):
    return lon * math.cos(math.radians(52)), -lat


def simplify(points, tol):
    """Douglas–Peucker (iteracyjnie); zamknięty pierścień traci powtórzony ostatni punkt (zamyka go „Z”)."""
    if len(points) > 1 and points[0] == points[-1]:
        points = points[:-1]
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = points[a]
        bx, by = points[b]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy)
        best, idx = 0.0, None
        for i in range(a + 1, b):
            px, py = points[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / norm if norm > 1e-9 else math.hypot(px - ax, py - ay)
            if d > best:
                best, idx = d, i
        if idx is not None and best > tol:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    return [p for p, k in zip(points, keep) if k]


def inside(pt, ring):
    x, y = pt
    hit = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            hit = not hit
    return hit


def centroid(ring):
    xs, ys = zip(*ring)
    return sum(xs) / len(xs), sum(ys) / len(ys)


def build(features, width, height, tol, pad=8):
    """Zwraca listę (nazwa, ścieżka, cx, cy) wpasowaną w viewBox width×height."""
    projected = [(f["properties"]["nazwa"].replace("powiat ", ""), [[project(*p) for p in r] for r in rings(f["geometry"])])
                 for f in features]
    allpts = [p for _, rs in projected for r in rs for p in r]
    minx, maxx = min(p[0] for p in allpts), max(p[0] for p in allpts)
    miny, maxy = min(p[1] for p in allpts), max(p[1] for p in allpts)
    scale = min((width - 2 * pad) / (maxx - minx), (height - 2 * pad) / (maxy - miny))
    ox = pad + ((width - 2 * pad) - (maxx - minx) * scale) / 2
    oy = pad + ((height - 2 * pad) - (maxy - miny) * scale) / 2

    def fit(p):
        return ((p[0] - minx) * scale + ox, (p[1] - miny) * scale + oy)

    out = []
    for name, rs in projected:
        parts, biggest = [], None
        for r in rs:
            pts = simplify([fit(p) for p in r], tol)
            if len(pts) < 3:
                continue
            parts.append("M" + " ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z")
            if biggest is None or len(r) > len(biggest):
                biggest = [fit(p) for p in r]
        cx, cy = centroid(biggest)
        out.append((name, "".join(parts), round(cx, 1), round(cy, 1)))
    return out


def main(folder=None):
    woj = load("woj", folder)["features"]
    pow_ = load("pow", folder)["features"]
    mp = next(f for f in woj if f["properties"]["nazwa"] == "małopolskie")
    mp_rings = [[project(*p) for p in r] for r in rings(mp["geometry"])]
    in_mp = [f for f in pow_ if any(inside(centroid([project(*p) for p in rings(f["geometry"])[0]]), r) for r in mp_rings)]
    names = {f["properties"]["nazwa"].replace("powiat ", ""): f for f in in_mp}
    missing = [p for p in POWIATY if p not in names]
    extra = [n for n in names if n not in POWIATY]
    assert not missing and not extra, (missing, extra)

    woj_rows = build(sorted(woj, key=lambda f: f["properties"]["nazwa"]), 600, 560, TOL_PL)
    pow_rows = build([names[p] for p in POWIATY], 600, 440, TOL_MP)
    lines = ['"""Kontury województw i powiatów Małopolski jako ścieżki SVG (wygenerowane przez scripts/mapa_svg.py).',
             "", "Źródło: ppatrzyk/polska-geojson (OSM/GUGiK). Współrzędne w viewBox 0 0 600 560 (Polska) i 0 0 600 440",
             '(Małopolska); cx, cy = środek etykiety."""', "",
             "ATTRIBUTION = \"Kontury: polska-geojson (dane OpenStreetMap / GUGiK)\"", "VIEWBOX_PL = \"0 0 600 560\"",
             "VIEWBOX_MP = \"0 0 600 440\"", "", "# (slug, nazwa, ścieżka, cx, cy)", "WOJEWODZTWA = ["]
    for name, path, cx, cy in woj_rows:
        lines.append(f'    ("{slug(name)}", "{name}", "{path}", {cx}, {cy}),')
    lines += ["]", "", "POWIATY_MALOPOLSKA = ["]
    for name, path, cx, cy in pow_rows:
        lines.append(f'    ("{slug(name)}", "{name}", "{path}", {cx}, {cy}),')
    lines.append("]")
    out = ROOT / "data" / "mapa.py"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{out}: {out.stat().st_size // 1024} KB, {len(woj_rows)} województw, {len(pow_rows)} powiatów")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
