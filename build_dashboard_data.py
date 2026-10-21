"""Build the compact result bundle used by the static dashboard."""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ANALYSIS = ROOT / "analysis"
OUTPUT = ROOT / "dashboard" / "results.js"
PRIMARY_CITIES = {
    "Perth",
    "Adelaide",
    "Melbourne",
    "Sydney",
    "Brisbane",
    "Darwin",
    "Alice Springs",
    "Hobart",
}


def read_csv(name):
    with (ANALYSIS / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def keep(row, fields):
    return {field: row[field] for field in fields}


comparisons = [
    keep(
        row,
        ("city", "primary", "window", "baseline", "element", "anomaly", "current_days", "supported"),
    )
    for row in read_csv("comparisons.csv")
    if row["city"] in PRIMARY_CITIES
    and row["primary"] == "True"
    and row["supported"] == "True"
    and row["element"] in {"tmean_c", "tmax_c", "tmin_c"}
]

monthly = [
    keep(
        row,
        (
            "city",
            "month",
            "baseline",
            "tmean_c_anomaly",
            "tmax_c_anomaly",
            "tmin_c_anomaly",
        ),
    )
    for row in read_csv("monthly_2026_anomalies.csv")
    if row["city"] in PRIMARY_CITIES
]

weighted = [
    keep(row, ("window", "baseline", "element", "anomaly", "share"))
    for row in read_csv("population_weighted_proxy.csv")
    if row["element"] in {"tmean_c", "tmax_c", "tmin_c"}
]

rainfall = [
    keep(
        row,
        (
            "city",
            "window",
            "baseline",
            "current",
            "baseline_value",
            "anomaly",
            "ratio",
            "current_days",
            "expected_days",
            "baseline_years",
        ),
    )
    for row in read_csv("comparisons.csv")
    if row["city"] in PRIMARY_CITIES
    and row["primary"] == "True"
    and row["element"] == "rain_mm"
]

soi = [
    keep(row, ("year", "month", "soi"))
    for row in read_csv("soi_monthly_1980_2026.csv")
    if row["year"] == "2026" and int(row["month"]) <= 9
]

station_population = {
    row["city"]: int(row["population"])
    for row in read_csv("stations.csv")
    if row["city"] in PRIMARY_CITIES and row["primary"] == "True"
}
trend_baseline = {
    row["city"]: float(row["baseline_value"])
    for row in read_csv("comparisons.csv")
    if row["city"] in PRIMARY_CITIES
    and row["primary"] == "True"
    and row["window"] == "Jan–Sep"
    and row["baseline"] == "2000–2025"
    and row["element"] == "tmean_c"
    and row["baseline_value"]
}
period_rows = [
    row
    for row in read_csv("matched_periods.csv")
    if row["city"] in PRIMARY_CITIES
    and row["window"] == "Jan–Sep"
    and row["tmean_c"]
]
annual = []
for year in sorted({int(row["year"]) for row in period_rows}):
    year_rows = {row["city"]: row for row in period_rows if int(row["year"]) == year}
    if set(year_rows) != PRIMARY_CITIES or set(trend_baseline) != PRIMARY_CITIES:
        continue
    population = sum(station_population.values())
    anomaly = sum(
        station_population[city]
        * (float(year_rows[city]["tmean_c"]) - trend_baseline[city])
        for city in PRIMARY_CITIES
    ) / population
    annual.append({"year": year, "anomaly": anomaly, "cities": len(year_rows)})

payload = {
    "comparisons": comparisons,
    "monthly": monthly,
    "weighted": weighted,
    "rainfall": rainfall,
    "soi": soi,
    "annual": annual,
}
OUTPUT.write_text(
    "window.CLIMATE_RESULTS = "
    + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    + ";\n"
)
print(f"Dashboard results: {OUTPUT}")
