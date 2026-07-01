#!/usr/bin/env bash
# generate_composite_storyboard.sh — FLUX multi-input storyboard for a STORY reel.
# Per beat, composites beat.assets (<=4 inputs: a background + characters) into a
# START frame (beat.start_prompt) and an END frame (beat.end_prompt). Kling then
# tweens start->end. Frames -> stills/story/<beat>_start.png / _end.png, recorded as
# beat.storyboard_start / beat.storyboard_end.
#
# Usage:
#   ./generate_composite_storyboard.sh <reel_folder>            # all beats
#   ./generate_composite_storyboard.sh <reel_folder> B07 B20    # specific beats
#   DRY_RUN=1 ...  FILL_ONLY=1 ...  MODEL_ID=flux_2  RES=1k  ASPECT=9:16
# Requires: jq, curl, and (unless DRY_RUN) an authenticated higgsfield CLI.
set -uo pipefail
FOLDER="${1:?usage: generate_composite_storyboard.sh <reel_folder> [BEAT_ID...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done
DRY_RUN="${DRY_RUN:-0}"; MODEL_ID="${MODEL_ID:-flux_2}"; RES="${RES:-1k}"; FLUX_MODEL="${FLUX_MODEL:-pro}"
ASPECT="${ASPECT:-$(jq -r '.metadata.aspect_ratio // "9:16"' "$SPEC")}"
MAX_RETRIES="${MAX_RETRIES:-4}"; RETRY_BASE="${RETRY_BASE:-20}"; THROTTLE="${THROTTLE:-2}"
TAG="${TAG:-}"   # e.g. 16x9 -> writes stills/story-16x9/ and storyboard_start_16x9 fields (keeps the 9:16 set)
OUT="$FOLDER/stills/story${TAG:+-$TAG}"; mkdir -p "$OUT"
if [ "$DRY_RUN" != 1 ]; then
  command -v higgsfield >/dev/null || { echo "missing: higgsfield (or DRY_RUN=1)" >&2; exit 1; }
  higgsfield account status >/dev/null 2>&1 || { echo "higgsfield not authenticated" >&2; exit 1; }
fi
abspath(){ case "$1" in /*) printf '%s' "$1";; *) printf '%s/%s' "$FOLDER" "$1";; esac; }
declare -a PICK=("$@"); want(){ [ ${#PICK[@]} -eq 0 ] && return 0; for x in "${PICK[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

# gen <prompt> <out.png> <asset1> [asset2 ...]
gen(){
  local prompt="$1" out="$2"; shift 2
  local args=(generate create "$MODEL_ID" --aspect_ratio "$ASPECT" --resolution "$RES" --prompt "$prompt")
  local a; for a in "$@"; do args+=(--image "$(abspath "$a")"); done
  [ "$MODEL_ID" = "flux_2" ] && args+=(--model "$FLUX_MODEL")
  args+=(--wait --json)
  if [ "$DRY_RUN" = 1 ]; then printf '    -> %s  (%d inputs)\n' "$out" "$#"; return 0; fi
  local attempt=1 resp url
  while [ "$attempt" -le "$MAX_RETRIES" ]; do
    resp=$(higgsfield "${args[@]}" 2>&1)
    url=$(printf '%s' "$resp" | jq -r '.[].result_url // empty' 2>/dev/null | head -1)
    if [ -n "$url" ] && curl -fsSL "$url" -o "$out"; then echo "    -> $out"; rm -f "${out%.png}.err"; return 0; fi
    printf '%s' "$resp" > "${out%.png}.err"
    if printf '%s' "$resp" | grep -qiE "rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
      local w=$((RETRY_BASE*attempt)); echo "    transient — wait ${w}s ($attempt/$MAX_RETRIES)"; sleep "$w"
    else echo "    FAILED: $(printf '%s' "$resp" | tail -1 | cut -c1-120)"; return 1; fi
    attempt=$((attempt+1))
  done; return 1
}

ok=0; skip=0; fail=0
n=$(jq '.beats | length' "$SPEC")
echo "composite storyboard: $FOLDER  $MODEL_ID $ASPECT $RES -> stills/story/$([ "$DRY_RUN" = 1 ] && echo '  (DRY_RUN)')"
for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC"); want "$bid" || continue
  startf="$OUT/${bid}_A_start.png"; endf="$OUT/${bid}_B_end.png"   # A/B = Kling's first/last-frame slots; sorts A->B
  # per-frame: with FILL_ONLY, only (re)generate the frame that's missing
  do_start=1; do_end=1
  if [ "${FILL_ONLY:-0}" = 1 ]; then [ -e "$startf" ] && do_start=0; [ -e "$endf" ] && do_end=0; fi
  if [ "$do_start" = 0 ] && [ "$do_end" = 0 ]; then echo "=== $bid both present, skip ==="; skip=$((skip+1)); continue; fi
  assets=()
  while IFS= read -r a; do [ -n "$a" ] && assets+=("$a"); done < <(jq -r ".beats[$i].assets[]" "$SPEC")
  miss=0; for a in "${assets[@]}"; do [ -f "$(abspath "$a")" ] || { echo "  $bid missing asset: $a"; miss=1; }; done
  [ "$miss" = 1 ] && { fail=$((fail+1)); continue; }
  sp=$(jq -r ".beats[$i].start_prompt" "$SPEC"); ep=$(jq -r ".beats[$i].end_prompt" "$SPEC")
  echo; echo "=== $bid  ${#assets[@]} inputs: $(printf '%s ' "${assets[@]##*/}") ==="
  if [ "$do_start" = 1 ]; then echo "  start:"; gen "$sp" "$startf" "${assets[@]}" && ok=$((ok+1)) || fail=$((fail+1)); sleep "$THROTTLE"; else echo "  start present, skip"; fi
  if [ "$do_end" = 1 ];   then echo "  end:";   gen "$ep" "$endf"   "${assets[@]}" && ok=$((ok+1)) || fail=$((fail+1)); sleep "$THROTTLE"; else echo "  end present, skip"; fi
done
if [ "$DRY_RUN" != 1 ]; then
  python3 - "$SPEC" "$FOLDER" "$TAG" <<'PY'
import json, os, sys
spec, folder, tag = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(spec))
sub = f"stills/story-{tag}" if tag else "stills/story"
kt = f"_{tag}" if tag else ""
for b in d["beats"]:
    for k, suf in ((f"storyboard_start{kt}","_A_start"), (f"storyboard_end{kt}","_B_end")):
        p = f"{sub}/{b['beat_id']}{suf}.png"
        if os.path.exists(os.path.join(folder, p)): b[k] = p
json.dump(d, open(spec, "w"), ensure_ascii=False, indent=2)
print(f"recorded{(' '+tag) if tag else ''} | starts:", sum(1 for b in d['beats'] if b.get(f'storyboard_start{kt}')),
      "ends:", sum(1 for b in d['beats'] if b.get(f'storyboard_end{kt}')))
PY
fi
echo; echo "done — $ok frames, $fail failed, $skip skipped."
exit 0
