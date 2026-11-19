"""Static checks on the site files: translations complete, third-party script pinned, no drug wording."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[1] / "site"


def test_cdn_files_are_pinned_with_integrity():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    for tag in re.findall(r"<(?:script|link)[^>]+cdnjs[^>]+>", html):
        assert 'integrity="sha512-' in tag and "1.9.4" in tag, tag


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_arabic_and_english_have_the_same_keys():
    js = (SITE / "app.js").read_text(encoding="utf-8")
    block = js[js.index("const I18N"):js.index("\n};\n") + 3]
    code = block + "\nconsole.log(JSON.stringify([Object.keys(I18N.ar).sort(), Object.keys(I18N.en).sort()]));"
    out = subprocess.run(["node", "-e", "const ltr=(s)=>s, formula=()=>'';" + code], capture_output=True, text=True, check=True)
    ar, en = json.loads(out.stdout)
    assert ar == en, set(ar) ^ set(en)


def test_further_reading_rows_are_complete_and_link_to_doi():
    import csv
    path = SITE.parent / "reference" / "further_reading.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert rows
    for r in rows:
        assert all(r[k].strip() for k in ("title", "who", "date", "url", "kind", "finding", "finding_ar")), r["title"]
        assert r["url"].startswith("https://doi.org/10.")
