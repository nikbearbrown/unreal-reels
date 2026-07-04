#!/usr/bin/env python3
"""
verify_deck.py — Phase 3 of the slide-deck skill (the required verification step).

Static, dependency-free audit of an emitted .dc.html against the DESIGN.md
constitution and the deck-lecture contract. It answers: will stage 3 accept this
deck, and does it obey the palette rules?

Checks (fail = exit 1):
  1. PARSE     every <section data-label> extracts cleanly via deck-lecture's own
               extract_slides.py, and EVERY beat has non-empty data-speaker-notes
               (stage 3's entire narration expands from these — a blank note is a
               silent slide).
  2. PALETTE   no blue anywhere (no #00f / #0000ff / rgb blue / `:blue`); the six
               --nu-* tokens + red-tint + white/#fff + #111/#2D2926 inks only for
               raw hex. Flags any stray non-palette hex as a warning.
  3. CHARTS    every [data-chart="NAME"] has a matching this._drawers['NAME'] = …
               registration, and no placeholder drawer text leaked in.
  4. KATEX     every [data-tex] block has balanced { } and $-free content.
  5. RUNTIME   support.js, deck-stage.js, and _ds/**/colors_and_type.css exist
               beside the deck.

The pixel audit (screenshot every slide, check numbers-are-mono / real Inter /
motion) needs a browser and is handed off, not faked:
    python ../deck-lecture/scripts/prerender_deck.py "<deck>.dc.html"

Pure stdlib. No deps.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# reuse the exact parser stage 3 uses
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent / "deck-lecture" / "scripts"))
try:
    from extract_slides import SlideParser  # type: ignore
except Exception:  # pragma: no cover
    SlideParser = None

BLUE = re.compile(r"#0{2,4}f{1,4}\b|#0000ff|rgb\(\s*\d+\s*,\s*\d+\s*,\s*2[0-9]{2}\s*\)|:\s*blue\b", re.I)
HEX = re.compile(r"#[0-9a-fA-F]{3,6}\b")
DATA_CHART = re.compile(r'data-chart="([^"]+)"')
DRAWER_REG = re.compile(r"this\._drawers\[?['\"]([\w-]+)['\"]\]?\s*=")
TEX = re.compile(r'data-tex[^>]*>(.*?)</div>', re.DOTALL)

PALETTE_HEX = {
    "#fff", "#ffffff", "#000", "#000000", "#c8102e", "#a50c25", "#870a1f",
    "#fbe7ea", "#e3e3e3", "#c4c4c4", "#909090", "#787878", "#545454",
    "#404040", "#2d2926", "#1a1a1a", "#a4804a", "#111", "#111111", "#d7cec8",
    "#2a1a0e", "#d4d4d4", "#c8860e",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck", help="path to the emitted .dc.html")
    args = ap.parse_args()

    deck = Path(args.deck).expanduser()
    if not deck.exists():
        sys.exit(f"[err] deck not found: {deck}")
    html = deck.read_text(encoding="utf-8", errors="replace")
    fails, warns, oks = [], [], []

    # 1. PARSE + speaker notes
    if SlideParser is None:
        warns.append("could not import extract_slides.py — skipped parse check")
    else:
        p = SlideParser()
        p.feed(html)
        n = len(p.slides)
        if n == 0:
            fails.append("no <section data-label> slides parsed")
        else:
            oks.append(f"parsed {n} slides via extract_slides.py")
            blank = [s["label"] or "(unlabeled)" for s in p.slides if not s["speaker_notes"].strip()]
            if blank:
                fails.append(f"{len(blank)} slide(s) with EMPTY data-speaker-notes: {', '.join(blank)}")
            else:
                oks.append("every slide has non-empty data-speaker-notes")

    # 2. PALETTE
    blues = BLUE.findall(html)
    if blues:
        fails.append(f"blue detected ({len(blues)}×): {sorted(set(blues))[:5]} — palette forbids blue")
    else:
        oks.append("no blue (palette clean)")
    stray = sorted({h for h in HEX.findall(html) if h.lower() not in PALETTE_HEX})
    if stray:
        warns.append(f"{len(stray)} non-palette hex value(s): {stray[:8]} "
                     f"(charts may legitimately use these; confirm they're grays/red)")

    # 3. CHARTS
    charts = DATA_CHART.findall(html)
    registered = set(DRAWER_REG.findall(html))
    unresolved = [c for c in charts if c not in registered]
    if unresolved:
        fails.append(f"[data-chart] with no drawer: {sorted(set(unresolved))}")
    elif charts:
        oks.append(f"{len(charts)} chart(s), all drawers registered")
    if "chart drawer missing:" in html:
        fails.append("placeholder drawer text present — a chart's drawer.js was not found")

    # 4. KATEX
    bad_tex = []
    for i, t in enumerate(TEX.findall(html)):
        inner = re.sub(r"<[^>]+>", "", t)
        if inner.count("{") != inner.count("}"):
            bad_tex.append(f"#{i+1} unbalanced braces")
        if "$" in inner:
            bad_tex.append(f"#{i+1} contains a $ (KaTeX content should be bare TeX)")
    if bad_tex:
        fails.append("data-tex issues: " + "; ".join(bad_tex[:6]))
    elif TEX.search(html):
        oks.append(f"{len(TEX.findall(html))} equation(s), TeX braces balanced")

    # 5. RUNTIME
    for f in ("support.js", "deck-stage.js"):
        (oks if (deck.parent / f).exists() else fails).append(
            f"runtime {f} " + ("present" if (deck.parent / f).exists() else "MISSING beside deck"))
    ds = list((deck.parent / "_ds").glob("*/colors_and_type.css")) if (deck.parent / "_ds").exists() else []
    (oks if ds else fails).append("_ds/**/colors_and_type.css " + ("present" if ds else "MISSING"))

    # report
    print(f"# verify {deck.name}\n")
    for o in oks:
        print("  ✓ " + o)
    for w in warns:
        print("  ! " + w)
    for f in fails:
        print("  ✗ " + f)
    print()
    if fails:
        print(f"[FAIL] {len(fails)} blocking issue(s). Fix before handing to deck-lecture.")
        print('[hand-off] pixel audit (browser): python ../deck-lecture/scripts/prerender_deck.py "'
              + str(deck) + '"')
        sys.exit(1)
    print("[PASS] deck is stage-3 ready.")
    print('[next] python ../deck-lecture/scripts/extract_slides.py "' + str(deck) + '" -o <lecture_folder>')


if __name__ == "__main__":
    main()
