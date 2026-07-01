#!/usr/bin/env bash
# extract_frames.sh — pull frames from a source video at a low fps so a frame's
# index ~= its second in the song. lyric-match's pick_stills.py relies on that.
#
#   <video>      the source music video (mp4/mov/...)
#   <out_dir>    where the PNG frames are written (usually the reel folder)
#   [FPS]        frames per second to extract (default 1)
#   [PREFIX]     filename prefix (default: the video basename)
#
# Output: <out_dir>/<PREFIX>_frame_000001.png ...  (numbered from 1; index ~= second*FPS)
#
# Usage:
#   ./extract_frames.sh "song.mp4" reels/my-reel
#   ./extract_frames.sh "song.mp4" reels/my-reel 1 my-reel
#
# Requires: ffmpeg.
set -euo pipefail
VIDEO="${1:?usage: extract_frames.sh <video> <out_dir> [FPS] [PREFIX]}"
OUT="${2:?usage: extract_frames.sh <video> <out_dir> [FPS] [PREFIX]}"
FPS="${3:-1}"
[ -f "$VIDEO" ] || { echo "no such video: $VIDEO" >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo "missing: ffmpeg" >&2; exit 1; }

base="$(basename "$VIDEO")"; base="${base%.*}"
PREFIX="${4:-$base}"
mkdir -p "$OUT"

echo "extracting frames at ${FPS} fps -> $OUT/${PREFIX}_frame_%06d.png"
ffmpeg -loglevel error -y -i "$VIDEO" -vf "fps=${FPS}" "$OUT/${PREFIX}_frame_%06d.png"
n=$(ls -1 "$OUT/${PREFIX}_frame_"*.png 2>/dev/null | wc -l | tr -d ' ')
echo "wrote $n frames."
echo "note: blurry/duplicate frames can be deleted by hand; pick_stills.py keeps the"
echo "      sharpest remaining frame inside each beat's time window."
