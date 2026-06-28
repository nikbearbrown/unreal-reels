#!/usr/bin/env python3
"""
segment_story.py — Unreal Reels beat segmenter (Phase 0/2).

Turn a plain-text story into a beat_sheet.json: one beat per ~spoken-line, each
short enough to land on a single generated clip (<= the 10s Hailuo tier). Verbatim
by default — it splits the source text, it does NOT rewrite it.

How it segments:
  1. Split into sentences.
  2. Any sentence longer than --max-words is split at clause boundaries (',' ';')
     greedily into <= max-words chunks; a single over-long clause is hard-split.
  3. Fragments shorter than --min-words are merged into a neighbour.
Each beat gets a B## id, narration_text + tts_normalized_text, characters_present
(inferred from the cast names + synonyms), a placeholder camera, and EMPTY
image_prompt/video_prompt (authored later in the storyboard phase). Phase fields
(audio/duration/stills/video) are null until each phase fills them.

Metadata (voice_id, style_bible, characters) is lifted from --meta-from (an existing
beat_sheet.json) so a tale inherits its cast/look; --slug/--title override the rest.

Usage:
  python segment_story.py source.txt --meta-from ../little-red-cap/beat_sheet.json \\
      --slug little-red-cap-full --title "Little Red-Cap (full)" -o beat_sheet.json
"""
import argparse, json, re, sys
from pathlib import Path

SYNONYMS = {
    # cast name -> lowercased substrings that imply they're on screen
    "Red Cap":     ["red-cap", "red cap", "little red", "the little girl", "the child", "the girl"],
    "Wolf":        ["wolf"],
    "Grandmother": ["grandmother", "grandma", "granny"],
    "Huntsman":    ["huntsman", "sportsman"],
}


def sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    # split after . ! ? plus an optional closing quote
    parts = re.split(r'(?<=[.!?])["\']?\s+', text)
    return [p.strip() for p in parts if p.strip()]


def split_long(sent, maxw):
    """Split a long sentence into <= maxw-word chunks at clause boundaries."""
    words = sent.split()
    if len(words) <= maxw:
        return [sent]
    clauses = re.split(r'(?<=[,;:])\s+', sent)
    chunks, cur = [], []
    for cl in clauses:
        cw = cl.split()
        if len(cw) > maxw:                      # a single clause too long -> hard split
            if cur:
                chunks.append(" ".join(cur)); cur = []
            for i in range(0, len(cw), maxw):
                chunks.append(" ".join(cw[i:i+maxw]))
            continue
        if len(cur) + len(cw) > maxw and cur:
            chunks.append(" ".join(cur)); cur = cw
        else:
            cur += cw
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def merge_small(chunks, minw, maxw):
    """Merge a too-short chunk into a neighbour, but never past maxw (so no beat
    exceeds the single-clip ceiling). Unmergeable short fragments stay as short beats."""
    out = []
    for c in chunks:
        if out and len(c.split()) < minw and len(out[-1].split()) + len(c.split()) <= maxw:
            out[-1] = out[-1] + " " + c
        else:
            out.append(c)
    if len(out) > 1 and len(out[0].split()) < minw and len(out[0].split()) + len(out[1].split()) <= maxw:
        out[1] = out[0] + " " + out[1]; out = out[1:]
    return out


def cast_present(text, cast_names):
    low = text.lower()
    present = []
    for name in cast_names:
        syns = SYNONYMS.get(name, [name.lower()])
        if any(s in low for s in syns):
            present.append(name)
    return present


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--meta-from", help="existing beat_sheet.json to lift metadata from")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--voice", default="TyW6NH39JcFb5M3xdIIk")
    ap.add_argument("--max-words", type=int, default=22)
    ap.add_argument("--min-words", type=int, default=7)
    ap.add_argument("-o", "--out", default="beat_sheet.json")
    args = ap.parse_args()

    text = Path(args.source).read_text(encoding="utf-8")

    meta = {"voice_id": args.voice, "style_bible": {}, "characters": []}
    if args.meta_from:
        src = json.loads(Path(args.meta_from).read_text())["metadata"]
        meta["voice_id"] = src.get("voice_id", args.voice)
        meta["style_bible"] = src.get("style_bible", {})
        meta["characters"] = src.get("characters", [])
        meta["aspect_ratio"] = src.get("aspect_ratio", "16:9")
        meta["style_preset"] = src.get("style_preset", "cinematic")
    meta["slug"] = args.slug
    meta["title"] = args.title
    cast_names = [c["name"] for c in meta.get("characters", [])]

    chunks = []
    for s in sentences(text):
        chunks.extend(split_long(s, args.max_words))
    chunks = merge_small(chunks, args.min_words, args.max_words)

    cams = ["push_in", "static", "slow_pan", "pull_back"]
    beats = []
    for i, c in enumerate(chunks, 1):
        beats.append({
            "beat_id": f"B{i:02d}",
            "narration_text": c,
            "tts_normalized_text": c,
            "scene_description": "",
            "characters_present": cast_present(c, cast_names),
            "camera": cams[i % len(cams)],
            "image_prompt": "",
            "video_prompt": "",
            "audio_file": None, "actual_duration_s": None, "word_timestamps": None, "clip_tier": None,
            "storyboard_candidates": [], "chosen_still": None, "raw_clip": None, "video_file": None,
        })

    Path(args.out).write_text(json.dumps({"metadata": meta, "beats": beats}, indent=2))
    wc = sum(len(b["narration_text"].split()) for b in beats)
    print(f"segmented {wc} words -> {len(beats)} beats  (max {args.max_words}, min {args.min_words} words)")
    print(f"wrote {args.out}")
    print("NOTE: image_prompt/video_prompt are EMPTY — author them in the storyboard phase. "
          "characters_present is heuristic; eyeball multi-character beats.")


if __name__ == "__main__":
    main()
