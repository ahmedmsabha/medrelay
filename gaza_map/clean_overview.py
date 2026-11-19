"""Clean the EWARS dashboard's "Epidemiological Overview" and "Core M&E" series.

Input : data/raw/ewars/ewars_overview_me_2024-2026.json   (pulled from the public dashboard API)
Output: data/clean/ewars_reporting_sites.csv   one row per epi week: reporting locations + M&E indicators
        data/clean/ewars_overview_totals.csv   one row per year: dashboard headline totals

Why this matters (found while auditing, see docs/study-notes/10-reporting-sites.md):
  In the first 14 weeks of 2024 only 1-9 locations reported per week, versus ~110 in 2025 and ~200 in 2026.
  A rate computed from 5 facilities is not comparable with one computed from 200, and a "peak week" taken
  from the 5-facility weeks is not a finding. We therefore keep the number of reporting sites next to
  every weekly rate and flag weeks below LOW_SITES.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/ewars/ewars_overview_me_2024-2026.json"
OUT = ROOT / "data/clean"
LOW_SITES = 20  # weeks with fewer reporting locations than this are flagged "very few sites"
WEEK = re.compile(r"^(\d{4})-WE(\d{2})")


def parse_week(label: str) -> tuple[int, int]:
    m = WEEK.match(label)
    if not m:
        raise ValueError(f"unrecognised week label: {label!r}")
    return int(m.group(1)), int(m.group(2))


def build(raw: Path = RAW) -> tuple[list[dict], list[dict]]:
    d = json.loads(raw.read_text(encoding="utf-8"))
    sites = {parse_week(r["week"]): r["reporting_locations"] for r in d["reporting_locations"]}
    weeks: dict[tuple[int, int], dict] = {}
    for key, n in sites.items():
        weeks[key] = {"year": key[0], "epi_week": key[1], "reporting_locations": n, "active_locations": None,
                      "completeness": None, "timeliness": None, "avg_delay_days": None}
    for m in d["me"]:
        key = parse_week(m["week"])
        if key[0] < 2024 or key not in weeks:
            continue  # M&E also lists 2023 and future weeks with 0 active locations: not part of our window
        w = weeks[key]
        w["active_locations"] = m["active_locations"]
        w["completeness"] = round(m["completeness"], 4) if m["completeness"] is not None else None
        w["timeliness"] = round(m["timeliness"], 4) if m["timeliness"] is not None else None
        w["avg_delay_days"] = m["avg_delay_days"]
    rows = []
    for key in sorted(weeks):
        w = weeks[key]
        w["low_sites"] = int(w["reporting_locations"] < LOW_SITES)
        rows.append(w)
    totals = [{"year": int(y), **v} for y, v in sorted(d["scalars"].items())]
    return rows, totals


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    rows, totals = build()
    write_csv(OUT / "ewars_reporting_sites.csv", rows)
    write_csv(OUT / "ewars_overview_totals.csv", totals)
    low = [r for r in rows if r["low_sites"]]
    print(f"{len(rows)} weeks; {len(low)} weeks with < {LOW_SITES} reporting locations "
          f"(2024 weeks {low[0]['epi_week']}-{low[-1]['epi_week']})")


if __name__ == "__main__":
    main()
