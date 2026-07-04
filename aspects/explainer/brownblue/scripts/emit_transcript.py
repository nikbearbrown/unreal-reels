#!/usr/bin/env python3
"""
emit_transcript.py — YouTube-ready caption/transcript files from the beat sheet.

Uploading YOUR transcript to YouTube makes its closed captions use the exact
narration — correct spelling, symbols, punctuation — instead of ASR guesswork,
and it's better for search/accessibility. Because audio is the master clock,
one beat = one sentence = one caption cue, timestamped by cumulative
actual_duration_s (the real spoken lengths).

Writes, next to the video:
    <slug>.srt              timed cues (upload this in YouTube Studio → Subtitles)
    <slug>.vtt              WebVTT (same content; players/other platforms)
    <slug>-transcript.txt   plain running text (paste into the description / notes)

If captions.json (from align_captions.py) exists, cue END times are tightened to
the last spoken word per beat so trailing animation silence isn't captioned.

Usage:
    python emit_transcript.py <folder> [--include-intro/--no-intro]
"""
import argparse
import json
import re
from pathlib import Path


def clean(s):
    s = (s or "").replace("\n\n", "\n").strip()
    # collapse intra-line whitespace but keep intentional line breaks
    return "\n".join(re.sub(r"\s+", " ", ln).strip() for ln in s.split("\n") if ln.strip())


def ts(sec, sep=","):
    sec = max(0.0, sec)
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--no-intro", dest="intro", action="store_false")
    ap.add_argument("--slug", default=None)
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    slug = args.slug or sheet["metadata"].get("slug", folder.name)

    # optional word timings to tighten ends
    caps = {}
    cpath = folder / "captions.json"
    if cpath.exists():
        blob = json.loads(cpath.read_text())
        fps = float(blob.get("fps", 30))
        for bid, b in blob.get("slides", {}).items():
            ws = [w for ln in b.get("lines", []) for w in ln.get("words", [])]
            if ws:
                caps[bid] = ws[-1]["endFrame"] / fps   # last spoken moment (beat-local)

    cues, plain = [], []
    t = 0.0
    for beat in sheet["beats"]:
        bid = beat["beat_id"]
        dur = float(beat.get("actual_duration_s", 0.0))
        if bid == "INTRO" and not args.intro:
            t += dur
            continue
        text = clean(beat.get("narration_text", ""))
        if text:
            spoken_end = caps.get(bid)
            end = t + (min(dur, spoken_end + 0.25) if spoken_end else dur) - 0.03
            end = max(end, t + 0.4)
            cues.append((t, end, text))
            plain.append(text.replace("\n", " "))
        t += dur

    # SRT
    srt = []
    for i, (a, b, text) in enumerate(cues, 1):
        srt.append(str(i))
        srt.append(f"{ts(a)} --> {ts(b)}")
        srt.append(text)
        srt.append("")
    (folder / f"{slug}.srt").write_text("\n".join(srt), encoding="utf-8")

    # VTT
    vtt = ["WEBVTT", ""]
    for a, b, text in cues:
        vtt.append(f"{ts(a, '.')} --> {ts(b, '.')}")
        vtt.append(text)
        vtt.append("")
    (folder / f"{slug}.vtt").write_text("\n".join(vtt), encoding="utf-8")

    # plain transcript
    (folder / f"{slug}-transcript.txt").write_text(" ".join(plain) + "\n", encoding="utf-8")

    print(f"[ok] {len(cues)} cues → {slug}.srt, {slug}.vtt, {slug}-transcript.txt")
    print(f"[i] total {ts(t)} — upload {slug}.srt in YouTube Studio → Subtitles → Add → Upload (with timing).")


if __name__ == "__main__":
    main()
