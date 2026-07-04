#!/usr/bin/env python3
"""
short_guard.py — enforce the YouTube Shorts 3-minute hard limit for the 9:16 cut.

The 9:16 Short must be STRICTLY under 3:00. This gate is checked on the audio
total (the master clock: sum of every beat's actual_duration_s), BEFORE any
portrait render or caption burn — so you never spend a render on a Short that
can't be posted, and you never caption one either.

  exit 0  → total < limit; safe to render the 9:16 (and later its -caption).
  exit 2  → total >= limit; DO NOT render the Short. Author a shortened beat
            sheet (e.g. beat_sheet.short.json) that gets under 3:00 — cut scope,
            not clarity (fewer instances / merge the scale beats), regenerate its
            audio, and re-run this guard against that sheet.

Two checks:
  • pre-render (cheap): audio total from beat_sheet.json — catch over-limit
    before wasting a portrait render.
  • post-render (authoritative): --probe <mp4> ffprobes the RENDERED non-caption
    Short's real duration, which is what actually gets uploaded. Only caption a
    Short that passes this.

The 16:9 long-form has NO such limit; this guard is portrait-only.

Usage:
    python short_guard.py <folder> [--limit 180] [--sheet beat_sheet.json]
    python short_guard.py <folder> --probe mp4/<slug>-short.mp4      # measure the rendered file
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def probe_seconds(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffprobe failed on {path}: {r.stderr.strip()}")
    return float(r.stdout.strip())


def total_seconds(sheet):
    beats = sheet.get("beats", [])
    have = [float(b.get("actual_duration_s", 0.0)) for b in beats]
    if any(v > 0 for v in have):
        return sum(have)
    # no measured audio yet — fall back to the metadata estimate
    return float(sheet.get("metadata", {}).get("total_estimated_duration_seconds", 0.0))


def fmt(s):
    m, sec = divmod(s, 60)
    return f"{int(m)}:{sec:05.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--limit", type=float, default=180.0, help="hard limit in seconds (Shorts = 180)")
    ap.add_argument("--sheet", default="beat_sheet.json")
    ap.add_argument("--probe", default=None, help="ffprobe this rendered mp4 instead of summing audio")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()

    if args.probe:
        p = Path(args.probe)
        if not p.is_absolute():
            p = folder / p
        if not p.exists():
            sys.exit(f"short_guard: --probe file not found: {p}")
        total = probe_seconds(p)
        source = f"rendered {p.name}"
    else:
        sheet = json.loads((folder / args.sheet).read_text())
        total = total_seconds(sheet)
        source = "audio total"

    if total <= 0:
        sys.exit("short_guard: no durations found (run generate_audio.py first).")

    if total < args.limit:
        margin = args.limit - total
        flag = "  ⚠ within 3s of the limit" if margin < 3 else ""
        nxt = "safe to caption the Short." if args.probe else "safe to render 9:16."
        print(f"[ok] Short duration {fmt(total)} < 3:00 ({source}) — {nxt}{flag}")
        sys.exit(0)

    over = total - args.limit
    print(
        f"[BLOCKED] Short duration {fmt(total)} ≥ 3:00 (over by {over:.1f}s).\n"
        f"YouTube Shorts hard-limits at 3 minutes. Do NOT render the 9:16 from\n"
        f"this beat sheet. Author a shortened beat sheet (beat_sheet.short.json)\n"
        f"under 3:00 — cut scope not clarity, regenerate its audio, re-run this\n"
        f"guard against it. The 16:9 long-form is unaffected.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
