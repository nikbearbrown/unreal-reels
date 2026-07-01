#!/usr/bin/env bash
# generate_video_songbird.sh — per-beat image->video for a Songbird beat_sheet.json
# via Higgsfield Minimax Hailuo, each clip CUT to its exact beat duration, then
# (optionally) concatenated with the original WAV into one song-length film.
#
#   video/raw/<beat_id>.mp4   the raw Minimax clip (model's native length)
#   video/<beat_id>.mp4       normalized 1920x1080@30 and cut to beat duration
#   <slug>.silent.mp4         all beats concatenated (FINAL=1)
#   <slug>.mp4                concatenated + original audio muxed (FINAL=1)
#
# Each beat uses beat.chosen_still as --image and beat.video_prompt as --prompt.
# (Minimax Hailuo takes a single --image; no audio/video is sent to the model — the
#  WAV is only muxed locally by ffmpeg in the optional FINAL concat step.)
# Clips longer than the beat are trimmed; clips shorter hold their last frame to fill
# (the audio is the master clock — beats tile the whole song with no gaps).
#
# Usage:
#   ./generate_video_songbird.sh <reel_folder>                 # all beats, clips only
#   ./generate_video_songbird.sh <reel_folder> B03 B07         # specific beats
#   FINAL=1   ./generate_video_songbird.sh <reel_folder>       # also concat + mux audio
#   DRY_RUN=1 ...                                              # print commands only
#   MODEL=minimax_hailuo  EXTRA_ARGS="--duration 6"            # see: higgsfield model get minimax_hailuo
#
# Requires: jq, curl, ffmpeg, ffprobe, and (unless DRY_RUN) an authenticated higgsfield CLI.

set -uo pipefail
FOLDER="${1:?usage: generate_video_songbird.sh <reel_folder> [BEAT_ID...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq curl ffmpeg ffprobe; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

DRY_RUN="${DRY_RUN:-0}"
MODEL="${MODEL:-minimax_hailuo}"
EXTRA_ARGS="${EXTRA_ARGS:-}"
W="${W:-1920}"; H="${H:-1080}"; FPS="${FPS:-30}"
STILL_KEY="${STILL_KEY:-chosen_still}"     # which beat field holds the --image still
TAG="${TAG:-}"                              # output suffix (e.g. vertical) so renders don't clobber
MAX_RETRIES="${MAX_RETRIES:-4}"; RETRY_BASE="${RETRY_BASE:-20}"; THROTTLE="${THROTTLE:-2}"
OUT="$FOLDER/video${TAG:+-$TAG}"; RAW="$OUT/raw"; mkdir -p "$RAW" "$OUT"

if [ "$DRY_RUN" != 1 ]; then
  command -v higgsfield >/dev/null || { echo "missing: higgsfield (or DRY_RUN=1)" >&2; exit 1; }
  higgsfield account status >/dev/null 2>&1 || { echo "higgsfield not authenticated — run: higgsfield auth login" >&2; exit 1; }
fi

declare -a PICK=("$@")
want(){ [ ${#PICK[@]} -eq 0 ] && return 0; for x in "${PICK[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }
abspath(){ case "$1" in /*) printf '%s' "$1";; *) printf '%s/%s' "$FOLDER" "$1";; esac; }

ok=0; skip=0; fail=0
n=$(jq '.beats | length' "$SPEC")
DRYLABEL=""; [ "$DRY_RUN" = 1 ] && DRYLABEL="  (DRY_RUN)"
echo "songbird video: $FOLDER  $MODEL -> cut-to-beat ${W}x${H}@${FPS}${DRYLABEL}"

for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC"); want "$bid" || continue
  dur=$(jq -r ".beats[$i].duration_s" "$SPEC")
  still=$(jq -r ".beats[$i].${STILL_KEY} // .beats[$i].chosen_still // empty" "$SPEC")
  vp=$(jq -r ".beats[$i].video_prompt // .beats[$i].image_prompt" "$SPEC")
  [ -z "$still" ] && { echo "=== $bid — no chosen_still, skip ==="; skip=$((skip+1)); continue; }
  stillp=$(abspath "$still")
  [ -f "$stillp" ] || { echo "=== $bid — still missing: $stillp ==="; fail=$((fail+1)); continue; }
  rawf="$RAW/$bid.mp4"; outf="$OUT/$bid.mp4"
  echo; echo "=== $bid  dur=${dur}s  still=$(basename "$stillp") ==="

  # 1) generate the raw clip (skip if present)
  if [ ! -f "$rawf" ]; then
    args=(generate create "$MODEL" --prompt "$vp" --image "$stillp" $EXTRA_ARGS --wait --json)
    if [ "$DRY_RUN" = 1 ]; then printf '  gen -> %s\n    higgsfield' "$rawf"; printf ' %q' "${args[@]}"; echo;
    else
      attempt=1; got=""
      while [ "$attempt" -le "$MAX_RETRIES" ]; do
        resp=$(higgsfield "${args[@]}" 2>&1)
        url=$(printf '%s' "$resp" | jq -r '.[].result_url // empty' 2>/dev/null | head -1)
        if [ -n "$url" ] && curl -fsSL "$url" -o "$rawf"; then echo "  raw -> $rawf"; got=1; break; fi
        printf '%s' "$resp" > "$RAW/$bid.err"
        if printf '%s' "$resp" | grep -qiE "rate|429|busy|timeout|temporarily|try again|concurrent|503|502"; then
          wsec=$((RETRY_BASE*attempt)); echo "  transient — wait ${wsec}s ($attempt/$MAX_RETRIES)"; sleep "$wsec"
        else echo "  GEN FAILED: $(printf '%s' "$resp" | tail -1 | cut -c1-120)"; break; fi
        attempt=$((attempt+1))
      done
      [ -z "$got" ] && { fail=$((fail+1)); sleep "$THROTTLE"; continue; }
      sleep "$THROTTLE"
    fi
  else echo "  raw exists, reuse"; fi

  # 2) normalize + cut to the EXACT beat duration. CENTER-trim a longer clip (shave
  #    both ends so the strongest motion sits in the middle); only freeze-pad the tail
  #    if the raw clip is actually shorter than the beat (shouldn't happen at 10s).
  base="scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},fps=${FPS}"
  if [ "$DRY_RUN" = 1 ]; then
    printf '  cut -> %s\n    ffmpeg -ss <center> -i %q -vf %q -t %s -an -c:v libx264 ... %q\n' "$outf" "$rawf" "$base" "$dur" "$outf"; ok=$((ok+1)); continue
  fi
  RD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$rawf" 2>/dev/null); [ -z "$RD" ] && RD=0
  read -r START PAD < <(awk -v rd="$RD" -v d="$dur" 'BEGIN{ if(rd+0>=d+0){printf "%.3f 0\n",(rd-d)/2} else {printf "0 %.3f\n",d-rd} }')
  vf="$base"
  awk -v p="$PAD" 'BEGIN{exit !(p+0>0)}' && vf="$base,tpad=stop_mode=clone:stop_duration=$PAD"
  if ffmpeg -loglevel error -y -ss "$START" -i "$rawf" -vf "$vf" -t "$dur" -an -c:v libx264 -pix_fmt yuv420p -r "$FPS" "$outf"; then
    note=$(awk -v p="$PAD" -v rd="$RD" 'BEGIN{print (p+0>0)?"FREEZE-PAD "p"s (raw "rd"s < beat)":"center-trim of "rd"s"}')
    echo "  cut -> $outf  ${dur}s  [$note]"; ok=$((ok+1))
  else echo "  CUT FAILED $bid"; fail=$((fail+1)); fi
done

# 3) optional: concat in beat order + mux original audio
if [ "${FINAL:-0}" = 1 ]; then
  slug=$(jq -r '.metadata.slug' "$SPEC"); audio=$(abspath "$(jq -r '.metadata.audio_file' "$SPEC")")
  list="$OUT/_concat.txt"; : > "$list"
  for bid in $(jq -r '.beats[].beat_id' "$SPEC"); do [ -f "$OUT/$bid.mp4" ] && echo "file '$OUT/$bid.mp4'" >> "$list"; done
  silent="$FOLDER/$slug${TAG:+.$TAG}.silent.mp4"; final="$FOLDER/$slug${TAG:+.$TAG}.mp4"
  if [ "$DRY_RUN" = 1 ]; then
    echo; echo "FINAL (dry):"
    echo "  ffmpeg -f concat -safe 0 -i $list -c:v libx264 -pix_fmt yuv420p -r $FPS $silent"
    echo "  ffmpeg -i $silent -i $audio -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest $final"
  else
    echo; echo "=== concat + audio ==="
    [ -f "$audio" ] || echo "  !! audio file missing: $audio" >&2
    ffmpeg -loglevel error -y -f concat -safe 0 -i "$list" -c:v libx264 -pix_fmt yuv420p -r "$FPS" "$silent" \
      || { echo "  CONCAT FAILED" >&2; }
    ffmpeg -loglevel error -y -i "$silent" -i "$audio" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest "$final" \
      || { echo "  MUX FAILED" >&2; }
    if [ -f "$final" ] && ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 "$final" 2>/dev/null | grep -q audio; then
      vd=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$final")
      echo "  final -> $final   audio: OK   duration: ${vd}s"
    else
      echo "  !! final has NO audio stream — check that $audio exists and is valid" >&2
    fi
  fi
fi

echo; echo "done — $ok clips, $fail failed, $skip skipped."
[ "$fail" -gt 0 ] && echo "failures saved as .err in video/raw/; re-run reuses finished raw clips."
exit 0
