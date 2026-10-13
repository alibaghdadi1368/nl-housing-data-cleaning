"""
03_build_wide_table.py
Pivot the long-format (EAV) Observations.csv into a wide table:
one row per region, one column per measure. Numeric and string
measures are pivoted separately (different value columns), then
joined, since pivot_table needs a single values column per call.
 
Measure codes below were confirmed against the real MeasureCodes.csv
for this specific 2025 export.
"""

import os

import pandas as pd

obs = pd.read_csv(
    "../data/raw/Observations.csv",
    sep=";",
    encoding="utf-8",
)

print("Observation shape: ", obs.shape)
print(obs.dtypes)

# --- Measure code -> friendly column name mappings ---
NUMERIC_MEASURES = {
    "T001036": "population",
    "M000100": "population_density",
    "M000297": "dwelling_count",
    "M001642": "avg_woz_value_k_eur",
    "ZW10290": "pct_single_family",
    "ZW10340": "pct_multi_family",
    "1014800": "pct_owner_occupied",
    "1014850_2": "pct_rental",
    "M008209": "pct_built_over_10y_ago",
    "M008210": "pct_built_last_10y",
    "D000028": "dist_gp_km",
    "D000025": "dist_supermarket_km",
    "D000029": "dist_daycare_km",
    "D000045": "dist_school_km",
    "D000263": "schools_within_3km",
    "M000222": "avg_standardized_income_k_eur",
    "ST0001": "urbanity_level",
    "ST0003": "address_density",
}

STRING_MEASURES = {
    "GM000C": "municipality",
    "R00003": "region_type",
    "R00004": "region_code",
    "PC000C": "postcode",
}

# --- Pivot numeric measures (uses the 'Value' column) ---
numeric_subset = obs[obs["Measure"].isin(NUMERIC_MEASURES.keys())]
numeric_wide = numeric_subset.pivot_table(
    index="WijkenEnBuurten",
    columns="Measure",
    values="Value",
    aggfunc="first",
)
numeric_wide = numeric_wide.rename(columns=NUMERIC_MEASURES)

# warn about measure codes that don't exist (or are empty) in this release
not_found = sorted(set(NUMERIC_MEASURES) - set(numeric_subset["Measure"].unique()))
for code in not_found:
    print(f"WARNING: measure {code} ({NUMERIC_MEASURES[code]}) not found in Observations.csv")

# --- Pivot string measures (uses the 'StringValue' column) ---
string_subset = obs[obs["Measure"].isin(STRING_MEASURES.keys())]
string_wide = string_subset.pivot_table(
    index="WijkenEnBuurten",
    columns="Measure",
    values="StringValue",
    aggfunc="first",
)
string_wide = string_wide.rename(columns=STRING_MEASURES)

# strip trailing whitespace padding seen in the raw StringValue field
for col in string_wide.columns:
    string_wide[col] = string_wide[col].str.strip()


# --- Combine into one wide table ---
wide = string_wide.join(numeric_wide).reset_index()

# --- Add the human-readable region name (e.g. "Annen") from WijkenEnBuurtenCodes ---
wb_codes = pd.read_csv(
    "../data/raw/WijkenEnBuurtenCodes.csv",
    sep=";",
    encoding="utf-8",
)
wb_codes = wb_codes.rename(columns={"Identifier": "WijkenEnBuurten", "Title": "region_name"})
wide = wide.merge(wb_codes[["WijkenEnBuurten", "region_name"]], on="WijkenEnBuurten", how="left")

print("\nWide table shape: ", wide.shape)
print("\nColumns: ", list(wide.columns))
print("\nregion_type value counts: ")
print(wide["region_type"].value_counts())

print("\nSample rows: ")
print(wide.head(10))

os.makedirs("../data/interim", exist_ok=True)
wide.to_csv("../data/interim/housing_wide.csv", index=False)
print("\nSaved to data/interim/housing_wide.csv")
