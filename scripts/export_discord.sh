#!/usr/bin/env bash
# export_discord.sh — downsized JPG of each beat's KEEPER still into <reel>/discord/.
#
# Purpose: a public, raw, small image per beat that Midjourney (and any tool that
# needs an image URL) can riff on — paste the GitHub raw URL as an image prompt to
# generate artistic variants. Also doubles as the viewable storyboard on GitHub.
#
# Full-res PNG stills stay LOCAL (git-ignored, your working masters); only the small
# discord JPGs are committed. One JPG per beat = the keeper (first surviving variation).
#
#   <reel>/discord/B<NN>.jpg     (~1280px wide, q~85)
#
# Usage:  ./export_discord.sh <reel_folder>        WIDTH=1280 (override)
# Requires: ffmpeg.

set -uo pipefail
FOLDER="${1:?usage: export_discord.sh <reel_folder>}"
command -v ffmpeg >/dev/null || { echo "needs ffmpeg" >&2; exit 1; }
S="$FOLDER/stills"; D="$FOLDER/discord"; WIDTH="${WIDTH:-1280}"
[ -d "$S" ] || { echo "no stills/ in $FOLDER" >&2; exit 1; }
mkdir -p "$D"; n=0

for f in "$S"/B*_v*.png "$S"/B*_v*.jpg; do
  [ -f "$f" ] || continue
  bid=$(basename "$f" | sed -E 's/_v[0-9]+\.(png|jpg)$//')
  out="$D/${bid}.jpg"
  [ -e "$out" ] && continue                 # one per beat: first keeper wins
  if ffmpeg -y -loglevel error -i "$f" -vf "scale=${WIDTH}:-1" -q:v 4 "$out"; then
    n=$((n + 1)); echo "  $bid -> discord/${bid}.jpg"
  fi
done

slug=$(basename "$FOLDER")
echo "exported $n stills -> $D  ($(du -sh "$D" 2>/dev/null | cut -f1))"
echo "after commit + push, Midjourney-ready raw URLs look like:"
echo "  https://raw.githubusercontent.com/nikbearbrown/unreal-reels/main/reels/$slug/discord/B01.jpg"
