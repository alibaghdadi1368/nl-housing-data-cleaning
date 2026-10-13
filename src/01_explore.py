"""
01_explore.py
First look at the raw CBS download. The file saved as 86165NED.zip is a ZIP
archive with 12 CSV files (Observations.csv, MeasureCodes.csv, ...), not one
flat table. This script lists every file with its encoding, size and first rows.

Not every file in the bundle is UTF-8: some are Windows-1252 (cp1252), which is
why each file is tried with UTF-8 first and cp1252 / latin-1 as fallbacks.
"""

from pathlib import Path

import pandas as pd

RAW = Path("../data/raw")
ENCODINGS = ("utf-8", "cp1252", "latin-1")  # latin-1 can decode any byte, so it is the last resort


def detect_encoding(path):
    """Return (encoding, number of data rows) for the first encoding that reads the whole file."""
    for enc in ENCODINGS:
        try:
            with open(path, encoding=enc) as f:
                return enc, sum(1 for _ in f) - 1  # minus the header line
        except UnicodeDecodeError:
            continue
    raise ValueError(f"could not decode {path.name}")


for path in sorted(RAW.glob("*.csv")):
    enc, n_rows = detect_encoding(path)
    print(f"\n=== {path.name}: {n_rows:,} rows, encoding {enc}")
    try:
        sample = pd.read_csv(path, sep=";", encoding=enc, nrows=5)
    except Exception as err:  # e.g. a ZIP saved with a .csv name
        print(f"    could not parse as a ';'-separated CSV: {err}")
        continue
    print(f"    {sample.shape[1]} columns")
    print(sample.head())