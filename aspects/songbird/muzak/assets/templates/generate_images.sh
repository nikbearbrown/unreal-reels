#!/usr/bin/env bash
# generate_images.sh — STEP 1 of Songbird media: one keyframe image per beat,
# N generations each (you pick the best). Lives in the song folder, reads
# media-jobs.json (written by media_prompts.py).
#
# Cast (from media-jobs.json): man/woman -> Soul-ID model + that character's
# soul_id + anchor description; none -> nano_banana.
#
# Output: gen/<id>_v1.jpg ...  On error: gen/<id>_v<n>.err holds the raw output.
#
# Usage:
#   ./generate_images.sh                 # all beats
#   ./generate_images.sh B05 B11         # only these beats
#   DRY_RUN=1 ./generate_images.sh B05   # print the commands, generate nothing
#
# Env knobs:
#   MAX_RETRIES=3   RETRY_BASE=15   (seconds; backoff is RETRY_BASE*attempt)
#   THROTTLE=2      (seconds to wait between submissions, eases rate limits)
#
# Requires: higgsfield CLI (authenticated), jq, curl.

set -uo pipefail
cd "$(dirname "$0")"
JOBS="media-jobs.json"; GEN="gen"; mkdir -p "$GEN"
MAX_RETRIES="${MAX_RETRIES:-3}"; RETRY_BASE="${RETRY_BASE:-15}"; THROTTLE="${THROTTLE:-2}"
DRY_RUN="${DRY_RUN:-0}"
# SHARD="k/n" — run n copies in parallel, each handling every n-th beat (disjoint,
# no collisions). e.g. three terminals: SHARD=1/3, SHARD=2/3, SHARD=3/3.
SHARD="${SHARD:-}"
if [ -n "$SHARD" ]; then SK_K="${SHARD%/*}"; SK_N="${SHARD#*/}"; else SK_K=1; SK_N=1; fi

for t in higgsfield jq curl; do
  command -v "$t" >/dev/null 2>&1 || { echo "missing required tool: $t" >&2; exit 1; }
done
[ -f "$JOBS" ] || { echo "no $JOBS — run media_prompts.py first" >&2; exit 1; }

# fail fast on auth before burning a whole run
if [ "$DRY_RUN" != "1" ] && ! higgsfield account status >/dev/null 2>&1; then
  echo "higgsfield not authenticated — run: higgsfield auth login" >&2; exit 1
fi

VARIATIONS=$(jq -r '.variations // 3' "$JOBS")
ONLY=("$@")
want() { [ ${#ONLY[@]} -eq 0 ] && return 0; for x in "${ONLY[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

# pull the first http(s) URL from arbitrary JSON shape (object OR array OR nested),
# preferring a real media file extension.
extract_url() {
  jq -r '[.. | strings | select(test("^https?://"))]
         | ( (map(select(test("\\.(jpe?g|png|webp|mp4|mov|m4v)($|\\?)"))) | .[0]) // .[0] // empty )' 2>/dev/null
}

ok=0; fail=0
count=$(jq '.jobs | length' "$JOBS")
echo "media-jobs: $count beats, $VARIATIONS generations each (retries=$MAX_RETRIES, throttle=${THROTTLE}s)${SHARD:+, shard $SHARD}"

for i in $(seq 0 $((count - 1))); do
  # sharding: this instance only handles beats where (index % n) == k-1
  [ "$SK_N" -gt 1 ] && [ $(( i % SK_N )) -ne $(( SK_K - 1 )) ] && continue
  id=$(jq -r ".jobs[$i].id" "$JOBS"); want "$id" || continue
  model=$(jq -r ".jobs[$i].model" "$JOBS")
  soul=$(jq -r ".jobs[$i].soul_id // \"\"" "$JOBS")
  aspect=$(jq -r ".jobs[$i].aspect_ratio // \"16:9\"" "$JOBS")
  prompt=$(jq -r ".jobs[$i].prompt" "$JOBS")
  cast=$(jq -r ".jobs[$i].cast" "$JOBS")

  echo; echo "=== $id  [$cast -> $model${soul:+ soul:$soul}] ==="
  for v in $(seq 1 "$VARIATIONS"); do
    err="$GEN/${id}_v${v}.err"
    existing=$(ls "$GEN/${id}_v${v}".* 2>/dev/null | grep -vE '\.err$' | head -1)
    [ -n "$existing" ] && { echo "  v$v exists ($(basename "$existing")), skip"; continue; }

    args=(generate create "$model" --prompt "$prompt" --aspect_ratio "$aspect" --wait --json)
    [ -n "$soul" ] && args+=(--soul-id "$soul")

    if [ "$DRY_RUN" = "1" ]; then
      printf '  v%s DRY: higgsfield' "$v"; printf ' %q' "${args[@]}"; echo; continue
    fi

    attempt=1; got=""
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
      resp=$(higgsfield "${args[@]}" 2>&1); rc=$?
      if [ $rc -eq 0 ]; then
        url=$(printf '%s' "$resp" | extract_url)
        if [ -n "$url" ]; then
          tmp=$(mktemp)
          if curl -fsSL "$url" -o "$tmp"; then
            # name the file by its ACTUAL content type (Higgsfield returns PNG),
            # so Finder/Remotion read it correctly instead of a mislabeled .jpg.
            mime=$(file -b --mime-type "$tmp" 2>/dev/null)
            case "$mime" in
              image/png) ext=png;; image/jpeg) ext=jpg;; image/webp) ext=webp;;
              video/mp4|video/quicktime) ext=mp4;;
              *) ext="${url##*.}"; ext="${ext%%\?*}"; [ "${#ext}" -gt 5 ] && ext=png;;
            esac
            out="$GEN/${id}_v${v}.${ext}"
            mv "$tmp" "$out"; rm -f "$err"
            echo "  v$v -> $out"; got=1; ok=$((ok+1)); break
          else rm -f "$tmp"; echo "  v$v download failed ($url)"; fi
        else
          printf '%s' "$resp" > "$err"
          echo "  v$v no URL in response (saved $err)"; break   # not a rate issue; don't retry
        fi
      else
        printf '%s' "$resp" > "$err"
        last=$(printf '%s' "$resp" | tail -n1)
        # retry on transient/rate/timeout; stop on clear hard errors
        if printf '%s' "$resp" | grep -qiE "rate|429|busy|timeout|temporarily|try again|503|502"; then
          wait=$((RETRY_BASE * attempt))
          echo "  v$v attempt $attempt failed (rate/transient): ${last:0:80} — waiting ${wait}s"
          sleep "$wait"
        else
          echo "  v$v FAILED: ${last:0:120} (full -> $err)"; break
        fi
      fi
      attempt=$((attempt+1))
    done
    [ -z "$got" ] && fail=$((fail+1))
    sleep "$THROTTLE"
  done
done

echo; echo "done — $ok generated, $fail failed."
[ "$fail" -gt 0 ] && echo "inspect a failure: cat $GEN/<id>_v<n>.err"
echo "then: cp $GEN/B05_v2.png public/<slug>/media/B05.png  and add it to src/media-manifest.json"
