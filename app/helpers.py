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


# ---------------------------------------------------------------------------
# The default view of the story. Every threshold is here, in one place, so the
# storyboard and the app use the same definition and I can defend each number.
# ---------------------------------------------------------------------------
DEFAULTS = {
    "max_km": 40,               # straight line; roughly the edge of a daily commute
    "min_private_rent_pct": 15, # at least ~1 in 7 homes rented from a non-corporation landlord
    "max_urbanity": 3,          # CBS class 1-3 = at least "matig stedelijk" (>= 1,000 addresses/km2)
    "max_supermarket_km": 1.0,  # a large supermarket within walking distance (by road)
    "min_dwellings": 50,        # skip tiny neighbourhoods where an average says little
    "include_estimated": False, # only neighbourhoods where WOZ and rental share were measured
}


def city_typical_woz(df, municipality):
    """Typical home value in the city itself: dwelling-weighted median, measured values only."""
    c = df[(df["municipality"] == municipality) & ~df["woz_estimated"]]
    return weighted_median(c["avg_woz_value_k_eur"], c["dwelling_count"])


def candidates(df, municipality, **overrides):
    """
    Neighbourhoods a newcomer working in `municipality` could look at first:
    within reach, lower value than a typical home in the city, a real share of
    private rentals, urban enough to have shops nearby.
    Returns (table with a `candidate` column, the settings used, the city's typical WOZ).
    """
    s = {**DEFAULTS, **overrides}
    d = add_distance(df, municipality)
    city_woz = city_typical_woz(d, municipality)
    ok = (
        (d["dist_to_city_km"] <= s["max_km"])
        & (d["avg_woz_value_k_eur"] < city_woz)
        & (d["pct_rent_private"] >= s["min_private_rent_pct"])
        & (d["urbanity_level"] <= s["max_urbanity"])
        & (d["dist_supermarket_km"] <= s["max_supermarket_km"])
        & (d["dwelling_count"] >= s["min_dwellings"])
    )
    if not s["include_estimated"]:
        ok &= ~d["woz_estimated"] & ~d["rent_estimated"]
    d["candidate"] = ok
    return d, s, city_woz
