#!/usr/bin/env bash
# Build the page for a date and send it to the reMarkable "00MORNING" folder.
# Usage: ./send_page.sh [YYYY-MM-DD]   (default: today in Japan)
# Set DRY_RUN=1 to build without sending.
set -euo pipefail
cd "$(dirname "$0")"

# Default: the coming morning in Japan. Runs start the evening before, and any
# run before noon (a late one) still counts for that same day.
DAY="${1:-$(TZ=Asia/Tokyo date -d '+12 hours' +%F)}"
FOLDER="00MORNING"

if [[ ! -f "days/$DAY.json" ]]; then
  echo "No page for $DAY; nothing to send."
  exit 0
fi

if grep -qx "$DAY" sent.log 2>/dev/null; then
  echo "Page for $DAY was already sent."
  exit 0
fi

# File name: date-romaji, e.g. 2026-11-03-iki.pdf (the tablet cannot show kanji in names)
NAME="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1], encoding="utf-8")); print("-".join([d["date"], d["romaji"]]))' "days/$DAY.json")"
python3 make_page.py "days/$DAY.json" "$NAME.pdf"

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  echo "Dry run: built $NAME.pdf, not sent."
  exit 0
fi

# -ni: fail instead of waiting for a pairing code when the token is missing or expired
rmapi -ni mkdir "$FOLDER" >/dev/null 2>&1 || true
rmapi -ni put "$NAME.pdf" "$FOLDER"
echo "$DAY" >> sent.log
echo "Sent $NAME.pdf to /$FOLDER."
