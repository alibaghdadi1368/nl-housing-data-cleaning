# Storyboard

Source: `notebooks/03_storyboard.ipynb`. Images in `docs/storyboard/`.
Format: interactive narrative (Streamlit). Audience: an international newcomer who just got a job in a Dutch city.

| # | reader's question | view | what the reader should conclude |
|---|---|---|---|
| 1 | Where is it expensive around my city? | ![](../storyboard/01_map.png) | The city is not the most expensive spot; the ring around it is. |
| 2 | Does moving out make it cheaper? | ![](../storyboard/02_distance.png) | Not until ~35 km, and distance alone is a poor guide. |
| 3 | Can I rent there? | ![](../storyboard/03_tradeoff.png) | Only 14% of neighbourhoods within 40 km are both lower in value and have ≥15% private rentals. |
| 4 | Where do I start? | ![](../storyboard/04_shortlist.png) | 309 candidates in 49 towns, mostly Amsterdam, Almere, Utrecht itself and Amersfoort. |

## Default view

Defined in `DEFAULTS` (`app/helpers.py`); reasons and sensitivity in the last section of `03_storyboard.ipynb`.

## What changed because of the data

I expected the answer to be "move further out". The data says the cheaper parts of Utrecht and of the larger cities nearby are where lower values and private rentals meet. And a lower WOZ there can simply mean smaller flats, because WOZ is per home, not per m2.
