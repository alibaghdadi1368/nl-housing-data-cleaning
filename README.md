# Dutch Housing Data Cleaning; CBS Neighborhood Statistics

A data cleaning project on official Dutch government housing data,
covering price, location, housing stock, and accessibility across
every neighborhood in the Netherlands; built with Pandas and NumPy
for the Data & AI course at HU University of Applied Sciences Utrecht.

## 📊 Data Source

**CBS (Centraal Bureau voor de Statistiek)**: the Dutch national
statistics office; *Kerncijfers wijken en buurten 2025* (Key figures
for districts and neighborhoods), table **86165NED**.

- Official page: https://www.cbs.nl/nl-nl/cijfers/detail/86165NED
- Direct download: https://datasets.cbs.nl/CSV/CBS/nl/86165NED
- License: CC-BY 4.0

## 🎯 What This Project Does

1. Loads CBS's raw export and reshapes it from a long (EAV) format
   into an analysis-ready wide table
2. Selects 21 measures relevant to housing: location, price, housing
   stock, ownership type, and accessibility (a 22nd, standardized
   income, turned out not to exist in the 2025 release)
3. Filters to neighborhood (*buurt*) level: 14,729 neighborhoods
4. Investigates and treats missing values, including a real data
   availability gap discovered along the way (see below)
5. Detects outliers using the IQR method and adds capped copies of
   the affected columns, with before/after visualizations
6. Produces a clean, 14,729-row analysis-ready CSV that keeps the real
   values and marks every imputed one

## 🧭 The Real Data Pipeline (and the problems solved along the way)

This section documents what actually happened, in order, including
the dead ends; because working through unexpected data problems is
the actual substance of a data cleaning project, not a footnote.

### 1. The download wasn't a CSV

The direct download link returns a file with a `.csv` extension, but
running `file` on it revealed it's actually a **ZIP archive**. Once
extracted, it contained 12 separate files, not one flat table:
`Observations.csv`, `MeasureCodes.csv`, `WijkenEnBuurtenCodes.csv`,
and several other dimension/metadata tables. CBS publishes this table
through its newer OData-style bulk export, not as a simple flat CSV.

### 2. The data is long (EAV), not wide

`Observations.csv` turned out to be a **1,596,799-row long-format
table**: each row is one `(region, measure, value)` triple, not one
row per neighborhood with all attributes as columns. To get a usable
housing table, I had to:

- Search `MeasureCodes.csv` (438 available measures) by keyword to
  find the exact codes for the 21 measures I actually needed (e.g.
  `M001642` = average WOZ property value, `D000028` = distance to a
  GP practice)
- Pivot `Observations.csv` on those codes; separately for numeric
  measures (stored in the `Value` column) and text measures like
  region name/type (stored in `StringValue`), then join the two
  pivoted tables back together
- Join in the human-readable neighborhood name from
  `WijkenEnBuurtenCodes.csv`

This produced an 18,495-row × 23-column wide table covering every
region level (country, municipality, district, neighborhood) at once.

### 3. Filtering to the right granularity

The wide table mixes four region levels in one file. I filtered to
`region_type == "Buurt"` (neighborhood), leaving **14,729 rows**, and
dropped `region_code`, a duplicate of the existing region identifier.

### 4. A data gap that turned out to be my own parsing bug

The five distance-to-amenity measures (distance to a GP practice,
supermarket, daycare, school, and number of schools within 3km) looked
**72–94% missing**. I first assumed CBS only publishes them at a higher
level, wrote `06_diagnostic_check_access_coverage.py` to check, saw the
same gap at district and municipality level, and concluded it was a
real gap in the 2025 release. I dropped the columns and used
`urbanity_level` and `address_density` as a proxy instead.

That conclusion was wrong. When I rebuilt the pipeline as a notebook
(`notebooks/01_cleaning.ipynb`) for the data story, the same rule
suddenly dropped zero columns. The cause: CBS writes decimals with a
comma (`1,2` km). `pd.to_numeric(..., errors="coerce")` does not read a
comma, and turns every such value into NaN **without a warning**.
Distances are the only measures with decimals, which is why only they
were hit, at every region level.

| Measure | values with a comma | missing, old way | missing, comma -> point |
|---|---|---|---|
| distance to supermarket | 16,251 | 91.9% | 0.0% |
| distance to GP practice | 16,174 | 91.5% | 0.0% |
| distance to daycare | 16,596 | 93.9% | 0.0% |
| distance to school | 16,410 | 92.8% | 0.0% |
| schools within 3km | 12,681 | 71.7% | 0.0% |

78,112 values were lost this way. No other measure contains a comma, so
the rest of the first pipeline is unaffected. The scripts in `src/` are
kept unchanged as the record of the first attempt; the notebook is the
corrected version. What I take from it: `errors="coerce"` hides errors,
so I now always count how many values it turned into NaN.

### 5. Missing values: three documented decision tiers

After dropping the five unsalvageable columns, the first
missing-value pass used a two-tier rule (impute under 10% missing,
drop columns over 40% missing) and left a gap: several genuinely
usable columns; average WOZ value, ownership %, building-age %,
dwelling-type %: sat in an untreated 10-25% missing range. Because
average WOZ value was also one of the "core fields" used to drop
rows, this silently dropped **1,838 neighborhoods** (12.5% of the
data) that were otherwise perfectly usable.

I revised the rule to a wider imputation tier (**under 25% missing →
impute with the municipality-level median**, rather than a national
median, since housing stock varies enormously between
municipalities). Re-running the pipeline with the corrected logic
recovered all of those neighborhoods: **0 rows were dropped** in the
final version.

### 6. Outliers: flagged and capped in separate columns

Using the IQR method on the five remaining unbounded numeric columns
(WOZ value, dwelling count, population, population density, address
density), 2.5%-5.7% of neighborhoods were flagged as outliers in
each column. A very expensive Amsterdam-canal neighborhood or a
nearly-empty rural buurt is real data, not an error, so nothing is
deleted and the original columns are never overwritten. The capped
(winsorized) values go into separate `*_capped` columns, for statistics
that are sensitive to extremes.

My first version overwrote the original columns with the capped values.
That quietly changed the data: hundreds of neighborhoods ended up with
exactly the same "maximum" WOZ value and population, the national
population total came out at 16.4 million instead of 18.0 million, and the most expensive municipality in the ranking was simply sitting on the cap.
Keeping both versions fixed that.

### 7. Marking what was estimated

Every value filled in by the municipality-median rule is listed in an
`imputed_fields` column (for example `avg_woz_value_k_eur;pct_rental`),
so anyone using the file can separate measured values from estimates.

## 📈 Final Results

| | Value |
|---|---|
| Raw observations (long format) | 1,596,799 rows |
| Total measures available | 438 |
| Wide table, all region levels | 18,495 rows × 23 columns |
| Neighborhood-level (Buurt) | 14,729 rows × 22 columns |
| After missing-value handling | 14,729 rows × 18 columns (0 rows dropped) |
| Final dataset (with `*_capped` columns) | 14,729 rows × 23 columns |
| Neighborhoods with at least one imputed value | 1,838 |
| Total population (real values) | 18,044,120 |
| Average WOZ property value (mean) | €444,994.195 |
| Average WOZ property value (median) | €418,000 |

**Top 5 most expensive municipalities** (mean neighborhood WOZ value):
1. Laren (NH.):        1188.400000
2. Blaricum:           1038.833333
3. Wassenaar:          965.809524
4. Bloemendaal:        863.454545
5. Ouder-Amstel:       823.142857

(All well-known high-income Dutch municipalities; a solid sanity
check that the pipeline produced sensible results.)

## 🗂️ Repository Structure

| Path | Purpose |
|---|---|
| `src/01_explore.py` | Initial inspection of the raw download |
| `src/02_find_measure_codes.py` | Search 438 CBS measures by keyword to find the 21 needed |
| `src/03_build_wide_table.py` | Pivot the long EAV format into a wide table |
| `src/04_filter_neighborhoods.py` | Filter to neighborhood (Buurt) level |
| `src/05_handling_missing.py` | First missing-value pass (two-tier rule) |
| `src/06_diagnostic_check_access_coverage.py` | Diagnostic that disproved the granularity theory |
| `src/07_handling_missing_revised.py` | Corrected three-tier missing-value handling |
| `src/08_handle_outliers.py` | IQR-based outlier detection; capped copies in `*_capped` columns |
| `src/09_summary_report.py` | Before/after summary statistics |
| `data/processed/nl_housing_clean.csv` | Final cleaned dataset (14,729 × 23) |
| `docs/` | Before/after outlier boxplots |

`data/raw/` and `data/interim/` are excluded via `.gitignore`; they're
large and fully reproducible by re-running the pipeline.

## 🚀 How to Reproduce

```bash
conda create -n housing python=3.10 -y
conda activate housing
pip install -r requirements.txt

mkdir -p data/raw data/interim
curl -L -A "Mozilla/5.0" -o data/raw/86165NED.zip "https://datasets.cbs.nl/CSV/CBS/nl/86165NED"
cd data/raw && unzip 86165NED.zip && cd ../../src

python 01_explore.py
python 02_find_measure_codes.py
python 03_build_wide_table.py
python 04_filter_neighborhoods.py
python 05_handling_missing.py
python 06_diagnostic_check_access_coverage.py
python 07_handling_missing_revised.py
python 08_handle_outliers.py
python 09_summary_report.py
```

`05_handling_missing.py` and `06_diagnostic_check_access_coverage.py` are
kept to document the first attempt and the diagnostic; the final pipeline
uses `07`. Running them is harmless.

## 🛠️ Tech Stack

Python · Pandas · NumPy · Matplotlib · Seaborn

## 📬 Contact

Ali Baghdadi · [LinkedIn](https://linkedin.com/in/alibaghdadi) · alibaghdadi1368@gmail.com
