#!/usr/bin/env python3
"""
composite_clips.py — drop full-frame footage into a bio cut's clip beats.

For a "bio"-style video (alternating render:"clip" footage beats and render:"manim"
cards), this overlays each clip beat's Higgsfield mp4 FULL-FRAME onto the silent
Manim master, at that beat's time window (from mp3/timings.json). The card beats are
left as rendered. Output is still silent — run `assemble.py --mode manim` afterward
to mux Bear's narration.

Footage lookup per clip beat <ID>:  <folder>/clips/<ID>.mp4   (or mp4/beat-<ID>.mp4)
Missing footage → that beat keeps its Manim placeholder (partial composites are fine).

Each clip is trimmed to the beat length and scaled to COVER the frame (center-crop),
so aspect mismatches never letterbox.

Usage:
    python composite_clips.py path/to/<bio-folder>
    python composite_clips.py path/to/<bio-folder> --manim-mp4 media/.../BearsDoodlesVideo.mp4 --out mp4/_composited.mp4
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print("[ffmpeg]", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def dims(mp4: Path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(mp4)],
                       capture_output=True, text=True)
    w, h = r.stdout.strip().split("x")
    return int(w), int(h)


def find_master(folder: Path, portrait: bool = False):
    cands = sorted((folder / "media" / "videos").rglob("BearsDoodlesVideo.mp4"),
                   key=lambda p: p.stat().st_mtime)
    matched = []
    for c in cands:
        try:
            w, h = dims(c)
        except Exception:
            continue
        if (h > w) == portrait:
            matched.append(c)
    pool = matched or cands
    return pool[-1] if pool else None


def footage_for(folder: Path, bid: str):
    for p in (folder / "clips" / f"{bid}.mp4", folder / "mp4" / f"beat-{bid}.mp4"):
        if p.exists():
            return p
    return None


def main():
    ap = argparse.ArgumentParser(description="Overlay footage into bio clip beats.")
    ap.add_argument("folder")
    ap.add_argument("--manim-mp4", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--portrait", action="store_true",
                    help="target the 9:16 master; footage is scale-to-cover + CENTER-CROPPED to portrait")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    beats = sheet["beats"]
    timings = json.loads((folder / "mp3" / "timings.json").read_text()) if (folder / "mp3" / "timings.json").exists() else {}

    out_default = "mp4/_composited-short.mp4" if args.portrait else "mp4/_composited.mp4"
    args.out = args.out or out_default
    master = Path(args.manim_mp4) if args.manim_mp4 else find_master(folder, args.portrait)
    if not master or not master.exists():
        print("[err] Manim master not found — render the scene first.", file=sys.stderr)
        return 1
    W, H = dims(master)

    # cumulative start time per beat (beat order); collect clip overlays that have footage
    overlays, t, missing = [], 0.0, []
    for b in beats:
        bid = b["beat_id"]
        d = float(timings.get(bid, b.get("actual_duration_s", 4.0)))
        if b.get("render") == "clip":
            f = footage_for(folder, bid)
            if f:
                overlays.append((f, t, d))
            else:
                missing.append(bid)
        t += d

    if not overlays:
        print(f"[composite] no footage found (looked in clips/ and mp4/). "
              f"Place <beat>.mp4 in {folder/'clips'}. Missing: {missing}")
        return 0

    out = folder / args.out
    out.parent.mkdir(exist_ok=True)
    inputs = ["-i", str(master)]
    for f, _, _ in overlays:
        inputs += ["-i", str(f)]

    parts, prev = [], "[0:v]"
    for i, (f, start, d) in enumerate(overlays, start=1):
        end = start + d
        # Normalize → cover-scale → FREEZE last frame to fill the window if the clip
        # is shorter than the narration (tpad clone) → trim to exactly the beat length
        # → shift to the beat's start time. Longer clips are simply trimmed.
        parts.append(
            f"[{i}:v]setpts=PTS-STARTPTS,"
            f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"tpad=stop_mode=clone:stop_duration={d:.3f},"
            f"trim=duration={d:.3f},setpts=PTS+{start:.3f}/TB[c{i}];")
        parts.append(f"{prev}[c{i}]overlay=0:0:enable='between(t,{start:.3f},{end:.3f})'[v{i}];")
        prev = f"[v{i}]"
    filt = "".join(parts)
    if filt.endswith(";"):
        filt = filt[:-1]
    last = prev.strip("[]")

    run(["ffmpeg", "-y", *inputs, "-filter_complex", filt, "-map", f"[{last}]",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", str(out)])
    print(f"[ok] composited → {out}")
    if missing:
        print(f"[note] still placeholders (no footage yet): {missing}")
    print("[next] assemble: python ../../bears-doodles/scripts/assemble.py . --mode manim "
          f"--manim-mp4 {out.relative_to(folder)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
