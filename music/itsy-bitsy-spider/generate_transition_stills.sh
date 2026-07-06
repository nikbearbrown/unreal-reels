#!/usr/bin/env bash
# Generate FLUX storyboard stills for this reel only.
#
# Each beat has two FLUX image prompts: image_prompt_a and image_prompt_b.
# This script creates the two still outputs for the beat. It does not generate
# video.
#
# Usage:
#   ASPECT=9:16  ./generate_transition_stills.sh
#   ASPECT=16:9 TAG=16x9 ./generate_transition_stills.sh
#   DRY_RUN=1 ASPECT=9:16 ./generate_transition_stills.sh B01 B02
set -uo pipefail

FOLDER="$(cd "$(dirname "$0")" && pwd)"
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

DRY_RUN="${DRY_RUN:-0}"
MODEL_ID="${MODEL_ID:-flux_2}"
RES="${RES:-1k}"
FLUX_MODEL="${FLUX_MODEL:-pro}"
ASPECT="${ASPECT:-$(jq -r '.metadata.aspect_ratio // "9:16"' "$SPEC")}"
TAG="${TAG:-}"
MAX_RETRIES="${MAX_RETRIES:-4}"
RETRY_BASE="${RETRY_BASE:-20}"
THROTTLE="${THROTTLE:-2}"
OUT="$FOLDER/stills/story${TAG:+-$TAG}"
mkdir -p "$OUT"

if [ "$DRY_RUN" != 1 ]; then
  command -v higgsfield >/dev/null || { echo "missing: higgsfield (or DRY_RUN=1)" >&2; exit 1; }
  higgsfield account status >/dev/null 2>&1 || { echo "higgsfield not authenticated" >&2; exit 1; }
fi

abspath(){ case "$1" in /*) printf '%s' "$1";; *) printf '%s/%s' "$FOLDER" "$1";; esac; }
declare -a PICK=("$@")
want(){ [ ${#PICK[@]} -eq 0 ] && return 0; for x in "${PICK[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

gen(){
  local prompt="$1" out="$2"; shift 2
  local args=(generate create "$MODEL_ID" --aspect_ratio "$ASPECT" --resolution "$RES" --prompt "$prompt")
  local a
  for a in "$@"; do args+=(--image "$(abspath "$a")"); done
  [ "$MODEL_ID" = "flux_2" ] && args+=(--model "$FLUX_MODEL")
  args+=(--wait --json)
  if [ "$DRY_RUN" = 1 ]; then
    printf '    -> %s  (%d inputs)\n' "$out" "$#"
    return 0
  fi
  local attempt=1 resp url
  while [ "$attempt" -le "$MAX_RETRIES" ]; do
    resp=$(higgsfield "${args[@]}" 2>&1)
    url=$(printf '%s' "$resp" | jq -r '.[].result_url // empty' 2>/dev/null | head -1)
    if [ -n "$url" ] && curl -fsSL "$url" -o "$out"; then
      echo "    -> $out"
      rm -f "${out%.png}.err"
      return 0
    fi
    printf '%s' "$resp" > "${out%.png}.err"
    if printf '%s' "$resp" | grep -qiE "rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
      local w=$((RETRY_BASE*attempt))
      echo "    transient - wait ${w}s ($attempt/$MAX_RETRIES)"
      sleep "$w"
    else
      echo "    FAILED: $(printf '%s' "$resp" | tail -1 | cut -c1-120)"
      return 1
    fi
    attempt=$((attempt+1))
  done
  return 1
}

ok=0; skip=0; fail=0
n=$(jq '.beats | length' "$SPEC")
echo "transition stills: $FOLDER  $MODEL_ID $ASPECT $RES -> $OUT$([ "$DRY_RUN" = 1 ] && echo '  (DRY_RUN)')"
for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC")
  want "$bid" || continue
  af="$OUT/${bid}_A_start.png"
  bf="$OUT/${bid}_B_end.png"
  assets=()
  while IFS= read -r a; do [ -n "$a" ] && assets+=("$a"); done < <(jq -r ".beats[$i].assets[]" "$SPEC")
  miss=0
  for a in "${assets[@]}"; do [ -f "$(abspath "$a")" ] || { echo "  $bid missing asset: $a"; miss=1; }; done
  [ "$miss" = 1 ] && { fail=$((fail+1)); continue; }
  pa=$(jq -r ".beats[$i].image_prompt_a // .beats[$i].start_prompt" "$SPEC")
  pb=$(jq -r ".beats[$i].image_prompt_b // .beats[$i].end_prompt" "$SPEC")
  echo; echo "=== $bid  ${#assets[@]} inputs: $(printf '%s ' "${assets[@]##*/}") ==="
  echo "  frame A:"
  gen "$pa" "$af" "${assets[@]}" && ok=$((ok+1)) || fail=$((fail+1))
  sleep "$THROTTLE"
  echo "  frame B:"
  gen "$pb" "$bf" "${assets[@]}" && ok=$((ok+1)) || fail=$((fail+1))
  sleep "$THROTTLE"
done

echo; echo "done - $ok frames, $fail failed, $skip skipped."
exit 0
