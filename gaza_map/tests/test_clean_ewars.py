"""Tests for gaza_map.clean_ewars.

Two kinds: unit tests on small functions (no data files needed), and checks against the real raw
pull. The raw-data tests are skipped when the file is missing (data/ is not in git).
"""

from datetime import date

import pytest

from gaza_map import clean_ewars as ce

needs_raw = pytest.mark.skipif(not ce.RAW.exists(), reason="raw EWARS file not present")


def test_parse_week_both_label_forms():
    assert ce.parse_week("2024-WE01") == (2024, 1, None)
    assert ce.parse_week("2024-WE01 (31-Dec to 06-Jan)") == (2024, 1, (31, 12, 6, 1))


def test_parse_week_rejects_garbage():
    with pytest.raises(ValueError):
        ce.parse_week("week one")


@pytest.mark.parametrize(
    "year,week,expected",
    [
        (2024, 1, date(2023, 12, 31)),  # label in the data: 31-Dec to 06-Jan
        (2025, 1, date(2024, 12, 29)),
        (2026, 1, date(2025, 12, 28)),
        (2026, 2, date(2026, 1, 4)),  # label in the data: 04-Jan to 10-Jan
        (2026, 44, date(2026, 10, 25)),  # label in the data: 25-Oct to 31-Oct
    ],
)
def test_week_start_matches_labels_seen_in_data(year, week, expected):
    assert ce.week_start(year, week) == expected
    assert ce.week_start(year, week).weekday() == 6  # always a Sunday


def test_every_metric_maps_to_a_measure_and_age_group():
    for measure, age in ce.METRIC_MAP.values():
        assert measure in {"cases", "deaths"}
        assert age in {"all", "under5", "over5"}


def test_coverage_treats_zero_consultations_as_not_reported():
    cons = [
        {"governorate": "X", "year": "2025", "epi_week": "1", "consultations": "100"},
        {"governorate": "X", "year": "2025", "epi_week": "2", "consultations": "0"},
    ]
    cov = ce.coverage(cons)[0]
    assert cov["weeks_reported"] == 1
    assert cov["weeks_missing"] == 51
    assert cov["missing_weeks"].split()[0] == "2"


def test_anomalies_reports_deaths_above_cases_but_does_not_alter_rows():
    rows = [{"governorate": "X", "year": 2025, "epi_week": 9, "disease": "tetanus",
             "cases": "0", "deaths": "1"}]
    assert len(ce.anomalies(rows)) == 1
    assert rows[0]["deaths"] == "1"


@needs_raw
def test_clean_runs_without_issues_and_is_deterministic():
    rows1, cons1, issues1 = ce.clean()
    rows2, _, _ = ce.clean()
    assert issues1 == []
    assert rows1 == rows2
    assert len(cons1) == 666


@needs_raw
def test_totals_match_the_dashboard_numbers_we_recorded():
    """Numbers copied from the public dashboard on 2026-11-19 (see docs/data-sources.md)."""
    rows, _, _ = ce.clean()

    def total(gov, year, disease, age="all", measure="cases"):
        return sum(int(r[measure]) for r in rows
                   if r["governorate"] == gov and r["year"] == year and r["disease"] == disease
                   and r["age_group"] == age and r[measure] != "")

    assert total("Gaza", 2026, "awd", "over5") + total("Gaza", 2026, "awd", "under5") == 125_508
    assert total("Khan Yunis", 2026, "ari") == 523_738
    govs = ["Gaza", "North Gaza", "Deir Al-Balah", "Khan Yunis", "Rafah"]
    assert sum(total(g, 2026, "measles") for g in govs) == 16
    assert sum(total(g, 2026, "ajs") for g in govs) == 3_623
    assert sum(total(g, 2026, "chickenpox") for g in govs if g == "Khan Yunis") == 36_256


@needs_raw
def test_no_negative_values_and_ages_only_on_split_diseases():
    rows, _, _ = ce.clean()
    for r in rows:
        for k in ("cases", "deaths"):
            assert r[k] == "" or int(r[k]) >= 0
    split = {r["disease"] for r in rows if r["age_group"] != "all"}
    assert split == {"awd", "cholera"}
