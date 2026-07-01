#!/usr/bin/env python3
"""
build_sections.py — extract the title / "Part N" divider / close slides so they
can render NATIVELY in Remotion instead of through the live deck iframe.

Those slides reload the whole deck (KaTeX + D3 + scripts) on each mount, and the
reload hitches the exported render at the section boundaries (~every few minutes).
They're just type cards, so we rebuild them natively (deterministic, smooth).

Writes <folder>/sections.json  { beat_id: {eyebrow, title, subtitle, bg} }
bg is "black" or "red" (mirrors the deck's divider backgrounds).

Usage:
    python build_sections.py <folder> --deck "<deck>.dc.html"
"""
import argparse
import html
import json
import re
from pathlib import Path


def strip(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--deck", required=True)
    args = ap.parse_args()

    deck = Path(args.deck).read_text(encoding="utf-8", errors="replace")
    secs = re.findall(r'<section\b([^>]*)>(.*?)</section>', deck, re.S)
    out = {}
    n = len(secs)
    for i, (attrs, body) in enumerate(secs):
        text = strip(body)
        is_card = (i == 0 or i == n - 1 or text.startswith("Part "))
        if not is_card:
            continue
        bid = f"S{i + 1:02d}"
        bg_m = re.search(r"background:\s*var\(--nu-(\w+)\)", attrs)
        bg = "red" if (bg_m and bg_m.group(1) == "red") else "black"
        eyebrow_m = re.search(r"<div[^>]*text-transform:\s*uppercase[^>]*>(.*?)</div>", body, re.S)
        title_m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", body, re.S)
        eyebrow = strip(eyebrow_m.group(1)) if eyebrow_m else ""
        title = strip(title_m.group(1)) if title_m else ""
        # subtitle = whatever text is left after the eyebrow and title
        subtitle = text
        for chunk in (eyebrow, title):
            if chunk:
                subtitle = subtitle.replace(chunk, "", 1)
        subtitle = subtitle.strip(" ·—-")
        out[bid] = {"eyebrow": eyebrow, "title": title, "subtitle": subtitle, "bg": bg}

    Path(args.folder, "sections.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"[ok] wrote {args.folder}/sections.json — {len(out)} native section cards")
    for bid, s in out.items():
        print(f"    {bid} [{s['bg']}] {s['eyebrow']} / {s['title'][:48]}")


if __name__ == "__main__":
    main()
