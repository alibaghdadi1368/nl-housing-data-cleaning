"""
04_filter_neighborhoods.py
Keep only Buurt-level rows (14,729 of them) -- Wijk, Gemeente, and
Land rows are higher-level aggregates of the same underlying data
and would double-count if left in for a neighborhood-level analysis.
"""

import pandas as pd

df = pd.read_csv("../data/interim/housing_wide.csv")

print(f"Before filtering: {len(df)} rows")

neighborhoods = df[df["region_type"] == "Buurt"].copy()

print(f"After filtering to Buurt: {len(neighborhoods)} rows")
print(f"Columns: {neighborhoods.shape[1]}")

# region_code (from measure R00004) duplicates WijkenEnBuurten -- confirm and drop if so
if(neighborhoods["region_code"] == neighborhoods["WijkenEnBuurten"]).all():
    print("\nregion_code is identical to WijkenEnBuurten -> dropping duplicate columns")
    neighborhoods = neighborhoods.drop(columns=["region_code"])
else:
    print("\nregion_code differs from WijkenEnBuurten in some rows -- keeping both, inspect manually")

neighborhoods.to_csv("../data/interim/neighborhoods_raw.csv", index=False)
print("\nSaved to data/interim/neighborhoods_raw.csv")
print(f"Final shape: {neighborhoods.shape}")