#!/usr/bin/env bash
# Build the page for a date and send it to the reMarkable "Morning" folder.
# Usage: ./send_page.sh [YYYY-MM-DD]   (default: today in Japan)
# Set DRY_RUN=1 to build without sending.
set -euo pipefail
cd "$(dirname "$0")"

DAY="${1:-$(TZ=Asia/Tokyo date +%F)}"
FOLDER="Morning"

if [[ ! -f "days/$DAY.json" ]]; then
  echo "No page for $DAY; nothing to send."
  exit 0
fi

if grep -qx "$DAY" sent.log 2>/dev/null; then
  echo "Page for $DAY was already sent."
  exit 0
fi

# The file name is only the date, so the tablet shows no spoiler.
python3 make_page.py "days/$DAY.json" "$DAY.pdf"

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  echo "Dry run: built $DAY.pdf, not sent."
  exit 0
fi

# -ni: fail instead of waiting for a pairing code when the token is missing or expired
rmapi -ni mkdir "$FOLDER" >/dev/null 2>&1 || true
rmapi -ni put "$DAY.pdf" "$FOLDER"
echo "$DAY" >> sent.log
echo "Sent $DAY.pdf to /$FOLDER."
