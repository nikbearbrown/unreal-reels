#!/usr/bin/env bash
# generate_videos.sh — STEP 2 of Songbird media: animate each kept keyframe into
# a clip (text+image -> video) with Minimax Hailuo. Sibling to generate_images.sh.
#
# For each beat it takes the kept still from gen/ (you pruned to one per beat) and
# that beat's video_prompt from media-jobs.json, runs minimax-2.3 with --image,
# and writes public/<slug>/media/<id>.mp4 — the file the overlay reads.
#
# Minimax does 6s or 10s only; beats are 5s, so a 6s clip is fine — the overlay's
# 5s slot just clips the last second.
#
# Usage:
#   ./generate_videos.sh                 # all beats that have a kept still
#   ./generate_videos.sh B09 B22         # only these
#   SRC=public/fishermans-wife/media ./generate_videos.sh   # animate picks already in media/
#   SHARD=1/3 ./generate_videos.sh       # run 3 in parallel (disjoint thirds)
#
# Env: VMODEL=minimax-2.3  VDUR=6  VRES=768  SRC=gen
#      MAX_RETRIES=3  RETRY_BASE=15  THROTTLE=2
#
# Requires: higgsfield CLI (authenticated), jq, curl.

set -uo pipefail
cd "$(dirname "$0")"
JOBS="media-jobs.json"
VMODEL="${VMODEL:-minimax-2.3}"
# NOTE: the CLI coerces numeric --duration/--resolution to JSON numbers, which the
# API rejects (it wants the strings "6"/"768"). Those are also the defaults, so we
# omit them by default (=> 6s, 768p). Only set VDUR/VRES if you must override, and
# expect a coercion error for non-default numeric values until the CLI is fixed.
VDUR="${VDUR:-}"; VRES="${VRES:-}"
SRC="${SRC:-gen}"
MAX_RETRIES="${MAX_RETRIES:-3}"; RETRY_BASE="${RETRY_BASE:-15}"; THROTTLE="${THROTTLE:-2}"
SHARD="${SHARD:-}"
if [ -n "$SHARD" ]; then SK_K="${SHARD%/*}"; SK_N="${SHARD#*/}"; else SK_K=1; SK_N=1; fi

for t in higgsfield jq curl; do command -v "$t" >/dev/null 2>&1 || { echo "missing: $t" >&2; exit 1; }; done
[ -f "$JOBS" ] || { echo "no $JOBS — run media_prompts.py first" >&2; exit 1; }
higgsfield account status >/dev/null 2>&1 || { echo "higgsfield not authenticated" >&2; exit 1; }

slug=$(jq -r '.slug // empty' src/media-manifest.json 2>/dev/null)
[ -z "$slug" ] && slug=$(basename "$PWD")
MEDIA="public/$slug/media"; mkdir -p "$MEDIA"
ONLY=("$@")
want() { [ ${#ONLY[@]} -eq 0 ] && return 0; for x in "${ONLY[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }
extract_url() {
  jq -r '[.. | strings | select(test("^https?://"))]
         | ( (map(select(test("\\.(mp4|mov|webm|m4v)($|\\?)"))) | .[0]) // .[0] // empty )' 2>/dev/null
}

count=$(jq '.jobs | length' "$JOBS")
echo "videos: scanning $count beats, stills from $SRC/, model $VMODEL ${VDUR:+dur=$VDUR }${VRES:+res=$VRES }(blank=defaults 6s/768p)${SHARD:+, shard $SHARD}"
ok=0; fail=0; skip=0
for i in $(seq 0 $((count-1))); do
  [ "$SK_N" -gt 1 ] && [ $(( i % SK_N )) -ne $(( SK_K - 1 )) ] && continue
  id=$(jq -r ".jobs[$i].id" "$JOBS"); want "$id" || continue
  out="$MEDIA/${id}.mp4"
  [ -s "$out" ] && { echo "$id: clip exists, skip"; skip=$((skip+1)); continue; }
  # find the kept still for this beat (Bxx.* or Bxx_v*.*, image only)
  still=$(ls "$SRC/${id}".* "$SRC/${id}_v"*.* 2>/dev/null | grep -viE '\.(mp4|mov|webm|err)$' | head -1)
  [ -z "$still" ] && { echo "$id: no still in $SRC/, skip"; skip=$((skip+1)); continue; }
  prompt=$(jq -r ".jobs[$i].video_prompt // .jobs[$i].prompt" "$JOBS")

  echo "=== $id  <- $(basename "$still") ==="
  args=(generate create minimax_hailuo --model "$VMODEL" --image "$still" --prompt "$prompt" --wait --json)
  [ -n "$VDUR" ] && args+=(--duration "$VDUR")
  [ -n "$VRES" ] && args+=(--resolution "$VRES")
  attempt=1; got=""
  while [ "$attempt" -le "$MAX_RETRIES" ]; do
    resp=$(higgsfield "${args[@]}" 2>&1); rc=$?
    if [ $rc -eq 0 ]; then
      url=$(printf '%s' "$resp" | extract_url)
      if [ -n "$url" ]; then
        if curl -fsSL "$url" -o "$out"; then echo "  -> $out"; got=1; ok=$((ok+1)); break
        else echo "  download failed ($url)"; fi
      else printf '%s' "$resp" > "$MEDIA/${id}.err"; echo "  no URL (saved ${id}.err)"; break; fi
    else
      printf '%s' "$resp" > "$MEDIA/${id}.err"; last=$(printf '%s' "$resp" | tail -n1)
      if printf '%s' "$resp" | grep -qiE "rate|429|busy|timeout|temporarily|try again|503|502"; then
        w=$((RETRY_BASE*attempt)); echo "  attempt $attempt transient: ${last:0:70} — wait ${w}s"; sleep "$w"
      else echo "  FAILED: ${last:0:120} (full -> $MEDIA/${id}.err)"; break; fi
    fi
    attempt=$((attempt+1))
  done
  [ -z "$got" ] && fail=$((fail+1))
  sleep "$THROTTLE"
done
echo; echo "videos done — $ok made, $skip skipped, $fail failed."
echo "now rebuild the overlay manifest:  ./rebuild_manifest.sh"
