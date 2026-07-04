#!/usr/bin/env bash
# Generate Miniver Cheevy storyboard stills with Higgsfield FLUX.2.
#
# This reel uses beat.assets as direct FLUX input images. The PNGs are references,
# not finished stills. Each output is generated from:
#   input image(s): beat.assets
#   text prompt:   image_prompt_a / image_prompt_b, falling back to image_prompt
#
# Usage:
#   FORCE=1 ASPECT=9:16  ./generate_flux_stills_from_assets.sh
#   FORCE=1 ASPECT=16:9 TAG=16x9 ./generate_flux_stills_from_assets.sh
#   ONLY="B01 B02" FORCE=1 ASPECT=9:16 ./generate_flux_stills_from_assets.sh
#   DRY_RUN=1 ASPECT=9:16 ./generate_flux_stills_from_assets.sh

set -uo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SPEC="$ROOT/beat_sheet.json"
[ -f "$SPEC" ] || { echo "missing beat_sheet.json" >&2; exit 1; }

for t in jq curl; do
  command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }
done

ASPECT="${ASPECT:-9:16}"
TAG="${TAG:-}"
RES="${RES:-2k}"
MODEL="${MODEL:-pro}"
DRY_RUN="${DRY_RUN:-0}"
FORCE="${FORCE:-0}"
MAX_RETRIES="${MAX_RETRIES:-4}"
RETRY_BASE="${RETRY_BASE:-20}"
THROTTLE="${THROTTLE:-2}"

if [ "$ASPECT" = "16:9" ] || [ "$TAG" = "16x9" ]; then
  OUTDIR="$ROOT/stills/story-16x9"
else
  OUTDIR="$ROOT/stills/story"
fi
mkdir -p "$OUTDIR"

if [ "$DRY_RUN" != 1 ]; then
  command -v higgsfield >/dev/null || { echo "missing: higgsfield" >&2; exit 1; }
  if ! higgsfield account status >/dev/null 2>&1; then
    echo "higgsfield is not authenticated. Run: higgsfield auth login" >&2
    exit 1
  fi
fi

STYLE=$(jq -r '
  if .metadata.style_bible then
    (.metadata.style_bible.visual_style // "") + ". " +
    (.metadata.style_bible.color_palette // "") + ". " +
    (.metadata.style_bible.lighting_style // "")
  else
    .metadata.style // ""
  end
' "$SPEC")
NEG="Single cinematic film still. No text, no captions, no speech bubbles, no lettering, no watermark. No split screen, no panels, no collage."

want() {
  [ -z "${ONLY:-}" ] && return 0
  case " $ONLY " in *" $1 "*) return 0 ;; *) return 1 ;; esac
}

generate_one() {
  bid="$1"; suffix="$2"; prompt="$3"; shift 3
  out="$OUTDIR/${bid}_${suffix}.png"
  [ "$FORCE" != 1 ] && [ -s "$out" ] && { echo "skip $out"; return 0; }

  args=(generate create flux_2 --aspect_ratio "$ASPECT" --resolution "$RES" --model "$MODEL" --prompt "$STYLE A single film still: $prompt. $NEG" "$@" --wait --json)

  if [ "$DRY_RUN" = 1 ]; then
    printf 'DRY_RUN %s\n  higgsfield' "$out"
    printf ' %q' "${args[@]}"
    echo
    return 0
  fi

  attempt=1
  while [ "$attempt" -le "$MAX_RETRIES" ]; do
    resp=$(higgsfield "${args[@]}" 2>&1)
    url=$(printf '%s' "$resp" | jq -r '.[0].result_url // .result_url // .[].result_url // empty' 2>/dev/null | head -1)
    if [ -n "$url" ] && curl -fsSL "$url" -o "$out.tmp"; then
      mv "$out.tmp" "$out"
      rm -f "${out%.png}.err"
      echo "wrote $out"
      return 0
    fi
    printf '%s' "$resp" > "${out%.png}.err"
    if printf '%s' "$resp" | grep -qiE "rate_limit|rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
      wsec=$((RETRY_BASE * attempt))
      echo "transient failure for $out; wait ${wsec}s ($attempt/$MAX_RETRIES)"
      sleep "$wsec"
    else
      echo "FAILED $out; see ${out%.png}.err" >&2
      return 1
    fi
    attempt=$((attempt + 1))
  done
  echo "FAILED $out after retries; see ${out%.png}.err" >&2
  return 1
}

ok=0
fail=0
n=$(jq '.beats | length' "$SPEC")
echo "Miniver FLUX stills: aspect=$ASPECT out=$OUTDIR model=flux_2/$MODEL res=$RES force=$FORCE dry_run=$DRY_RUN"

for i in $(seq 0 $((n - 1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC")
  want "$bid" || continue

  prompt_a=$(jq -r ".beats[$i].image_prompt_a // .beats[$i].image_prompt // empty" "$SPEC")
  prompt_b=$(jq -r ".beats[$i].image_prompt_b // .beats[$i].image_prompt // empty" "$SPEC")
  [ -n "$prompt_a" ] || { echo "missing prompt for $bid" >&2; fail=$((fail + 1)); continue; }
  [ -n "$prompt_b" ] || prompt_b="$prompt_a"

  imgs=()
  while IFS= read -r asset; do
    [ -n "$asset" ] || continue
    path="$ROOT/$asset"
    [ -f "$path" ] || { echo "missing asset for $bid: $asset" >&2; fail=$((fail + 1)); continue; }
    imgs+=(--image "$path")
  done < <(jq -r ".beats[$i].assets[]?" "$SPEC")

  [ "${#imgs[@]}" -gt 0 ] || { echo "no assets for $bid" >&2; fail=$((fail + 1)); continue; }

  echo
  echo "=== $bid ($((${#imgs[@]} / 2)) input image(s)) ==="
  if generate_one "$bid" "A_start" "$prompt_a" "${imgs[@]}"; then ok=$((ok + 1)); else fail=$((fail + 1)); fi
  sleep "$THROTTLE"
  if generate_one "$bid" "B_end" "$prompt_b" "${imgs[@]}"; then ok=$((ok + 1)); else fail=$((fail + 1)); fi
  sleep "$THROTTLE"
done

echo
echo "done: $ok generated/skipped, $fail failed"
[ "$fail" -gt 0 ] && exit 1
exit 0
