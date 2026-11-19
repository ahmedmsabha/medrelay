# Gaza Disease & Care Map: the site

Static site: `index.html`, `style.css`, `app.js` (Leaflet from cdnjs) and two data files in `data/`.
No server code, no basemap tiles, no tracking. Language choice is kept in `localStorage` only.

## Rebuild everything (from the repo root)

```bash
python3 -I -W ignore gaza_map/clean_ewars.py     # raw EWARS -> data/clean/
python3 -W ignore -m gaza_map.build_db           # data/clean -> data/db/gaza_health.sqlite
python3 -W ignore -m gaza_map.build_geo          # OCHA boundaries -> data/governorates.geojson (needs data/raw/boundaries)
python3 -W ignore -m gaza_map.export_site        # sqlite -> data/data.json
python3 -m http.server 8765 --directory gaza_map/site
```

Open http://localhost:8765. `data/data.json` and `data/governorates.geojson` are committed so the site works
without the raw files.

## Attribution (keep visible on any published copy)

- EWARS: WHO / Palestinian Ministry of Health (ask WHO oPt / the MoH EWARS focal point before publishing).
- HeRAMS: WHO, data up to 30 June 2025.
- Boundaries: OCHA / HDX COD-AB (pre-war administrative limits).
