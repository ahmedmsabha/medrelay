"""Clean the raw EWARS pull into a tidy weekly table.

Input : data/raw/ewars/ewars_gaza_weekly_by_governorate_2024-2026.csv   (long, messy)
Output: data/clean/ewars_weekly.csv         one row per governorate x epi week x disease x age group
        data/clean/ewars_consultations.csv  total consultations per governorate x epi week
        data/clean/ewars_quality_report.txt what we checked and what we found

Why these steps (see docs/study-notes/06-data-cleaning-ewars.md):
  1. The same week appears as "2024-WE01" or "2024-WE01 (31-Dec to 06-Jan)" -> parse both into
     (year, week number) and compute the dates ourselves, then check them against the labels.
  2. Metrics are named differently per card ("cases", "AWD Cases (Under 5)", ...) -> map to
     (measure, age_group).
  3. "Total Consultations" is repeated on every disease card -> collapse to one value per week
     and verify that the copies agree.
  4. Nothing is guessed: unknown values stay empty, and we only *report* oddities.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/ewars/ewars_gaza_weekly_by_governorate_2024-2026.csv"
REF = ROOT / "gaza_map/reference/diseases.csv"
OUT = ROOT / "data/clean"

WEEK_RE = re.compile(r"^(\d{4})-WE(\d{2})(?: \((\d{2})-([A-Za-z]{3}) to (\d{2})-([A-Za-z]{3})\))?$")
MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

# raw metric name -> (measure, age_group)
METRIC_MAP = {
    "cases": ("cases", "all"),
    "deaths": ("deaths", "all"),
    "AWD Cases (Over 5)": ("cases", "over5"),
    "AWD Cases (Under 5)": ("cases", "under5"),
    "AWD Deaths (Over 5)": ("deaths", "over5"),
    "AWD Deaths (Under 5)": ("deaths", "under5"),
    "Cholera Cases (Over 5)": ("cases", "over5"),
    "Cholera Cases (Under 5)": ("cases", "under5"),
    "Cholera Deaths (Over 5)": ("deaths", "over5"),
    "Cholera Deaths (Under 5)": ("deaths", "under5"),
}
CONSULT = "Total Consultations"


def parse_week(label: str) -> tuple[int, int, tuple[int, int, int, int] | None]:
    """'2024-WE01 (31-Dec to 06-Jan)' -> (2024, 1, (31, 12, 6, 1)). Date range is None if absent."""
    m = WEEK_RE.match(label.strip())
    if not m:
        raise ValueError(f"unrecognised week label: {label!r}")
    year, week = int(m.group(1)), int(m.group(2))
    rng = None
    if m.group(3):
        rng = (int(m.group(3)), MONTHS[m.group(4)], int(m.group(5)), MONTHS[m.group(6)])
    return year, week, rng


def week_start(year: int, week: int) -> date:
    """EWARS epi weeks run Sunday-Saturday; week 1 starts on the Sunday on/before 1 January.

    Checked against the labels in the data (2024-WE01 = 31 Dec-6 Jan, 2026-WE02 = 4-10 Jan).
    """
    jan1 = date(year, 1, 1)
    first_sunday = jan1 - timedelta(days=(jan1.weekday() + 1) % 7)  # Monday=0 .. Sunday=6
    return first_sunday + timedelta(weeks=week - 1)


def load_disease_map() -> dict[str, str]:
    with REF.open(encoding="utf-8") as f:
        return {r["card"]: r["disease_key"] for r in csv.DictReader(f)}


def clean(raw_path: Path = RAW) -> tuple[list[dict], list[dict], list[str]]:
    disease_of = load_disease_map()
    issues: list[str] = []
    cells: dict[tuple, dict] = defaultdict(dict)  # (gov, year, week, disease, age) -> {measure: v}
    consult: dict[tuple, set[int]] = defaultdict(set)  # (gov, year, week) -> {values seen}
    label_mismatch = 0

    with raw_path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            year, week, rng = parse_week(r["week"])
            if str(year) != r["year"]:
                issues.append(f"year column {r['year']} != week label {r['week']}")
            start = week_start(year, week)
            if rng is not None:
                end = start + timedelta(days=6)
                if (start.day, start.month, end.day, end.month) != rng:
                    label_mismatch += 1
            if r["value"] == "":
                issues.append(f"empty value: {r['governorate']} {r['week']} {r['card']} {r['metric']}")
                continue
            value = int(float(r["value"]))
            gov = r["governorate"]
            if r["metric"] == CONSULT:
                consult[(gov, year, week)].add(value)
                continue
            if r["card"] not in disease_of:
                issues.append(f"unknown card: {r['card']}")
                continue
            if r["metric"] not in METRIC_MAP:
                issues.append(f"unknown metric: {r['metric']}")
                continue
            measure, age = METRIC_MAP[r["metric"]]
            cells[(gov, year, week, disease_of[r["card"]], age)][measure] = value

    if label_mismatch:
        issues.append(f"{label_mismatch} rows where computed dates differ from the week label")

    cons_rows, cons_lookup = [], {}
    for (gov, year, week), vals in sorted(consult.items()):
        if len(vals) > 1:
            issues.append(f"consultations disagree across cards: {gov} {year}-WE{week:02d} {sorted(vals)}")
        v = max(vals)  # if they disagree we keep the max and have already reported it
        cons_lookup[(gov, year, week)] = v
        s = week_start(year, week)
        cons_rows.append({"governorate": gov, "year": year, "epi_week": week,
                          "week_start": s.isoformat(), "week_end": (s + timedelta(days=6)).isoformat(),
                          "consultations": v})

    rows = []
    for (gov, year, week, dis, age), m in sorted(cells.items()):
        s = week_start(year, week)
        rows.append({
            "governorate": gov, "year": year, "epi_week": week,
            "week_start": s.isoformat(), "week_end": (s + timedelta(days=6)).isoformat(),
            "disease": dis, "age_group": age,
            "cases": m.get("cases", ""), "deaths": m.get("deaths", ""),
            "consultations": cons_lookup.get((gov, year, week), ""),
        })
    return rows, cons_rows, issues


def coverage(cons_rows: list[dict]) -> list[dict]:
    """Which weeks are present per governorate-year.

    A week that is *absent* means "no report reached the system", NOT "zero cases". Charts must show
    a gap there, never a zero. Weeks with consultations == 0 are also treated as not reported.
    """
    seen: dict[tuple, set[int]] = defaultdict(set)
    for r in cons_rows:
        if int(r["consultations"]) > 0:
            seen[(r["governorate"], r["year"])].add(int(r["epi_week"]))
    out = []
    for (gov, year), weeks in sorted(seen.items()):
        last = 45 if year == 2026 else 52  # 2026 pull stops at week 45; 2024/2025 run to week 52
        missing = [w for w in range(1, last + 1) if w not in weeks]
        out.append({"governorate": gov, "year": year, "weeks_expected": last,
                    "weeks_reported": len(weeks), "weeks_missing": len(missing),
                    "pct_reported": round(100 * len(weeks) / last),
                    "missing_weeks": " ".join(map(str, missing))})
    return out


def anomalies(rows: list[dict]) -> list[str]:
    """Things that look odd but that we keep (we report, we do not 'fix')."""
    notes = []
    for r in rows:
        if r["cases"] != "" and r["deaths"] != "" and int(r["deaths"]) > int(r["cases"]):
            notes.append(f"deaths > cases: {r['governorate']} {r['year']}-WE{int(r['epi_week']):02d} "
                         f"{r['disease']} cases={r['cases']} deaths={r['deaths']}")
    return notes


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    rows, cons_rows, issues = clean()
    write_csv(OUT / "ewars_weekly.csv", rows)
    write_csv(OUT / "ewars_consultations.csv", cons_rows)
    cov = coverage(cons_rows)
    write_csv(OUT / "ewars_coverage.csv", cov)
    notes = anomalies(rows)
    years = sorted({r["year"] for r in rows})
    report = [
        f"rows (weekly disease table): {len(rows)}",
        f"rows (consultations): {len(cons_rows)}",
        f"years: {years}",
        f"issues found: {len(issues)}",
        *issues[:50],
        f"anomalies kept as-is: {len(notes)}",
        *notes,
        "coverage (weeks reported / expected):",
        *[f"  {c['governorate']} {c['year']}: {c['weeks_reported']}/{c['weeks_expected']}"
          f" ({c['pct_reported']}%)" for c in cov],
    ]
    (OUT / "ewars_quality_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
