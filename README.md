# Australian city climate analysis

Reproduce the eight-city temperature comparison, monthly heatmap and SOI analysis discussed in the accompanying ChatGPT conversation.

This is a source only analysis repository, not an interactive dashboard or live data service. The scripts download the required public inputs and reproduce the January to September 2026 results. Baselines are **2000–2025**, **1981–2010**, and **1980–1989** where enough reference years are available.

## Results at a glance

| Result | Value | Interpretation |
|---|---:|---|
| Eight-city weighted mean anomaly, Jan–Sep vs 2000–2025 | **+0.728°C** | Warm relative to the recent baseline |
| Eight-city weighted mean anomaly, Jan–Sep vs 1981–2010 | **+1.172°C** | Larger anomaly against the earlier baseline |
| Jan–Apr weighted anomaly vs 2000–2025 | **+0.349°C** | More modest warmth early in the year |
| May–Sep weighted anomaly vs 2000–2025 | **+1.029°C** | Stronger warmth in the middle of the year |
| Aug–Sep weighted anomaly vs 2000–2025 | **+1.021°C** | Late-winter/early-spring warmth remained elevated |
| Hobart Jan–Sep derived-mean anomaly vs 2000–2025 | **+0.814°C** | Tmax +0.977°C; Tmin +0.647°C |
| Population represented | **18.30 million (66.3% of Australia)** | A city-population proxy, not a national land average |

The 2026 monthly SOI changed sign in April and became strongly negative from May, reaching −29.1 in July and −21.4 in September. That timing is consistent with an ENSO contribution, but this descriptive analysis does not attribute the observed warmth to ENSO. Results use one station per city, are not homogenised, and should not be read as an official national climate assessment.

## Quick start

Use Python 3.11 or later (tested with Python 3.12). Unzip the download, open a terminal in the `australian-city-climate` folder, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py --download
```

On Windows, activate with `.venv\Scripts\activate` instead.

No source data or generated results are included in the repository. `python run.py --download` retrieves the documented public inputs and then builds the analysis tables and chart. No API key is required.

For the analysis tables alone, no external packages are needed:

```bash
python3 analyze_cities.py
```

To download/validate sources and rebuild in one command:

```bash
python run.py --download
```

To run the lightweight result checks:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

## Contents

| File or directory | Purpose |
|---|---|
| `run.py` | Runs the analysis and chart generation in sequence. |
| `download_data.py` | Downloads or validates all NOAA GHCN-Daily, BoM SOI and ABS inputs consumed by the analysis. |
| `analyze_cities.py` | Parses daily records, applies quality/coverage rules, computes climatologies, anomalies and population weights; exports CSV and JSON. |
| `plot_cities.py` | Recreates the baseline-comparison chart, monthly heatmap and SOI row. |
| `requirements.txt` | Plotting dependencies pinned to the versions used for this package. |
| `requirements-dev.txt` | Optional local test dependency. |
| `raw/` | Created by `download_data.py` and ignored by Git. Contains the downloaded NOAA, BoM and ABS source files. |
| `analysis/` | Created when the analysis runs; contains daily/monthly CSVs, baseline tables, comparisons, quality flags and analysis JSON. |
| `outputs/` | Created when the analysis runs; contains the generated PNG chart. |
| `METHODS.md` | Detailed station choices, sources, aggregation rules and limitations. |

## Scope and modifications

The primary series represent Perth, Adelaide, Melbourne, Sydney, Brisbane, Darwin, Alice Springs and Hobart. Archerfield is included as a Brisbane sensitivity check. `SPECS`, `BASES`, `WINDOWS` and `CUTOFF` are near the top of `analyze_cities.py`.

The scripts currently target the 2026 analysis. To extend the date range, update the raw observations, date/window configuration, year loops and plot labels together. Changing `CUTOFF` alone is not enough. A general station selector and automatic refresh are future app work.

The population-weighted result is a proxy based on one station per city, not a national gridded exposure estimate. Station records are not homogenised; missing observations and reference-year counts matter. See `METHODS.md` before interpreting results or publishing derivative work.

## Relationship to the Snowy forecast app

Keep this project as a separate GitHub repository. It is the source historical analysis, not a live forecast app. The Snowy rainfall scorecard uses a compact export of the monthly 2000–2025 city climatologies for its separate city temperature page. The Snowy repository stores its own copy of that export and does not depend on this repository at runtime.

Source data retain the terms and attribution requirements of their providers: Bureau of Meteorology, NOAA NCEI and the Australian Bureau of Statistics. Source URLs are documented in `METHODS.md` and generated `analysis/stations.csv`.
