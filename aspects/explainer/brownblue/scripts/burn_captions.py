#!/usr/bin/env python3
"""
burn_captions.py — Brown Blue karaoke caption cut.

Turns the APPROVED clean master into the captioned version, ending in
`-caption.mp4`. Pure ffmpeg + libass — no Remotion project to stand up.

Pipeline:
  1. (you first run) deck-lecture/scripts/align_captions.py <folder>
     → <folder>/captions.json  (per-beat, word-level, beat-local frames)
  2. this script reads beat_sheet.json (beat order + actual_duration_s) to turn
     beat-local word frames into ABSOLUTE times, writes an .ass karaoke track,
     and burns it onto the input mp4.

Karaoke look (brownblue style): EB Garamond, upcoming words in --ink, each word
lighting to --highlight as it is spoken, sitting in the lower safe band so it
never covers the active Manim element. Captions DISPLAY narration_text (correct
spelling), never the tts respelling — align_captions already guarantees this.

Usage:
    python burn_captions.py <folder> --input mp4/<slug>.mp4              # 16:9
    python burn_captions.py <folder> --input mp4/<slug>-short.mp4 --portrait   # 9:16

Output: alongside the input, same name with `-caption` before `.mp4`.
Requires: ffmpeg with libass; EB Garamond installed (or in <folder>/fonts/).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

INK = "#ECE6D8"
HIGHLIGHT = "#F0E442"
OUTLINE = "#16161D"


def hexbgr(h, alpha="00"):
    """#RRGGBB -> ASS &HAABBGGRR."""
    h = h.lstrip("#")
    rr, gg, bb = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha}{bb}{gg}{rr}".upper()


def fmt_time(sec):
    sec = max(0.0, sec)
    cs = int(round(sec * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--input", required=True, help="approved clean master mp4 (rel to folder or abs)")
    ap.add_argument("--portrait", action="store_true")
    ap.add_argument("--allow-long", action="store_true",
                    help="skip the 3:00 Shorts guard — for the 9:16 LONG cut, "
                         "which is a regular vertical video, not a YouTube Short")
    ap.add_argument("--ink", default=INK)
    ap.add_argument("--highlight", default=HIGHLIGHT)
    ap.add_argument("--font", default=None, help="override font name (default from metadata.text_font)")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    caps_path = folder / "captions.json"
    if not caps_path.exists():
        sys.exit("no captions.json — run align_captions.py <folder> first.")
    caps = json.loads(caps_path.read_text())
    fps = float(caps.get("fps", 30))
    font = args.font or sheet["metadata"].get("text_font", "EB Garamond")

    inp = Path(args.input)
    if not inp.is_absolute():
        inp = folder / inp
    if not inp.exists():
        sys.exit(f"input not found: {inp}")
    out = inp.with_name(inp.stem + "-caption.mp4")

    # Portrait safety net: never caption a Short that breaks the 3:00 Shorts limit.
    # (--allow-long bypasses this for the 9:16 LONG cut, which is not a Short.)
    if args.portrait and not args.allow_long:
        total = sum(float(b.get("actual_duration_s", 0.0)) for b in sheet["beats"])
        if total >= 180.0:
            sys.exit(
                f"short_guard: Short is {total:.1f}s ≥ 3:00 — do not caption it. "
                "Shorten the beat sheet first (see scripts/short_guard.py)."
            )

    # absolute start time of each beat = cumulative real audio duration (audio is
    # the master clock; the scene paces every beat to its measured mp3 length).
    offset = {}
    acc = 0.0
    for b in sheet["beats"]:
        offset[b["beat_id"]] = acc
        acc += float(b.get("actual_duration_s", 0.0))

    # geometry
    if args.portrait:
        resx, resy, fontsize, marginv = 1080, 1920, 46, 430
    else:
        resx, resy, fontsize, marginv = 1920, 1080, 52, 90

    events = []
    for bid, blob in caps.get("slides", {}).items():
        base = offset.get(bid)
        if base is None:
            continue
        for line in blob.get("lines", []):
            words = line.get("words", [])
            if not words:
                continue
            l_start = base + words[0]["startFrame"] / fps
            l_end = base + words[-1]["endFrame"] / fps + 0.15
            chunks = []
            for w in words:
                ws = base + w["startFrame"] / fps
                we = base + w["endFrame"] / fps
                dur_cs = max(1, int(round((we - ws) * 100)))
                chunks.append(rf"{{\k{dur_cs}}}{w['text']} ")
            events.append((l_start, l_end, "".join(chunks).rstrip()))

    events.sort()
    prim = hexbgr(args.highlight)   # sung word
    sec = hexbgr(args.ink)          # upcoming word
    outl = hexbgr(OUTLINE)

    ass = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {resx}",
        f"PlayResY: {resy}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        ("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
         "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, "
         "ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
         "MarginL, MarginR, MarginV, Encoding"),
        (f"Style: bb,{font},{fontsize},{prim},{sec},{outl},&H64000000,0,0,0,0,"
         f"100,100,0,0,1,3,0,2,120,120,{marginv},1"),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for s, e, text in events:
        ass.append(f"Dialogue: 0,{fmt_time(s)},{fmt_time(e)},bb,,0,0,0,,{text}")

    ass_path = folder / ("captions-portrait.ass" if args.portrait else "captions.ass")
    ass_path.write_text("\n".join(ass), encoding="utf-8")
    print(f"[ok] wrote {ass_path} ({len(events)} caption lines)")

    fontsdir = folder / "fonts"
    vf = f"subtitles={ass_path.name}"
    if fontsdir.exists():
        vf += f":fontsdir={fontsdir}"
    cmd = ["ffmpeg", "-y", "-i", str(inp), "-vf", vf,
           "-c:v", "libx264", "-crf", "18", "-preset", "medium",
           "-c:a", "copy", str(out)]
    print("[run]", " ".join(cmd))
    r = subprocess.run(cmd, cwd=str(folder))
    if r.returncode == 0:
        print(f"[ok] wrote {out}")
    else:
        sys.exit(f"ffmpeg failed ({r.returncode})")


if __name__ == "__main__":
    main()
