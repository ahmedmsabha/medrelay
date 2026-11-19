from datetime import date

import pytest

from gaza_map import clean_overview as co
from gaza_map.trends import peaks


def test_parse_week():
    assert co.parse_week("2025-WE07") == (2025, 7)
    with pytest.raises(ValueError):
        co.parse_week("week 7")


def test_low_sites_flag_marks_the_first_weeks_of_2024():
    if not co.RAW.exists():
        pytest.skip("raw overview not downloaded")
    rows, totals = co.build()
    low = [r for r in rows if r["low_sites"]]
    assert low and all(r["reporting_locations"] < co.LOW_SITES for r in low)
    assert (2024, 1) in {(r["year"], r["epi_week"]) for r in low}
    assert {t["year"] for t in totals} == {2024, 2025, 2026}


def test_peaks_ignore_excluded_weeks():
    def row(week, cases, cons):
        return {"disease": "ari", "year": 2024, "epi_week": week, "week_start": date(2024, 1, week), "governorate": "gaza",
                "cases": cases, "deaths": 0, "consultations": cons}
    rows = [row(6, 900, 6000), row(30, 500, 6000)]  # week 6 has the higher rate
    assert peaks(rows)[0]["epi_week"] == 6
    assert peaks(rows, exclude={(2024, 6)})[0]["epi_week"] == 30
