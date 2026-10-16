# Provenance and ethics

## Where the data comes from

| | Statistics | Neighbourhood map |
|---|---|---|
| Name | Kerncijfers wijken en buurten 2025 (table 86165NED) | Wijk- en buurtkaart 2025, version 1 |
| Publisher | CBS (Statistics Netherlands) | CBS, municipal boundaries from Kadaster |
| Where | https://www.cbs.nl/nl-nl/cijfers/detail/86165NED, bulk download https://datasets.cbs.nl/CSV/CBS/nl/86165NED | https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/wijk-en-buurtkaart-2025 |
| What I got | A ZIP (despite the .csv name) with 12 files; Observations.csv has 1,596,799 rows in long format | A ZIP with one GeoPackage: layers buurten (14,823 shapes), wijken, gemeenten |
| Downloaded | 2026-09-13 | 2026-10-16 |
| Licence | CC BY 4.0: free to reuse with credit to CBS | Free to reuse with credit to CBS and Kadaster |
| How | Direct download, no scraping, no login | Direct download, no scraping, no login |

Both raw downloads are kept out of Git (too large); the README has the exact download commands, so anyone can rebuild everything from scratch with `notebooks/01_cleaning.ipynb`.

## Why this source

I needed something that covers **every** neighbourhood in the country with the same definitions. CBS is the official statistics office and publishes one consistent table for all 14,729 neighbourhoods. Housing websites have rents, but only for homes on offer right now, without definitions, and their terms do not allow scraping. I chose a source I can defend over one that has the exact number I wanted (rent).

## Personal data and privacy

- There is no data about people or single homes in this project, only neighbourhood totals and averages.
- CBS already protects privacy at the source: no average WOZ for neighbourhoods with fewer than 20 homes, and no ownership figures where too few homes are known. That is why 1,692 neighbourhoods have no rental figures (see the cleaning log).
- I do not combine this with any other data that could point to a person or a household.

## Ethical choices I made

1. **No "cheap" or "bad" labels.** A neighbourhood is the home of real people. The app never ranks neighbourhoods from best to worst and never calls a place cheap or poor; it says "lower value than a typical home in the city", which is what the data measures.
2. **Average is not a person.** A low average WOZ says nothing about any single home or household living there. The app says this in its limits section, so nobody draws conclusions about the people in a neighbourhood.
3. **Estimates are marked.** 1,842 neighbourhoods have at least one value filled with the municipality median. They are left out of the shortlist by default and labelled "(estimated)" when shown.
4. **My point of view is built in.** The story starts from my own situation: a newcomer with a job who needs a private rental. A student, a family or someone on a waiting list for social housing would need different criteria. The sidebar lets readers change the thresholds, but the questions are still mine.
5. **A tool can push people to the same places.** If many newcomers use the same shortlist, they all look in the same neighbourhoods, which could add to the pressure there. At the scale of a course project this is small, but it is a reason to show a wide list and the reader's own criteria rather than a single "best" answer.
6. **The data has an age.** These are 2025 figures and WOZ is a valuation with a reference date in the past. Values and rental shares change; the app shows the year in its sources.
