"""
05_handle_missing.py
Quantify and treat missing values. CBS suppresses figures for small
neighborhoods for privacy reasons (visible above as NaN in columns
like pct_single_family/pct_multi_family for very small or non-
residential areas such as "UMCG").
"""

import pandas as pd
import numpy as np

df = pd.read_csv("../data/interim/neighborhoods_raw.csv")

# Numeric columns that were pivoted from Value (may have been read as
# object/str if any non-numeric artifact slipped through -- coerce now)
NUMERIC_COLS = [
    "pct_owner_occupied", "pct_rental", "dist_supermarket_km", "dist_gp_km",
    "dist_daycare_km", "dist_school_km", "schools_within_3km",
    "population_density", "dwelling_count", "avg_woz_value_k_eur",
    "pct_built_over_10y_ago", "pct_built_last_10y", "urbanity_level",
    "address_density", "population", "pct_single_family", "pct_multi_family",
]
for col in NUMERIC_COLS:
    df[col] = pd.to_numeric(df[col], errors="coerce")

missing_pct = (df[NUMERIC_COLS].isna().sum() / len(df) * 100).sort_values(ascending=False)
print("Missing % per numeric column:")
print(missing_pct)

# Decision 1: columns with >40% missing -> drop (too sparse to be meaningful)
high_missing = missing_pct[missing_pct > 40].index.to_list()
print(f"\nDropping {len(high_missing)} columns with > 40% missing: {high_missing}")

remaining_numeric = [c for c in NUMERIC_COLS if c not in high_missing]

# Decision 2: <10% missing -> impute with the municipality-level median
# (a supermarket-distance value should be filled from similar nearby
# neighborhoods, not a nationwide average)
for col in remaining_numeric:
    pct = df[col].isna().mean()
    if 0 < pct < 0.10:
        df[col] = df.groupby("municipality")[col].transform(
            lambda s: s.fillna(s.median())
        )
        df[col] = df[col].fillna(df[col].median()) #fallback for all-NaN groups
        print(f"Imputed {col} ({pct:.1%} missing) with municipality median")

# Decision 3: rows still missing the core fields this analysis depends on
core_fields = ["avg_woz_value_k_eur", "dwelling_count", "population"]
before = len(df)
df = df.dropna(subset=core_fields)
print(f"Dropped {before - len(df)} rows missing core fields {core_fields}")

df.to_csv("../data/interim/neighborhoods_missing_handled.csv", index=False)
print(f"\nFinal shape after missing-value handling: {df.shape}")