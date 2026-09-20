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
   stock, ownership type, and accessibility
3. Filters to neighborhood (*buurt*) level: 14,729 neighborhoods
4. Investigates and treats missing values, including a real data
   availability gap discovered along the way (see below)
5. Detects and treats outliers using the IQR method, with
   before/after visualizations
6. Produces a clean, 14,729-row analysis-ready CSV

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

### 4. A real data availability gap: the accessibility measures

The five distance-to-amenity measures I originally selected
(distance to a GP practice, supermarket, daycare, school, and number
of schools within 3km) were **86–94% missing**. I initially assumed
this was because CBS only publishes reliable distance statistics at
a higher aggregation level than individual neighborhoods, and wrote
a diagnostic script (`06_diagnostic_check_access_coverage.py`) to
check the missing rate for these same measures at *Wijk* (district)
and *Gemeente* (municipality) level too.

The result disproved that theory: missing rates stayed at
86–94% at every level, including municipality. This is a genuine
data availability gap in this specific 2025 release, not a
granularity artifact; CBS distance-to-amenity measures have had
known coverage issues in recent editions. Rather than fabricate or
force-impute data that mostly doesn't exist, I dropped these five
columns and used two CBS's own, well-populated (<1% missing)
urbanicity indicators: `urbanity_level` (*Mate van stedelijkheid*)
and `address_density` (*Omgevingsadressendichtheid*), as the
accessibility signal instead, since higher urbanity density is
itself CBS's standard proxy for amenity proximity.

### 5. Missing values: three documented decision tiers

After dropping the five unsalvageable columns, the first
missing-value pass used a two-tier rule (impute under 10% missing,
drop columns over 40% missing) and left a gap: several genuinely
usable columns; average WOZ value, ownership %, building-age %,
dwelling-type %: sat in an untreated 10–25% missing range. Because
average WOZ value was also one of the "core fields" used to drop
rows, this silently dropped **1,838 neighborhoods** (12.5% of the
data) that were otherwise perfectly usable.

I revised the rule to a wider imputation tier (**under 25% missing →
impute with the municipality-level median**, rather than a national
median, since housing stock varies enormously between
municipalities). Re-running the pipeline with the corrected logic
recovered all of those neighborhoods: **0 rows were dropped** in the
final version.

### 6. Outliers: capped, not deleted

Using the IQR method on the five remaining unbounded numeric columns
(WOZ value, dwelling count, population, population density, address
density), 2.5%–5.7% of neighborhoods were flagged as outliers in
each column. These were **capped (winsorized) rather than deleted**:
a very expensive Amsterdam-canal neighborhood or a nearly-empty rural
buurt is real data, not an error, so capping limits its distorting
effect on aggregate statistics while keeping full national coverage
in the final dataset.

## 📈 Final Results

| | Value |
|---|---|
| Raw observations (long format) | 1,596,799 rows |
| Total measures available | 438 |
| Wide table, all region levels | 18,495 rows × 23 columns |
| Neighborhood-level (Buurt) | 14,729 rows × 22 columns |
| After missing-value handling | 14,729 rows × 17 columns (0 rows dropped) |
| After outlier capping | 14,729 rows × 17 columns |
| Average WOZ property value (mean) | €437,932 |
| Average WOZ property value (median) | €418,000 |

**Top 5 most expensive municipalities** (mean neighborhood WOZ value):
1. Rozendaal: €784,500
2. Laren (NH.): €770,800
3. Blaricum: €746,222
4. Ouder-Amstel: €723,357
5. Wassenaar: €696,548

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
| `src/08_handle_outliers.py` | IQR-based outlier detection and capping |
| `src/09_summary_report.py` | Before/after summary statistics |
| `data/processed/nl_housing_clean.csv` | Final cleaned dataset (14,729 × 17) |
| `docs/` | Before/after outlier boxplots |

`data/raw/` and `data/interim/` are excluded via `.gitignore`; they're
large and fully reproducible by re-running the pipeline.

## 🚀 How to Reproduce

```bash
conda create -n housing python=3.10 -y
conda activate housing
pip install -r requirements.txt

mkdir -p data/raw
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

## 🛠️ Tech Stack

Python · Pandas · NumPy · Matplotlib · Seaborn

## 📬 Contact

**Ali Baghdadi**:

[LinkedIn](https://linkedin.com/in/alibaghdadi)

alibaghdadi1368@gmail.com
