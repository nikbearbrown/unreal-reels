#!/usr/bin/env python3
"""
preview_tangent.py — snapshot an equation tangent (fixed 5-zone template) to SVG.

See brutalist/EQUATIONS.md. Zones: symbolic form (dark box) · LHS/RHS sentences +
the = claim · glossary with a Role column · worked example that holds/breaks.
Numbers in mono. White = mechanics, pink = value judgment.

Usage:
    python preview_tangent.py <folder> <beat_id> [-o out.svg]
"""
import argparse
import json
import re
from pathlib import Path

RED = "#C8102E"
INK = "#2a1a0e"
SEC = "#545454"
PINK = "#fdecea"
FONT = "Inter, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, Menlo, monospace"
NUM = re.compile(r"(\d[\d.,]*\s*%?|≠)")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def mono(text):
    out = []
    for part in NUM.split(text):
        if not part:
            continue
        out.append(f'<tspan font-family="{MONO}">{esc(part)}</tspan>' if NUM.fullmatch(part) else esc(part))
    return "".join(out)


def T(x, y, s, size, fill=INK, fam=FONT, weight=400, anchor="start", mononum=False, ls=""):
    inner = mono(s) if mononum else esc(s)
    extra = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-family="{fam}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{extra}>{inner}</text>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("beat_id"); ap.add_argument("-o", "--out")
    a = ap.parse_args()
    d = json.loads((Path(a.folder) / "tangents.json").read_text())[a.beat_id]
    b = ['<rect width="1920" height="1080" fill="#fff"/>',
         f'<rect width="1920" height="10" fill="{RED}"/>']

    # header
    b.append(T(130, 116, d["eyebrow"].upper(), 26, RED, weight=700, ls="3"))
    b.append(T(130, 188, d["title"], 56, INK))

    # zone 1 — symbolic form (dark box). Real math: italic serif (KaTeX in the
    # component), NOT mono — mono is only for data numbers.
    b.append(f'<rect x="130" y="220" width="1660" height="120" rx="8" fill="{INK}"/>')
    b.append(f'<text x="960" y="300" font-size="52" fill="#fff" font-style="italic" '
             f'font-family="Georgia, \'Times New Roman\', serif" text-anchor="middle">{esc(d["equation"])}</text>')

    # zone 2 — LHS / RHS as sentences + the = claim
    b.append(T(160, 408, "LEFT SIDE", 22, RED, weight=700, ls="2"))
    b.append(T(160, 452, d["lhs"], 30, INK))
    b.append(T(990, 408, "RIGHT SIDE", 22, RED, weight=700, ls="2"))
    b.append(T(990, 452, d["rhs"], 30, INK))
    b.append(T(160, 524, d["claim"], 30, INK))

    # zone 3 — glossary with Role column
    cols = (160, 430, 820, 1480)
    head = ("SYMBOL", "ROLE", "PLAIN MEANING", "DOMAIN")
    b.append(f'<line x1="160" y1="572" x2="1790" y2="572" stroke="#D4D4D4" stroke-width="1"/>')
    for x, h in zip(cols, head):
        b.append(T(x, 606, h, 20, SEC, weight=700, ls="1"))
    y = 660
    for g in d["glossary"]:
        b.append(T(cols[0], y, g["sym"], 30, RED, fam=MONO, weight=700))
        b.append(T(cols[1], y, g["role"], 27, SEC))
        b.append(T(cols[2], y, g["mean"], 27, INK))
        b.append(T(cols[3], y, g["dom"], 27, SEC, fam=MONO))
        y += 52

    # zone 4 — worked example (mechanics = white box w/ red hairline)
    ex = d["example"]
    b.append('<rect x="130" y="892" width="1660" height="150" rx="8" fill="#fff" '
             f'stroke="{RED}" stroke-width="2"/>')
    b.append(T(160, 936, "WORKED EXAMPLE", 20, RED, weight=700, ls="2"))
    b.append(T(160, 980, ex["scenario"], 28, INK, mononum=True))
    b.append(T(160, 1022, ex["compare"], 28, RED, fam=MONO, weight=700))
    b.append(T(900, 1022, ex["cost"], 24, SEC, mononum=True))

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080">'
           '<style>@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;700&amp;family=JetBrains+Mono:wght@400;700&amp;display=swap");</style>'
           + "".join(b) + "</svg>")
    out = Path(a.out) if a.out else Path(a.folder) / f"{a.beat_id}-tangent-preview.svg"
    out.write_text(svg)
    print(f"[ok] wrote {out}")


if __name__ == "__main__":
    main()
