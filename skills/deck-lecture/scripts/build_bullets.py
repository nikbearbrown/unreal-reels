#!/usr/bin/env python3
"""
build_bullets.py — auto-condensed bullet specs for text-heavy slides.

The fallback for a doodle-mode slide with NO authored doodle: instead of holding
the live slide for 30s, animate its key points in as bullets. This condenses each
slide's narration into short bullets (one per sentence, ~7 words, lead-in filler
stripped) and times each to the caption line where that sentence is spoken.

Writes <folder>/bullets.json  { beat_id: {title, bullets:[{text, atLine}]} }
- only for beats with visual_mode == "doodle" that have NO doodle spec.
- preserves any hand-edited entry (one without "_auto": true) unless --force.

Usage:
    python build_bullets.py <folder> [--max 6] [--only S02 S10] [--force]
"""
import argparse
import json
import re
from pathlib import Path

# discourse lead-ins to strip from the front of a bullet (spoken glue, not content)
LEADINS = re.compile(
    r"^(so|now|and|but|then|here'?s the thing,?|here'?s why,?|the thing is,?|"
    r"notice( that)?,?|note( that)?,?|i want you to|i want to|let'?s|look,?|"
    r"think about|picture|consider|remember,?|of course,?|in other words,?|"
    r"that is,?|basically,?|essentially,?|first,?|second,?|third,?|finally,?|"
    r"crucially,?|importantly,?|the key (thing|point) is,?)\s+", re.IGNORECASE)

# clause cut points — keep the first clause if a sentence is long
CLAUSE = re.compile(r"\s+(?:—|–|-|because|so that|which|where|while|whereas|"
                    r"unless|since|as long as|even though|but)\s+", re.IGNORECASE)


def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in re.split(r"(?<=[.!?]) ", text) if s.strip()]


# function words we must never END a bullet on (prevents "...definitions of")
TRAIL = set("of the a an to and or that like with for in on is are as at by this these "
            "those it its their your you we but so than into about".split())


def condense(sentence, max_words=10):
    """Rough starter only — a real summary should be hand-written. This keeps a
    COMPLETE leading clause and never dangles on a function word."""
    s = sentence.strip().rstrip(".!?")
    s = LEADINS.sub("", s).strip()
    s = re.sub(r"\([^)]*\)", "", s).strip()          # drop parentheticals
    m = CLAUSE.search(s)                               # keep first clause if long
    if m and len(s[: m.start()].split()) >= 4:
        s = s[: m.start()].strip()
    s = s.split(",")[0].strip()                       # first comma clause
    words = s.split()
    if len(words) > max_words:
        words = words[:max_words]
    while words and words[-1].lower().strip(",.;:") in TRAIL:  # no dangling glue
        words.pop()
    s = " ".join(words)
    return s[:1].upper() + s[1:] if s else s


def line_for_word(lines, word_index):
    """Caption line index whose word span contains the given narration word index."""
    cum = 0
    for i, ln in enumerate(lines):
        wc = len(ln.get("words") or ln["text"].split())
        if word_index < cum + wc:
            return i
        cum += wc
    return max(0, len(lines) - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--max", type=int, default=6, help="max bullets per slide")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    folder = Path(args.folder)
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    caps = json.loads((folder / "captions.json").read_text()) if (folder / "captions.json").exists() else {"slides": {}}
    doodles = json.loads((folder / "doodles.json").read_text()) if (folder / "doodles.json").exists() else {}
    out_path = folder / "bullets.json"
    spec = json.loads(out_path.read_text()) if out_path.exists() else {}

    beats = sheet["beats"]
    made = []
    for idx, b in enumerate(beats):
        bid = b["beat_id"]
        if b.get("visual_mode") != "doodle":
            continue
        if doodles.get(bid, {}).get("elements"):
            continue  # has a real doodle → bullets not needed
        # title slide, closing slide, and "Part N" section dividers are already
        # big-type visual cards — leave them live, don't bulletize.
        ost = b.get("on_slide_text", "").strip()
        if idx == 0 or idx == len(beats) - 1 or ost.startswith("Part "):
            continue
        if args.only and bid not in args.only:
            continue
        if bid in spec and not spec[bid].get("_auto") and not args.force:
            continue  # keep hand-edited bullets

        sentences = split_sentences(b.get("narration_text", ""))
        lines = caps.get("slides", {}).get(bid, {}).get("lines", [])
        bullets = []
        word_cursor = 0
        for s in sentences:
            text = condense(s, max_words=8)
            n_words = len(s.split())
            at = line_for_word(lines, word_cursor) if lines else None
            word_cursor += n_words
            if text:
                bullets.append({"text": text, **({"atLine": at} if at is not None else {})})
        # cap count: keep evenly spaced bullets if too many
        if len(bullets) > args.max:
            step = len(bullets) / args.max
            bullets = [bullets[int(i * step)] for i in range(args.max)]
        if not bullets:
            continue
        spec[bid] = {"title": b["label"], "_auto": True, "bullets": bullets}
        made.append(bid)

    out_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    print(f"[ok] wrote {out_path}")
    print(f"[ok] auto-bullets for {len(made)} slide(s): {', '.join(made) or '(none)'}")
    print("[note] auto-condensed from narration — skim and tweak any that read oddly; "
          "edits survive (remove \"_auto\": true on a slide to lock it).")


if __name__ == "__main__":
    main()
