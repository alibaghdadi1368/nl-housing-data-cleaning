"""
08_handle_outliers.py
Identify outliers with the IQR method on the key unbounded numeric
columns (percentage columns are already bounded 0-100 and are left
alone here), visualize before/after, and cap rather than delete.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import os

df = pd.read_csv("../data/interim/neighborhoods_missing_handled_revised.csv")
os.makedirs("../doc", exist_ok=True)


# Unbounded numeric columns -- these are the ones where a handful of
# extreme values (e.g. a very expensive Amsterdam canal-house
# neighborhood, or a near-empty rural buurt) can meaningfully skew
# aggregates. Percentage columns (pct_owner_occupied etc.) are already
# bounded 0-100 and are not treated here.
KEY_COLUMNS = [
    "avg_woz_value_k_eur", "dwelling_count", "population",
    "population_density", "address_density",
]
KEY_COLUMNS = [c for c in KEY_COLUMNS if c in df.columns]

def iqr_bounds(series, k=1.5):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr

print("Outlier summary (before treatment):")
for col in KEY_COLUMNS:
    lower, upper = iqr_bounds(df[col].dropna())
    n_out = ((df[col] < lower) | (df[col] > upper)).sum()
    print(f" {col}: bounds=({lower:.1f}, {upper:.1f}), "
          f"outliers={n_out} ({n_out/len(df):.1%})")

    plt.figure(figsize=(6, 3))
    sns.boxplot(x=df[col])
    plt.title(f"Before capping: {col}")
    plt.tight_layout()
    plt.savefig(f"../docs/before_{col}.png")
    plt.close()


# Decision: cap (winsorize), don't delete rows. A very high-value
# Amsterdam neighborhood or a very sparse rural buurt is real data,
# not an error -- capping limits its distorting effect on aggregate
# statistics while preserving full geographic coverage of the
# Netherlands in the final dataset.
for col in KEY_COLUMNS:
    lower, upper = iqr_bounds(df[col].dropna())
    df[col] = df[col].clip(lower=lower, upper=upper)

    plt.figure(figsize=(6, 3))
    sns.boxplot(x=df[col])
    plt.title(f"After capping: {col}")
    plt.tight_layout()
    plt.savefig(f"../docs/after_{col}.png")
    plt.close()

os.makedirs("../data/processed", exist_ok=True)
df.to_csv("../data/processed/nl_housing_clean.csv", index=False)
print(f"\nSaved final cleaned dataset: {df.shape}")