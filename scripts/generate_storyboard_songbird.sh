#!/usr/bin/env bash
# generate_storyboard_songbird.sh — storyboard stills for a Songbird beat_sheet.json
# via Higgsfield FLUX.2, honoring this repo's songbird schema:
#   - each beat carries its OWN reference plate (random): .character_ref or .location_ref
#   - each beat carries TWO distinct prompts: .storyboard_prompts[0], [1]
# So we emit 2 stills per beat (v1 = prompt A, v2 = prompt B), each locked to that
# beat's single assigned plate. Cull the one you don't want; set beat.chosen_still.
#
#   stills/<beat_id>_v1.png   stills/<beat_id>_v2.png
#
# Usage:
#   ./generate_storyboard_songbird.sh <reel_folder>                 # all beats
#   ./generate_storyboard_songbird.sh <reel_folder> B03 B07         # specific beats
#   DRY_RUN=1 ...                       # print the higgsfield commands, generate nothing
#   ONLY=tuzi | ONLY=paris ...          # only that subject
#   FILL_ONLY=1 ...                     # skip beats that already have a still
#   ASPECT=16:9  RES=2k  MODEL=pro      # overrides (default from metadata)
#
# Requires: jq, curl, and (unless DRY_RUN) an authenticated `higgsfield` CLI.

set -uo pipefail
FOLDER="${1:?usage: generate_storyboard_songbird.sh <reel_folder> [BEAT_ID...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

DRY_RUN="${DRY_RUN:-0}"
ASPECT="${ASPECT:-$(jq -r '.metadata.aspect_ratio // "16:9"' "$SPEC")}"
RES="${RES:-2k}"; MODEL="${MODEL:-pro}"
SUBJ="${ONLY:-}"
MAX_RETRIES="${MAX_RETRIES:-4}"; RETRY_BASE="${RETRY_BASE:-20}"; THROTTLE="${THROTTLE:-2}"
GEN="$FOLDER/stills"; mkdir -p "$GEN"

if [ "$DRY_RUN" != 1 ]; then
  command -v higgsfield >/dev/null || { echo "missing: higgsfield (or use DRY_RUN=1)" >&2; exit 1; }
  higgsfield account status >/dev/null 2>&1 || { echo "higgsfield not authenticated — run: higgsfield auth login" >&2; exit 1; }
fi

STYLE=$(jq -r '.metadata.style_bible | "\(.visual_style). \(.color_palette). \(.lighting_style)."' "$SPEC")
NEG="A single continuous full-frame photographic film still. No text, no captions, no lettering, no subtitles, no watermark. No split screen, no panels, no collage."

declare -a PICK=("$@")
want(){ [ ${#PICK[@]} -eq 0 ] && return 0; for x in "${PICK[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

ok=0; skip=0; fail=0
n=$(jq '.beats | length' "$SPEC")
echo "songbird storyboard: $FOLDER  flux_2/$MODEL  aspect=$ASPECT  res=$RES  2/beat${DRY_RUN:+  (DRY_RUN)}"

for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC"); want "$bid" || continue
  subject=$(jq -r ".beats[$i].subject" "$SPEC")
  [ -n "$SUBJ" ] && [ "$SUBJ" != "$subject" ] && continue
  if [ "${FILL_ONLY:-0}" = 1 ] && ls "$GEN/${bid}_v"*.png >/dev/null 2>&1; then
    echo "=== $bid — has a still, skip (FILL_ONLY) ==="; skip=$((skip+1)); continue
  fi

  ref=$(jq -r ".beats[$i].character_ref // .beats[$i].location_ref // empty" "$SPEC")
  refpath=""
  if [ -n "$ref" ]; then
    case "$ref" in /*) refpath="$ref";; *) refpath="$FOLDER/$ref";; esac
    [ -f "$refpath" ] || { echo "  !! $bid ref missing: $refpath" >&2; refpath=""; }
  fi
  echo; echo "=== $bid  [$subject]  ref=$(basename "${refpath:-none}") ==="

  for v in 1 2; do
    out="$GEN/${bid}_v${v}.png"
    [ -e "$out" ] && { echo "  v$v exists, skip"; skip=$((skip+1)); continue; }
    iprompt=$(jq -r ".beats[$i].storyboard_prompts[$((v-1))] // .beats[$i].image_prompt" "$SPEC")
    prompt="$STYLE A single film still: $iprompt. $NEG"
    args=(generate create flux_2 --aspect_ratio "$ASPECT" --resolution "$RES" --model "$MODEL" --prompt "$prompt")
    [ -n "$refpath" ] && args+=(--image "$refpath")
    args+=(--wait --json)
    if [ "$DRY_RUN" = 1 ]; then printf '  v%s -> %s\n    higgsfield' "$v" "$out"; printf ' %q' "${args[@]}"; echo; continue; fi
    attempt=1; got=""
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
      resp=$(higgsfield "${args[@]}" 2>&1)
      url=$(printf '%s' "$resp" | jq -r '.[].result_url // empty' 2>/dev/null | head -1)
      if [ -n "$url" ] && curl -fsSL "$url" -o "$out"; then
        echo "  v$v -> $out"; got=1; ok=$((ok+1)); rm -f "${out%.png}.err"; break
      fi
      printf '%s' "$resp" > "${out%.png}.err"
      if printf '%s' "$resp" | grep -qiE "rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
        wsec=$((RETRY_BASE*attempt)); echo "  v$v transient — wait ${wsec}s ($attempt/$MAX_RETRIES)"; sleep "$wsec"
      else
        echo "  v$v FAILED: $(printf '%s' "$resp" | tail -1 | cut -c1-120)"; break
      fi
      attempt=$((attempt+1))
    done
    [ -z "$got" ] && fail=$((fail+1))
    sleep "$THROTTLE"
  done
done
echo; echo "done — $ok stills, $fail failed, $skip skipped.  cull each beat to one, then set beat.chosen_still."
[ "$fail" -gt 0 ] && echo "failures saved as .err next to the target; re-run skips finished stills."
exit 0
