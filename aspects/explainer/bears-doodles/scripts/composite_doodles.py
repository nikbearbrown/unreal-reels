#!/usr/bin/env python3
"""
composite_doodles.py — overlay the doodle clips onto the Manim render.

The Manim render is the full 16:9 master timeline (text, plot, markers, audio).
This pass overlays each `render: doodle` beat's clip into the marker region for that
beat's time window, keeping the Manim audio. Output: mp4/<slug>.mp4.

Per-beat source clip (in <video-folder>/mp4/):
  INTRO  -> doodle-INTRO.mp4   (already trimmed by build_intro.py)
  others -> src-<BEAT>.mp4     (trimmed here to the beat's narration length)

Timing is taken from mp3/timings.json — the SAME source the Manim scene used — so
the overlays line up with the rendered beats. Generate all audio (incl. the doodle
beats) and render Manim before running this.

Requires ffmpeg. Usage:
    python composite_doodles.py <video-folder>
    python composite_doodles.py <video-folder> --captions
    python composite_doodles.py <video-folder> --manim-mp4 path/to/BearsDoodlesVideo.mp4
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

OVERLAY_H = 680  # doodle height in px on a 1080-tall frame; clears intro text bands


def run(cmd):
    print("[ffmpeg]", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def find_manim(folder: Path):
    hits = sorted((folder / "media" / "videos").rglob("BearsDoodlesVideo.mp4"))
    return hits[-1] if hits else None


def beat_durations(folder: Path):
    tp = folder / "mp3" / "timings.json"
    return json.loads(tp.read_text()) if tp.exists() else {}


def srt_ts(s):
    h = int(s // 3600); m = int((s % 3600) // 60); sec = s % 60
    return f"{h:02}:{m:02}:{sec:06.3f}".replace(".", ",")


def main() -> int:
    ap = argparse.ArgumentParser(description="Overlay doodle clips onto the Manim render.")
    ap.add_argument("folder")
    ap.add_argument("--manim-mp4", default=None)
    ap.add_argument("--captions", action="store_true", help="burn narration captions (skips INTRO)")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    beats = sheet["beats"]
    slug = sheet["metadata"]["slug"]
    timings = beat_durations(folder)

    base = Path(args.manim_mp4) if args.manim_mp4 else find_manim(folder)
    if not base or not base.exists():
        print("[err] Manim render not found; render BearsDoodlesVideo first.", file=sys.stderr)
        return 1

    # cumulative start time per beat + collect doodle overlays
    overlays, t, missing = [], 0.0, []
    for b in beats:
        bid = b["beat_id"]
        dur = timings.get(bid) or b.get("actual_duration_s")
        if not dur:
            print(f"[err] no duration for beat {bid}; generate its audio first.", file=sys.stderr)
            return 2
        if b.get("render") == "doodle":
            src = folder / "mp4" / ("doodle-INTRO.mp4" if bid == "INTRO" else f"src-{bid}.mp4")
            if src.exists():
                overlays.append((src, float(t), float(dur)))
            else:
                missing.append(src.name)
        t += float(dur)

    if missing:
        print(f"[warn] missing doodle clips (skipped): {', '.join(missing)}")
    if not overlays:
        print("[err] no doodle clips found to composite.", file=sys.stderr)
        return 3

    # build filter_complex: trim+scale+time-shift each doodle, chain overlays
    inputs = ["-i", str(base)]
    parts, prev = [], "[0:v]"
    for i, (src, start, dur) in enumerate(overlays):
        inputs += ["-i", str(src)]
        idx = i + 1
        parts.append(
            f"[{idx}:v]trim=duration={dur:.3f},scale=-2:{OVERLAY_H},"
            f"setpts=PTS-STARTPTS+{start:.3f}/TB[d{i}]"
        )
        out = f"[v{i}]"
        parts.append(
            f"{prev}[d{i}]overlay=(W-w)/2:(H-h)/2:"
            f"enable='between(t,{start:.3f},{start + dur:.3f})'{out}"
        )
        prev = out

    filtergraph = ";".join(parts)
    out_dir = folder / "mp4"; out_dir.mkdir(exist_ok=True)
    final = out_dir / f"{slug}.mp4"

    cmd = ["ffmpeg", "-y", *inputs,
           "-filter_complex", filtergraph,
           "-map", prev, "-map", "0:a?",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
           str(final)]
    run(cmd)

    if args.captions:
        srt = out_dir / f"{slug}.srt"
        lines, tt, n = [], 0.0, 1
        for b in beats:
            d = timings.get(b["beat_id"]) or b.get("actual_duration_s") or 0
            if b["beat_id"] != "INTRO":
                txt = (b.get("narration_text") or "").replace("\n\n", " ").replace("\n", " ")
                lines.append(f"{n}\n{srt_ts(tt)} --> {srt_ts(tt + d)}\n{txt}\n")
                n += 1
            tt += d
        srt.write_text("\n".join(lines))
        capped = out_dir / f"{slug}-captioned.mp4"
        style = "FontName=Arial,FontSize=16,Alignment=2,MarginV=60,BorderStyle=1,Outline=2"
        run(["ffmpeg", "-y", "-i", str(final),
             "-vf", f"subtitles={srt.as_posix()}:force_style='{style}'",
             "-c:a", "copy", str(capped)])
        print(f"[ok] captioned -> {capped}")

    print(f"[ok] final -> {final}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
