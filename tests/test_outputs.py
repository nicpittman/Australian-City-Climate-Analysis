import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_primary_city_climatologies_cover_every_month():
    with (ROOT / "analysis" / "monthly_climatologies.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    primary = {"Perth", "Adelaide", "Melbourne", "Sydney", "Brisbane",
               "Darwin", "Alice Springs", "Hobart"}
    recent = [row for row in rows if row["baseline"] == "2000–2025"]
    for city in primary:
        assert {int(row["month"]) for row in recent if row["city"] == city} == set(range(1, 13))


def test_key_published_result_matches_analysis_snapshot():
    analysis = json.loads((ROOT / "analysis" / "analysis.json").read_text())
    result = next(
        row for row in analysis["weighted"]
        if row["window"] == "Jan–Sep"
        and row["baseline"] == "2000–2025"
        and row["element"] == "tmean_c"
    )
    assert round(result["anomaly"], 3) == 0.728
    assert round(analysis["population"]["share"] * 100, 1) == 66.3
