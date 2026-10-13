"""
09_summary_report.py
Before/after summary for README.
"""

import pandas as pd

raw = pd.read_csv("../data/interim/neighborhoods_raw.csv")
clean = pd.read_csv("../data/processed/nl_housing_clean.csv")

print(f"Raw (post-pivot, Buurt-level): {raw.shape[0]} rows, {raw.shape[1]} columns")
print(f"Clean (final):                 {clean.shape[0]} rows, {clean.shape[1]} columns")
print(f"Rows removed:                  {raw.shape[0] - clean.shape[0]}")
print(f"Columns removed:                {raw.shape[1] - clean.shape[1]}")


KEY = ["avg_woz_value_k_eur", "dwelling_count", "population",
       "urbanity_level", "address_density"]

print("\nFinal descriptive statistics (real values):")
print(clean[KEY].describe())

print("\nTop 5 most expensive municipalities (mean of real neighborhood WOZ values):")
print(
    clean.groupby("municipality")["avg_woz_value_k_eur"]
    .mean()
    .sort_values(ascending=False)
    .head(5)
)

print(f"\nTotal population (real values): {clean['population'].sum():,.0f}")
print(f"Neighborhoods with at least one imputed value: {(clean['imputed_fields'].fillna('') != '').sum():,}")

ownership_sum = clean["pct_owner_occupied"] + clean["pct_rental"]
print(f"Neighborhoods where owner + rental is more than 2 points off 100%: {((ownership_sum - 100).abs() > 2).sum()}")
