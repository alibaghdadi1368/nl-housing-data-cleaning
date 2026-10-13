"""
02_find_measure_codes.py
The Observations file references measures by opaque codes (e.g. T001036).
This script searches MeasureCodes.csv by keyword to find the exact codes
we need, instead of guessing them.
"""

import pandas as pd

measures = pd.read_csv(
    "../data/raw/MeasureCodes.csv",
    sep=";",
    encoding="utf-8",
)

print("Total measures available: ", len(measures))
print("\nColumns: ", list(measures.columns))

KEYWORDS = [
    "inwoners", "dichtheid", "woningvoorraad", "WOZ", "koopwoning",
    "huurwoning", "bouwjaar", "eengezins", "meergezins",
    "huisartsenpraktijk", "supermarkt", "kinderdagverblijf",
    "school", "postcode", "stedelijkheid", "adressendichtheid",
    "gestandaardiseerd inkomen", "soort regio", "gemeentenaam", "codering",
]

for kw in KEYWORDS:
    matches = measures[measures["Title"].str.contains(kw, case=False, na=False)]
    print(f"\n--- '{kw}' ---")
    for _, row in matches.iterrows():
        print(f" {row['Identifier']}: {row['Title']}")