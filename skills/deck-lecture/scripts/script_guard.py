#!/usr/bin/env python3
"""
script_guard.py — flag beats whose narration READS the slide instead of
discussing it. Run after Phase 1 (narration_text filled), before Phase 2 audio.

Computes Jaccard overlap of content words between narration_text and
on_slide_text. High overlap ⇒ the script is reciting the slide; rewrite it to
explain rather than read.

Usage:
    python script_guard.py path/to/lecture_folder [--threshold 0.6]
"""
import argparse
import json
import re
from pathlib import Path

STOP = set("""a an the of to in on for and or but is are was were be been being as at by
with from this that these those it its their your you we i he she they them our us if then
than so such not no can will would should could may might do does did have has had each one
two three over under into about which who whom whose what when where why how all any both
""".split())


def content_words(text: str):
    toks = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {t for t in toks if t not in STOP and len(t) > 2}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--threshold", type=float, default=0.6)
    args = ap.parse_args()

    sheet = json.loads((Path(args.folder) / "beat_sheet.json").read_text())
    flagged, empty = [], []
    for b in sheet["beats"]:
        nar = b.get("narration_text", "")
        if not nar.strip():
            empty.append(b["beat_id"])
            continue
        ov = jaccard(content_words(nar), content_words(b.get("on_slide_text", "")))
        mark = "  <-- READS THE SLIDE, rewrite" if ov >= args.threshold else ""
        print(f"{b['beat_id']}  overlap={ov:0.2f}{mark}")
        if ov >= args.threshold:
            flagged.append(b["beat_id"])

    print("-" * 40)
    if empty:
        print(f"[todo] no narration yet: {', '.join(empty)}")
    if flagged:
        print(f"[warn] too close to the slide text: {', '.join(flagged)}")
    if not flagged and not empty:
        print("[ok] all beats discuss rather than read.")


if __name__ == "__main__":
    main()
