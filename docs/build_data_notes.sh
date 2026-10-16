#!/usr/bin/env bash
# Builds docs/DATA_NOTES.md from the separate notes in docs/appendix/.
# Run from the project root:  bash docs/build_data_notes.sh
set -e
cd "$(dirname "$0")/.."
OUT=docs/DATA_NOTES.md
{
  echo "# Data notes: Where can I afford to live?"
  echo
  echo "Ali Baghdadi · HU Utrecht · Data & AI · A Data-Informed Story"
  echo
  echo "Generated $(date +%Y-%m-%d) from the files in \`docs/appendix/\`."
  echo
  echo "**Contents:** 0 Provenance and ethics · 1 Brief · 2 Cleaning log · 3 Statistical profile · 4 Storyboard · 5 Limits · 6 AI use · Appendix: AI-build log"
  for f in 00_provenance_ethics 01_brief 02_cleaning_log 03_statistical_profile 04_storyboard 05_limits 06_ai_use_note ai_build_log; do
    echo
    echo "---"
    echo
    # image links in the storyboard are relative to docs/appendix/; fix them for docs/
    sed 's#(\.\./storyboard/#(storyboard/#g' "docs/appendix/$f.md"
  done
} > "$OUT"
echo "written $OUT ($(wc -l < "$OUT") lines)"
