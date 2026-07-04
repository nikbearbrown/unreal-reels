#!/usr/bin/env bash
# recreate.sh — rebuild an EXISTING reel's video from its committed definition + assets,
# and show it. This is the getting-started tutorial: one command, one video. What runs
# depends on the reel's skill/kind —
#   • Manim mini-bio (Bios)  -> renders cards, composites the clips, muxes -> mp4/<slug>.mp4
#   • Remotion (Songbird / lecture) -> opens the video in Remotion studio
# Because the assets (mp3/, clips/) are already committed, the mini-bio path needs NO
# API keys — it just re-renders and re-assembles what's there.
#
# Usage:
#   bash scripts/recreate.sh <reel_folder>            # 16:9 (or the reel's primary aspect)
#   bash scripts/recreate.sh <reel_folder> --short    # also build the 9:16 Short (Bios)
#   e.g.  bash scripts/recreate.sh reels/bio-bose
set -uo pipefail

FOLDER="${1:?usage: recreate.sh <reel_folder> [--short]}"
SHORT=0; [ "${2:-}" = "--short" ] && SHORT=1
FOLDER="$(cd "$FOLDER" 2>/dev/null && pwd)" || { echo "no such folder: $1" >&2; exit 1; }
SPEC="$FOLDER/beat_sheet.json"; [ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
REPO="$(cd "$(dirname "$0")/.." && pwd)"
BD="$REPO/aspects/explainer/bears-doodles/scripts"

kind=$(jq -r '.metadata.kind // ""' "$SPEC" 2>/dev/null)
slug=$(jq -r '.metadata.slug // "video"' "$SPEC" 2>/dev/null)

show(){ f="$1"; [ -f "$f" ] || return 0; echo "==> done: $f"; (open "$f" 2>/dev/null || xdg-open "$f" 2>/dev/null || true); }

# --- Remotion reel: a remotion/ project => you watch it in Remotion studio ---
if [ -d "$FOLDER/remotion" ]; then
  echo "=== Remotion reel — launching studio (Ctrl-C to stop) ==="
  cd "$FOLDER/remotion" && npm install >/dev/null 2>&1
  exec npm run studio
fi

# --- Manim mini-bio (Bios) => rebuild the MP4 from committed assets, no keys ---
if [ "$kind" = "bio" ]; then
  scene_py=$(ls "$FOLDER"/*.py 2>/dev/null | grep -vE 'bn_layout|__' | head -1)
  [ -f "$scene_py" ] || { echo "no Manim scene .py in $FOLDER" >&2; exit 1; }
  [ -f "$FOLDER/mp3/timings.json" ] || echo "[warn] mp3/timings.json missing — run generate_audio.py first (needs ELEVENLABS_API_KEY)."

  if [ "$SHORT" = 1 ]; then
    echo "=== [9:16] manim + composite + assemble ==="
    ( cd "$FOLDER" && manim -r 1080,1920 --fps 60 --disable_caching --flush_cache "$(basename "$scene_py")" BearsDoodlesVideo )
    python3 "$BD/composite_clips.py" "$FOLDER" --portrait
    python3 "$BD/assemble.py"       "$FOLDER" --mode manim --portrait --manim-mp4 "$FOLDER/mp4/_composited-short.mp4"
    show "$FOLDER/mp4/${slug}-short.mp4"
  else
    echo "=== [16:9] manim + composite + assemble ==="
    ( cd "$FOLDER" && manim -qh "$(basename "$scene_py")" BearsDoodlesVideo )
    python3 "$BD/composite_clips.py" "$FOLDER"
    python3 "$BD/assemble.py"       "$FOLDER" --mode manim --manim-mp4 "$FOLDER/mp4/_composited.mp4"
    show "$FOLDER/mp4/${slug}.mp4"
  fi
  exit 0
fi

echo "No recreate recipe for kind='$kind' (and no remotion/ project). See docs/getting-started.md." >&2
exit 1
