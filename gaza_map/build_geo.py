"""M4 step 1 - cut the five Gaza governorates out of the OCHA boundary file and make them web-light.

Input : data/raw/boundaries/extracted/pse_admin2.geojson   (OCHA COD-AB, 16 governorates)
Output: gaza_map/site/data/governorates.geojson            (5 features, simplified, committed)

Why simplify: the raw polygons are ~1.8 MB for the whole territory. A choropleth does not need
metre-level coasts, so we drop points with Douglas-Peucker (tolerance ~30 m) and round to 4 decimals
(~11 m). We then check the result still has 5 valid-looking rings and nearly the same area.

Run (repo root): python3 -W ignore -m gaza_map.build_geo
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/boundaries/extracted/pse_admin2.geojson"
OUT = ROOT / "gaza_map/site/data/governorates.geojson"

TOLERANCE_DEG = 0.0003  # ~33 m
PCODE_TO_KEY = {
    "PS0255": "north_gaza", "PS0260": "gaza", "PS0265": "deir_al_balah",
    "PS0270": "khan_yunis", "PS0275": "rafah",
}
NAMES_AR = {"north_gaza": "شمال غزة", "gaza": "غزة", "deir_al_balah": "دير البلح",
            "khan_yunis": "خان يونس", "rafah": "رفح"}
ATTRIBUTION = "OCHA / HDX COD-AB State of Palestine, boundaries valid 2023-10-19 (pre-war administrative limits)"


def _dist(p, a, b) -> float:
    """Perpendicular distance from p to the segment a-b (planar degrees; fine at this scale)."""
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


def simplify(points: list[list[float]], tol: float = TOLERANCE_DEG) -> list[list[float]]:
    """Douglas-Peucker, iterative (rings can have thousands of points). Keeps the first/last point."""
    if len(points) <= 4:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        i, j = stack.pop()
        far, idx = 0.0, -1
        for k in range(i + 1, j):
            d = _dist(points[k], points[i], points[j])
            if d > far:
                far, idx = d, k
        if far > tol and idx != -1:
            keep[idx] = True
            stack += [(i, idx), (idx, j)]
    return [p for p, k in zip(points, keep) if k]


def ring_area_deg2(ring: list[list[float]]) -> float:
    """Shoelace area in square degrees (only used to compare before/after simplifying)."""
    s = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def simplify_geometry(geom: dict) -> dict:
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    out = []
    for poly in polys:
        rings = []
        for ring in poly:
            s = [[round(x, 4), round(y, 4)] for x, y in simplify(ring)]
            if len(s) >= 4:  # a closed ring needs at least 4 points
                if s[0] != s[-1]:
                    s.append(s[0])
                rings.append(s)
        if rings:
            out.append(rings)
    return {"type": "MultiPolygon", "coordinates": out}


def geometry_area(geom: dict) -> float:
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    return sum(ring_area_deg2(poly[0]) - sum(ring_area_deg2(h) for h in poly[1:]) for poly in polys)


def build(raw: Path = RAW, out: Path = OUT) -> dict:
    src = json.loads(raw.read_text(encoding="utf-8"))
    feats = []
    for f in src["features"]:
        p = f["properties"]
        key = PCODE_TO_KEY.get(p["adm2_pcode"])
        if key is None:
            continue
        geom = simplify_geometry(f["geometry"])
        ratio = geometry_area(geom) / geometry_area(
            f["geometry"] if f["geometry"]["type"] == "MultiPolygon"
            else {"type": "MultiPolygon", "coordinates": [f["geometry"]["coordinates"]]})
        if not 0.97 <= ratio <= 1.03:
            raise RuntimeError(f"{key}: simplification changed area by {100 * (ratio - 1):.1f}%")
        feats.append({
            "type": "Feature", "geometry": geom,
            "properties": {"key": key, "name_en": p["adm2_name"], "name_ar": NAMES_AR[key],
                           "pcode": p["adm2_pcode"], "lat": round(p["center_lat"], 4),
                           "lon": round(p["center_lon"], 4), "area_sqkm": round(p["area_sqkm"], 1)},
        })
    if {f["properties"]["key"] for f in feats} != set(PCODE_TO_KEY.values()):
        raise RuntimeError("did not find all five Gaza governorates in the boundary file")
    feats.sort(key=lambda f: f["properties"]["key"])
    fc = {"type": "FeatureCollection", "attribution": ATTRIBUTION, "features": feats}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"features": len(feats), "bytes": out.stat().st_size}


if __name__ == "__main__":
    print(build())
