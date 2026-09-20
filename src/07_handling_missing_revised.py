"""
07_handle_missing.py (revised)
Handles missing values with three documented decision tiers.
 
Key finding from diagnostics: the five distance-to-amenity measures
(dist_gp_km, dist_supermarket_km, dist_daycare_km, dist_school_km,
schools_within_3km) are 86-94% missing across ALL region levels
(Buurt, Wijk, Gemeente) in this 2025 CBS release -- not a granularity
issue, but a genuine data availability gap in this year's source data.
They are dropped, and urbanity_level + address_density (CBS's own
standard urbanicity indicators, <1% missing) are kept as the proxy
for "access to amenities" instead.
"""

import pandas as pd
import numpy as np

df = pd.read_csv("../data/interim/neighborhoods_raw.csv")

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


# --- Tier 1: >40% missing -> drop column ---
# Confirmed via diagnostic_check_access_coverage.py that the distance
# measures are sparse at EVERY region level, not just Buurt -- this is
# a genuine 2025-release data gap, documented here rather than silently
# dropped.
high_missing = missing_pct[missing_pct > 40].index.tolist()
print(f"\nDropping {len(high_missing)} columns with 40% missing (confirmed "
      f"spare across all region levels, not a granularity artifact):")
print(high_missing)
df = df.drop(columns=high_missing)
remaining = [c for c in NUMERIC_COLS if c not in high_missing]

# --- Tier 2: <25% missing -> impute with municipality-level median ---
# Widened from the original <10% threshold after finding several
# genuinely usable columns (WOZ value, ownership %, building-age %,
# dwelling-type %) sitting in the 10-25% range -- median-imputing
# within the same municipality is more meaningful than a national
# median, since housing stock varies a lot between municipalities.
for col in remaining:
    pct = df[col].isna().mean()
    if 0 < pct < 0.25:
        df[col] = df.groupby("municipality")[col].transform(
            lambda s: s.fillna(s.median())
        )
        df[col] = df[col].fillna(df[col].median()) # fallback for all-NaN groups
        print(f"Imputed {col} ({pct:.1%} missing) with municipality median")

# --- Tier 3: rows still missing core fields -> drop ---
core_fields = ["avg_woz_value_k_eur", "dwelling_count", "population"]
before = len(df)
df = df.dropna(subset=core_fields)
print(f"\nDropped {before - len(df)} rows still missing core fields {core_fields}")

df.to_csv("../data/interim/neighborhoods_missing_handled_revised.csv", index=False)
print(f"nFinal shape after missing-value handling: {df.shape}")
print("\nRemaining missing values per column:")
print(df.isna().sum())