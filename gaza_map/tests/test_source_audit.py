"""Pre-publication audit (M5): numbers the site can show, checked against the SOURCE, not against our own code.

Where each reference value comes from:
  * EWARS dashboard totals: read from the public dashboard on 2026-11-19 (see docs/data-sources.md),
    which shows rounded values like "424.6k"; exact ones (e.g. 72,472) are shown as is.
  * HeRAMS: the WHO PDF (June 2025): "Out of 127 HSDUs evaluated" (overview page); the Gaza Strip page
    footnote "Out of 44 HSDUs" are at least partially functioning; per-governorate "Out of N HSDUs evaluated".
    The 25 domain percentages were compared one by one with the rendered pages.
If one of these fails, do not publish until you know whether the source or our pipeline changed.
"""

import pytest

from gaza_map.build_db import CLEAN, build
import sqlite3

pytestmark = pytest.mark.skipif(not (CLEAN / "ewars_weekly.csv").exists(), reason="run clean_ewars.py first")


@pytest.fixture(scope="module")
def con(tmp_path_factory):
    p = tmp_path_factory.mktemp("audit") / "a.sqlite"
    build(p)
    c = sqlite3.connect(p)
    yield c
    c.close()


def total(con, disease, year, location=None):
    sql = ("SELECT SUM(o.cases) FROM observations o JOIN diseases d USING(disease_id) "
           "JOIN locations l USING(location_id) WHERE d.key=? AND o.year=?")
    args = [disease, year]
    if location:
        sql += " AND l.key=?"
        args.append(location)
    return con.execute(sql, args).fetchone()[0]


# (disease, location) -> exact or rounded dashboard value for 2026 (weeks 1-45)
DASHBOARD_2026_EXACT = {
    ("ari", "north_gaza"): 72_472, ("awd", "north_gaza"): 25_695, ("measles", "north_gaza"): 1,
    ("awd", "deir_al_balah"): 99_363, ("measles", "deir_al_balah"): 4,
    ("ari", "rafah"): 13_534, ("awd", "rafah"): 3_672, ("measles", "rafah"): 0,
    ("awd", "gaza"): 125_508, ("measles", "gaza"): 6, ("measles", "khan_yunis"): 5,
    ("chickenpox", "khan_yunis"): 36_256, ("chickenpox", "gaza"): 20_922,
    ("chickenpox", "deir_al_balah"): 13_239, ("chickenpox", "north_gaza"): 3_868,
    ("chickenpox", "rafah"): 645,
}
DASHBOARD_2026_ROUNDED_K = {  # shown as "x.xk" on the dashboard: must round to it
    ("ari", "gaza"): 424.6, ("ari", "deir_al_balah"): 307.4, ("ari", "khan_yunis"): 523.7,
    ("awd", "khan_yunis"): 208.6,
}


@pytest.mark.parametrize("key,expected", DASHBOARD_2026_EXACT.items())
def test_2026_governorate_totals_exact(con, key, expected):
    assert total(con, key[0], 2026, key[1]) == expected


@pytest.mark.parametrize("key,expected", DASHBOARD_2026_ROUNDED_K.items())
def test_2026_governorate_totals_rounded(con, key, expected):
    assert round(total(con, key[0], 2026, key[1]) / 1000, 1) == expected


def test_yearly_national_totals(con):
    assert round(total(con, "ari", 2024) / 1000, 1) == 461.6
    assert round(total(con, "awd", 2024) / 1000, 1) == 203.4
    assert round(total(con, "ari", 2025) / 1e6, 1) == 1.1
    assert round(total(con, "awd", 2025) / 1000, 1) == 495.0
    assert round(total(con, "ari", 2026) / 1e6, 1) == 1.3
    assert round(total(con, "awd", 2026) / 1000, 1) == 462.9
    assert total(con, "measles", 2026) == 16


def test_awd_2025_close_to_pcbs_statement(con):
    # PCBS statement (docx on microdata.pcbs.gov.ps) says about 496 thousand; ours is 495.0k
    assert abs(total(con, "awd", 2025) - 496_000) < 2_000


def test_herams_hsdu_totals_match_the_pdf(con):
    ev, fn = con.execute("SELECT SUM(hsdu_evaluated), SUM(at_least_partially_functioning) "
                         "FROM hsdu_functionality").fetchone()
    assert ev == 127   # "Out of 127 HSDUs evaluated"
    assert fn == 44    # Gaza Strip page: "Out of 44 HSDUs"
    per = dict(con.execute("SELECT l.key, hsdu_evaluated FROM hsdu_functionality h JOIN locations l "
                           "USING(location_id)").fetchall())
    assert per == {"deir_al_balah": 27, "gaza": 39, "khan_yunis": 25, "north_gaza": 21, "rafah": 15}


def test_herams_domain_rows_checked_against_rendered_pages(con):
    # all five governorate/strip pages were compared visually on 2026-11-19; spot-lock the sharpest ones
    rows = dict(((k, d), (a, p, n, nn)) for k, d, a, p, n, nn in con.execute(
        "SELECT l.key, f.domain, pct_available, pct_partial, pct_not_available, pct_not_normally_provided "
        "FROM facility_domains f JOIN locations l USING(location_id)"))
    assert rows[("khan_yunis", "General clinical and trauma care")] == (3, 60, 13, 24)
    assert rows[("north_gaza", "Communicable diseases")] == (0, 0, 0, 100)
    assert rows[("strip", "NCD and mental health")] == (10, 18, 8, 64)
    assert rows[("gaza", "NCD and mental health")] == (6, 18, 10, 65)
    assert len(rows) == 25
