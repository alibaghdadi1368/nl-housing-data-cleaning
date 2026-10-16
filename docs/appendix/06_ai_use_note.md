# AI-use note

I used Claude (Anthropic) as an assistant during this project. The step-by-step record is in `ai_build_log.md`; this note is the summary.

## What AI helped with

- **Finding and understanding the data.** It pointed me to CBS as a reliable source for Dutch neighbourhood data, explained the Dutch names of the measures, and helped me understand the EAV (long) format, which I had never worked with before, and how to turn it into one table.
- **Code.** It helped me draft code for the notebooks and the Streamlit app, which I ran, read and tested on my own laptop.
- **Debugging.** It suggested the hypothesis behind my biggest finding (the decimal comma that `errors="coerce"` silently turned into missing values), and it found why the app was slow and why the map was blank without internet.
- **Documentation.** It helped with grammar and sentence structure in my notes, captions, the story text in the app and these appendix files. English is not my first language.

## What was mine

- The question and the audience: my own search for a home after moving from Iran to work in data, wanting to live in or near Utrecht.
- Choosing the measures I needed for that question, and the first cleaning project (`src/`), which this project builds on.
- Running every notebook and the app on my own laptop, and reading every output.
- The decisions: changing the story when the data showed a hump instead of a steady fall, keeping the city's own neighbourhoods in the shortlist, and the default thresholds after looking at the sensitivity table.
- The content of the text: findings, decisions and numbers. Where a corrected sentence did not sound like me, I rewrote it.

## How I checked AI output

- **Restart & Run All** on all three notebooks before submitting.
- **Totals that must not change:** 14,729 neighbourhoods and a total population of 18,044,120, the same as in my first project.
- **Every number in my text** is copied from notebook output, not from the chat.
- **Measure meanings** checked against CBS's own descriptions in `MeasureCodes.csv`.
- **Sanity checks in the data:** corporation + other landlords = total rentals (±1); the comma comparison table (old method vs new method).
- **The app against the notebook:** the default view shows 309 candidates, the same as `03_storyboard.ipynb`.
- **Real-world tests:** wifi off, dark and light theme, full-size data.

## What I corrected or rejected

- My own earlier claim that CBS did not publish distance data: it was a parsing bug.
- The first map (Plotly geo), because it needs the internet.
- Presenting the housing shortage as a finding; it stays my personal experience, because my data does not measure it.
