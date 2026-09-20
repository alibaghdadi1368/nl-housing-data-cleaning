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


print("\nFinal descriptive statistics (key_columns):")
print(clean[["avg_woz_value_k_eur", "dwelling_count", "population",
             "urbanity_level", "address_density"]].describe())

print("\nTop 5 most expensive municipalities (avg WOZ value, mean across their neighborhoods):")
print(
    clean.groupby("municipality")["avg_woz_value_k_eur"]
    .mean()
    .sort_values(ascending=False)
    .head(5)
)