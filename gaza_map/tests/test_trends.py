from datetime import date

import pytest

from gaza_map import trends
from gaza_map.trends import (
    CLEAN, drop_untracked, load_weekly, month_of, monthly, national_yoy, rate, year_over_year,
)


def row(gov="Gaza", year=2025, week=1, disease="ari", cases=10, cons=1000, start=date(2024, 12, 29)):
    return {"governorate": gov, "year": year, "epi_week": week, "week_start": start, "disease": disease,
            "cases": cases, "deaths": None, "consultations": cons}


def test_rate_basic_and_no_denominator():
    assert rate(50, 1000) == 50.0
    assert rate(1, 3) == 333.33
    assert rate(5, 0) is None  # never divide by zero, never invent 0


def test_month_uses_the_thursday_rule():
    # week 2023-12-31..2024-01-06 mostly lies in January 2024
    assert month_of(date(2023, 12, 31)) == "2024-01"
    assert month_of(date(2024, 1, 28)) == "2024-02"  # 28 Jan..3 Feb: Thursday is 1 Feb


def test_pooling_sums_before_dividing():
    # a tiny week with a huge rate must not outweigh a big week:
    rows = [row(week=1, cases=5, cons=10), row(week=2, cases=100, cons=10000)]
    pooled = national_yoy(rows, 45)[0]["per_1000"]
    assert pooled == round(105 * 1000 / 10010, 2)  # ~10.49, not the average of 500 and 10
    assert pooled != (500 + 10) / 2


def test_consultations_counted_once_per_week_across_diseases():
    rows = [row(disease="ari", cases=10), row(disease="awd", cases=5)]  # same gov/week, cons repeated
    y = {r["disease"]: r for r in year_over_year(rows, 45)}
    assert y["ari"]["consultations"] == 1000 and y["awd"]["consultations"] == 1000


def test_same_week_window_excludes_later_weeks():
    rows = [row(week=10), row(week=50, cases=999)]
    assert year_over_year(rows, 45)[0]["cases"] == 10


def test_late_added_disease_loses_untracked_weeks_but_rare_disease_keeps_zero():
    rows = [
        row(disease="impetigo", week=1, cases=0), row(disease="impetigo", week=30, cases=7),
        row(disease="measles", week=1, cases=0), row(disease="measles", week=30, cases=0),
    ]
    kept, starts = drop_untracked(rows)
    assert starts == {"impetigo": (2025, 30)}
    assert [(r["disease"], r["epi_week"]) for r in kept if r["disease"] == "impetigo"] == [("impetigo", 30)]
    assert len([r for r in kept if r["disease"] == "measles"]) == 2  # a real zero stays


def test_comparable_flag():
    rows = [row(disease="impetigo", year=2025, week=30, cases=7),
            row(disease="impetigo", year=2026, week=1, cases=70)]
    kept, starts = drop_untracked(rows)
    flags = {r["year"]: r["comparable"] for r in national_yoy(kept, 45, starts)}
    assert flags == {2025: False, 2026: True}


def test_low_coverage_month_flag():
    rows = [row(week=1, start=date(2025, 1, 5)), row(week=2, start=date(2025, 1, 12))]
    m = monthly(rows)[0]
    assert m["weeks_reported"] == 2 and m["low_coverage"] is True


needs_data = pytest.mark.skipif(not (CLEAN / "ewars_weekly.csv").exists(), reason="run clean_ewars.py first")


@needs_data
def test_awd_all_ages_equals_dashboard_total():
    rows = [r for r in load_weekly() if r["disease"] == "awd" and r["year"] == 2026 and r["governorate"] == "Gaza"]
    assert sum(r["cases"] for r in rows) == 125_508  # same figure as the dashboard (week 45 pull)


@needs_data
def test_no_zero_consultation_weeks_and_no_negative_rates():
    rows = load_weekly()
    assert all(r["consultations"] > 0 for r in rows)
    assert all(r["cases"] >= 0 for r in rows)
    assert trends.rate(1, 1) == 1000.0
