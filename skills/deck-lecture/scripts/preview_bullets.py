#!/usr/bin/env python3
"""
preview_bullets.py — snapshot a bullets slide to a static SVG (final state).

Eyeball the bullets look (deck typography, NU-red markers) without a Remotion
render. Matches Bullets.tsx styling; shows all bullets revealed, last emphasized.

Usage:
    python preview_bullets.py <folder> <beat_id> [-o out.svg]
"""
import argparse
import json
import re
from pathlib import Path

NU_RED = "#C8102E"
INK = "#2a1a0e"
PAST = "#545454"
FONT = "Inter, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, Menlo, monospace"
NUM_RE = re.compile(r"(\d[\d.,]*\s*%?|\d+\s*/\s*\d+)")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def with_mono(text):
    """SVG inner markup: numeric tokens in a mono tspan."""
    out = []
    for part in NUM_RE.split(text):
        if not part:
            continue
        if NUM_RE.fullmatch(part):
            out.append(f'<tspan font-family="{MONO}">{esc(part)}</tspan>')
        else:
            out.append(esc(part))
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("beat_id")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    folder = Path(args.folder)
    spec = json.loads((folder / "bullets.json").read_text())[args.beat_id]
    bullets = spec["bullets"]
    n = len(bullets)
    size = 40 if n > 6 else 48 if n > 4 else 56
    gap = (26 if n > 6 else 34) + size * 1.3

    body = [f'<rect width="1920" height="1080" fill="#fff"/>',
            f'<rect width="1920" height="10" fill="{NU_RED}"/>']
    y = 150
    if spec.get("title"):
        body.append(f'<text x="130" y="{y}" fill="{INK}" font-size="68" '
                    f'font-family="{FONT}">{with_mono(spec["title"])}</text>')
        body.append(f'<rect x="130" y="{y+34}" width="96" height="6" fill="{NU_RED}"/>')
        y += 150
    for i, b in enumerate(bullets):
        cur = i == n - 1
        ty = y + i * gap
        body.append(f'<rect x="130" y="{ty - size*0.42:.0f}" width="38" height="6" fill="{NU_RED}"/>')
        body.append(f'<text x="196" y="{ty:.0f}" fill="{INK if cur else PAST}" font-size="{size}" '
                    f'font-weight="{700 if cur else 400}" font-family="{FONT}">{with_mono(b["text"])}</text>')

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">'
           '<style>@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;700&amp;family=JetBrains+Mono:wght@400;700&amp;display=swap");</style>'
           + "".join(body) + "</svg>")
    out = Path(args.out) if args.out else folder / f"{args.beat_id}-bullets-preview.svg"
    out.write_text(svg)
    print(f"[ok] wrote {out}")


if __name__ == "__main__":
    main()
