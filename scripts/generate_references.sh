#!/usr/bin/env bash
# generate_references.sh — build the character reference library (Stage 0).
#
# For each SoulID character in a reel's beat_sheet.json, generate COUNT (default 10)
# CLEAN reference plates — the kind FLUX reads identity + costume from best: front/¾
# view, even light, plain background, full costume. You then pick the ONE great plate
# per character and copy it to references/characters/<character_look>.png.
#
#   references/candidates/<ref_prefix>-<ref_key>-NN.png
#
# The wolf (driver: reference) is skipped — you already have that image.
# This is NOT the storyboard; these are the reference inputs the storyboard runner uses.
#
# Usage:
#   ./generate_references.sh <reel_folder>                 # 10 each, all soul characters
#   ./generate_references.sh <reel_folder> red woodsman    # only these ref_keys
#   COUNT=10  ASPECT=2:3  QUALITY=2k   DRY_RUN=1
#
# Requires: higgsfield (authenticated), jq, curl.  Re-runs skip finished plates.

set -uo pipefail
FOLDER="${1:?usage: generate_references.sh <reel_folder> [ref_key...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

COUNT="${COUNT:-10}"
ASPECT="${ASPECT:-2:3}"          # portrait plate; FLUX reads any aspect later
QUALITY="${QUALITY:-2k}"
MAX_RETRIES="${MAX_RETRIES:-4}"; RETRY_BASE="${RETRY_BASE:-20}"; THROTTLE="${THROTTLE:-2}"
DRY_RUN="${DRY_RUN:-0}"
OUT="$FOLDER/references/candidates"; mkdir -p "$OUT"

[ "$DRY_RUN" = 1 ] || command -v higgsfield >/dev/null || { echo "missing: higgsfield" >&2; exit 1; }
if [ "$DRY_RUN" != 1 ] && ! higgsfield account status >/dev/null 2>&1; then
  echo "higgsfield not authenticated — run: higgsfield auth login" >&2; exit 1
fi

PREFIX=$(jq -r '.metadata.ref_prefix // .metadata.slug // "ref"' "$SPEC")
# clean-reference suffix: the studio-plate recipe FLUX reads best
SUFFIX="full-length front or three-quarter view, facing camera, even soft studio lighting, plain neutral grey background, full costume clearly visible, sharp focus, natural skin, no dramatic shadows, no motion blur, no text, no props"

ONLY=("$@")
want() { [ ${#ONLY[@]} -eq 0 ] && return 0; for x in "${ONLY[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

ok=0; skip=0; fail=0
nc=$(jq '.metadata.characters | length' "$SPEC")
echo "references: $FOLDER  prefix=$PREFIX  count=$COUNT  aspect=$ASPECT${DRY_RUN:+  DRY_RUN=$DRY_RUN}"

for ci in $(seq 0 $((nc-1))); do
  driver=$(jq -r ".metadata.characters[$ci].driver" "$SPEC")
  [ "$driver" = "soul" ] || continue                       # skip wolf (reference) etc.
  name=$(jq -r ".metadata.characters[$ci].name" "$SPEC")
  key=$(jq -r ".metadata.characters[$ci].ref_key // empty" "$SPEC")
  [ -z "$key" ] && key=$(echo "$name" | tr '[:upper:] ' '[:lower:]-')
  want "$key" || continue
  soul=$(jq -r ".metadata.characters[$ci].soul_id" "$SPEC")
  look=$(jq -r ".metadata.characters[$ci].look" "$SPEC")
  prompt="$look, $SUFFIX"
  echo; echo "=== $name  [$key]  soul:$soul ==="

  for nn in $(seq 1 "$COUNT"); do
    n=$(printf '%02d' "$nn")
    out="$OUT/${PREFIX}-${key}-${n}.png"
    [ -e "$out" ] && { echo "  $n exists, skip"; skip=$((skip+1)); continue; }
    args=(generate create text2image_soul_v2 --soul-id "$soul" --prompt "$prompt" --aspect_ratio "$ASPECT" --quality "$QUALITY" --wait --json)
    if [ "$DRY_RUN" = 1 ]; then printf '  %s -> %s\n    higgsfield' "$n" "$out"; printf ' %q' "${args[@]}"; echo; continue; fi
    attempt=1; got=""
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
      resp=$(higgsfield "${args[@]}" 2>&1)
      url=$(printf '%s' "$resp" | jq -r '.[].result_url // empty' 2>/dev/null | head -1)
      if [ -n "$url" ] && curl -fsSL "$url" -o "$out"; then
        echo "  $n -> $(basename "$out")"; got=1; ok=$((ok+1)); rm -f "${out%.png}.err"; break
      fi
      printf '%s' "$resp" > "${out%.png}.err"
      if printf '%s' "$resp" | grep -qiE "rate_limit|rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
        wsec=$((RETRY_BASE*attempt)); echo "  $n rate/transient — wait ${wsec}s ($attempt/$MAX_RETRIES)"; sleep "$wsec"
      else
        echo "  $n FAILED: $(printf '%s' "$resp" | tail -1 | cut -c1-100)"; break
      fi
      attempt=$((attempt+1))
    done
    [ -z "$got" ] && fail=$((fail+1))
    sleep "$THROTTLE"
  done
done

echo; echo "done — $ok plates, $fail failed, $skip skipped  -> $OUT"
echo "Pick the GREAT one per character; copy it to references/characters/<character_look>.png"
echo "(e.g. cp references/candidates/${PREFIX}-red-04.png references/characters/red-cap_cloak.png)"
