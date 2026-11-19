import json
import sqlite3

import pytest

from gaza_map import build_geo, trends
from gaza_map.build_db import CLEAN, GEO, build
from gaza_map.build_geo import ring_area_deg2, simplify
from gaza_map.export_site import export

needs_clean = pytest.mark.skipif(not (CLEAN / "ewars_weekly.csv").exists(), reason="run clean_ewars.py first")


def test_simplify_keeps_ends_and_drops_collinear_points():
    line = [[0, 0], [1, 0.00001], [2, 0], [3, 0.00001], [4, 0]]
    out = simplify(line, tol=0.0003)
    assert out[0] == [0, 0] and out[-1] == [4, 0] and len(out) < len(line)


def test_simplify_keeps_real_corners():
    square_ish = [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]
    assert simplify(square_ish, tol=0.0003) == square_ish


def test_ring_area():
    assert ring_area_deg2([[0, 0], [2, 0], [2, 3], [0, 3], [0, 0]]) == 6


def test_committed_layer_has_the_five_governorates_with_sane_coordinates():
    fc = json.loads(GEO.read_text(encoding="utf-8"))
    keys = {f["properties"]["key"] for f in fc["features"]}
    assert keys == {"north_gaza", "gaza", "deir_al_balah", "khan_yunis", "rafah"}
    for f in fc["features"]:
        p = f["properties"]
        assert 31.0 < p["lat"] < 31.7 and 34.0 < p["lon"] < 34.7  # inside the Gaza Strip's box
        for poly in f["geometry"]["coordinates"]:
            for ring in poly:
                assert ring[0] == ring[-1] and len(ring) >= 4
    assert GEO.stat().st_size < 50_000  # web-light
    assert "OCHA" in fc["attribution"]


def test_geo_feature_set_is_exact():
    assert set(build_geo.PCODE_TO_KEY.values()) == set(build_geo.NAMES_AR)


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    d = tmp_path_factory.mktemp("site")
    db = d / "t.sqlite"
    build(db)
    out = d / "data.json"
    export(db, out)
    return json.loads(out.read_text(encoding="utf-8")), db


@needs_clean
def test_export_agrees_with_trends_script(exported):
    data, _ = exported
    rows, starts = trends.drop_untracked(trends.load_weekly())
    last = data["meta"]["last_week"]
    for r in trends.year_over_year(rows, last, starts):
        slug = {"Gaza": "gaza", "North Gaza": "north_gaza", "Deir Al-Balah": "deir_al_balah",
                "Khan Yunis": "khan_yunis", "Rafah": "rafah"}[r["governorate"]]
        got = data["yearly"][r["disease"]][slug][str(r["year"])]
        assert got["per_1000"] == pytest.approx(r["per_1000"], abs=0.01)
        assert got["comparable"] == r["comparable"]


@needs_clean
def test_strip_total_matches_dashboard_and_pooling(exported):
    data, _ = exported
    assert data["yearly"]["ari"]["strip"]["2026"]["cases"] == 1_341_805  # dashboard: ARI 1.3M for 2026
    assert data["meta"]["last_week"] == 45


@needs_clean
def test_sparse_months_are_left_out_not_zeroed(exported):
    data, db = exported
    k = data["monthly"]["ari"]["north_gaza"]
    present = {p[0] for p in k}
    n = len(data["months"])
    assert len(present) < n  # North Gaza has missing months
    assert all(p[4] >= data["meta"]["min_weeks_per_month"] for p in k)
    assert all(p[3] > 0 for p in k)  # a point exists only where real consultations exist


@needs_clean
def test_late_added_2025_not_comparable_in_export(exported):
    data, _ = exported
    for d in ("chickenpox", "ectoparasitic", "impetigo"):
        assert data["yearly"][d]["strip"]["2025"]["comparable"] is False
        assert data["yearly"][d]["strip"]["2026"]["comparable"] is True
    assert data["yearly"]["measles"]["strip"]["2025"]["comparable"] is True


@needs_clean
def test_export_carries_no_medicine_claims_and_every_source_has_caveats(exported):
    data, _ = exported
    assert data["meta"]["medicine_needs_rows"] == 0
    assert all(s["caveats"] and s["type"] for s in data["meta"]["sources"])
    text = json.dumps(data)
    assert "dose" not in text.lower()


@needs_clean
def test_herams_in_export(exported):
    data, db = exported
    assert data["herams"]["hsdu"]["rafah"] == [15, 0]
    assert "rafah" not in data["herams"]["domains"]  # no domain page for Rafah
    assert data["herams"]["domains"]["gaza"]["NCD and mental health"] == [6, 18, 10, 65]
    assert sqlite3.connect(db).execute("PRAGMA foreign_key_check").fetchall() == []
