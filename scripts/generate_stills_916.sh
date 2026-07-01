#!/usr/bin/env bash
# generate_stills_916.sh — make 9:16 (vertical) stills from a reel's existing 16:9
# stills + their existing prompts. For each beat it feeds the chosen 16:9 still as
# the reference image and the beat's image_prompt to FLUX.2 at aspect 9:16, so the
# subject/mood carry over but the frame is recomposed vertically (for Shorts/Reels).
#
#   stills/916/<beat_id>_v1.png
#
# Usage:
#   ./generate_stills_916.sh <reel_folder>                 # all beats
#   ./generate_stills_916.sh <reel_folder> B03 B07         # specific beats
#   DRY_RUN=1 ...                       # print higgsfield commands, generate nothing
#   FILL_ONLY=1 ...                     # skip beats whose 9:16 still already exists
#   MODEL_ID=nano_banana_2_shots ...    # different image model (default flux_2)
#   RES=2k  FLUX_MODEL=pro              # resolution / flux sub-model
#
# Requires: jq, curl, and (unless DRY_RUN) an authenticated `higgsfield` CLI.

set -uo pipefail
FOLDER="${1:?usage: generate_stills_916.sh <reel_folder> [BEAT_ID...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

DRY_RUN="${DRY_RUN:-0}"
MODEL_ID="${MODEL_ID:-flux_2}"
RES="${RES:-2k}"; FLUX_MODEL="${FLUX_MODEL:-pro}"
ASPECT="9:16"
MAX_RETRIES="${MAX_RETRIES:-4}"; RETRY_BASE="${RETRY_BASE:-20}"; THROTTLE="${THROTTLE:-2}"
OUT="$FOLDER/stills/916"; mkdir -p "$OUT"

if [ "$DRY_RUN" != 1 ]; then
  command -v higgsfield >/dev/null || { echo "missing: higgsfield (or use DRY_RUN=1)" >&2; exit 1; }
  higgsfield account status >/dev/null 2>&1 || { echo "higgsfield not authenticated — run: higgsfield auth login" >&2; exit 1; }
fi

STYLE=$(jq -r '.metadata.style_bible | "\(.visual_style). \(.color_palette). \(.lighting_style)."' "$SPEC")
RECOMPOSE="Recompose this image as a vertical 9:16 portrait, keeping the same subject, wardrobe, palette and mood; extend the scene naturally above and below; keep the main subject centered and fully in frame."
NEG="A single continuous full-frame photographic film still. No text, no captions, no lettering, no subtitles, no watermark. No split screen, no panels, no collage, no black bars."

abspath(){ case "$1" in /*) printf '%s' "$1";; *) printf '%s/%s' "$FOLDER" "$1";; esac; }
declare -a PICK=("$@")
want(){ [ ${#PICK[@]} -eq 0 ] && return 0; for x in "${PICK[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

ok=0; skip=0; fail=0
n=$(jq '.beats | length' "$SPEC")
echo "9:16 stills: $FOLDER  $MODEL_ID  aspect=$ASPECT  res=$RES -> stills/916/$([ "$DRY_RUN" = 1 ] && echo '  (DRY_RUN)')"

for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC"); want "$bid" || continue
  out="$OUT/${bid}_v1.png"
  if [ "${FILL_ONLY:-0}" = 1 ] && [ -e "$out" ]; then echo "=== $bid — exists, skip ==="; skip=$((skip+1)); continue; fi

  still=$(jq -r ".beats[$i].chosen_still // empty" "$SPEC")
  [ -z "$still" ] && { echo "=== $bid — no chosen_still, skip ==="; skip=$((skip+1)); continue; }
  stillp=$(abspath "$still")
  [ -f "$stillp" ] || { echo "=== $bid — 16:9 still missing: $stillp ==="; fail=$((fail+1)); continue; }
  iprompt=$(jq -r ".beats[$i].image_prompt // .beats[$i].storyboard_prompts[0]" "$SPEC")
  prompt="$STYLE $RECOMPOSE Scene: $iprompt. $NEG"
  echo; echo "=== $bid  still=$(basename "$stillp") ==="

  args=(generate create "$MODEL_ID" --aspect_ratio "$ASPECT" --resolution "$RES" --prompt "$prompt" --image "$stillp")
  [ "$MODEL_ID" = "flux_2" ] && args+=(--model "$FLUX_MODEL")
  args+=(--wait --json)

  if [ "$DRY_RUN" = 1 ]; then printf '  -> %s\n    higgsfield' "$out"; printf ' %q' "${args[@]}"; echo; ok=$((ok+1)); continue; fi

  attempt=1; got=""
  while [ "$attempt" -le "$MAX_RETRIES" ]; do
    resp=$(higgsfield "${args[@]}" 2>&1)
    url=$(printf '%s' "$resp" | jq -r '.[].result_url // empty' 2>/dev/null | head -1)
    if [ -n "$url" ] && curl -fsSL "$url" -o "$out"; then echo "  -> $out"; got=1; ok=$((ok+1)); rm -f "${out%.png}.err"; break; fi
    printf '%s' "$resp" > "${out%.png}.err"
    if printf '%s' "$resp" | grep -qiE "rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
      wsec=$((RETRY_BASE*attempt)); echo "  transient — wait ${wsec}s ($attempt/$MAX_RETRIES)"; sleep "$wsec"
    else echo "  FAILED: $(printf '%s' "$resp" | tail -1 | cut -c1-120)"; break; fi
    attempt=$((attempt+1))
  done
  [ -z "$got" ] && fail=$((fail+1))
  sleep "$THROTTLE"
done
echo; echo "done — $ok stills, $fail failed, $skip skipped.  9:16 stills in $OUT"
[ "$fail" -gt 0 ] && echo "failures saved as .err next to the target; re-run skips finished stills."
exit 0
