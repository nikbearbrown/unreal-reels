#!/usr/bin/env python3
"""
align_lyrics.py — turn raw lyrics into a timed lyrics.json the Remotion
LyricLayer can render frame-by-frame.

This produces a *seed* timing, not a transcription. It distributes lyric lines
across the beat grid from beat_data.json so every line lands on a beat, then a
human nudges the anchors that matter (chorus hits, the drop). Getting timing
right here is far cheaper than discovering drift after a render.

Strategy:
  - Split lyrics into lines; blank lines separate stanzas. Lines like
    "[Chorus]" / "[Verse 2]" become section tags, not sung lines.
  - Map stanzas onto the analyzed sections (in order; if counts differ, fall
    back to spreading all lines evenly across all beats).
  - Within a section, give each line a contiguous run of beats so lines change
    on the beat. End frame = next line's start (minus a small gap).

Output schema (frames are at beat_data.json's fps):

    {
      "version": 1,
      "fps": 30,
      "lines": [
        {"index": 0, "text": "...", "section": "section_1",
         "tag": null|"Chorus", "startFrame": 0, "endFrame": 90}
      ]
    }

Usage:
    python align_lyrics.py lyrics.txt --beat-data beat_data.json -o lyrics.json
"""

import argparse
import json
import re
import sys

TAG_RE = re.compile(r"^\s*[\[(]\s*([A-Za-z][A-Za-z0-9 \-]*?)\s*[\])]\s*$")
TITLE_RE = re.compile(r"^\s*TITLE\s*:\s*(.+?)\s*$", re.IGNORECASE)


def extract_title(text):
    """Return the song title from a leading 'TITLE: ...' line, or None."""
    for raw in text.splitlines():
        m = TITLE_RE.match(raw)
        if m:
            return m.group(1).strip()
    return None


def parse_lyrics(text):
    """Return list of stanzas; each stanza = {tag, lines:[str]}."""
    stanzas = []
    cur = {"tag": None, "lines": []}
    pending_tag = None
    for raw in text.splitlines():
        line = raw.strip()
        if TITLE_RE.match(line):
            continue  # a TITLE: line is metadata, never a sung lyric
        if not line:
            if cur["lines"]:
                stanzas.append(cur)
                cur = {"tag": pending_tag, "lines": []}
                pending_tag = None
            continue
        m = TAG_RE.match(line)
        if m:
            # a tag on its own line starts a new stanza
            if cur["lines"]:
                stanzas.append(cur)
                cur = {"tag": None, "lines": []}
            cur["tag"] = m.group(1)
            continue
        cur["lines"].append(line)
    if cur["lines"]:
        stanzas.append(cur)
    return stanzas


def distribute(stanzas, beat_data, gap_frames=3):
    fps = beat_data["fps"]
    beat_frames = beat_data["beatFrames"] or [0, beat_data["durationInFrames"]]
    sections = beat_data.get("sections") or [{
        "startFrame": 0, "endFrame": beat_data["durationInFrames"], "label": "section_1"
    }]
    total_frames = beat_data["durationInFrames"]

    all_lines = []  # flat (text, tag, stanza_idx)
    for si, st in enumerate(stanzas):
        for ln in st["lines"]:
            all_lines.append((ln, st["tag"], si))

    if not all_lines:
        return {"version": 1, "fps": fps, "lines": []}

    # Map each stanza to a section when counts line up; else even spread.
    use_sections = len(stanzas) == len(sections) and len(stanzas) > 1
    out = []

    def beats_in(a, b):
        bs = [f for f in beat_frames if a <= f < b]
        return bs or [a]

    if use_sections:
        idx = 0
        for st, sec in zip(stanzas, sections):
            sbs = beats_in(sec["startFrame"], sec["endFrame"])
            n = len(st["lines"])
            # assign each line a roughly equal slice of this section's beats
            for li, ln in enumerate(st["lines"]):
                start = sbs[min(int(li * len(sbs) / n), len(sbs) - 1)]
                nxt = sbs[min(int((li + 1) * len(sbs) / n), len(sbs) - 1)]
                end = (nxt if nxt > start else sec["endFrame"]) - gap_frames
                out.append({
                    "index": idx, "text": ln, "section": sec["label"],
                    "tag": st["tag"],
                    "startFrame": int(start), "endFrame": int(max(start + fps // 2, end)),
                })
                idx += 1
    else:
        # even spread of all lines across all beats
        n = len(all_lines)
        # choose anchor beats spaced through the song
        anchors = [beat_frames[min(int(i * len(beat_frames) / n), len(beat_frames) - 1)]
                   for i in range(n)]
        anchors.append(total_frames)
        for i, (ln, tag, _si) in enumerate(all_lines):
            start = anchors[i]
            end = anchors[i + 1] - gap_frames
            # section label for context
            label = next((s["label"] for s in sections
                          if s["startFrame"] <= start < s["endFrame"]), sections[-1]["label"])
            out.append({
                "index": i, "text": ln, "section": label, "tag": tag,
                "startFrame": int(start), "endFrame": int(max(start + fps // 2, end)),
            })

    return {"version": 1, "fps": fps, "lines": out}


def density(stanzas, beat_data):
    """Words-per-second + density class — constrains which lyric animation
    styles are even legible (see references/design-inference.md). Fast lyrics
    physically can't use character-by-character springs; they'd never finish."""
    dur = beat_data.get("durationInSeconds") or 1.0
    sung = [ln for st in stanzas for ln in st["lines"]]
    n_words = sum(len(ln.split()) for ln in sung)
    wps = n_words / dur if dur else 0.0
    if wps < 1.5:
        cls = "sparse"      # ballad — character/word springs fine
    elif wps < 2.5:
        cls = "moderate"    # pop — word-by-word fine
    elif wps < 3.5:
        cls = "dense"       # fast verse — line-at-a-time only
    else:
        cls = "rapid"       # rap — instant appear, opacity only
    avg_len = (sum(len(ln.split()) for ln in sung) / len(sung)) if sung else 0.0
    return {
        "words_per_second": round(wps, 2),
        "density_class": cls,
        "avg_line_length": round(avg_len, 1),
        "line_count": len(sung),
        "word_count": n_words,
    }


def main():
    ap = argparse.ArgumentParser(description="Seed lyric timing from the beat grid.")
    ap.add_argument("lyrics", help="plain-text lyrics file")
    ap.add_argument("--beat-data", required=True, help="beat_data.json from analyze_audio")
    ap.add_argument("-o", "--out", default="lyrics.json")
    ap.add_argument("--gap", type=int, default=3, help="frames of gap between lines")
    args = ap.parse_args()

    with open(args.lyrics) as f:
        text = f.read()
    with open(args.beat_data) as f:
        beat_data = json.load(f)

    stanzas = parse_lyrics(text)
    if not any(st["lines"] for st in stanzas):
        sys.stderr.write("muzak: no lyric lines found in %s\n" % args.lyrics)
        sys.exit(1)

    data = distribute(stanzas, beat_data, args.gap)
    data["density"] = density(stanzas, beat_data)
    title = extract_title(text)
    if title:
        data["title"] = title
    with open(args.out, "w") as f:
        json.dump(data, f, indent=2)

    d = data["density"]
    print("muzak: wrote %s" % args.out)
    print("  lines:    %d  across %d stanza(s)"
          % (len(data["lines"]), len(stanzas)))
    print("  density:  %.2f words/sec  -> %s (constrains lyric animation style)"
          % (d["words_per_second"], d["density_class"]))
    print("  note:     timing is a beat-grid SEED — review the lines and nudge anchors.")
    for ln in data["lines"][:6]:
        print("    f%-6d %-9s %s" % (ln["startFrame"], (ln["tag"] or ""), ln["text"][:48]))
    if len(data["lines"]) > 6:
        print("    ... (%d more)" % (len(data["lines"]) - 6))


if __name__ == "__main__":
    main()
