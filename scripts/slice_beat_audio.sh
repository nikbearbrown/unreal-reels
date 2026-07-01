#!/usr/bin/env bash
# slice_beat_audio.sh — cut the master audio into one clip per beat, so an
# audio-aware video model (e.g. Higgsfield seedance_2_0, which takes --audio)
# can lock each beat's motion to its own slice of the song. Beats are already
# <=15s (the Seedance audio cap), so the beat sheet IS the chunking.
#
#   audio/<beat_id>.wav   the beat's [start_s, end_s) slice of metadata.audio_file
#
# Usage:
#   ./slice_beat_audio.sh <reel_folder>                 # all beats
#   ./slice_beat_audio.sh <reel_folder> B03 B07         # specific beats
#   DRY_RUN=1 ...                                        # print ffmpeg commands only
#   EXT=mp3 ...                                          # output mp3 instead of wav
#
# Requires: jq, ffmpeg.
set -uo pipefail
FOLDER="${1:?usage: slice_beat_audio.sh <reel_folder> [BEAT_ID...]}"; shift || true
SPEC="$FOLDER/beat_sheet.json"
[ -f "$SPEC" ] || { echo "no beat_sheet.json in $FOLDER" >&2; exit 1; }
for t in jq ffmpeg; do command -v "$t" >/dev/null || { echo "missing: $t" >&2; exit 1; }; done

DRY_RUN="${DRY_RUN:-0}"; EXT="${EXT:-wav}"
abspath(){ case "$1" in /*) printf '%s' "$1";; *) printf '%s/%s' "$FOLDER" "$1";; esac; }
audio=$(abspath "$(jq -r '.metadata.audio_file' "$SPEC")")
[ -f "$audio" ] || { echo "audio file missing: $audio" >&2; exit 1; }
OUT="$FOLDER/audio"; mkdir -p "$OUT"

declare -a PICK=("$@")
want(){ [ ${#PICK[@]} -eq 0 ] && return 0; for x in "${PICK[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

n=$(jq '.beats | length' "$SPEC"); ok=0
echo "slice audio: $(basename "$audio") -> audio/<beat>.$EXT  ($n beats)$([ "$DRY_RUN" = 1 ] && echo '  (DRY_RUN)')"
for i in $(seq 0 $((n-1))); do
  bid=$(jq -r ".beats[$i].beat_id" "$SPEC"); want "$bid" || continue
  ss=$(jq -r ".beats[$i].start_s" "$SPEC"); dur=$(jq -r ".beats[$i].duration_s" "$SPEC")
  out="$OUT/$bid.$EXT"
  if [ "$DRY_RUN" = 1 ]; then
    echo "  ffmpeg -ss $ss -t $dur -i <audio> -ac 2 $out"; ok=$((ok+1)); continue
  fi
  if [ "$EXT" = wav ]; then enc=(-c:a pcm_s16le); else enc=(-c:a libmp3lame -q:a 2); fi
  if ffmpeg -loglevel error -y -ss "$ss" -t "$dur" -i "$audio" -ac 2 "${enc[@]}" "$out"; then
    ok=$((ok+1))
  else echo "  FAILED $bid" >&2; fi
done
echo "done — $ok beat audio clips in $OUT"
