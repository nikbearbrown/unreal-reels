#!/usr/bin/env python3
"""
build_intro.py — prep a doodle clip for compositing.

Manim now renders the intro TEXT (brand + title) and the marker box, so this
script's job is just to prepare the doodle CLIP that gets composited over a marker:
it picks a random clip from the shared bear-intro pool, copies it into the project's
own mp4/, and trims it to the beat's voiceover length so the clip matches the
narration. Output: <video-folder>/mp4/doodle-<BEAT>.mp4 (video only — the Manim
render already carries the voiceover).

The pool is a SERIES asset at <Manim>/shared/bear-intros/. Drop raw clips there and
use --ingest to renumber them into the pool (bear-intro-05.mp4, ...); existing
word-named clips (bear-intro-one..four) are kept.

Requires ffmpeg on PATH. Audio (timings) must exist first — run generate_audio.py.

Usage:
    python build_intro.py <video-folder>
    python build_intro.py <video-folder> --ingest "shared/bear-intros/*_720_N.mp4"
    python build_intro.py <video-folder> --beat INTRO --seed 1
"""
import argparse
import glob
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print("[ffmpeg]", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def ingest(intros_dir: Path, patterns):
    intros_dir.mkdir(parents=True, exist_ok=True)
    n = len(list(intros_dir.glob("bear-intro-*.mp4"))) + 1
    for pat in patterns:
        for src in sorted(glob.glob(pat)):
            if Path(src).name.startswith("bear-intro-"):
                continue  # already in the pool
            dst = intros_dir / f"bear-intro-{n:02d}.mp4"
            shutil.copy2(src, dst)
            print(f"[ingest] {Path(src).name} -> {dst.name}")
            n += 1
    print(f"[ingest] pool now: {len(list(intros_dir.glob('bear-intro-*.mp4')))} clips")


def beat_duration(folder: Path, beat_id: str):
    tp = folder / "mp3" / "timings.json"
    if tp.exists():
        t = json.loads(tp.read_text())
        if beat_id in t:
            return float(t[beat_id])
    for b in json.loads((folder / "beat_sheet.json").read_text())["beats"]:
        if b["beat_id"] == beat_id and b.get("actual_duration_s"):
            return float(b["actual_duration_s"])
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Prep a trimmed doodle clip for compositing.")
    ap.add_argument("folder")
    ap.add_argument("--beat", default="INTRO", help="beat id to prep a clip for (default INTRO)")
    ap.add_argument("--ingest", nargs="*", default=None, help="glob(s) of raw clips to add to the pool first")
    ap.add_argument("--seed", type=int, default=None, help="seed the random pick (reproducible)")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    intros_dir = folder.parent / "shared" / "bear-intros"
    if args.ingest:
        ingest(intros_dir, args.ingest)

    pool = sorted(intros_dir.glob("bear-intro-*.mp4"))
    if not pool:
        print(f"[err] no clips in {intros_dir}", file=sys.stderr)
        return 1

    dur = beat_duration(folder, args.beat)
    if not dur:
        print(f"[err] no audio duration for beat {args.beat}; run generate_audio.py first.", file=sys.stderr)
        return 2

    if args.seed is not None:
        random.seed(args.seed)
    pick = random.choice(pool)
    out = folder / "mp4" / f"doodle-{args.beat}.mp4"
    out.parent.mkdir(exist_ok=True)
    print(f"[pick] {pick.name} -> {out.name}  (trim to {dur:.2f}s, video only)")

    # trim to the voiceover length; strip audio (Manim render carries the narration)
    run(["ffmpeg", "-y", "-i", str(pick), "-t", f"{dur:.3f}", "-an",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)])
    print(f"[ok] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
