"""M2 - trends from the cleaned EWARS table.

Input : data/clean/ewars_weekly.csv  (made by clean_ewars.py)
Output: data/clean/trends_weekly.csv     rate per 1,000 consultations, governorate x week x disease
        data/clean/trends_monthly.csv    same, aggregated to months (for the map)
        data/clean/trends_yoy.csv        same epi weeks (1..N) compared across years
        data/clean/trends_awd_age.csv    share of under-5 among watery-diarrhoea cases
        data/clean/trends_report.txt     headline findings (read this first)

The one idea behind everything here:
  raw counts depend on HOW MANY facilities reported that week, so they cannot be compared
  between places or years. Dividing by total consultations (cases per 1,000 consultations)
  removes most of that. It is still a *proxy*, not an incidence rate (no population denominator).

Rules we keep:
  * A week with consultations == 0 is "not reported" and is dropped, never turned into a rate of 0.
  * To combine rows we SUM cases and SUM consultations first, then divide. Never average rates:
    a week with 100 consultations would weigh the same as one with 10,000.
  * A month is flagged low_coverage when fewer than 3 of its weeks reported.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data/clean"
MIN_WEEKS_PER_MONTH = 3
PER = 1000
# Added to the dashboard mid-2025: no deaths field, no cases at all before epi week 23-35 of 2025.
# For these, earlier weeks mean "not tracked". For every other disease a 0 is a real zero
# (e.g. measles 2025), so we must NOT apply this rule to them.
LATE_ADDED = {"chickenpox", "ectoparasitic", "impetigo"}


def rate(cases: float, consultations: float) -> float | None:
    """Cases per 1,000 consultations; None when there is no denominator."""
    if consultations <= 0:
        return None
    return round(cases * PER / consultations, 2)


def month_of(week_start: date) -> str:
    """Assign a week to a month by its Thursday (the ISO rule): 2023-12-31..2024-01-06 -> 2024-01."""
    mid = week_start + timedelta(days=4)
    return f"{mid.year}-{mid.month:02d}"


def load_weekly(path: Path = CLEAN / "ewars_weekly.csv") -> list[dict]:
    """One row per governorate x week x disease, for weeks that actually reported (consultations > 0).

    Watery diarrhoea and cholera only exist split by age (under5 / over5), so their "all ages"
    value is the sum of the two parts.
    """
    merged: dict = {}
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cons = int(r["consultations"] or 0)
            if cons <= 0:
                continue
            key = (r["governorate"], int(r["year"]), int(r["epi_week"]), r["disease"])
            row = merged.setdefault(key, {
                "governorate": r["governorate"], "year": int(r["year"]), "epi_week": int(r["epi_week"]),
                "week_start": date.fromisoformat(r["week_start"]), "disease": r["disease"],
                "cases": 0, "deaths": None, "consultations": cons,
            })
            row["cases"] += int(r["cases"])
            if r["deaths"] != "":
                row["deaths"] = (row["deaths"] or 0) + int(r["deaths"])
    return list(merged.values())


def tracking_starts(rows: list[dict]) -> dict[str, tuple[int, int]]:
    """First (year, epi_week) in which a disease has any case anywhere in the strip.

    Chickenpox, ectoparasitic infections and impetigo have no cases at all until mid-2025:
    they were added to the system then. Before that date the honest value is "not tracked",
    not "0 cases", so those weeks are dropped (same lesson as missing weeks).
    """
    first: dict[str, tuple[int, int]] = {}
    for r in rows:
        if r["disease"] in LATE_ADDED and r["cases"] > 0:
            k = (r["year"], r["epi_week"])
            if r["disease"] not in first or k < first[r["disease"]]:
                first[r["disease"]] = k
    return first


def drop_untracked(rows: list[dict]) -> tuple[list[dict], dict[str, tuple[int, int]]]:
    starts = tracking_starts(rows)
    kept = [r for r in rows
            if r["disease"] not in LATE_ADDED or (
                r["disease"] in starts and (r["year"], r["epi_week"]) >= starts[r["disease"]])]
    return kept, starts


def weekly_rates(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        out.append({
            "governorate": r["governorate"], "year": r["year"], "epi_week": r["epi_week"],
            "week_start": r["week_start"].isoformat(), "disease": r["disease"],
            "cases": r["cases"], "consultations": r["consultations"],
            "per_1000": rate(r["cases"], r["consultations"]),
        })
    return out


def _sum_by(rows: list[dict], keyfn) -> dict:
    """key -> [cases, deaths, consultations, set of weeks]; consultations counted ONCE per week
    (it is repeated on every disease row of that week)."""
    acc: dict = defaultdict(lambda: [0, 0, 0, set()])
    for r in rows:
        k = keyfn(r)
        a = acc[k]
        a[0] += r["cases"]
        a[1] += r["deaths"] or 0  # deaths are not reported for some diseases; only cases drive rates
        wk = (r["governorate"], r["year"], r["epi_week"])
        if wk not in a[3]:
            a[3].add(wk)
            a[2] += r["consultations"]
    return acc


def monthly(rows: list[dict]) -> list[dict]:
    acc = _sum_by(rows, lambda r: (r["governorate"], month_of(r["week_start"]), r["disease"]))
    out = []
    for (gov, month, disease), (cases, deaths, cons, weeks) in sorted(acc.items()):
        out.append({
            "governorate": gov, "month": month, "disease": disease, "cases": cases, "deaths": deaths,
            "consultations": cons, "weeks_reported": len(weeks),
            "per_1000": rate(cases, cons), "low_coverage": len(weeks) < MIN_WEEKS_PER_MONTH,
        })
    return out


def year_over_year(rows: list[dict], last_week: int,
                   starts: dict[str, tuple[int, int]] | None = None) -> list[dict]:
    """Compare years on the SAME epi weeks (1..last_week) so 2026 is not judged against full years."""
    sub = [r for r in rows if r["epi_week"] <= last_week]
    acc = _sum_by(sub, lambda r: (r["governorate"], r["year"], r["disease"]))
    out = []
    for (gov, year, disease), (cases, deaths, cons, weeks) in sorted(acc.items()):
        out.append({
            "governorate": gov, "year": year, "disease": disease, "weeks_1_to": last_week,
            "weeks_reported": len(weeks), "cases": cases, "deaths": deaths,
            "consultations": cons, "per_1000": rate(cases, cons),
            # comparable only if the disease was already tracked from week 1 of that year
            "comparable": (starts is None) or disease not in LATE_ADDED
                          or (disease in starts and (year, 1) >= starts[disease]),
        })
    return out


def national_yoy(rows: list[dict], last_week: int,
                 starts: dict[str, tuple[int, int]] | None = None) -> list[dict]:
    """Strip-wide version: all governorates pooled (sum then divide)."""
    sub = [r for r in rows if r["epi_week"] <= last_week]
    acc = _sum_by(sub, lambda r: (r["year"], r["disease"]))
    return [{"year": y, "disease": d, "cases": c, "consultations": n, "per_1000": rate(c, n),
             "comparable": (starts is None) or d not in LATE_ADDED or (d in starts and (y, 1) >= starts[d])}
            for (y, d), (c, _dt, n, _w) in sorted(acc.items())]


def awd_age_share(path: Path = CLEAN / "ewars_weekly.csv") -> list[dict]:
    """Under-5 share of watery-diarrhoea cases per governorate x year (only AWD carries age)."""
    cases: dict = defaultdict(lambda: {"under5": 0, "over5": 0})
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["disease"] == "awd" and r["age_group"] in ("under5", "over5"):
                cases[(r["governorate"], int(r["year"]))][r["age_group"]] += int(r["cases"])
    out = []
    for (gov, year), v in sorted(cases.items()):
        tot = v["under5"] + v["over5"]
        out.append({"governorate": gov, "year": year, "under5": v["under5"], "over5": v["over5"],
                    "under5_share_pct": round(100 * v["under5"] / tot, 1) if tot else None})
    return out


def low_site_weeks(path: Path = CLEAN / "ewars_reporting_sites.csv") -> set[tuple[int, int]]:
    """(year, epi_week) with fewer than 20 reporting locations (first 14 weeks of 2024: 1-9 sites)."""
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as f:
        return {(int(r["year"]), int(r["epi_week"])) for r in csv.DictReader(f) if r["low_sites"] == "1"}


def median_sites(path: Path = CLEAN / "ewars_reporting_sites.csv") -> dict[int, float]:
    if not path.exists():
        return {}
    by: dict[int, list[int]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            by[int(r["year"])].append(int(r["reporting_locations"]))
    out = {}
    for y, v in by.items():
        v.sort()
        mid = len(v) // 2
        out[y] = v[mid] if len(v) % 2 else (v[mid - 1] + v[mid]) / 2
    return out


def peaks(rows: list[dict], exclude: set[tuple[int, int]] | None = None) -> list[dict]:
    """Pooled (strip-wide) peak week per disease: the week with the highest per-1,000 rate.

    Weeks in `exclude` (very few reporting sites) cannot be a peak: a rate from 5 facilities is not
    comparable with one from 200 (see docs/study-notes/10-reporting-sites.md).
    """
    exclude = exclude or set()
    rows = [r for r in rows if (r["year"], r["epi_week"]) not in exclude]
    acc = _sum_by(rows, lambda r: (r["disease"], r["year"], r["epi_week"], r["week_start"]))
    # consultations summed across governorates for that week (each governorate counted once)
    best: dict = {}
    for (d, y, w, ws), (c, _dt, n, _wk) in acc.items():
        if n < 5000 or c == 0:  # ignore weeks with tiny denominators: one clinic would dominate
            continue
        p = rate(c, n)
        if d not in best or p > best[d]["per_1000"]:
            best[d] = {"disease": d, "year": y, "epi_week": w, "week_start": ws.isoformat(),
                       "cases": c, "consultations": n, "per_1000": p}
    return sorted(best.values(), key=lambda r: -r["per_1000"])


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    rows, starts = drop_untracked(load_weekly())
    last_week = max(r["epi_week"] for r in rows if r["year"] == max(x["year"] for x in rows))
    write_csv(CLEAN / "trends_weekly.csv", weekly_rates(rows))
    mon = monthly(rows)
    write_csv(CLEAN / "trends_monthly.csv", mon)
    yoy = year_over_year(rows, last_week, starts)
    write_csv(CLEAN / "trends_yoy.csv", yoy)
    age = awd_age_share()
    write_csv(CLEAN / "trends_awd_age.csv", age)
    nat = national_yoy(rows, last_week, starts)

    lines = [f"Same-weeks comparison: epi weeks 1-{last_week} of each year", "",
             "Strip-wide cases per 1,000 consultations (pooled):"]
    for d in sorted({r["disease"] for r in nat}):
        vals = {r["year"]: r["per_1000"] for r in nat if r["disease"] == d}
        comp = {r["year"]: r["comparable"] for r in nat if r["disease"] == d}
        lines.append(f"  {d:<20} " + "  ".join(
            f"{y}: {v}{'' if comp[y] else '*'}" for y, v in sorted(vals.items())))
    late = {d: f"{y}-WE{w:02d}" for d, (y, w) in starts.items()}
    lines += ["", "* = disease not tracked for the whole period; not comparable. First case seen:"]
    lines += [f"  {d:<20} {v}" for d, v in sorted(late.items())]
    ms = median_sites()
    if ms:
        lines += ["", "Median reporting locations per week (strip-wide): "
                  + "  ".join(f"{y}: {v:g}" for y, v in sorted(ms.items())),
                  "Weeks with < 20 reporting locations are excluded from the peak table."]
    lines += ["", "Peak week per disease (pooled, weeks with >= 5,000 consultations and >= 20 reporting locations):"]
    for p in peaks(rows, low_site_weeks()):
        lines.append(f"  {p['disease']:<20} {p['year']}-WE{p['epi_week']:02d} ({p['week_start']}) "
                     f"{p['per_1000']} per 1,000 ({p['cases']} cases)")
    lines += ["", "Under-5 share of watery diarrhoea cases (%):"]
    for r in age:
        lines.append(f"  {r['governorate']:<14} {r['year']}: {r['under5_share_pct']}")
    low = sum(1 for m in mon if m["low_coverage"])
    lines += ["", f"Monthly cells: {len(mon)}; flagged low coverage (<{MIN_WEEKS_PER_MONTH} weeks): {low}",
              "", "NOT answerable from EWARS: sex, language, allergy/asthma, anything below governorate."]
    (CLEAN / "trends_report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
