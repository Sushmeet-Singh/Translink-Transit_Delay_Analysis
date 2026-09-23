"""
Step 2: Join TSPR reliability scores to GTFS route geometry (for mapping)
"""
import pandas as pd

exploded = pd.read_csv("/home/claude/tspr_exploded_for_join.csv", dtype={"gtfs_route_short_name": str})
routes = pd.read_csv("/home/claude/gtfs/routes.txt", dtype={"route_short_name": str})
trips = pd.read_csv("/home/claude/gtfs/trips.txt")
shapes = pd.read_csv("/home/claude/gtfs/shapes.txt")

exploded["key"] = exploded["gtfs_route_short_name"].str.strip().str.upper()
routes["key"] = routes["route_short_name"].str.strip().str.upper()

merged = exploded.merge(routes[["route_id", "key"]], on="key", how="left")
print(f"Route-code match rate: {merged['route_id'].notna().mean():.1%}")

# For each route_id, pick the most common (longest) shape_id as representative
trip_counts = trips.groupby(["route_id", "shape_id"]).size().reset_index(name="n_trips")
best_shape = trip_counts.sort_values("n_trips", ascending=False).drop_duplicates("route_id")

merged = merged.merge(best_shape[["route_id", "shape_id"]], on="route_id", how="left")

# Attach shape point sequences
shapes_indexed = shapes.set_index("shape_id")

geo_rows = []
for _, row in merged.dropna(subset=["shape_id"]).iterrows():
    sid = row["shape_id"]
    if sid not in shapes_indexed.index:
        continue
    pts = shapes_indexed.loc[[sid]].sort_values("shape_pt_sequence")
    geo_rows.append({
        "Line": row["Line"],
        "Line_Name": row["Line_Name"],
        "reliability_risk_score": row["reliability_risk_score"],
        "on_time_pct": row["on_time_pct"],
        "Annual_Boardings": row["Annual_Boardings"],
        "Sub_Region_of_Primary_Service": row["Sub_Region_of_Primary_Service"],
        "lats": pts["shape_pt_lat"].tolist(),
        "lons": pts["shape_pt_lon"].tolist(),
    })

geo_df = pd.DataFrame(geo_rows)
geo_df.to_json("/home/claude/route_geometry.json", orient="records")
print(f"Saved geometry for {len(geo_df)} route entries (some Lines have multiple GTFS route_ids -> multiple geometry rows)")
print(geo_df[["Line","Line_Name","reliability_risk_score"]].sort_values("reliability_risk_score", ascending=False).head(10))
