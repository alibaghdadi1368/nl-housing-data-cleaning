
# Cleaning log

Every decision, in the order it happened. Numbers come from `notebooks/01_cleaning.ipynb` (section 10).

| #    | Date       | What I found                                                 | What I decided                                               | Why                                                          |
| ---- | ---------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 1    | 2026-09-21 | The "CSV" download was a ZIP with 12 files; Observations.csv is long format (1,596,799 rows) | Pivot to one row per region                                  | Analysis needs one row per neighbourhood                     |
| 2    | 2026-09-21 | 4 region levels mixed in one table (18,495 rows)             | Keep `Buurt` only (14,729)                                   | Higher levels would count people twice                       |
| 3    | 2026-09-21 | WOZ, ownership and building-age columns 10–25% missing; my first <10% rule silently dropped 1,838 neighbourhoods | Fill <25% missing with the municipality median, list every filled value in `imputed_fields` | Housing differs more between municipalities than within one; 0 rows dropped |
| 4    | 2026-09-21 | IQR outliers 2.5–5.7% per column; my first version overwrote the real values | Keep real values, add `*_capped` copies                      | Expensive or empty neighbourhoods are real, not errors       |
| 5    | 2026-10-16 | `pct_rental` mixes social housing (years of waiting) with private rentals | Added `A047047` corporation and `A047048` other landlords    | A newcomer can realistically only use the private part       |
| 6    | 2026-10-16 | Ownership block missing for 1,692 neighbourhoods (11.5%), always all three columns together | Same municipality-median rule, marked in `imputed_fields`    | CBS leaves the whole block out, most likely for very small neighbourhoods |
| 7    | 2026-10-16 | Corporation + other landlords = total rentals, gap never more than ±1 | Accepted the split as consistent                             | ±1 is rounding of whole percentages                          |
| 8    | 2026-10-16 | Map has 14,823 shapes, my table 14,729; the 94 extra are 93 water areas and 1 "abroad" | Left those 94 out; all 14,729 neighbourhoods found a shape   | They have no inhabitants and no statistics                   |
| 9    | 2026-10-16 | **Distance measures were not missing: CBS writes decimals with a comma and `errors="coerce"` silently made 78,112 values NaN** | Convert comma to point before `to_numeric`, count what still fails (0) | My earlier "data gap" conclusion was a parsing bug; distances are now usable (5.3% filled) |

**Result:** 14,729 neighbourhoods, total population 18,044,120, 1,842 neighbourhoods with at least one estimated value.
