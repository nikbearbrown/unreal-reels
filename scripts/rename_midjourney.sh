#!/usr/bin/env bash
# rename_midjourney.sh — after a Midjourney bulk download, rename every image back
# to its beat id. MJ names files from the start of the prompt, which is "BXX", so the
# beat id is recoverable from the filename. Multiple variants per beat -> BXX, BXX_1,
# BXX_2, ...  Originals are COPIED (never moved) into <dest_dir>, so nothing is lost.
#
# Usage:  ./rename_midjourney.sh <download_dir> [<dest_dir>]
#   <dest_dir> defaults to <download_dir>/renamed
#
# Heuristic: the first  b<digits>  token in the filename is the beat id. MJ puts it
# right after your username because BXX leads the prompt (see midjourney_prompts.sh).

set -uo pipefail
SRC="${1:?usage: rename_midjourney.sh <download_dir> [dest_dir]}"
DEST="${2:-$SRC/renamed}"
[ -d "$SRC" ] || { echo "no such dir: $SRC" >&2; exit 1; }
mkdir -p "$DEST"
shopt -s nullglob nocaseglob 2>/dev/null || true
n=0; skip=0

for f in "$SRC"/*.png "$SRC"/*.jpg "$SRC"/*.jpeg "$SRC"/*.webp; do
  [ -f "$f" ] || continue
  base=$(basename "$f"); ext="${f##*.}"
  tok=$(printf '%s' "$base" | grep -oiE 'b[0-9]{1,3}' | head -1)
  if [ -z "$tok" ]; then
    echo "  ?  no beat id in: $base  (skipped)" >&2; skip=$((skip + 1)); continue
  fi
  num=$(printf '%s' "$tok" | grep -oE '[0-9]{1,3}')
  bid=$(printf 'B%02d' "$((10#$num))")
  out="$DEST/$bid.$ext"; i=1
  while [ -e "$out" ]; do out="$DEST/${bid}_$i.$ext"; i=$((i + 1)); done
  cp "$f" "$out"; n=$((n + 1)); echo "  $base  ->  $(basename "$out")"
done

echo "renamed $n files -> $DEST   (skipped $skip)"
