"""M4 step 2 - export the database to the one JSON file the website reads.

Input : data/db/gaza_health.sqlite   (python3 -W ignore -m gaza_map.build_db)
Output: gaza_map/site/data/data.json (committed: it is aggregated public data, no patient-level rows)

The site never computes a rate itself: every number it shows was produced by the SQL views, so the
site, the database and trends.py all agree (tests check this).

Layout (kept compact on purpose, the site loads it in one request):
  months      ["2024-01", ...]
  monthly     disease -> location -> [[month_index, cases, consultations, per_1000, weeks_reported], ...]
              months with fewer than MIN_WEEKS reported weeks are left OUT, so the chart shows a gap
  yearly      disease -> location -> year -> {per_1000, cases, weeks, comparable}   (same epi weeks 1..N)
  location "strip" = all five governorates pooled (sum, then divide).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

from gaza_map.build_db import DB_PATH
from gaza_map.trends import MIN_WEEKS_PER_MONTH

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "gaza_map/site/data/data.json"


def rows(con: sqlite3.Connection, sql: str, *args) -> list[tuple]:
    return con.execute(sql, args).fetchall()


def export(db_path: Path = DB_PATH, out: Path = OUT) -> dict:
    con = sqlite3.connect(db_path)
    try:
        locs = rows(con, "SELECT location_id, key, name_en, name_ar, level FROM locations ORDER BY location_id")
        loc_key = {i: k for i, k, *_ in locs}
        diseases = rows(con, "SELECT disease_id, key, name_en, name_ar, grp, note, late_added FROM diseases "
                             "ORDER BY disease_id")
        dis_key = {i: k for i, k, *_ in diseases}

        last_year, last_week = rows(con, "SELECT year, MAX(epi_week) FROM reporting "
                                         "WHERE year=(SELECT MAX(year) FROM reporting)")[0]
        months = sorted(m for (m,) in rows(con, "SELECT DISTINCT month FROM observations"))
        mi = {m: i for i, m in enumerate(months)}

        # ---- monthly: per governorate, then the strip pooled
        monthly: dict = {}
        for did, lid, month, cases, cons, weeks in rows(
                con, "SELECT disease_id, location_id, month, SUM(cases), SUM(consultations), COUNT(*) "
                     "FROM v_cases_weekly GROUP BY disease_id, location_id, month"):
            if weeks < MIN_WEEKS_PER_MONTH:
                continue
            monthly.setdefault(dis_key[did], {}).setdefault(loc_key[lid], []).append(
                [mi[month], cases, cons, round(cases * 1000.0 / cons, 2), weeks])
        for did, month, cases, cons, weeks in rows(
                con, "SELECT disease_id, month, SUM(cases), SUM(consultations), COUNT(*) "
                     "FROM v_cases_weekly GROUP BY disease_id, month"):
            # a strip-wide month needs the minimum coverage summed over governorates
            if weeks < MIN_WEEKS_PER_MONTH:
                continue
            monthly.setdefault(dis_key[did], {}).setdefault("strip", []).append(
                [mi[month], cases, cons, round(cases * 1000.0 / cons, 2), weeks])
        for per_loc in monthly.values():
            for series in per_loc.values():
                series.sort()

        # ---- yearly, same epi weeks so 2026 (partial) is judged on equal terms
        late = {k for _i, k, *_r, late_added in diseases if late_added}
        starts = dict(rows(con, "SELECT d.key, MIN(o.year * 100 + o.epi_week) FROM observations o "
                                "JOIN diseases d USING(disease_id) WHERE d.late_added=1 AND o.cases>0 "
                                "GROUP BY d.key"))
        yearly: dict = {}

        def put(d, loc, year, cases, cons, weeks):
            comparable = d not in late or (d in starts and year * 100 + 1 >= starts[d])
            yearly.setdefault(d, {}).setdefault(loc, {})[str(year)] = {
                "per_1000": round(cases * 1000.0 / cons, 2), "cases": cases, "weeks": weeks,
                "comparable": comparable}

        for did, lid, year, cases, cons, weeks in rows(
                con, "SELECT disease_id, location_id, year, SUM(cases), SUM(consultations), COUNT(*) "
                     "FROM v_cases_weekly WHERE epi_week <= ? GROUP BY disease_id, location_id, year", last_week):
            put(dis_key[did], loc_key[lid], year, cases, cons, weeks)
        for did, year, cases, cons, weeks in rows(
                con, "SELECT disease_id, year, SUM(cases), SUM(consultations), COUNT(*) "
                     "FROM v_cases_weekly WHERE epi_week <= ? GROUP BY disease_id, year", last_week):
            put(dis_key[did], "strip", year, cases, cons, weeks)

        # ---- reporting sites (how many locations reported): strip-wide, by month and per year
        wk_month = {(y, w): m for y, w, m in rows(con, "SELECT DISTINCT year, epi_week, month FROM observations")}
        by_month: dict = {}
        by_year: dict = {}
        for y, w, n, low in rows(con, "SELECT year, epi_week, reporting_locations, low_sites FROM reporting_sites"):
            if (y, w) in wk_month:
                by_month.setdefault(wk_month[(y, w)], []).append(n)
            by_year.setdefault(y, []).append(n)
        sites_month = [round(sum(by_month[m]) / len(by_month[m]), 1) if m in by_month else None for m in months]

        def median(v):
            v = sorted(v)
            mid = len(v) // 2
            return v[mid] if len(v) % 2 else (v[mid - 1] + v[mid]) / 2

        sites_median = {str(y): median(v) for y, v in by_year.items()}
        overview = {}
        for (y, cons, pct, deaths, tot, act, rep, pact) in rows(
                con, "SELECT year, consultations, pct_reportable_of_consultations, deaths_reportable, "
                     "total_locations, active_locations, reporting_locations, pct_active_reporting FROM overview_totals"):
            comp = rows(con, "SELECT ROUND(AVG(completeness),3), ROUND(AVG(timeliness),3), ROUND(AVG(avg_delay_days),1) "
                             "FROM reporting_sites WHERE year=?", y)[0]
            overview[str(y)] = {"consultations": cons, "pct_reportable": round(pct * 100, 1), "deaths": deaths,
                                "locations_total": tot, "locations_active": act, "locations_reporting": rep,
                                "pct_active_reporting": round(pact * 100, 1),
                                "mean_completeness": comp[0], "mean_timeliness": comp[1], "mean_delay_days": comp[2]}

        coverage: dict = {}
        for lid, year, exp, rep in rows(con, "SELECT location_id, year, weeks_expected, weeks_reported FROM coverage"):
            coverage.setdefault(loc_key[lid], {})[str(year)] = [exp, rep]

        domains: dict = {}
        for lid, dom, a, p, n, nn in rows(
                con, "SELECT location_id, domain, pct_available, pct_partial, pct_not_available, "
                     "pct_not_normally_provided FROM facility_domains"):
            domains.setdefault(loc_key[lid], {})[dom] = [a, p, n, nn]
        hsdu = {loc_key[lid]: [ev, fn] for lid, ev, fn in
                rows(con, "SELECT location_id, hsdu_evaluated, at_least_partially_functioning FROM hsdu_functionality")}

        age: dict = {}
        for lid, year, u5, o5 in rows(
                con, "SELECT o.location_id, o.year, "
                     "SUM(CASE WHEN o.age_group='under5' THEN o.cases END), "
                     "SUM(CASE WHEN o.age_group='over5' THEN o.cases END) "
                     "FROM observations o JOIN diseases d USING(disease_id) "
                     "WHERE d.key='awd' AND o.age_group IN ('under5','over5') GROUP BY o.location_id, o.year"):
            age.setdefault(loc_key[lid], {})[str(year)] = round(100.0 * u5 / (u5 + o5), 1)

        medicine: dict = {}
        for dk, cls, cls_ar, sid, ref, url, note in rows(
                con, "SELECT d.key, m.medicine_class, m.class_ar, m.source_id, m.source_ref, m.source_url, m.note "
                     "FROM medicine_needs m JOIN diseases d USING(disease_id) ORDER BY m.need_id"):
            medicine.setdefault(dk, []).append({"class_en": cls, "class_ar": cls_ar, "source": sid, "ref": ref,
                                                "url": url, "note": note})
        supply = [dict(zip(("as_of", "pct", "wording", "source", "ref", "caveat"), r)) for r in rows(
            con, "SELECT as_of, pct_zero_stock, wording, source_id, source_ref, caveat FROM supply_signals "
                 "ORDER BY as_of, source_id")]
        ncd = [dict(zip(("en", "ar", "available", "partial", "not_available", "expected", "not_standard"), r))
               for r in rows(con, "SELECT service, service_ar, pct_available, pct_partial, pct_not_available, "
                                  "n_hsdu_expected, n_not_up_to_standard FROM ncd_services")]

        sources = [dict(zip(("id", "name", "publisher", "type", "url", "data_up_to", "caveats"), r))
                   for r in rows(con, "SELECT source_id, name, publisher, source_type, url, data_up_to, caveats "
                                      "FROM sources")]
        data = {
            "meta": {"generated": date.today().isoformat(), "last_year": last_year, "last_week": last_week,
                     "min_weeks_per_month": MIN_WEEKS_PER_MONTH, "low_sites_threshold": 20, "sources": sources,
                     "medicine_needs_rows": rows(con, "SELECT COUNT(*) FROM medicine_needs")[0][0]},
            "diseases": [dict(zip(("key", "name_en", "name_ar", "group", "note", "late_added"), r[1:])) for r in diseases],
            "locations": [dict(zip(("key", "name_en", "name_ar", "level"), r[1:])) for r in locs],
            "months": months, "sites_month": sites_month, "sites_median": sites_median, "overview": overview,
            "monthly": monthly, "yearly": yearly, "coverage": coverage,
            "herams": {"domains": domains, "hsdu": hsdu, "ncd": ncd},
            "medicine": medicine, "supply": supply, "awd_under5_share": age,
        }
    finally:
        con.close()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"bytes": out.stat().st_size, "diseases": len(data["diseases"]), "months": len(months)}


if __name__ == "__main__":
    print(export())
