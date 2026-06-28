#!/usr/bin/env bash
# generate_storyboard.sh — Unreal Reels Phase 3: storyboard stills.
#
# Reads a reel's beat_sheet.json and generates N candidate stills per beat (you pick
# the keeper, then set "chosen_still"). The style_bible is prepended to every prompt so
# the look stays consistent; identity comes from each character's Higgsfield Soul.
#
#   stills/<beat_id>_v1.png ...   (then choose; set beat.chosen_still in beat_sheet.json)
#
# Casting per beat (from characters_present + metadata.characters):
#   • exactly one soul character, alone   -> text2image_soul_v2 --soul-id  (clean)
#   • no soul character (pure world/object)-> nano_banana
#   • two+ characters, or a soul + a reference (e.g. Red Cap + Wolf)
#         -> SKIPPED with a flag: needs the multi-ref path (FLUX.2 / reference image),
#            handled by a separate runner. Single Soul can't place two locked identities
#            in one frame.
#
# Usage:
#   ./generate_storyboard.sh <reel_folder>                 # all beats
#   ./generate_storyboard.sh <reel_folder> B01 B02         # only these beats
#   DRY_RUN=1 ./generate_storyboard.sh <reel_folder> B01   # print commands, generate nothing
#   VARIATIONS=3  (default)   ASPECT=<override>  (default: metadata.aspect_ratio)
#
# Requires: higgsfield (authenticated), jq, curl, file.

set -uo pipefail
FOLDER="${1:?usage: generate_storyboard.sh <reel_folder> [BEAT_ID...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl file; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

VARIATIONS="${VARIATIONS:-3}"
ASPECT="${ASPECT:-$(jq -r '.metadata.aspect_ratio // "16:9"' "$SPEC")}"
DRY_RUN="${DRY_RUN:-0}"
MAX_RETRIES="${MAX_RETRIES:-4}"; RETRY_BASE="${RETRY_BASE:-20}"; THROTTLE="${THROTTLE:-3}"
# parallel image jobs at once. Keep well under your Higgsfield concurrent-slot limit (8);
# the website draws from the same 8 slots, so 3 leaves headroom. Raise if the site is idle.
CONCURRENCY="${CONCURRENCY:-3}"
# ALLOW_MULTI=1: don't skip multi-character beats — generate them with the PRIMARY Soul
# (protagonist, cast-order first); other characters come from the prompt text, not locked
# refs. A rough first pass for every beat until the multi-ref runner exists.
ALLOW_MULTI="${ALLOW_MULTI:-0}"
SOUL_MODEL="text2image_soul_v2"; PLAIN_MODEL="nano_banana"
GEN="$FOLDER/stills"; mkdir -p "$GEN"

[ "$DRY_RUN" = 1 ] || command -v higgsfield >/dev/null || { echo "missing: higgsfield" >&2; exit 1; }
if [ "$DRY_RUN" != 1 ] && ! higgsfield account status >/dev/null 2>&1; then
  echo "higgsfield not authenticated — run: higgsfield auth login" >&2; exit 1
fi

# style_bible -> one prefix string prepended to every prompt
STYLE=$(jq -r '.metadata.style_bible | "\(.visual_style). \(.color_palette). \(.lighting_style)."' "$SPEC")
# hard negative appended to EVERY prompt: never text, never split-screen.
NEG="Single cinematic film still, one continuous full-frame photographic image. No text, no captions, no subtitles, no speech bubbles, no thought bubbles, no lettering, no signage, no watermark. No split screen, no panels, no diptych, no triptych, no collage, no comic layout, no borders, no frame divisions."

ONLY=("$@")
want() { [ ${#ONLY[@]} -eq 0 ] && return 0; for x in "${ONLY[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }
extract_url() { jq -r '[.. | strings | select(test("^https?://"))] | ((map(select(test("\\.(jpe?g|png|webp)($|\\?)")))|.[0]) // .[0] // empty)' 2>/dev/null; }

# gen_one — generate ONE still (one Higgsfield job) with rate-limit backoff. Run in the
# background; CONCURRENCY of these run at once. Args: OUT MODEL PROMPT SOUL_ID(optional).
gen_one() {
  local out="$1" model="$2" prompt="$3" sid="$4"
  local sa=(); [ -n "$sid" ] && sa=(--soul-id "$sid")
  local attempt=1 resp url
  while [ "$attempt" -le "$MAX_RETRIES" ]; do
    resp=$(higgsfield generate create "$model" --prompt "$prompt" --aspect_ratio "$ASPECT" ${sa[@]+"${sa[@]}"} --wait --json 2>&1)
    url=$(printf '%s' "$resp" | extract_url)
    if [ -n "$url" ] && curl -fsSL "$url" -o "$out"; then
      echo "  ok   $(basename "$out")"; rm -f "${out%.png}.err"; return 0
    fi
    printf '%s' "$resp" > "${out%.png}.err"
    if printf '%s' "$resp" | grep -qiE "rate_limit|rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
      sleep $((RETRY_BASE * attempt))
    else
      echo "  FAIL $(basename "$out"): $(printf '%s' "$resp" | tail -1 | cut -c1-80)"; return 1
    fi
    attempt=$((attempt + 1))
  done
  echo "  FAIL $(basename "$out"): retries exhausted (rate limit?)"; return 1
}

skip=0; flagged=0; running=0
n=$(jq '.beats | length' "$SPEC")
echo "storyboard: $FOLDER  aspect=$ASPECT  ${VARIATIONS} variations/beat${DRY_RUN:+  DRY_RUN=$DRY_RUN}"

for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC"); want "$bid" || continue
  # scene prompt: image_prompt if authored, else scene_description, else the narration line
  iprompt=$(jq -r ".beats[$i].image_prompt" "$SPEC")
  [ -z "$iprompt" ] && iprompt=$(jq -r ".beats[$i].scene_description" "$SPEC")
  [ -z "$iprompt" ] && iprompt=$(jq -r ".beats[$i].narration_text" "$SPEC")

  # resolve characters present (Bash 3.2-safe: no mapfile, guard empty arrays)
  present=(); souls=(); soul_id=""; look=""
  while IFS= read -r cname; do
    [ -z "$cname" ] && continue
    present+=("$cname")
    drv=$(jq -r --arg n "$cname" '.metadata.characters[] | select(.name==$n) | .driver' "$SPEC")
    if [ "$drv" = "soul" ]; then
      souls+=("$cname")
      if [ -z "$soul_id" ]; then   # primary = first soul in cast order (protagonist preferred)
        soul_id=$(jq -r --arg n "$cname" '.metadata.characters[] | select(.name==$n) | .soul_id' "$SPEC")
        look=$(jq -r --arg n "$cname" '.metadata.characters[] | select(.name==$n) | .look' "$SPEC")
      fi
    fi
  done < <(jq -r ".beats[$i].characters_present[]?" "$SPEC")

  np=${#present[@]}; ns=${#souls[@]}
  if [ "$np" -gt 0 ]; then plist="${present[*]}"; else plist="none"; fi
  echo; echo "=== $bid  [$plist] ==="
  if [ "$np" -gt 1 ] || { [ "$ns" -ge 1 ] && [ "$np" -gt "$ns" ]; } || [ "$ns" -ge 2 ]; then
    if [ "$ALLOW_MULTI" = 1 ]; then
      echo "  ~ multi-character — primary Soul (${souls[0]:-none}) only; others from the prompt text (redo with the multi-ref runner later)."
    else
      echo "  ! multi-character beat — needs the multi-ref path (FLUX.2 / reference image). Skipping here."
      flagged=$((flagged+1)); continue
    fi
  fi

  if [ "$ns" -ge 1 ]; then
    model="$SOUL_MODEL"; soul_args=(--soul-id "$soul_id"); prompt="$STYLE A single film still: $iprompt, $look. $NEG"
  else
    model="$PLAIN_MODEL"; soul_args=(); prompt="$STYLE A single film still: $iprompt. $NEG"
  fi

  sid=""; [ "$ns" -ge 1 ] && sid="$soul_id"
  for v in $(seq 1 "$VARIATIONS"); do
    out="$GEN/${bid}_v${v}.png"
    existing=$(ls "$GEN/${bid}_v${v}".* 2>/dev/null | grep -vE '\.err$' | head -1)
    [ -n "$existing" ] && { echo "  v$v exists ($(basename "$existing")), skip"; skip=$((skip+1)); continue; }
    if [ "$DRY_RUN" = 1 ]; then printf '  v%s -> %s  [%s%s]\n' "$v" "$out" "$model" "${sid:+ soul:$sid}"; continue; fi
    echo "  v$v queued"
    gen_one "$out" "$model" "$prompt" "$sid" &        # one of CONCURRENCY parallel jobs
    running=$((running + 1))
    if [ "$running" -ge "$CONCURRENCY" ]; then wait; running=0; fi
  done
done

wait   # drain the final batch of background jobs
made=$(ls "$GEN"/*.png 2>/dev/null | wc -l | tr -d ' ')
errs=$(ls "$GEN"/*.err 2>/dev/null | wc -l | tr -d ' ')
echo; echo "done — $made stills present, $errs errors, $skip skipped, $flagged multi-char beats flagged (need the multi-ref runner)."
[ "$errs" -gt 0 ] && echo "errors saved as .err. If 'rate_limit_reached': lower CONCURRENCY or close any Higgsfield-website jobs (they share your 8 slots). The script also backs off; re-running skips finished stills."
[ "$made" -gt 0 ] && echo "Pick a keeper per beat, set beat.chosen_still in beat_sheet.json, then run Phase 4 (video)."
