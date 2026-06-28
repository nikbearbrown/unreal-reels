#!/usr/bin/env bash
# generate_storyboard_flux.sh — Unreal Reels storyboard via Higgsfield FLUX.2 multi-ref.
#
# THE engine: FLUX.2 (`flux_2`) takes multiple reference images (`--image` repeated,
# up to 4) PLUS a text prompt — so it locks every character to its reference AND keeps
# them as distinct beings in one frame (proven: Red Cap + wolf, no werewolf blend).
# This replaces the Soul/nano split; one reference image per character (the wardrobe
# stills) drives every beat the character appears in, for cross-shot consistency.
#
#   stills/<beat_id>_v<N>.png   (then pick keepers; set beat.chosen_still)
#
# Per beat: prompt = style_bible + "A single film still: " + image_prompt + hard negative.
# References = the reference_image of each character in characters_present (cap 4).
# Scene-only beats (no characters) run prompt-only.
#
# Usage:
#   ./generate_storyboard_flux.sh <reel_folder>              # all beats
#   ./generate_storyboard_flux.sh <reel_folder> B11 B30      # specific beats
#   VARIATIONS=2  (default 1)   ASPECT=16:9 (default: metadata)   RES=2k   MODEL=pro
#   DRY_RUN=1 ...   (print commands, generate nothing)
#
# Requires: higgsfield (authenticated), jq, curl.  Re-runs skip finished stills.

set -uo pipefail
FOLDER="${1:?usage: generate_storyboard_flux.sh <reel_folder> [BEAT_ID...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

VARIATIONS="${VARIATIONS:-1}"
ASPECT="${ASPECT:-$(jq -r '.metadata.aspect_ratio // "16:9"' "$SPEC")}"
RES="${RES:-2k}"; MODEL="${MODEL:-pro}"
MAX_RETRIES="${MAX_RETRIES:-4}"; RETRY_BASE="${RETRY_BASE:-20}"; THROTTLE="${THROTTLE:-2}"
DRY_RUN="${DRY_RUN:-0}"
GEN="$FOLDER/stills"; mkdir -p "$GEN"

[ "$DRY_RUN" = 1 ] || command -v higgsfield >/dev/null || { echo "missing: higgsfield" >&2; exit 1; }
if [ "$DRY_RUN" != 1 ] && ! higgsfield account status >/dev/null 2>&1; then
  echo "higgsfield not authenticated — run: higgsfield auth login" >&2; exit 1
fi

STYLE=$(jq -r '.metadata.style_bible | "\(.visual_style). \(.color_palette). \(.lighting_style)."' "$SPEC")
NEG="Single cinematic film still, one continuous full-frame photographic image. No text, no captions, no speech bubbles, no lettering, no watermark. No split screen, no panels, no collage. Distinct separate subjects, not merged."

ONLY=("$@")
want() { [ ${#ONLY[@]} -eq 0 ] && return 0; for x in "${ONLY[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

ok=0; skip=0; fail=0
n=$(jq '.beats | length' "$SPEC")
echo "flux storyboard: $FOLDER  model=flux_2/$MODEL  aspect=$ASPECT  res=$RES  ${VARIATIONS}/beat${DRY_RUN:+  DRY_RUN=$DRY_RUN}"

for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC"); want "$bid" || continue
  iprompt=$(jq -r ".beats[$i].image_prompt" "$SPEC")
  [ -z "$iprompt" ] && iprompt=$(jq -r ".beats[$i].narration_text" "$SPEC")
  prompt="$STYLE A single film still: $iprompt. $NEG"

  # collect reference images for the characters present.
  # Each character has a folder references/characters/<ref_key>/ — drop 1+ plates in it.
  #   one plate  -> that plate is used.
  #   several    -> the runner feeds up to MAXPERCHAR of them (more views = stronger lock).
  # Total capped at 4 refs/scene. Falls back to metadata.reference_image if no folder yet.
  MAXPERCHAR="${MAXPERCHAR:-2}"
  imgs=(); present=""
  while IFS= read -r cname; do
    [ -z "$cname" ] && continue
    present="$present $cname"
    key=$(jq -r --arg n "$cname" '.metadata.characters[] | select(.name==$n) | .ref_key // empty' "$SPEC")
    cdir="$FOLDER/references/characters/$key"
    cn=0
    if [ -n "$key" ] && [ -d "$cdir" ]; then
      for rp in "$cdir"/*.png "$cdir"/*.jpg; do
        [ -f "$rp" ] || continue
        [ "$cn" -ge "$MAXPERCHAR" ] && break
        [ "$((${#imgs[@]}/2))" -ge 4 ] && break
        imgs+=(--image "$rp"); cn=$((cn+1))
      done
    fi
    if [ "$cn" -eq 0 ]; then    # fallback: single reference_image from metadata
      ref=$(jq -r --arg n "$cname" '.metadata.characters[] | select(.name==$n) | .reference_image // empty' "$SPEC")
      [ -n "$ref" ] && [ -f "$ref" ] && [ "$((${#imgs[@]}/2))" -lt 4 ] && imgs+=(--image "$ref")
    fi
  done < <(jq -r ".beats[$i].characters_present[]?" "$SPEC")

  echo; echo "=== $bid  [${present# }]  ($((${#imgs[@]}/2)) refs) ==="

  for v in $(seq 1 "$VARIATIONS"); do
    out="$GEN/${bid}_v${v}.png"
    [ -e "$out" ] && { echo "  v$v exists, skip"; skip=$((skip+1)); continue; }
    args=(generate create flux_2 --aspect_ratio "$ASPECT" --resolution "$RES" --model "$MODEL" --prompt "$prompt" ${imgs[@]+"${imgs[@]}"} --wait --json)
    if [ "$DRY_RUN" = 1 ]; then printf '  v%s -> %s\n    higgsfield' "$v" "$out"; printf ' %q' "${args[@]}"; echo; continue; fi

    attempt=1; got=""
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
      resp=$(higgsfield "${args[@]}" 2>&1)
      url=$(printf '%s' "$resp" | jq -r '.[].result_url // empty' 2>/dev/null | head -1)
      if [ -n "$url" ] && curl -fsSL "$url" -o "$out"; then
        echo "  v$v -> $out"; got=1; ok=$((ok+1)); rm -f "${out%.png}.err"; break
      fi
      printf '%s' "$resp" > "${out%.png}.err"
      if printf '%s' "$resp" | grep -qiE "rate_limit|rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
        wsec=$((RETRY_BASE*attempt)); echo "  v$v rate/transient — wait ${wsec}s ($attempt/$MAX_RETRIES)"; sleep "$wsec"
      else
        echo "  v$v FAILED: $(printf '%s' "$resp" | tail -1 | cut -c1-100)"; break
      fi
      attempt=$((attempt+1))
    done
    [ -z "$got" ] && fail=$((fail+1))
    sleep "$THROTTLE"
  done
done

echo; echo "done — $ok stills, $fail failed, $skip skipped."
[ "$fail" -gt 0 ] && echo "failures saved as .err; re-run skips finished stills."
[ "$ok" -gt 0 ] && echo "Pick keepers, set beat.chosen_still, then Phase 4 (video)."
