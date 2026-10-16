# Statistical profile

Source: `notebooks/02_profile.ipynb`. Measured values only (12,891 neighbourhoods).

## Centre and spread: average WOZ value per neighbourhood

| | value |
|---|---|
| median | 422k |
| mean | 450k |
| middle half (Q1-Q3) | 333k - 528k (IQR 195k) |
| range | 31k - 2,286k |
| skew | 2.0 |

The mean sits above the median because a few very expensive neighbourhoods pull it up. I report the median.

## One place where a summary misleads

| | per neighbourhood | per home (weighted by dwellings) |
|---|---|---|
| median | 422k | 374k |
| mean | 450k | 397k |

Counting every neighbourhood once overstates a typical home by about 48k (13%). The smallest quarter of neighbourhoods holds 2.5% of all homes but has a median of 515k against 393k for the rest: villages and rural areas with large houses get the same weight as city districts.

## One relationship: value and distance to Utrecht

| distance | 0-5 | 5-10 | 10-15 | 15-20 | 20-25 | 25-30 | 30-35 | 35-40 | 40-45 | 45-50 km |
|---|---|---|---|---|---|---|---|---|---|---|
| median WOZ (k) | 469 | 484 | 578 | 551 | 475 | 497 | 489 | 446 | 421 | 451 |

Not a steady fall: the 10-20 km ring is the most expensive, and only beyond ~35 km is the median below the city. Spearman = -0.17 (n = 4,454), which on its own would suggest "almost no relationship" and hide the hump. Within every band the middle half spans 150-280k, more than the change in the median across 50 km.

Private rentals: median 20% inside the city, 8-12% further out.

## Caveat

All band medians count neighbourhoods, not homes, so their level is somewhat too high (see above); I rely on the shape, not the exact numbers.
