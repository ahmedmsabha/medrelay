import sqlite3

import pytest

from gaza_map import trends
from gaza_map.build_db import CLEAN, build

pytestmark = pytest.mark.skipif(not (CLEAN / "ewars_weekly.csv").exists(),
                                reason="run clean_ewars.py first")


@pytest.fixture(scope="module")
def con(tmp_path_factory):
    path = tmp_path_factory.mktemp("db") / "t.sqlite"
    counts = build(path)
    c = sqlite3.connect(path)
    c.execute("PRAGMA foreign_keys = ON")
    yield c, counts
    c.close()


def q(con, sql, *args):
    con = con[0] if isinstance(con, tuple) else con
    return con.execute(sql, args).fetchall()


def test_row_counts_match_the_csvs(con):
    counts = con[1]
    assert counts["observations"] == 12654
    assert counts["locations"] == 6 and counts["diseases"] == 17
    assert counts["reporting"] == 664  # 666 weeks minus the 2 zero-consultation weeks


def test_foreign_keys_clean(con):
    assert q(con, "PRAGMA foreign_key_check") == []


def test_source_spellings_unify(con):
    # HeRAMS says "Gaza City"/"Khan Younis"; EWARS says "Gaza"/"Khan Yunis": same locations
    rows = q(con, "SELECT l.key FROM facility_domains f JOIN locations l USING(location_id) "
                  "WHERE l.key IN ('gaza','khan_yunis') GROUP BY l.key")
    assert {r[0] for r in rows} == {"gaza", "khan_yunis"}


def test_missing_weeks_have_no_reporting_row(con):
    # North Gaza 2024 week 2 sent consultations = 0 -> not reported -> no row, no rate
    assert q(con, "SELECT 1 FROM reporting r JOIN locations l USING(location_id) "
                  "WHERE l.key='north_gaza' AND year=2024 AND epi_week=2") == []
    assert q(con, "SELECT 1 FROM v_cases_weekly v JOIN locations l USING(location_id) "
                  "WHERE l.key='north_gaza' AND year=2024 AND epi_week=2") == []


def test_unknown_stays_null(con):
    assert q(con, "SELECT COUNT(*) FROM observations WHERE sex IS NOT NULL")[0][0] == 0
    assert q(con, "SELECT COUNT(*) FROM locations WHERE lat IS NOT NULL")[0][0] == 0
    # chickenpox has no deaths field: NULL, not 0
    assert q(con, "SELECT COUNT(*) FROM observations o JOIN diseases d USING(disease_id) "
                  "WHERE d.key='chickenpox' AND o.deaths IS NOT NULL")[0][0] == 0


def test_db_rate_equals_trends_script(con):
    """Two independent implementations (SQL view vs trends.py) must agree."""
    rows, starts = trends.drop_untracked(trends.load_weekly())
    expected = {(r["governorate"], r["year"], r["disease"]): r["per_1000"]
                for r in trends.year_over_year(rows, 45, starts)}
    got = q(con, "SELECT l.name_en, w.year, d.key, "
                 "ROUND(SUM(w.cases)*1000.0/SUM(w.consultations),2) "
                 "FROM v_cases_weekly w JOIN locations l USING(location_id) "
                 "JOIN diseases d USING(disease_id) WHERE w.epi_week <= 45 "
                 "GROUP BY l.name_en, w.year, d.key")
    assert len(got) == len(expected)
    for gov, year, disease, per_1000 in got:
        assert per_1000 == pytest.approx(expected[(gov, year, disease)], abs=0.01)


def test_dashboard_total_survives_the_database(con):
    cases = q(con, "SELECT SUM(w.cases) FROM v_cases_weekly w JOIN locations l USING(location_id) "
                   "JOIN diseases d USING(disease_id) "
                   "WHERE l.key='gaza' AND d.key='awd' AND w.year=2026")[0][0]
    assert cases == 125_508


def test_untracked_weeks_excluded_from_views_but_kept_in_table(con):
    in_table = q(con, "SELECT COUNT(*) FROM observations o JOIN diseases d USING(disease_id) "
                      "WHERE d.key='impetigo' AND o.tracked=0")[0][0]
    in_view = q(con, "SELECT COUNT(*) FROM v_cases_weekly w JOIN diseases d USING(disease_id) "
                     "WHERE d.key='impetigo' AND w.year=2024")[0][0]
    assert in_table > 0 and in_view == 0


def test_by_location_exposes_partial_years(con):
    r = q(con, "SELECT weeks_reported FROM v_by_location WHERE location='north_gaza' "
               "AND disease='ari' AND year=2024")[0][0]
    assert r < 52


def test_medicine_needs_requires_a_source(con):
    assert q(con, "SELECT COUNT(*) FROM medicine_needs")[0][0] == 0  # nothing invented from memory
    db = con[0]
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO medicine_needs(disease_id, medicine_class, source_id, source_ref) "
                   "VALUES (1, 'x', NULL, 'p1')")
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO medicine_needs(disease_id, medicine_class, source_id, source_ref) "
                   "VALUES (1, 'x', 'no_such_source', 'p1')")
    db.rollback()
    assert q(con, "SELECT COUNT(*) FROM v_by_medicine")[0][0] == 0


def test_herams_percentages_add_to_100(con):
    for row in q(con, "SELECT pct_available+pct_partial+pct_not_available+pct_not_normally_provided "
                      "FROM facility_domains"):
        assert 99 <= row[0] <= 101  # rounding in the source


def test_rebuild_is_deterministic(tmp_path):
    a, b = tmp_path / "a.sqlite", tmp_path / "b.sqlite"
    assert build(a) == build(b)
