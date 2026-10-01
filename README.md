# Metro Vancouver Bus Reliability Prioritization

An independent, end-to-end data analytics project: finding which Metro Vancouver bus routes
TransLink should prioritize for reliability investment, using TransLink's own public data.

**[Live dashboard](https://mavenshowcase.com/project/57746)** | **[Case study write-up](case_study.html)** | **[Landing page](index.html)**

Not affiliated with or endorsed by TransLink. Independent analysis for portfolio purposes.

---

## The question

TransLink publishes on-time performance for 195 bus routes every year. A simple "worst
on-time percentage" ranking treats a route with 50,000 riders a year the same as one with
8 million, which isn't how a transit planner would actually prioritize limited investment.

**This project asks: which corridors, if fixed, would improve reliability for the most
riders, not just look worst on paper?**

## The answer

A rider-weighted metric, not a raw percentage ranking:

```
Reliability Risk Score = Annual Boardings x (100 - On-Time Performance %) / 100
```

This estimates how many annual boardings happen on a route running below target, so a
high-ridership route with moderate delay outranks a near-empty route with worse delay.

**Key findings:**
- The top 10 routes by this score carry **25% of all system boardings** while running
  **9 points below** the system-average on-time performance.
- **412,000+ boardings** happen on an average weekday on a route running below the 80%
  on-time target, 56% of all annual ridership on the network.
- **Vancouver/UBC carries roughly 4x the reliability risk per route** of any other
  sub-region, even after adjusting for route count, pointing to shared corridor issues
  (Broadway, Kingsway) rather than isolated routes.
- Two of the top-ranked routes (049, R4) independently match corridors TransLink's own
  Bus Speed & Reliability program has already flagged, a useful cross-check that this
  approach converges with TransLink's internal prioritization.

Full write-up: **[case_study.html](case_study.html)**. One-page memo for a non-technical
reader: **[recommendation_memo.md](recommendation_memo.md)**.

## Data sources

| Source | What it provides | Link |
|---|---|---|
| TransLink Transit Service Performance Review (TSPR) 2024 | Route-level ridership, on-time performance, revenue hours, service cost, sub-region | [TSPR Open Data Catalog](https://experience.arcgis.com/experience/bedca58037104e468cbcf97aa38ca602) |
| TransLink GTFS Static feed | Route, stop, and shape geometry for mapping | [TransLink GTFS Data](https://www.translink.ca/about-us/doing-business-with-translink/app-developer-resources/gtfs/gtfs-data) |

Both are official, publicly licensed TransLink datasets (Open Government Licence).

## What's in this repo

**Analysis pipeline (Python)**
```
01_clean_and_score.py     cleans TSPR data, computes the reliability risk score
02_join_geometry.py       joins TSPR routes to GTFS shape geometry
03_visualize.py           generates charts and the interactive map
tspr_clean.csv            cleaned, full TSPR dataset (195 routes) with engineered fields
tspr_ranked.csv           ranked, analysis-ready subset (188 routes)
route_geometry.json       route geometry and scores, used for the map
Route_Path_Points.csv     ordered lat/lon points per route, for Power BI line rendering
```

**Deliverables**
```
dashboard.html            interactive HTML dashboard (Leaflet map, Chart.js charts, searchable table)
case_study.html           full narrative case study write-up
index.html                portfolio landing page
recommendation_memo.md    one-page recommendation memo
reliability_map.html      standalone interactive map
chart_*.png               static chart exports
```

**Power BI**
```
TransLink_PowerBI_Data.xlsx       star-schema data model (fact + dimension tables)
TransLink_PowerBI_Theme.json      custom color theme matching the dashboard/case study
DAX_Measures_Library.md           28 measures organized into 5 display folders
DAX_Additions_Quadrant_Gauge.md   quadrant classification and gauge-target measures
PowerBI_Build_Guide.md            step-by-step build instructions
PowerBI_2Page_Report_Spec.md      full 2-page report layout spec
```

## Data cleaning: decisions and why

Raw TSPR data was not analysis-ready. Every decision below is reproducible from
`01_clean_and_score.py`:

1. **Type coercion**: `AVG_speed_km_per_hr` and `On_Time_Performance_Percentage` arrive as
   strings ("78%", "18 km/h") rather than numbers. Stripped and cast to float.
2. **Partial-year routes flagged, not silently dropped**: 9 routes carry a footnote about a
   launch, redesign, or seasonal-only status. A first pass over-flagged this, incorrectly
   treating routes launched back in 2020 (R1 to R4) as having partial-year data, when they'd
   had 4+ full comparable years since. Fixed by only flagging notes that reference the
   reporting year itself, or are permanently partial (seasonal-only service). This left 7
   routes genuinely excluded from ranking: new/redesigned-in-2024 routes, plus SeaBus, which
   isn't measured on a comparable basis.
3. **Combined route codes**: TSPR reports 10 routes as connected pairs (e.g. `005/006`,
   `102/103`). GTFS treats these as separate route IDs with separate physical geometry.
   Exploding them naively under one shared key caused line segments from both physical routes
   to connect into a single tangled shape on the map. Fixed by assigning each physical shape
   its own `PathID` (e.g. `005/006__1`, `005/006__2`) while preserving the original combined
   code for ranking, so ridership isn't double-counted.
4. **Route code matching to GTFS**: TSPR's `Line` field and GTFS's `route_short_name` don't
   share identical formatting. Normalized both before joining; final match rate was 99.5%
   (only SeaBus failed to match, due to a different GTFS classification).

## Method

```
Reliability Risk Score = Annual Boardings x (100 - On-Time Performance %) / 100
```

This is a prioritization heuristic, not a causal measure of *why* a route is late. It
estimates how many annual boardings occur on a route running below 100% on-time, which
directly supports a resourcing argument ("fixing Route X improves reliability for ~2.4M
rider-trips/year") rather than ranking by raw lateness percentage alone.

188 of 195 TSPR routes were included in the final ranking; 7 were excluded and documented
above.

## Tools

Python (pandas) for cleaning and scoring. Leaflet and Chart.js for the interactive HTML
dashboard. Power BI (DAX, star-schema modeling) for the enterprise-facing version.

## Limitations

- This is a prioritization heuristic, not a causal model. It identifies where to look, not
  why a given route is unreliable (traffic, signal timing, dwell time); that would require
  trip-level or time-of-day data not published at this granularity.
- TSPR is an annual snapshot. It cannot show whether reliability is trending within the
  year, or isolate one-off disruptions from chronic issues.
- Sub-region risk concentration may partly reflect service density rather than purely
  operational failure. Vancouver/UBC is also the highest-density service area.

## Author

Sushmeet Nandra. Independent analysis for portfolio purposes, not affiliated with or
endorsed by TransLink.
