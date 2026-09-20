"""
01_explore.py
First step: load the raw CSV and actually look at it before assuming
anything. Confirmed from the CBS StatLine preview: missing/suppressed
values in this table appear as a literal '.' character, not a numeric
code, and thousands-separators use '.' while decimals use ',' (Dutch
number format); both need handling before any numeric analysis.
"""
"The raw CBS export was not UTF-8 encoded as expected; it required cp1252 encoding, a common issue with European government CSV exports."

import pandas as pd

df = pd.read_csv(
    "../data/raw/86165NED.csv",
    sep=";", # CBS CSV exports are typically semicolon-separated
    encoding="latin-1",
    na_values=["."], # confirmed: CBS uses '.' for suppressed/missing values
)

print("Shape: ", df.shape)

print("\nColumn name (first 20): ")
for col in df.columns[:20]:
    print("-", col)

print("\nFirst 5 rows: ")
print(df.head())

print("\nData types: ")
print(df.dtypes.value_counts())

# Confirm the region-type column and its values
region_col_candidates = [c for c in df.columns if "SoortRegio" in c or "soort" in c.lower()]
print("\nRegion_type column candidates:", region_col_candidates)
if region_col_candidates:
    print(df[region_col_candidates[0]].value_counts())
