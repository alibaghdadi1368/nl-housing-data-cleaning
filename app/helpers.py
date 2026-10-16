"""
Shared helpers for the notebooks and the Streamlit app, so a number in the
app is computed by exactly the same code as the number in the notebook.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"


def load_buurten(path=DATA / "buurten_story.csv"):
    """The cleaned neighbourhood table written by notebooks/01_cleaning.ipynb."""
    df = pd.read_csv(path, dtype={"postcode": "string"})
    df["imputed_fields"] = df["imputed_fields"].fillna("")
    df["woz_estimated"] = df["imputed_fields"].str.contains("avg_woz_value_k_eur")
    df["rent_estimated"] = df["imputed_fields"].str.contains("pct_rent_private")
    return df


def city_centre(df, municipality):
    """
    Population-weighted centre of a municipality, in RD metres.
    Derived from the data itself (no hand-typed coordinates): the point where
    the municipality's inhabitants are, on average.
    """
    m = df[df["municipality"] == municipality]
    if m.empty:
        raise ValueError(f"unknown municipality: {municipality}")
    w = m["population"].clip(lower=0)
    if w.sum() == 0:
        w = pd.Series(1.0, index=m.index)
    return float(np.average(m["x_rd"], weights=w)), float(np.average(m["y_rd"], weights=w))


def add_distance(df, municipality):
    """Straight-line distance in km from each neighbourhood to the chosen city's centre."""
    cx, cy = city_centre(df, municipality)
    out = df.copy()
    out["dist_to_city_km"] = np.hypot(out["x_rd"] - cx, out["y_rd"] - cy) / 1000
    return out


def weighted_median(values, weights):
    """Median where each neighbourhood counts as many times as it has homes."""
    v = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    keep = ~(np.isnan(v) | np.isnan(w)) & (w > 0)
    v, w = v[keep], w[keep]
    order = np.argsort(v)
    v, w = v[order], w[order]
    cum = np.cumsum(w)
    return float(v[np.searchsorted(cum, cum[-1] / 2)])
