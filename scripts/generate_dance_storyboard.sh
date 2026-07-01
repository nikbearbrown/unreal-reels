#!/usr/bin/env bash
# generate_dance_storyboard.sh — FLUX 16:9 storyboard stills for a dance reel.
# Per beat: image-to-image from the (portrait) character still to a wide 16:9 frame,
# posing the character mid-dance against the reel's background. The 16:9 still is what
# Seedance then animates (run seedance with STILL_KEY=storyboard_169).
#
#   stills/16x9/<beat_id>_v1.png   the FLUX 16:9 storyboard still
#   beat.storyboard_169            recorded back into beat_sheet.json
#
# Usage:
#   ./generate_dance_storyboard.sh <reel_folder>            # all beats
#   ./generate_dance_storyboard.sh <reel_folder> B01 B02    # specific beats
#   DRY_RUN=1 ...                      # print commands only
#   FILL_ONLY=1 ...                    # skip beats whose 16:9 still already exists
#   MODEL_ID=flux_2  RES=2k  FLUX_MODEL=pro   ASPECT=16:9
#
# Requires: jq, curl, and (unless DRY_RUN) an authenticated higgsfield CLI.
set -uo pipefail
FOLDER="${1:?usage: generate_dance_storyboard.sh <reel_folder> [BEAT_ID...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

DRY_RUN="${DRY_RUN:-0}"; MODEL_ID="${MODEL_ID:-flux_2}"; RES="${RES:-2k}"; FLUX_MODEL="${FLUX_MODEL:-pro}"
ASPECT="${ASPECT:-16:9}"
MAX_RETRIES="${MAX_RETRIES:-4}"; RETRY_BASE="${RETRY_BASE:-20}"; THROTTLE="${THROTTLE:-2}"
OUT="$FOLDER/stills/16x9"; mkdir -p "$OUT"

if [ "$DRY_RUN" != 1 ]; then
  command -v higgsfield >/dev/null || { echo "missing: higgsfield (or DRY_RUN=1)" >&2; exit 1; }
  higgsfield account status >/dev/null 2>&1 || { echo "higgsfield not authenticated" >&2; exit 1; }
fi
abspath(){ case "$1" in /*) printf '%s' "$1";; *) printf '%s/%s' "$FOLDER" "$1";; esac; }
CHAR=$(jq -r '.metadata.character // "the character"' "$SPEC")
BG=$(jq -r '.metadata.background // "a plain backdrop"' "$SPEC")
STYLE=$(jq -r '.metadata.style_suffix // ""' "$SPEC")
NEG="A single continuous full-frame still of one character. No text, no captions, no lettering, no watermark, no split screen, no panels, no collage, no black bars."

declare -a PICK=("$@")
want(){ [ ${#PICK[@]} -eq 0 ] && return 0; for x in "${PICK[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }
ok=0; skip=0; fail=0
n=$(jq '.beats | length' "$SPEC")
echo "dance storyboard: $FOLDER  $MODEL_ID  $ASPECT $RES -> stills/16x9/$([ "$DRY_RUN" = 1 ] && echo '  (DRY_RUN)')"

VARIANTS="${VARIANTS:-1}"   # candidates per beat (e.g. 2 -> _v1 and _v2 to pick from)
for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC"); want "$bid" || continue
  # FILL_ONLY skips beats that already have a keeper (_v1)
  [ "${FILL_ONLY:-0}" = 1 ] && [ -e "$OUT/${bid}_v1.png" ] && { echo "=== $bid has _v1, skip ==="; skip=$((skip+1)); continue; }
  src=$(abspath "$(jq -r ".beats[$i].chosen_still" "$SPEC")")
  [ -f "$src" ] || { echo "=== $bid src still missing: $src ==="; fail=$((fail+1)); continue; }
  move=$(jq -r ".beats[$i].dance_move // \"a dance pose\"" "$SPEC")
  prompt="$CHAR, mid-dance in $move, full body, centered, wide 16:9 framing. $BG. $STYLE. $NEG"
  echo; echo "=== $bid  src=$(basename "$src")  (${VARIANTS} candidate(s)) ==="
  for v in $(seq 1 "$VARIANTS"); do
    out="$OUT/${bid}_v${v}.png"
    args=(generate create "$MODEL_ID" --aspect_ratio "$ASPECT" --resolution "$RES" --prompt "$prompt" --image "$src")
    [ "$MODEL_ID" = "flux_2" ] && args+=(--model "$FLUX_MODEL")
    args+=(--wait --json)
    if [ "$DRY_RUN" = 1 ]; then printf '  v%s -> %s\n    higgsfield' "$v" "$out"; printf ' %q' "${args[@]}"; echo; ok=$((ok+1)); continue; fi
    attempt=1; got=""
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
      resp=$(higgsfield "${args[@]}" 2>&1)
      url=$(printf '%s' "$resp" | jq -r '.[].result_url // empty' 2>/dev/null | head -1)
      if [ -n "$url" ] && curl -fsSL "$url" -o "$out"; then echo "  v$v -> $out"; got=1; ok=$((ok+1)); rm -f "${out%.png}.err"; break; fi
      printf '%s' "$resp" > "${out%.png}.err"
      if printf '%s' "$resp" | grep -qiE "rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
        wsec=$((RETRY_BASE*attempt)); echo "  v$v transient — wait ${wsec}s ($attempt/$MAX_RETRIES)"; sleep "$wsec"
      else echo "  v$v FAILED: $(printf '%s' "$resp" | tail -1 | cut -c1-120)"; break; fi
      attempt=$((attempt+1))
    done
    [ -z "$got" ] && fail=$((fail+1)); sleep "$THROTTLE"
  done
done

# record storyboard_169 for every beat whose 16:9 still now exists
if [ "$DRY_RUN" != 1 ]; then
  python3 - "$SPEC" "$FOLDER" <<'PY'
import json, os, sys, glob
spec, folder = sys.argv[1], sys.argv[2]
d = json.load(open(spec))
for b in d["beats"]:
    cands = sorted(glob.glob(os.path.join(folder, f"stills/16x9/{b['beat_id']}_v*.png")))
    if cands:  # prefer the lowest-numbered surviving candidate (_v1); repoint after you pick
        b["storyboard_169"] = os.path.relpath(cands[0], folder)
json.dump(d, open(spec, "w"), ensure_ascii=False, indent=2)
print("recorded storyboard_169 for", sum(1 for b in d['beats'] if b.get('storyboard_169')), "beats")
PY
fi
echo; echo "done — $ok ok, $fail failed, $skip skipped.  Then: STILL_KEY=storyboard_169 ASPECT=16:9 W=1920 H=1080 generate_video_seedance.sh $FOLDER"
exit 0
