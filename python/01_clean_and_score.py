"""
TransLink Bus Reliability Prioritization — Step 1: Clean TSPR data + compute priority score
Data source: TransLink TSPR 2024 Open Data (route-level) + GTFS Static (Aug 2026)
"""
import pandas as pd
import numpy as np

RAW_PATH = "/mnt/user-data/uploads/TSPR_OpenData_Archive_-4253847859733962239.csv"
OUT_PATH = "/home/claude/tspr_clean.csv"

df = pd.read_csv(RAW_PATH, encoding="utf-8-sig")

print(f"Raw shape: {df.shape}")

# --- 1. Type cleaning ---------------------------------------------------
# AVG_speed_km_per_hr comes in as "18 km/h" (string) -> float
df["avg_speed_kmh"] = (
    df["AVG_speed_km_per_hr"].astype(str).str.replace(" km/h", "", regex=False)
)
df["avg_speed_kmh"] = pd.to_numeric(df["avg_speed_kmh"], errors="coerce")

# On_Time_Performance_Percentage comes in as "78%" (string) -> float 0-100
df["on_time_pct"] = (
    df["On_Time_Performance_Percentage"].astype(str).str.replace("%", "", regex=False)
)
df["on_time_pct"] = pd.to_numeric(df["on_time_pct"], errors="coerce")

# --- 2. Flag incomplete-year routes (documented, not silently dropped) --
# NOTE column flags new routes / redesigns / seasonal-only routes. Only
# routes launched or redesigned WITHIN the reporting year (2024) lack a
# comparable full year of data -- a route launched in 2020 has had 4+
# full years since and is perfectly comparable by 2024. First pass of
# this filter mistakenly flagged old (2020) launch notes too; fixed by
# requiring the note to reference the report year itself, or being an
# always-partial case (seasonal-only routes, which never run all year).
report_year = str(df["TSPR_Year"].iloc[0])
df["is_partial_year_data"] = df["NOTE"].fillna("").apply(
    lambda x: (report_year in x) or ("seasonal only" in x.lower())
)

# Rows with missing OTP / speed / cost after cleaning (5 rows) are almost
# entirely the same partial-year / new routes flagged above, or SeaBus /
# combined-route entries with structurally different reporting. We keep
# them in the dataset but they'll naturally fall out of ranking calcs
# that require on_time_pct (NaN propagates).
missing_after_clean = df[df["on_time_pct"].isna() | df["avg_speed_kmh"].isna()]
print(f"\nRows with missing on_time_pct or avg_speed after cleaning: {len(missing_after_clean)}")
print(missing_after_clean[["Line", "Line_Name", "NOTE"]].to_string(index=False))

# --- 3. Core prioritization metric ---------------------------------------
# Business logic: a route with mediocre on-time performance but low
# ridership matters far less to the network than a route with the same
# OTP but high ridership. Raw OTP ranking (what a first pass usually does)
# does not capture this. So we compute a rider-weighted unreliability
# score = the number of boardings, per year, that occur on a route
# operating below 100% on-time performance.
#
#   Reliability Risk Score = Annual_Boardings * (100 - on_time_pct) / 100
#
# Interpretation: "how many annual boardings are exposed to unreliable
# service on this route" — directly maps to a prioritization argument
# ("fixing Route X improves reliability for N riders/year").
df["reliability_risk_score"] = df["Annual_Boardings"] * (100 - df["on_time_pct"]) / 100

# Secondary metric: efficiency (boardings per revenue hour) — useful to
# distinguish "underperforming due to low demand" vs "underperforming
# despite high demand" (the latter = under-resourced, not low-value).
df["boardings_per_revenue_hour"] = df["Annual_Boardings"] / df["Annual_Revenue_Hours_with_Overc"]

# --- 4. Split combined route codes for GTFS join --------------------------
# TSPR reports some routes as connected pairs (e.g. "005/006", "015/050").
# GTFS treats these as separate route_ids. We explode them into individual
# rows for the geometry join, while keeping the original combined code for
# the ranking table (so ridership isn't double counted in the ranking).
df["line_id_list"] = df["Line"].str.split("/")

exploded = df.explode("line_id_list").rename(columns={"line_id_list": "gtfs_route_short_name"})
exploded["gtfs_route_short_name"] = exploded["gtfs_route_short_name"].str.strip()

df.to_csv(OUT_PATH, index=False)
exploded.to_csv("/home/claude/tspr_exploded_for_join.csv", index=False)

print(f"\nCleaned TSPR saved: {OUT_PATH} ({df.shape})")
print(f"Exploded (for GTFS join) saved: {len(exploded)} rows")
print(f"\nCombined-route codes found (documented data quirk): "
      f"{df[df['Line'].str.contains('/')]['Line'].tolist()}")
