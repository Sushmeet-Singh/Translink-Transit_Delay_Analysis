# Bus Reliability Investment Priorities - Metro Vancouver
**Prepared as an independent analysis using TransLink's public TSPR 2024 and GTFS Static data**

## The question
Which bus corridors should TransLink prioritize for reliability investment, given that not
every late route matters equally - a route carrying 8 million riders a year is a very
different problem than one carrying 200,000?

## The finding
A small number of high-ridership corridors are absorbing a disproportionate share of the
network's unreliability. The **top 10 routes by rider-weighted risk account for 24.9% of all
system boardings but sit at an average 72.8% on-time performance**, nearly 9 points below the
system average of 81.5%.

**Top 5 priority routes:**

| Route | Corridor | On-Time % | Annual Boardings | Riders exposed to lateness/yr |
|---|---|---|---|---|
| 049 | Metrotown Stn / Dunbar Loop / UBC | 71% | 8.5M | ~2.46M |
| R4 | 41st Ave RapidBus | 74% | 8.8M | ~2.29M |
| 099 | Commercial-Broadway / UBC (B-Line) | 79% | 10.6M | ~2.23M |
| 025 | Brentwood Stn / UBC | 67% | 6.4M | ~2.10M |
| 016 | 29th Ave Stn / Arbutus | 74% | 5.3M | ~1.38M |

Geographically, this isn't evenly spread: **the Vancouver/UBC sub-region carries roughly 4x
the reliability risk per route of any other sub-region** - 31 routes there account for
$25.3M in cumulative risk score vs. $10.5M for the next-highest region (Southeast, 47 routes).
This holds even after adjusting for route count, so it isn't just a "more routes" effect -
these corridors are structurally harder to run on time (likely a mix of density, traffic
signal priority gaps, and curb congestion along shared corridors like Broadway/UBC and
Kingsway).

Two of these routes (049 and R4) independently match corridors TransLink's own Bus Speed &
Reliability program has already flagged for delay hours - which is a useful cross-check that
this rider-weighted approach converges with TransLink's internal prioritization, while also
surfacing 025 and 016 as comparably urgent but less discussed candidates.

## The recommendation
1. **Prioritize Routes 049, R4, 099, 025, and 016 for the next round of transit priority
   measures** (signal priority, dedicated lanes, curb management) - together they represent
   ~11.5M annual riders currently experiencing below-target reliability.
2. **Treat Vancouver/UBC as a sub-region for corridor-level investment, not just individual
   routes** - several of the top corridors overlap geographically (Broadway, Kingsway, Main
   St), suggesting shared infrastructure fixes could improve multiple routes at once.
3. **Re-run this analysis after each infrastructure investment** to measure whether the
   rider-weighted risk score actually drops - this metric could become an ongoing before/after
   accountability tool, not just a one-time ranking.

## Method (short version)
Reliability Risk Score = Annual Boardings × (100 − On-Time Performance %) / 100 - an
estimate of how many annual boardings occur on a route running below 100% on-time, so high-
ridership, low-reliability routes are weighted far above low-ridership ones with the same OTP.
188 of 195 TSPR routes were ranked; 7 were excluded (partial-year data for new/redesigned
routes, or SeaBus, which isn't measured on the same OTP basis). Full methodology and cleaning
decisions are documented in `README.md`.

## Limitations
- Reliability Risk Score is a prioritization heuristic, not a causal measure - it doesn't
  identify *why* a route is late (traffic, dwell time, scheduling slack).
- TSPR data is annual; it can't show whether reliability is trending better or worse within
  the year, or isolate one-off disruptions (construction, detours) from chronic issues.
- Sub-region risk concentration may partly reflect where the busiest corridors happen to be,
  not exclusively an operational failure - Vancouver/UBC is also the highest-density service
  area.
