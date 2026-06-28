#!/usr/bin/env bash
# rebuild_manifest.sh — scan public/<slug>/media for delivered media and write
# src/media-manifest.json (what the Remotion overlay reads). Prefers a clip
# (.mp4) over a still (.png/.jpg) for the same beat. Run after generating videos
# (or after copying picked stills into media/). Safe to re-run any time.

set -euo pipefail
cd "$(dirname "$0")"
command -v jq >/dev/null 2>&1 || { echo "needs jq" >&2; exit 1; }

MANIFEST="src/media-manifest.json"
slug=$(jq -r '.slug // empty' "$MANIFEST" 2>/dev/null || true)
[ -z "${slug:-}" ] && slug=$(basename "$PWD")
chunk=$(jq -r '.chunkSeconds // 5' "$MANIFEST" 2>/dev/null || echo 5)
[ "$chunk" = "null" ] && chunk=5
MEDIA="public/$slug/media"
mkdir -p "$MEDIA"

# If media/ has no beats yet but gen/ holds curated picks, promote them:
# copy the single gen file per beat to media/<id>.<ext> (strip the _vN suffix).
if ! ls "$MEDIA"/B*.* >/dev/null 2>&1 && [ -d gen ]; then
  echo "media/ empty — promoting curated picks from gen/ ..."
  declare -A seen
  for f in gen/B*.*; do
    [ -e "$f" ] || continue
    b=$(basename "$f"); ext="${b##*.}"
    [ "$ext" = "err" ] && continue
    id="${b%%_*}"; id="${id%%.*}"
    if [ -n "${seen[$id]:-}" ]; then
      echo "  WARN: more than one gen file for $id (kept ${seen[$id]}, skipped $b)"; continue
    fi
    cp "$f" "$MEDIA/$id.$ext"; seen[$id]="$b"
  done
fi

# emit "<id>\t<rank>\t<file>" for every media file, then keep the best per beat.
rows=""
for f in "$MEDIA"/B*.*; do
  [ -e "$f" ] || continue
  b=$(basename "$f")
  ext="${b##*.}"
  [ "$ext" = "err" ] && continue
  id="${b%%.*}"; id="${id%%_*}"          # B07.mp4 / B07_v2.png -> B07
  case "$ext" in
    mp4|mov|webm|m4v) rank=0 ;;
    png|jpg|jpeg|webp) rank=2 ;;
    *) rank=3 ;;
  esac
  rows+="$id $rank $b"$'\n'
done

json=$(printf '%s' "$rows" \
  | sort -k1,1 -k2,2n \
  | awk '!seen[$1]++ {printf "%s\t%s\n",$1,$3}' \
  | jq -R 'select(length>0)|split("\t")|{(.[0]):.[1]}' \
  | jq -s 'add // {}')

jq -n --arg slug "$slug" --argjson chunk "$chunk" --argjson blocks "$json" \
  '{slug:$slug, chunkSeconds:$chunk, blocks:$blocks}' > "$MANIFEST"

echo "wrote $MANIFEST — $(printf '%s' "$json" | jq 'length') beats mapped"
printf '%s' "$json" | jq -r 'to_entries[] | "  \(.key) -> \(.value)"' | head -60
