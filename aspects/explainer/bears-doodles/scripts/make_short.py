#!/usr/bin/env python3
"""
make_short.py  —  Bear's Notes 16:9 master  →  9:16 Short (branded reframe)

The fast, universal path: NO re-render, NO new audio. It scales the finished
16:9 master to full width and centers it in a 1080x1920 white card, then draws
the brand + title above and the channel handle below — all in Shadows Into Light.
Because the scenes are on white, the padding bands blend seamlessly, so it reads
as a portrait title-card with the animation playing in the middle.

This is the always-on Shorts fallback. For dual-panel scenes where the centered
band is too small to read, prefer a native 9:16 re-render (see --help notes).

Usage:
    python make_short.py <video-folder>                 # reads mp4/*.mp4 + beat_sheet.json
    python make_short.py <video-folder> --master path.mp4 --title "..." --channel "..."

Output: <folder>/mp4/<slug>-short.mp4
"""
from __future__ import annotations
import argparse, json, subprocess, sys, tempfile, textwrap
from pathlib import Path

FONT_CANDIDATES = [
    "Manim/shared/fonts/ShadowsIntoLight-Regular.ttf",
    "shared/fonts/ShadowsIntoLight-Regular.ttf",
]
INK, ACCENT = "0x1a1a1a", "0x5A5653"
CW, CH = 1080, 1920          # portrait canvas
BRAND = "Bear's Notes"


def find_font(folder: Path) -> str:
    # walk up from the video folder looking for the shared font
    for base in [folder, *folder.parents]:
        for rel in FONT_CANDIDATES:
            p = base / rel
            if p.exists():
                return str(p)
    # last resort: any matching ttf under a Manim/ root
    for base in folder.parents:
        hit = list(base.glob("**/ShadowsIntoLight-Regular.ttf"))
        if hit:
            return str(hit[0])
    return ""


def wrap(s: str, width: int) -> list[str]:
    return textwrap.wrap(s, width=width) or [s]


def drawtext(textfile: str, font: str, size: int, color: str, y: str) -> str:
    # x centers each line; textfile avoids quote/apostrophe escaping headaches
    return (f"drawtext=fontfile='{font}':textfile='{textfile}':"
            f"fontsize={size}:fontcolor={color}:x=(w-text_w)/2:y={y}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--master", default=None, help="path to 16:9 master mp4")
    ap.add_argument("--title", default=None)
    ap.add_argument("--channel", default=None)
    ap.add_argument("--wrap", type=int, default=17, help="title chars per line")
    ap.add_argument("--vh", type=int, default=720,
                    help="rendered height of the centered video band (px)")
    args = ap.parse_args(argv)

    folder = Path(args.folder).resolve()
    mp4dir = folder / "mp4"
    # locate master
    if args.master:
        master = Path(args.master).resolve()
    else:
        cands = [p for p in mp4dir.glob("*.mp4") if "-short" not in p.name]
        if not cands:
            print(f"[short] no master mp4 in {mp4dir}", file=sys.stderr); return 2
        master = max(cands, key=lambda p: p.stat().st_size)

    # metadata
    title, channel = args.title, args.channel
    bs = folder / "beat_sheet.json"
    if (title is None or channel is None) and bs.exists():
        m = json.load(open(bs)).get("metadata", {})
        title = title or m.get("title", folder.name.replace("-", " "))
        channel = channel or m.get("channel_url", "youtube.com/@NikBearBrown")
    title = title or folder.name.replace("-", " ")
    channel = channel or "youtube.com/@NikBearBrown"

    font = find_font(folder)
    if not font:
        print("[short] Shadows Into Light TTF not found near the video folder", file=sys.stderr)
        return 2

    slug = master.stem.replace("-short", "")
    out = mp4dir / f"{slug}-short.mp4"

    # geometry: video band height = args.vh, centered; bands above/below for text
    vw = CW
    vh = args.vh
    band_top = (CH - vh) // 2

    # write text line files
    tmp = Path(tempfile.mkdtemp())
    title_lines = wrap(title, args.wrap)
    files = {}
    for i, ln in enumerate(title_lines):
        f = tmp / f"t{i}.txt"; f.write_text(ln); files[f"t{i}"] = str(f)
    fb = tmp / "brand.txt"; fb.write_text(BRAND); files["brand"] = str(fb)
    fc = tmp / "chan.txt"; fc.write_text(channel); files["chan"] = str(fc)

    # build filtergraph: scale master, pad to portrait white, draw text
    parts = [f"[0:v]scale={vw}:{vh}:force_original_aspect_ratio=decrease,"
             f"pad={CW}:{CH}:(ow-iw)/2:{band_top}:color=white[v0]"]
    chain = "[v0]"
    n = 0

    def add(dt):
        nonlocal chain, n
        tag = f"[v{n+1}]"
        parts.append(f"{chain}{dt}{tag}")
        chain = tag; n += 1

    # top band: brand then title lines, stacked, centered in the upper margin
    title_size = 64
    brand_size = 46
    line_h = title_size + 16
    title_block_h = line_h * len(title_lines)
    # place title block so it sits comfortably above the video band
    title_top = max(150, band_top - title_block_h - 70)
    brand_y = max(70, title_top - brand_size - 30)

    add(drawtext(files["brand"], font, brand_size, ACCENT, str(brand_y)))
    for i in range(len(title_lines)):
        y = title_top + i * line_h
        add(drawtext(files[f"t{i}"], font, title_size, INK, str(y)))

    # bottom band: channel handle
    chan_y = band_top + vh + 90
    if chan_y > CH - 90:
        chan_y = CH - 130
    add(drawtext(files["chan"], font, 44, INK, str(chan_y)))

    fc_graph = ";".join(parts).replace(chain, "[vout]", 1) if False else ";".join(parts)
    # rename final tag to [vout]
    fc_graph = fc_graph[::-1].replace(chain[::-1], "[vout]"[::-1], 1)[::-1]

    cmd = ["ffmpeg", "-y", "-i", str(master),
           "-filter_complex", fc_graph,
           "-map", "[vout]", "-map", "0:a?",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
           "-preset", "medium", "-c:a", "aac", "-b:a", "192k", str(out)]
    print("[short] rendering", out.name, "...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:], file=sys.stderr); return 1
    print(f"[short] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
