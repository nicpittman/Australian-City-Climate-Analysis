# Australian cities: 2026 temperature comparison

Current period: 1 January to 30 September 2026.

This is an exploratory, reproducible station analysis. It is not an official BoM climate assessment. Temperature and rainfall observations are BoM station records distributed through NOAA GHCN-Daily.

## Main results

The January to September population-weighted eight-station mean-temperature anomaly is +0.728°C against 2000–2025 and +1.172°C against 1981–2010.

Against 2000–2025, the weighted mean anomaly rises from +0.349°C in January–April to +1.029°C in May–September. August–September is +1.021°C. These are descriptive comparisons, not a test of an abrupt climate regime change.

Hobart's January to September anomalies are +0.977°C for daily maxima, +0.647°C for daily minima and +0.814°C for derived mean temperature.

The monthly BoM SOI in 2026 was +9.9, +11.0, +8.9, −11.2, −14.5, −24.9, −29.1, −14.6 and −21.4 from January through September. The sign reversed in April and the negative signal strengthened in May–July. Negative SOI is associated with El Niño. This timing is consistent with an ENSO contribution, but this analysis does not quantify or attribute the warming to ENSO.

## Stations

| City represented | Station | BoM ID | Choice and limits |
|---|---|---|---|
| Perth | Perth Airport M.O. | 009021 | Long airport record; distinct from newer airport site 009291 and Perth Metro. |
| Adelaide | Parafield Airport | 023013 | 17 km north of central Adelaide. Old Adelaide Airport M.O. 023034 stops in September 2026; it is not spliced to replacement 023154. |
| Melbourne | Melbourne Airport | 086282 | Avoids concatenating Latrobe Street and Olympic Park. |
| Sydney | Sydney Airport AMO | 066037 | Avoids Observatory Hill station changes; coastal airport does not represent all of western Sydney. |
| Brisbane region | Amberley AMO | 040004 | Ipswich within Greater Brisbane; has better early-1980s coverage than Archerfield, but it is not central Brisbane. |
| Darwin | Darwin Airport | 014015 | Long airport record. |
| Alice Springs | Alice Springs Airport | 015590 | About 11 km from the township. |
| Hobart | Ellerslie Road | 094029 | Same city station as the earlier Hobart analysis. |
| Brisbane sensitivity check | Archerfield Airport | 040211 | Not included in population weights. Modern January to September mean anomaly +0.732°C, compared with Amberley's +0.708°C. |

Site identity is maintained. This does not establish homogeneity: instruments, local exposure and station surroundings can still change within a station ID. Long-term trend attribution should use homogenised ACORN-SAT records and/or appropriate gridded analyses.

## Baselines and aggregation

* Modern baseline: 2000–2025, excluding the target year 2026.
* Historical baseline: 1981–2010, used here to give a 30-year reference beginning around 1980. It is not a preindustrial baseline or the single year 1980.
* Optional 1980s decade: 1980–1989, supplied separately. It is a shorter, noisier reference. Brisbane's YTD decade comparison is suppressed because fewer than eight years pass the coverage rule; therefore no eight-city weighted decade result is reported.
* Tmax and Tmin are daily maximum and minimum temperature in °C. Derived daily mean is (Tmax + Tmin)/2, only on dates with both values; it is not an average of subdaily thermometer readings.
* Monthly temperature requires at least 90% valid days. Matched period temperature requires at least 98%; rainfall requires 100% for either aggregation.
* Matched comparisons omit 29 February from all years. The same calendar window is compared, but a small number of missing temperature dates can differ between years. No infilling is performed.
* Each eligible reference year gets equal weight. The reference sample is chosen separately for each station, measure and window. Therefore a derived-mean anomaly need not exactly equal the average of the separately estimated Tmax and Tmin anomalies.
* At least 20 valid reference periods are required for anomalies against the 26- or 30-year baselines, and eight for the 10-year baseline. Unsuppressed temperature comparisons remain exploratory when reference coverage is incomplete.
* For January to September derived mean, modern reference counts range 22–26 years and historical counts range 22–30. These are available-observation reference means, not official WMO climate normals. Full lists of eligible years are written to `comparisons.csv`.
* Current January to September paired-temperature counts range 271–273 of 273 expected dates.

Raw GHCN values equal to −9999 are missing. Values with nonblank quality flags are excluded, but their values and flags remain in the generated daily table. GHCN measurements are converted from tenths of °C and tenths of mm. Source flag `a` denotes Australian Bureau of Meteorology data.

Rainfall is retained as supporting data, but many station-period totals or references fail completeness requirements. In particular, very small complete-period rainfall reference samples at Parafield and Amberley are suppressed. Do not infer nationwide dryness from the eight temperature anomalies. The Hobart raw rain event on 11 May 2018 is quality-flagged in GHCN and is excluded here, as in the earlier workbook; it merits verification against BoM before a production rainfall climatology is fixed.

## Population weighting

Seven ABS Greater Capital City Statistical Areas (GCCSAs), excluding Canberra, plus Alice Springs Significant Urban Area (SUA 7001), contain 18,297,133 residents, 66.261% of Australia's 27,613,654 residents in the same June 2025 ABS regional-population release. Populations are read directly from the saved ABS spreadsheets. This denominator differs slightly from earlier national-population releases because estimates are revised. The population-weighted anomaly is sum(city population × station anomaly) / sum(city population).

This is a city-station proxy. It is neither a national land-area average nor a full residential exposure estimate. Each city is spatially heterogeneous; airport, coastal, inland and urban exposures differ. Canberra, other major urban areas and regional Australia are absent. A stronger population-exposure analysis would intersect BoM gridded temperature anomalies with the ABS 1 km residential population grid, calculate the same baselines for each cell, and weight all populated cells. The ABS regional-population release includes the grid download.

A +1°C anomaly against a recent baseline describes this particular period relative to that reference. It is not an additional permanent +1°C of climate change, and is not directly comparable to global warming thresholds. Baseline differences are also affected by sampling and station history as well as long-term climate change.

## ENSO interpretation

The downloaded BoM monthly SOI series extends from 1980 through September 2026. Monthly calendar means differ from rolling 30-day values in BoM's fortnightly bulletins.

No causal regression is fitted to nine 2026 monthly observations. A useful follow-up would use season-specific temperature/rain anomalies, detrending or a time term, lagged ENSO, IOD and SAM, and block resampling by season/year. A same-year correlation would confound seasonality, trend, coincident climate drivers and persistence. Hobart also had unusually warm May, a smaller anomaly in June, and renewed August–September warmth rather than a monotonic rise.

## Files and reproduction

* `outputs/Australian_cities_climate_2026.png`: generated comparison graphic for January to September.
* `analysis/`: generated daily and monthly observations, three baseline climatologies, matched annual windows, comparisons, population-weighted proxy, flags and JSON.
* raw/: downloaded source snapshots created by `download_data.py` and excluded from Git. Station choices used in the calculation are explicit in `analyze_cities.py`.
* analyze_cities.py: standard-library analysis. Run `python3 analyze_cities.py` from this folder.
* plot_cities.py: optional figure using numpy and matplotlib.

## Primary sources

1. NOAA GHCN-Daily: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt and station files under https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/ (exact station URLs in stations.csv).
2. BoM SOI: https://www.bom.gov.au/clim_data/IDCKGSH000/soi_monthly.txt
3. ABS regional population 2024–25: https://www.abs.gov.au/statistics/people/population/regional-population/2024-25 . Files 32180DS0003_2001-25.xlsx and 32180DS0004_2001-25.xlsx are saved as population_all.xlsx and population_sua.xlsx.

BoM data attribution: Commonwealth of Australia, Bureau of Meteorology. ABS population attribution: Australian Bureau of Statistics. Derived calculations and graphics are prepared for this analysis, with no official endorsement implied.
