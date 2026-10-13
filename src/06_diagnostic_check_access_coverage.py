"""
06_diagnostic_check_access_coverage.py
Test the hypothesis: are the access/distance measures only reliably
populated at Wijk (district) level, not Buurt (neighborhood) level?
Uses the pre-filter wide table (all region types) to compare.
"""

import pandas as pd

df = pd.read_csv("../data/interim/housing_wide.csv")

ACCESS_COLS = [
    "dist_gp_km", "dist_supermarket_km", "dist_daycare_km",
    "dist_school_km", "schools_within_3km",
]

for col in ACCESS_COLS:
    df[col] = pd.to_numeric(df[col], errors="coerce")


print("Missing % for each column, broken down by region_type:\n")
for region_type in ["Buurt", "Wijk", "Gemeente"]:
    subset = df[df["region_type"] == region_type]
    print(f"---{region_type} (n={len(subset)}) ---")
    for col in ACCESS_COLS:
        pct = subset[col].isna().mean() * 100
        print(f" {col}: {pct:.1f}% missing")
    print()