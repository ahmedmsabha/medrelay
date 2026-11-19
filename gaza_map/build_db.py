"""M3 - build the SQLite database from data/clean/ and data/raw/herams/.

Run (from the repo root):  python3 -W ignore -m gaza_map.build_db   ->  data/db/gaza_health.sqlite

The database is rebuilt from scratch every time (delete + create), so it is never the source of
truth: the CSVs are. That keeps the build deterministic and easy to test.

Tables
  sources            where every number comes from (+ source type and caveats)
  locations          Gaza Strip + 5 governorates (aliases map "Gaza City" -> "Gaza" etc.)
  diseases           from gaza_map/reference/diseases.csv
  observations       EWARS weekly cases/deaths: location x week x disease x age group
  reporting          consultations per location x week (the denominator); only weeks that reported
  coverage           weeks expected vs reported per location x year
  facility_domains   HeRAMS service-domain availability (%) per location
  hsdu_functionality HeRAMS facilities evaluated vs at least partially functioning
  medicine_needs     disease -> medicine CLASS, one row per sourced claim. EMPTY until sourced.
Views (the three groupings the site needs)
  v_cases_weekly, v_by_disease, v_by_location, v_by_medicine

Design rules
  * Unknown stays NULL (deaths for chickenpox/impetigo/ectoparasitic, sex, coordinates).
  * Rates are always SUM(cases)/SUM(consultations), never an average of rates.
  * A week that did not report has no row in `reporting`, so it can never look like a zero.
  * medicine_needs.source_id is NOT NULL: a medicine class without a source cannot be stored.
    Classes only, never drug names or doses (CLAUDE.md safety rule 4).
"""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import date
from pathlib import Path

from gaza_map.trends import LATE_ADDED, drop_untracked, load_weekly, month_of

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT / "data/clean"
HERAMS = ROOT / "data/raw/herams"
REF = ROOT / "gaza_map/reference/diseases.csv"
DB_PATH = ROOT / "data/db/gaza_health.sqlite"
GEO = ROOT / "gaza_map/site/data/governorates.geojson"  # made by build_geo.py (OCHA COD-AB)

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE sources (
  source_id   TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  publisher   TEXT NOT NULL,
  source_type TEXT NOT NULL CHECK (source_type IN
              ('official statistic','survey','modelled estimate','press coverage')),
  url         TEXT,
  data_up_to  TEXT,
  caveats     TEXT NOT NULL
);

CREATE TABLE locations (
  location_id INTEGER PRIMARY KEY,
  key         TEXT NOT NULL UNIQUE,
  name_en     TEXT NOT NULL,
  name_ar     TEXT NOT NULL,
  level       TEXT NOT NULL CHECK (level IN ('strip','governorate')),
  lat         REAL,   -- centre point from the OCHA boundary layer; NULL for the strip as a whole
  lon         REAL
);
CREATE TABLE location_aliases (
  alias       TEXT PRIMARY KEY,
  location_id INTEGER NOT NULL REFERENCES locations(location_id)
);

CREATE TABLE diseases (
  disease_id INTEGER PRIMARY KEY,
  key        TEXT NOT NULL UNIQUE,
  name_en    TEXT NOT NULL,
  name_ar    TEXT NOT NULL,
  grp        TEXT NOT NULL,
  note       TEXT,
  late_added INTEGER NOT NULL DEFAULT 0   -- 1 = added to the system mid-2025; earlier weeks untracked
);

CREATE TABLE observations (
  obs_id       INTEGER PRIMARY KEY,
  source_id    TEXT    NOT NULL REFERENCES sources(source_id),
  location_id  INTEGER NOT NULL REFERENCES locations(location_id),
  disease_id   INTEGER NOT NULL REFERENCES diseases(disease_id),
  period_start TEXT    NOT NULL,           -- ISO date, Sunday
  period_end   TEXT    NOT NULL,
  year         INTEGER NOT NULL,
  epi_week     INTEGER NOT NULL,
  month        TEXT    NOT NULL,           -- YYYY-MM by the Thursday rule
  age_group    TEXT    NOT NULL CHECK (age_group IN ('all','under5','over5')),
  sex          TEXT,                       -- always NULL for EWARS (not reported)
  cases        INTEGER NOT NULL CHECK (cases >= 0),
  deaths       INTEGER CHECK (deaths >= 0),
  tracked      INTEGER NOT NULL CHECK (tracked IN (0,1)),
  UNIQUE (location_id, year, epi_week, disease_id, age_group)
);
CREATE INDEX ix_obs_loc ON observations(location_id, year, epi_week);
CREATE INDEX ix_obs_dis ON observations(disease_id, month);

CREATE TABLE reporting (
  location_id   INTEGER NOT NULL REFERENCES locations(location_id),
  year          INTEGER NOT NULL,
  epi_week      INTEGER NOT NULL,
  consultations INTEGER NOT NULL CHECK (consultations > 0),
  PRIMARY KEY (location_id, year, epi_week)
);

CREATE TABLE coverage (
  location_id    INTEGER NOT NULL REFERENCES locations(location_id),
  year           INTEGER NOT NULL,
  weeks_expected INTEGER NOT NULL,
  weeks_reported INTEGER NOT NULL,
  missing_weeks  TEXT,
  PRIMARY KEY (location_id, year)
);

CREATE TABLE facility_domains (
  location_id INTEGER NOT NULL REFERENCES locations(location_id),
  source_id   TEXT    NOT NULL REFERENCES sources(source_id),
  domain      TEXT    NOT NULL,
  pct_available INTEGER, pct_partial INTEGER, pct_not_available INTEGER, pct_not_normally_provided INTEGER,
  PRIMARY KEY (location_id, domain)
);

CREATE TABLE hsdu_functionality (
  location_id INTEGER PRIMARY KEY REFERENCES locations(location_id),
  source_id   TEXT    NOT NULL REFERENCES sources(source_id),
  hsdu_evaluated INTEGER NOT NULL,
  at_least_partially_functioning INTEGER NOT NULL
);

CREATE TABLE medicine_needs (
  need_id        INTEGER PRIMARY KEY,
  disease_id     INTEGER NOT NULL REFERENCES diseases(disease_id),
  medicine_class TEXT    NOT NULL,         -- a CLASS (e.g. oral rehydration), never a drug name or dose
  source_id      TEXT    NOT NULL REFERENCES sources(source_id),
  source_ref     TEXT    NOT NULL,         -- page / table in the source
  note           TEXT
);

-- one row per location x week x disease (all ages), only for weeks that reported.
-- age-split diseases (watery diarrhoea, cholera) are summed over under5 + over5.
CREATE VIEW v_cases_weekly AS
SELECT o.location_id, o.year, o.epi_week, o.period_start, o.month, o.disease_id,
       SUM(o.cases)  AS cases,
       SUM(o.deaths) AS deaths,
       r.consultations,
       ROUND(SUM(o.cases) * 1000.0 / r.consultations, 2) AS per_1000
FROM observations o
JOIN reporting r USING (location_id, year, epi_week)
WHERE o.tracked = 1
GROUP BY o.location_id, o.year, o.epi_week, o.disease_id;

-- grouping 1: by disease (strip-wide, monthly)
CREATE VIEW v_by_disease AS
SELECT d.key AS disease, d.name_en, d.name_ar, w.month,
       SUM(w.cases) AS cases, SUM(w.consultations) AS consultations,
       ROUND(SUM(w.cases) * 1000.0 / SUM(w.consultations), 2) AS per_1000,
       COUNT(*) AS location_weeks_reported
FROM v_cases_weekly w JOIN diseases d USING (disease_id)
GROUP BY d.key, w.month;

-- grouping 2: by location (governorate x year x disease); weeks_reported shows partial years
CREATE VIEW v_by_location AS
SELECT l.key AS location, l.name_en AS location_name, l.name_ar AS location_name_ar,
       d.key AS disease, w.year,
       SUM(w.cases) AS cases, SUM(w.consultations) AS consultations,
       ROUND(SUM(w.cases) * 1000.0 / SUM(w.consultations), 2) AS per_1000,
       COUNT(*) AS weeks_reported
FROM v_cases_weekly w JOIN locations l USING (location_id) JOIN diseases d USING (disease_id)
GROUP BY l.key, d.key, w.year;

-- grouping 3: by medicine class (empty until medicine_needs has sourced rows)
CREATE VIEW v_by_medicine AS
SELECT m.medicine_class, d.key AS disease, w.month,
       SUM(w.cases) AS cases, SUM(w.consultations) AS consultations,
       ROUND(SUM(w.cases) * 1000.0 / SUM(w.consultations), 2) AS per_1000,
       s.name AS need_source, m.source_ref
FROM medicine_needs m
JOIN diseases d USING (disease_id)
JOIN sources s USING (source_id)
JOIN v_cases_weekly w ON w.disease_id = d.disease_id
GROUP BY m.need_id, w.month;
"""

SOURCES = [
    ("ewars", "EWARS Unified Disease Surveillance Dashboard - The Gaza Strip",
     "WHO / Palestinian Ministry of Health", "official statistic",
     "https://bi.sehatty.ps (public Metabase dashboard 881c87a0-f2c6-440a-bab4-9996b5c0fb8c)",
     "2026-epi-week-45",
     "Suspected cases from reporting facilities only; the number of reporting facilities changes, "
     "so rates are per 1,000 consultations (a proxy, not incidence). Some weeks did not report. "
     "Consultations include war injuries. No sex; age only for watery diarrhoea and cholera. "
     "Chickenpox, ectoparasitic infections and impetigo were added mid-2025. Attribution required."),
    ("herams", "HeRAMS occupied Palestinian territory - Health services across the governorates of Gaza",
     "WHO", "survey",
     "https://www.who.int (publication herams-opt-gaza-governorate-infographics-2025-06)",
     "2025-06-30",
     "Only facilities reporting to HeRAMS; WHO states the analysis is not final. Rafah has no "
     "domain page. Tables hand-extracted from the PDF and checked against rendered pages."),
]

LOCATIONS = [  # key, en, ar, level
    ("strip", "Gaza Strip", "قطاع غزة", "strip"),
    ("gaza", "Gaza", "غزة", "governorate"),
    ("north_gaza", "North Gaza", "شمال غزة", "governorate"),
    ("deir_al_balah", "Deir Al-Balah", "دير البلح", "governorate"),
    ("khan_yunis", "Khan Yunis", "خان يونس", "governorate"),
    ("rafah", "Rafah", "رفح", "governorate"),
]
ALIASES = {  # spelling in a source -> location key
    "Gaza Strip": "strip", "Gaza": "gaza", "Gaza City": "gaza", "North Gaza": "north_gaza",
    "Deir Al-Balah": "deir_al_balah", "Khan Yunis": "khan_yunis", "Khan Younis": "khan_yunis",
    "Rafah": "rafah",
}


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_int(v: str) -> int | None:
    return int(v) if v not in ("", None) else None


def build(db_path: Path = DB_PATH) -> dict[str, int]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    try:
        con.executescript(SCHEMA)
        con.executemany("INSERT INTO sources VALUES (?,?,?,?,?,?,?)", SOURCES)
        con.executemany("INSERT INTO locations(key,name_en,name_ar,level) VALUES (?,?,?,?)", LOCATIONS)
        loc = {k: i for i, k in con.execute("SELECT location_id, key FROM locations")}
        if GEO.exists():
            for f in json.loads(GEO.read_text(encoding="utf-8"))["features"]:
                pr = f["properties"]
                con.execute("UPDATE locations SET lat=?, lon=? WHERE key=?", (pr["lat"], pr["lon"], pr["key"]))
        con.executemany("INSERT INTO location_aliases VALUES (?,?)",
                        [(a, loc[k]) for a, k in ALIASES.items()])

        dis = {}
        for r in read_csv(REF):
            cur = con.execute(
                "INSERT INTO diseases(key,name_en,name_ar,grp,note,late_added) VALUES (?,?,?,?,?,?)",
                (r["disease_key"], r["name_en"], r["name_ar"], r["group"], r["note"] or None,
                 int(r["disease_key"] in LATE_ADDED)))
            dis[r["disease_key"]] = cur.lastrowid

        # the tracking rule is shared with trends.py so the two can never disagree
        _, starts = drop_untracked(load_weekly())

        def tracked(disease: str, year: int, week: int) -> int:
            if disease not in LATE_ADDED:
                return 1
            return int(disease in starts and (year, week) >= starts[disease])

        obs = []
        for r in read_csv(CLEAN / "ewars_weekly.csv"):
            y, w = int(r["year"]), int(r["epi_week"])
            obs.append(("ewars", loc[ALIASES[r["governorate"]]], dis[r["disease"]], r["week_start"],
                        r["week_end"], y, w, month_of(date.fromisoformat(r["week_start"])),
                        r["age_group"], None, int(r["cases"]), to_int(r["deaths"]),
                        tracked(r["disease"], y, w)))
        con.executemany(
            "INSERT INTO observations(source_id,location_id,disease_id,period_start,period_end,year,"
            "epi_week,month,age_group,sex,cases,deaths,tracked) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", obs)

        con.executemany(
            "INSERT INTO reporting VALUES (?,?,?,?)",
            [(loc[ALIASES[r["governorate"]]], int(r["year"]), int(r["epi_week"]), int(r["consultations"]))
             for r in read_csv(CLEAN / "ewars_consultations.csv") if int(r["consultations"]) > 0])
        con.executemany(
            "INSERT INTO coverage VALUES (?,?,?,?,?)",
            [(loc[ALIASES[r["governorate"]]], int(r["year"]), int(r["weeks_expected"]),
              int(r["weeks_reported"]), r["missing_weeks"] or None)
             for r in read_csv(CLEAN / "ewars_coverage.csv")])

        if HERAMS.exists():
            con.executemany(
                "INSERT INTO facility_domains VALUES (?,?,?,?,?,?,?)",
                [(loc[ALIASES[r["governorate"]]], "herams", r["domain"], to_int(r["pct_available"]),
                  to_int(r["pct_partial"]), to_int(r["pct_not_available"]),
                  to_int(r["pct_not_normally_provided"]))
                 for r in read_csv(HERAMS / "herams_domain_availability_by_governorate_2025-06.csv")])
            con.executemany(
                "INSERT INTO hsdu_functionality VALUES (?,?,?,?)",
                [(loc[ALIASES[r["governorate"]]], "herams", int(r["hsdu_evaluated"]),
                  int(r["at_least_partially_functioning"]))
                 for r in read_csv(HERAMS / "herams_hsdu_functionality_by_governorate_2025-06.csv")])
        con.commit()
        counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                  for t in ("sources", "locations", "diseases", "observations", "reporting", "coverage",
                            "facility_domains", "hsdu_functionality", "medicine_needs")}
        bad = con.execute("PRAGMA foreign_key_check").fetchall()
        if bad:
            raise RuntimeError(f"foreign key violations: {bad[:3]}")
        return counts
    finally:
        con.close()


if __name__ == "__main__":
    for table, n in build().items():
        print(f"{table:<20} {n}")
    print(f"-> {DB_PATH}")
