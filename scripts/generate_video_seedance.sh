#!/usr/bin/env bash
# generate_video_seedance.sh — per-beat image+audio -> video for a DANCE beat_sheet.json
# via Higgsfield Seedance 2.0. Each beat: --image chosen_still + --audio audio_slice
# (drives ON-BEAT motion) + --prompt video_prompt, --duration = beat length (<=15s),
# generate_audio=false (clips are silent; the master WAV is muxed at assembly).
#
#   video/raw/<beat_id>.mp4   raw Seedance clip
#   video/<beat_id>.mp4       normalized WxH and trimmed to the exact beat duration
#   <slug>.silent.mp4 / <slug>.mp4   (FINAL=1) concat + master audio muxed
#
# Usage:
#   ./generate_video_seedance.sh <reel_folder>                 # all beats
#   ./generate_video_seedance.sh <reel_folder> B01             # one beat (test the beat-match first!)
#   DRY_RUN=1 ...                       # print commands only
#   FINAL=1 ...                         # also concat + mux the master WAV
#   RES=1080p  SMODE=std  GENRE=auto  W=1080 H=1920            # overrides
#
# Requires: jq, curl, ffmpeg, ffprobe, and (unless DRY_RUN) an authenticated higgsfield CLI
# with the model registered:  higgsfield model get seedance_2_0
set -uo pipefail
FOLDER="${1:?usage: generate_video_seedance.sh <reel_folder> [BEAT_ID...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl ffmpeg ffprobe; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

DRY_RUN="${DRY_RUN:-0}"; MODEL="${MODEL:-seedance_2_0}"
RES="${RES:-1080p}"; SMODE="${SMODE:-std}"; GENRE="${GENRE:-auto}"
ASPECT="${ASPECT:-$(jq -r '.metadata.aspect_ratio // "9:16"' "$SPEC")}"
W="${W:-1080}"; H="${H:-1920}"; FPS="${FPS:-30}"
MAX_RETRIES="${MAX_RETRIES:-4}"; RETRY_BASE="${RETRY_BASE:-20}"; THROTTLE="${THROTTLE:-3}"
PREVIEW="${PREVIEW:-0}"   # 1 = also write <beat>_preview.mp4 with the beat's audio muxed (for judging beat-match)
TAG="${TAG:-}"            # output suffix (e.g. vertical) so a 9:16 render doesn't clobber the 16:9 one
STILL_KEY="${STILL_KEY:-chosen_still}"   # beat field for the --image still (e.g. storyboard_169 for FLUX 16:9 stills)
ASSEMBLE_ONLY="${ASSEMBLE_ONLY:-0}"      # 1 = don't generate; just cut the clips you dropped in video/raw/<beat>.mp4 and assemble
OUT="$FOLDER/video${TAG:+-$TAG}"; RAW="$OUT/raw"; mkdir -p "$RAW" "$OUT"

if [ "$DRY_RUN" != 1 ]; then
  command -v higgsfield >/dev/null || { echo "missing: higgsfield (or DRY_RUN=1)" >&2; exit 1; }
  higgsfield account status >/dev/null 2>&1 || { echo "higgsfield not authenticated" >&2; exit 1; }
fi
abspath(){ case "$1" in /*) printf '%s' "$1";; *) printf '%s/%s' "$FOLDER" "$1";; esac; }
declare -a PICK=("$@")
want(){ [ ${#PICK[@]} -eq 0 ] && return 0; for x in "${PICK[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

ok=0; skip=0; fail=0
n=$(jq '.beats | length' "$SPEC")
echo "seedance dance: $FOLDER  $MODEL  ${ASPECT} ${RES} -> cut-to-beat ${W}x${H}$([ "$DRY_RUN" = 1 ] && echo '  (DRY_RUN)')"

for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC"); want "$bid" || continue
  dur=$(jq -r ".beats[$i].duration_s" "$SPEC")
  still=$(abspath "$(jq -r ".beats[$i].${STILL_KEY} // .beats[$i].chosen_still" "$SPEC")")
  audio=$(abspath "$(jq -r ".beats[$i].audio_slice // empty" "$SPEC")")
  vp=$(jq -r ".beats[$i].video_prompt" "$SPEC")
  durint=$(awk -v d="$dur" 'BEGIN{x=int(d); if(x<d)x=x+1; if(x>15)x=15; if(x<1)x=1; print x}')
  [ "$ASSEMBLE_ONLY" = 1 ] || [ -f "$still" ] || { echo "=== $bid still missing: $still ==="; fail=$((fail+1)); continue; }
  rawf="$RAW/$bid.mp4"; outf="$OUT/$bid.mp4"
  echo; echo "=== $bid  beat=${dur}s  req=${durint}s  still=$(basename "$still")  audio=$(basename "${audio:-none}") ==="

  if [ "$ASSEMBLE_ONLY" = 1 ]; then
    [ -f "$rawf" ] || { echo "  no clip at video/raw/$bid.mp4 — drop your web-generated clip there; skipping"; skip=$((skip+1)); continue; }
    echo "  using dropped clip $rawf"
  elif [ ! -f "$rawf" ]; then
    args=(generate create "$MODEL" --prompt "$vp" --image "$still"
          --duration "$durint" --aspect_ratio "$ASPECT" --resolution "$RES"
          --generate_audio false --mode "$SMODE" --genre "$GENRE")
    [ -n "$audio" ] && [ -f "$audio" ] && args+=(--audio "$audio")
    args+=(--wait --json)
    if [ "$DRY_RUN" = 1 ]; then printf '  gen -> %s\n    higgsfield' "$rawf"; printf ' %q' "${args[@]}"; echo; ok=$((ok+1)); continue; fi
    attempt=1; got=""
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
      resp=$(higgsfield "${args[@]}" 2>&1)
      url=$(printf '%s' "$resp" | jq -r '.[].result_url // empty' 2>/dev/null | head -1)
      if [ -n "$url" ] && curl -fsSL "$url" -o "$rawf"; then echo "  raw -> $rawf"; got=1; break; fi
      printf '%s' "$resp" > "$RAW/$bid.err"
      if printf '%s' "$resp" | grep -qiE "rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
        wsec=$((RETRY_BASE*attempt)); echo "  transient — wait ${wsec}s ($attempt/$MAX_RETRIES)"; sleep "$wsec"
      else echo "  GEN FAILED: $(printf '%s' "$resp" | tail -1 | cut -c1-140)"; break; fi
      attempt=$((attempt+1))
    done
    [ -z "$got" ] && { fail=$((fail+1)); sleep "$THROTTLE"; continue; }
    sleep "$THROTTLE"
  else echo "  raw exists, reuse"; fi

  [ "$DRY_RUN" = 1 ] && { ok=$((ok+1)); continue; }
  # fit the clip to the EXACT beat duration (clips silent; audio muxed at FINAL):
  #   raw shorter than beat (e.g. 5s Kling clip in a 5.8s beat) -> time-stretch to fill (no freeze)
  #   raw longer  than beat (e.g. 10/15s Seedance clip)          -> center-trim
  base="scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H}"
  RD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$rawf" 2>/dev/null); [ -z "$RD" ] && RD="$dur"
  if awk -v rd="$RD" -v d="$dur" 'BEGIN{exit !(rd < d-0.05)}'; then
    factor=$(awk -v rd="$RD" -v d="$dur" 'BEGIN{printf "%.5f", d/rd}')
    vf="${base},setpts=${factor}*PTS,fps=${FPS}"; ss=""; mode="stretch x${factor} (raw ${RD}s)"
  else
    START=$(awk -v rd="$RD" -v d="$dur" 'BEGIN{printf "%.3f",(rd-d)/2}')
    vf="${base},fps=${FPS}"; ss="-ss $START"; mode="center-trim (raw ${RD}s)"
  fi
  if ffmpeg -loglevel error -y $ss -i "$rawf" -vf "$vf" -t "$dur" -an -c:v libx264 -pix_fmt yuv420p -r "$FPS" "$outf"; then
    echo "  cut -> $outf  ${dur}s  [$mode]"; ok=$((ok+1))
    if [ "$PREVIEW" = 1 ] && [ -n "$audio" ] && [ -f "$audio" ]; then
      pv="$OUT/${bid}_preview.mp4"
      if ffmpeg -loglevel error -y -i "$outf" -i "$audio" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest "$pv"; then
        echo "  preview -> $pv  (dance + its music, for judging beat-match)"
      fi
    fi
  else echo "  CUT FAILED $bid"; fail=$((fail+1)); fi
done

if [ "${FINAL:-0}" = 1 ]; then
  slug=$(jq -r '.metadata.slug' "$SPEC"); audio=$(abspath "$(jq -r '.metadata.audio_file' "$SPEC")")
  list="$OUT/_concat.txt"; : > "$list"; missing=""
  for bid in $(jq -r '.beats[].beat_id' "$SPEC"); do
    if [ -f "$OUT/$bid.mp4" ]; then echo "file '$OUT/$bid.mp4'" >> "$list"; else missing="$missing $bid"; fi
  done
  if [ -n "$missing" ]; then
    echo "  !! MISSING beat clips:$missing — the song would be cut short. Generate them first:" >&2
    echo "     STILL_KEY=$STILL_KEY ASPECT=$ASPECT W=$W H=$H $0 $FOLDER$missing" >&2
    echo "     (skipping concat/mux to avoid a truncated video)" >&2
  fi
  silent="$FOLDER/$slug${TAG:+.$TAG}.silent.mp4"; final="$FOLDER/$slug${TAG:+.$TAG}.mp4"
  if [ "$DRY_RUN" = 1 ]; then echo; echo "FINAL (dry): concat -> $silent ; mux $audio -> $final"
  elif [ -n "$missing" ]; then echo "  concat/mux skipped (missing clips above)." >&2
  else
    echo; echo "=== concat + master audio ==="
    ffmpeg -loglevel error -y -f concat -safe 0 -i "$list" -c:v libx264 -pix_fmt yuv420p -r "$FPS" "$silent" || echo "  CONCAT FAILED" >&2
    ffmpeg -loglevel error -y -i "$silent" -i "$audio" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest "$final" || echo "  MUX FAILED" >&2
    vd=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$final" 2>/dev/null)
    ad=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$audio" 2>/dev/null)
    [ -f "$final" ] && echo "  final -> $final  (video ${vd}s vs audio ${ad}s)"
  fi
fi
echo; echo "done — $ok ok, $fail failed, $skip skipped."
exit 0
