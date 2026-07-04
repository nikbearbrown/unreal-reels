#!/usr/bin/env bash
# build_videos.sh — for a reel whose clips were generated on the web: download +
# rename them by prompt (fetch_and_match), then assemble EVERY aspect present into a
# final muxed video. fetch routes 16:9 jobs to video-16x9/raw/ and the reel's primary
# aspect to video/raw/, so each builds independently.
#
#   video/raw/<beat>.mp4        -> <slug>.mp4            (primary aspect, e.g. 9:16)
#   video-16x9/raw/<beat>.mp4   -> <slug>.16x9.mp4
#
# Usage:
#   ./build_videos.sh <reel_folder>
#   SKIP_FETCH=1 ./build_videos.sh <reel_folder>     # assemble only (already downloaded)
#   FETCH_ARGS="--size 120 --all" ./build_videos.sh <reel_folder>
# Requires: jq, ffmpeg, python3, and (for fetch) an authenticated higgsfield CLI.
set -uo pipefail
FOLDER="${1:?usage: build_videos.sh <reel_folder>}"
SPEC="$FOLDER/beat_sheet.json"; [ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
SEED="$HERE/generate_video.sh"

if [ "${SKIP_FETCH:-0}" != 1 ]; then
  echo "=== download + rename web clips (both aspects) ==="
  python3 "$HERE/fetch_and_match.py" "$FOLDER" --video ${FETCH_ARGS:-} || echo "  (fetch reported issues — continuing to assemble what's present)"
fi

echo; echo "=== reconcile (collapse variants, write REDO.md) ==="
python3 "$HERE/reconcile.py" "$FOLDER" || true

built=0
for d in "$FOLDER"/video "$FOLDER"/video-*; do
  [ -d "$d/raw" ] || continue
  ls "$d"/raw/*.mp4 >/dev/null 2>&1 || { echo "=== $(basename "$d"): no clips, skip ==="; continue; }
  name=$(basename "$d"); tag=""; [ "$name" != "video" ] && tag="${name#video-}"
  case "$tag" in
    16x9) W=1920; H=1080; AR="16:9";;
    *)    W=1080; H=1920; AR=$(jq -r '.metadata.aspect_ratio // "9:16"' "$SPEC");;
  esac
  echo; echo "=== assemble $name  (tag='${tag:-none}'  ${AR}  ${W}x${H}) ==="
  ASSEMBLE_ONLY=1 FINAL=1 TAG="$tag" ASPECT="$AR" W="$W" H="$H" "$SEED" "$FOLDER" && built=$((built+1))
done

echo; echo "=== finals ==="
slug=$(jq -r '.metadata.slug' "$SPEC")
for f in "$FOLDER/$slug.mp4" "$FOLDER/$slug".*.mp4; do
  [ -f "$f" ] && printf '  %s  %ss\n' "$(basename "$f")" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null)"
done
echo "built $built aspect(s)."
