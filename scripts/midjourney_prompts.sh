#!/usr/bin/env bash
# midjourney_prompts.sh — build ready-to-paste Midjourney prompts, one per beat,
# from a reel's committed discord/ stills + beat_sheet.json image_prompts.
#
# Each line is exactly:
#   <raw github url of BXX.jpg>  BXX, <image_prompt>, <STYLE> <FLAGS>
#
# BXX sits IMMEDIATELY after the URL on purpose: Midjourney seeds the downloaded
# filename from the start of the prompt text, so every render comes down named
# "..._bXX_..." and rename_midjourney.sh can sort it straight back to the beat.
#
# Stills must be committed + pushed first, or the raw URLs won't resolve in MJ.
#
# Default look is neutral: "as a simple wooden mannequin --ar 16:9".
# Replace STYLE with ANY style string (and FLAGS with any MJ flags / your own
# --profile) per batch, without editing the script:
#   STYLE="the style of Simon Stålenhag, digital art, sci-fi, chiaroscuro effect" \
#   FLAGS="--ar 16:9 --profile <your-profile-id>" \
#   ./midjourney_prompts.sh reels/little-red-cap-full
#
# Requires: jq.

set -uo pipefail
FOLDER="${1:?usage: midjourney_prompts.sh <reel_folder>}"
command -v jq >/dev/null || { echo "needs jq" >&2; exit 1; }
SHEET="$FOLDER/beat_sheet.json"; D="$FOLDER/discord"
[ -f "$SHEET" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
[ -d "$D" ]     || { echo "no discord/ in $FOLDER — run export_discord.sh first" >&2; exit 1; }

REPO="${REPO:-nikbearbrown/unreal-reels}"
BRANCH="${BRANCH:-main}"
slug=$(basename "$FOLDER")
BASE="https://raw.githubusercontent.com/$REPO/$BRANCH/reels/$slug/discord"
STYLE="${STYLE:-as a simple wooden mannequin}"
FLAGS="${FLAGS:---ar 16:9}"

OUT="$FOLDER/midjourney_prompts.txt"
: > "$OUT"; n=0
for img in "$D"/B*.jpg; do
  [ -f "$img" ] || continue
  bid=$(basename "$img" .jpg)
  prompt=$(jq -r --arg b "$bid" '.beats[] | select(.beat_id==$b) | .image_prompt' "$SHEET" \
             | tr '\n' ' ' | sed 's/  */ /g; s/^ *//; s/ *$//')
  [ -z "$prompt" ] || [ "$prompt" = "null" ] && prompt="$bid"
  printf '%s %s, %s, %s %s\n' "$BASE/$bid.jpg" "$bid" "$prompt" "$STYLE" "$FLAGS" >> "$OUT"
  n=$((n + 1))
done
echo "wrote $n prompts -> $OUT"
echo "paste each line into Midjourney; then rename downloads with rename_midjourney.sh"
