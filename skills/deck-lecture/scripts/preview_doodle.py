#!/usr/bin/env python3
"""
preview_doodle.py — snapshot a doodle spec to a static SVG (fully-drawn state).

Lets you eyeball a slide's doodle (layout, labels, shapes) without running a full
Remotion render. Geometry matches Doodle.tsx; this is the final frame (everything
drawn, full opacity).

Usage:
    python preview_doodle.py <folder> <beat_id> [-o out.svg]
"""
import argparse
import json
import math
import re
from pathlib import Path

INK = "#2a1a0e"
FONT = "Inter, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, Menlo, monospace"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def is_numeric(s):
    return bool(re.fullmatch(r"[\d.,/%\s]+", s)) and any(c.isdigit() for c in s)


def el_svg(el):
    color = el.get("color", INK)
    k = el["kind"]
    if k == "label":
        anchor = el.get("anchor", "start")
        size = el.get("size", 46)
        fam = MONO if is_numeric(el["text"]) else FONT
        return (f'<text x="{el["x"]}" y="{el["y"]}" fill="{color}" font-size="{size}" '
                f'font-family="{fam}" text-anchor="{anchor}">{esc(el["text"])}</text>')
    if k == "rect":
        return (f'<rect x="{el["x"]}" y="{el["y"]}" width="{el["w"]}" height="{el["h"]}" rx="10" '
                f'fill="none" stroke="{color}" stroke-width="4"/>')
    if k == "line":
        return (f'<line x1="{el["x1"]}" y1="{el["y1"]}" x2="{el["x2"]}" y2="{el["y2"]}" '
                f'stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
    if k == "circle":
        return (f'<circle cx="{el["cx"]}" cy="{el["cy"]}" r="{el["r"]}" fill="none" '
                f'stroke="{color}" stroke-width="4"/>')
    if k == "arrow":
        x1, y1, x2, y2 = el["x1"], el["y1"], el["x2"], el["y2"]
        ang = math.atan2(y2 - y1, x2 - x1)
        hl = 22
        ax, ay = x2 - hl * math.cos(ang - math.pi / 6), y2 - hl * math.sin(ang - math.pi / 6)
        bx, by = x2 - hl * math.cos(ang + math.pi / 6), y2 - hl * math.sin(ang + math.pi / 6)
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M{ax} {ay} L{x2} {y2} L{bx} {by}" fill="none" stroke="{color}" stroke-width="4" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    if k == "dots":
        out = []
        n = 0
        for r in range(el["rows"]):
            for c in range(el["cols"]):
                filled = n < el["filled"]
                cx, cy = el["x"] + c * el["gap"], el["y"] + r * el["gap"]
                out.append(f'<circle cx="{cx}" cy="{cy}" r="12" fill="{color if filled else "none"}" '
                           f'stroke="{color}" stroke-width="3"/>')
                n += 1
        return "".join(out)
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("beat_id")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    folder = Path(args.folder)
    spec = json.loads((folder / "doodles.json").read_text())[args.beat_id]
    body = []
    if spec.get("title"):
        body.append(f'<text x="120" y="130" fill="{INK}" font-size="66" font-weight="700" '
                    f'font-family="{FONT}">{esc(spec["title"])}</text>')
    for el in spec["elements"]:
        body.append(el_svg(el))

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">'
        '<style>@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;700&amp;family=JetBrains+Mono:wght@400;700&amp;display=swap");</style>'
        '<rect width="1920" height="1080" fill="#ffffff"/>'
        + "".join(body) + "</svg>"
    )
    out = Path(args.out) if args.out else folder / f"{args.beat_id}-doodle-preview.svg"
    out.write_text(svg)
    print(f"[ok] wrote {out}")


if __name__ == "__main__":
    main()
