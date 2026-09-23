import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import folium
import json

plt.rcParams["font.size"] = 11
tspr = pd.read_csv("/home/claude/tspr_clean.csv")

# Only rank routes with complete-year data (exclude partial-year / missing OTP)
rankable = tspr[~tspr["is_partial_year_data"] & tspr["on_time_pct"].notna()].copy()
rankable = rankable.sort_values("reliability_risk_score", ascending=False)

# ---------------------------------------------------------------- Chart 1
# Top 15 routes by Reliability Risk Score
top15 = rankable.head(15).iloc[::-1]  # reverse for horizontal bar (largest on top)
fig, ax = plt.subplots(figsize=(9, 7))
bars = ax.barh(top15["Line"] + " – " + top15["Line_Name"].str.title(),
                top15["reliability_risk_score"], color="#c0392b")
ax.set_xlabel("Reliability Risk Score  (annual boardings exposed to late service)")
ax.set_title("Top 15 Bus Routes by Reliability Risk\nMetro Vancouver, TSPR 2024", fontsize=13, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K"))
for bar, otp in zip(bars, top15["on_time_pct"]):
    ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height()/2,
            f"{otp:.0f}% on-time", va="center", fontsize=9, color="#555")
plt.tight_layout()
plt.savefig("/home/claude/chart_top15_risk.png", dpi=150)
plt.close()
print("Saved chart_top15_risk.png")

# ---------------------------------------------------------------- Chart 2
# OTP vs Annual Boardings scatter, sized by risk score
fig, ax = plt.subplots(figsize=(9, 7))
sizes = (rankable["reliability_risk_score"] / rankable["reliability_risk_score"].max()) * 800 + 20
sc = ax.scatter(rankable["Annual_Boardings"], rankable["on_time_pct"],
                 s=sizes, alpha=0.55, c=rankable["reliability_risk_score"],
                 cmap="Reds", edgecolors="grey", linewidths=0.4)
ax.set_xscale("log")
ax.set_xlabel("Annual Boardings (log scale)")
ax.set_ylabel("On-Time Performance (%)")
ax.set_title("Where Ridership Meets Unreliability\nBubble size/colour = Reliability Risk Score", fontsize=13, fontweight="bold")
ax.axhline(80, color="green", linestyle="--", linewidth=0.8, alpha=0.6)
ax.text(rankable["Annual_Boardings"].max()*0.5, 80.5, "TransLink system target ~80% OTP", fontsize=8, color="green")

# label top 6 outliers
for _, r in rankable.head(6).iterrows():
    ax.annotate(r["Line"], (r["Annual_Boardings"], r["on_time_pct"]),
                textcoords="offset points", xytext=(6, 4), fontsize=9, fontweight="bold")
plt.tight_layout()
plt.savefig("/home/claude/chart_otp_vs_ridership.png", dpi=150)
plt.close()
print("Saved chart_otp_vs_ridership.png")

# ---------------------------------------------------------------- Chart 3
# Risk score by sub-region (where should investment focus geographically)
region_summary = rankable.groupby("Sub_Region_of_Primary_Service")["reliability_risk_score"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 5))
region_summary.plot(kind="bar", ax=ax, color="#2c3e50")
ax.set_ylabel("Total Reliability Risk Score")
ax.set_title("Total Reliability Risk by Sub-Region", fontsize=13, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M"))
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("/home/claude/chart_region_summary.png", dpi=150)
plt.close()
print("Saved chart_region_summary.png")

# ---------------------------------------------------------------- Map
with open("/home/claude/route_geometry.json") as f:
    geo = json.load(f)

m = folium.Map(location=[49.2488, -123.05], zoom_start=11, tiles="cartodbpositron")
max_score = max(g["reliability_risk_score"] for g in geo if g["reliability_risk_score"] == g["reliability_risk_score"])

def color_for(score, max_score):
    if score != score:  # NaN
        return "#999999"
    ratio = min(score / max_score, 1)
    r = int(255 * ratio + 40 * (1 - ratio))
    g = int(60 * (1 - ratio) + 180 * (1 - ratio))
    b = int(50 * (1 - ratio) + 180 * (1 - ratio))
    return f"#{r:02x}{g:02x}{b:02x}"

for g in geo:
    if not g["lats"]:
        continue
    coords = list(zip(g["lats"], g["lons"]))
    score = g["reliability_risk_score"]
    weight = 2 + 6 * (min(score, max_score) / max_score) if score == score else 1.5
    folium.PolyLine(
        coords,
        color=color_for(score, max_score),
        weight=weight,
        opacity=0.8,
        tooltip=f"Route {g['Line']} – {g['Line_Name']}<br>OTP: {g['on_time_pct']:.0f}%<br>"
                f"Annual Boardings: {g['Annual_Boardings']:,}<br>"
                f"Risk Score: {score:,.0f}" if score == score else f"Route {g['Line']}"
    ).add_to(m)

m.save("/home/claude/reliability_map.html")
print("Saved reliability_map.html")

rankable.to_csv("/home/claude/tspr_ranked.csv", index=False)
print("\nTop 10 priority routes:")
print(rankable[["Line","Line_Name","Sub_Region_of_Primary_Service","on_time_pct","Annual_Boardings","reliability_risk_score"]].head(10).to_string(index=False))
