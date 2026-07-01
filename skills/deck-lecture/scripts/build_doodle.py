#!/usr/bin/env python3
"""
build_doodle.py — starter doodle specs for the doodle-mode slides.

Writes/updates <folder>/doodles.json — a map { beat_id: {title, elements:[...]} }
that the Remotion <Doodle> component draws on progressively (bears-doodles style:
line art on white, one narration line = one new element). This generates a
BASELINE (one label per caption line, timed to that line) so every doodle slide
has something better than a static 30s hold; you then upgrade the slides that
deserve real sketches (boxes, arrows, dot-grids) by hand.

It never overwrites a hand-authored spec (one without "_starter": true) unless you
pass --force or name it in --only.

Element timing: prefers `atLine` (locks to the spoken caption line). If captions
aren't built yet, falls back to `atFrac` spread evenly across the slide.

Usage:
    python build_doodle.py <folder>                 # starters for all doodle slides
    python build_doodle.py <folder> --only S05 S14  # just these
    python build_doodle.py <folder> --force         # overwrite existing starters too
"""
import argparse
import json
import re
from pathlib import Path


def shorten(text, max_words=6):
    w = text.split()
    return " ".join(w[:max_words]) + ("…" if len(w) > max_words else "")


def starter_elements(label, lines, sentences):
    """One label per caption line (timed by atLine); fall back to sentences/atFrac."""
    els = []
    if lines:
        n = min(len(lines), 8)
        for i in range(n):
            els.append({
                "kind": "label", "text": shorten(lines[i]["text"]),
                "x": 170, "y": 320 + i * 92, "size": 44, "atLine": i,
            })
    else:
        n = min(len(sentences), 8)
        for i, s in enumerate(sentences[:n]):
            els.append({
                "kind": "label", "text": shorten(s),
                "x": 170, "y": 320 + i * 92, "size": 44,
                "atFrac": round(i / max(n, 1), 3),
            })
    return els


def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    return [s for s in re.split(r"(?<=[.!?]) ", text) if s.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    folder = Path(args.folder)
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    caps_path = folder / "captions.json"
    caps = json.loads(caps_path.read_text()) if caps_path.exists() else {"slides": {}}

    spec_path = folder / "doodles.json"
    spec = json.loads(spec_path.read_text()) if spec_path.exists() else {}

    made = []
    for b in sheet["beats"]:
        bid = b["beat_id"]
        if b.get("visual_mode") != "doodle":
            continue
        if args.only and bid not in args.only:
            continue
        existing = spec.get(bid)
        if existing and not existing.get("_starter") and not args.force and not (args.only and bid in args.only):
            continue  # keep hand-authored work
        lines = caps.get("slides", {}).get(bid, {}).get("lines", [])
        sentences = split_sentences(b.get("narration_text", ""))
        els = starter_elements(b["label"], lines, sentences)
        if not els:
            continue
        spec[bid] = {"title": b["label"], "_starter": True, "elements": els}
        made.append(bid)

    spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    print(f"[ok] wrote {spec_path}")
    print(f"[ok] starter specs for {len(made)} slide(s): {', '.join(made) or '(none)'}")
    print("[note] these are placeholder labels — upgrade the important slides to real "
          "sketches (rect/arrow/dots/circle). Hand-authored specs (no \"_starter\") are kept.")


if __name__ == "__main__":
    main()
