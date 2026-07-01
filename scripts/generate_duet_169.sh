#!/usr/bin/env bash
# generate_duet_169.sh — build 16:9 Cookie+Grover DUET stills by outpainting each
# preserved 9:16 Cookie still (stills/916/<id>_v1.png) into a wide frame and adding
# Grover. The beat's image_prompt already carries the full duet instruction; this
# just feeds the 9:16 still as --image at aspect 16:9 and writes the result to
# stills/<id>_v1.png (the 9:16 original stays in stills/916/).
#
# Usage:
#   ./generate_duet_169.sh <reel_folder>                 # all beats
#   ./generate_duet_169.sh <reel_folder> B11 B12         # specific beats
#   DRY_RUN=1 ...                       # print commands only
#   FILL_ONLY=1 ...                     # skip beats whose 16:9 still already exists
#   MODEL_ID=flux_2 ...                 # image model (default nano_banana_2_shots — holds source tighter)
#   RES=2k
#
# Requires: jq, curl, and (unless DRY_RUN) an authenticated `higgsfield` CLI.
set -uo pipefail
FOLDER="${1:?usage: generate_duet_169.sh <reel_folder> [BEAT_ID...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

DRY_RUN="${DRY_RUN:-0}"
MODEL_ID="${MODEL_ID:-nano_banana_2}"   # FLUX.2 false-flags felt-puppet content as nsfw; Nano Banana passes
RES="${RES:-2k}"; FLUX_MODEL="${FLUX_MODEL:-pro}"; ASPECT="16:9"
MAX_RETRIES="${MAX_RETRIES:-4}"; RETRY_BASE="${RETRY_BASE:-20}"; THROTTLE="${THROTTLE:-2}"
OUT="$FOLDER/stills"; mkdir -p "$OUT"

if [ "$DRY_RUN" != 1 ]; then
  command -v higgsfield >/dev/null || { echo "missing: higgsfield (or use DRY_RUN=1)" >&2; exit 1; }
  higgsfield account status >/dev/null 2>&1 || { echo "higgsfield not authenticated — run: higgsfield auth login" >&2; exit 1; }
fi

NEG="One continuous photographic film still of a two-puppet duet. No text, no captions, no lettering, no watermark. No split screen, no panels, no collage, no black bars."
abspath(){ case "$1" in /*) printf '%s' "$1";; *) printf '%s/%s' "$FOLDER" "$1";; esac; }
declare -a PICK=("$@")
want(){ [ ${#PICK[@]} -eq 0 ] && return 0; for x in "${PICK[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

ok=0; skip=0; fail=0
n=$(jq '.beats | length' "$SPEC")
echo "16:9 duet stills: $FOLDER  $MODEL_ID  aspect=$ASPECT  res=$RES -> stills/$([ "$DRY_RUN" = 1 ] && echo '  (DRY_RUN)')"

for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC"); want "$bid" || continue
  out="$OUT/${bid}_v1.png"
  if [ "${FILL_ONLY:-0}" = 1 ] && [ -e "$out" ]; then echo "=== $bid — exists, skip ==="; skip=$((skip+1)); continue; fi

  src=$(jq -r ".beats[$i].duet_source_916 // empty" "$SPEC")
  [ -z "$src" ] && { echo "=== $bid — no duet_source_916, skip ==="; skip=$((skip+1)); continue; }
  srcp=$(abspath "$src")
  [ -f "$srcp" ] || { echo "=== $bid — 9:16 source missing: $srcp ==="; fail=$((fail+1)); continue; }
  iprompt=$(jq -r ".beats[$i].image_prompt" "$SPEC")
  prompt="$iprompt $NEG"
  echo; echo "=== $bid  src=916/$(basename "$srcp")  grover=$(jq -r ".beats[$i].grover_side" "$SPEC") ==="

  args=(generate create "$MODEL_ID" --aspect_ratio "$ASPECT" --prompt "$prompt" --image "$srcp")
  case "$MODEL_ID" in
    flux_2)       args+=(--resolution "$RES" --model "$FLUX_MODEL");;  # flux: resolution + sub-model
    nano_banana*) : ;;                                                # nano: prompt + image + aspect only
    *)            args+=(--resolution "$RES");;
  esac
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
echo; echo "done — $ok stills, $fail failed, $skip skipped.  16:9 duets in $OUT (9:16 originals kept in stills/916/)"
[ "$fail" -gt 0 ] && echo "failures saved as .err next to the target; re-run skips finished stills."
exit 0
