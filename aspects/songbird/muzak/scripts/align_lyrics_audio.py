#!/usr/bin/env python3
"""
align_lyrics_audio.py — REAL lyric timing via forced alignment.

The beat-grid seed from align_lyrics.py spreads lines evenly; it does not know
*when* a word is actually sung, so the screen drifts from the vocal. This script
fixes that:

  1. Whisper (faster-whisper) transcribes the audio WITH word-level timestamps.
     Whisper supplies the TIMING but may mis-hear sung words.
  2. We sequence-align Whisper's recognized words against the KNOWN lyrics (your
     song text). The lyrics supply the correct WORDS; the alignment snaps each
     correct word onto the timestamp of the recognized word it matches.
  3. Any lyric word Whisper dropped/mis-heard gets a timestamp interpolated
     between its anchored neighbours, so every word — and therefore every line —
     lands on a real moment in the audio.

Output is the same lyrics.json shape as align_lyrics.py (line -> start/end frames,
section, tag, density) PLUS a per-line `words` array of {text,startFrame,endFrame}
so the build can do true word-by-word / karaoke timing.

Whisper is an optional dependency. If faster-whisper isn't installed the script
prints an install hint and exits; the beat-grid seed remains a fallback.

Usage:
    python align_lyrics_audio.py song.txt --audio track.wav \
        --beat-data beat_data.json -o lyrics.json [--model base]
"""

import argparse
import json
import re
import sys
import unicodedata

# reuse the lyric parsing + density logic from the seed aligner
from align_lyrics import parse_lyrics, density, extract_title


def _norm(tok):
    """Normalize a token for matching: lowercase, strip accents + punctuation."""
    tok = unicodedata.normalize("NFKD", tok)
    tok = "".join(c for c in tok if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", tok.lower())


def whisper_words(audio_path, model_size="base", language="en", vad=False):
    """Return [(word, start_s, end_s), ...] from faster-whisper, or raise."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.stderr.write(
            "muzak: faster-whisper not installed. Install it (CPU is fine):\n"
            "    pip install faster-whisper\n"
            "(it pulls ctranslate2 + downloads a small model on first run).\n"
            "Until then, use align_lyrics.py for the beat-grid seed.\n"
        )
        raise SystemExit(2)

    # int8 on CPU keeps it light; bump model_size (small/medium) for better
    # timing on heavily sung/erratic vocals.
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    # vad_filter OFF by default: the speech VAD often clips SUNG intros over music,
    # which anchors the whole lyric block late. Turn it on only if needed.
    segments, _info = model.transcribe(
        audio_path, language=language, word_timestamps=True, vad_filter=vad
    )
    words = []
    for seg in segments:
        for w in (seg.words or []):
            text = w.word.strip()
            if text:
                words.append((text, float(w.start), float(w.end)))
    if not words:
        raise SystemExit("muzak: Whisper returned no word timestamps "
                         "(silent track or wrong --language?).")
    return words


def align(lyric_words, recognized):
    """Map each known lyric word to a (start_s, end_s) using the recognized
    word timestamps. lyric_words: list of dicts with 'text'. recognized:
    list of (word, start, end). Returns the lyric_words list with start/end set."""
    from difflib import SequenceMatcher

    lyr_norm = [_norm(w["text"]) for w in lyric_words]
    rec_norm = [_norm(r[0]) for r in recognized]

    # match the two token streams; autojunk off so common words still anchor
    sm = SequenceMatcher(a=lyr_norm, b=rec_norm, autojunk=False)
    for i in range(len(lyric_words)):
        lyric_words[i]["start"] = None
        lyric_words[i]["end"] = None

    for block in sm.get_matching_blocks():
        for k in range(block.size):
            li = block.a + k
            ri = block.b + k
            lyric_words[li]["start"] = recognized[ri][1]
            lyric_words[li]["end"] = recognized[ri][2]

    # interpolate words Whisper missed/misheard (still None) between anchors
    anchors = [i for i, w in enumerate(lyric_words) if w["start"] is not None]
    if not anchors:
        raise SystemExit("muzak: no lyric words could be aligned to the audio. "
                         "Try a larger --model, or check the lyrics match the song.")

    # head: before first anchor — back-fill from the first anchor
    first = anchors[0]
    for i in range(first):
        lyric_words[i]["start"] = lyric_words[first]["start"]
        lyric_words[i]["end"] = lyric_words[first]["start"]
    # tail: after last anchor — extend from the last anchor
    last = anchors[-1]
    for i in range(last + 1, len(lyric_words)):
        lyric_words[i]["start"] = lyric_words[last]["end"]
        lyric_words[i]["end"] = lyric_words[last]["end"]
    # gaps: linearly space the unmatched run between the two surrounding anchors
    for a, b in zip(anchors, anchors[1:]):
        gap = b - a
        if gap <= 1:
            continue
        t0 = lyric_words[a]["end"]
        t1 = lyric_words[b]["start"]
        span = max(t1 - t0, 0.0)
        for j in range(1, gap):
            frac = j / gap
            t = t0 + span * frac
            lyric_words[a + j]["start"] = t
            lyric_words[a + j]["end"] = t0 + span * ((j + 0.9) / gap)
    return lyric_words


def build_lines(stanzas, lyric_words, fps):
    """Group the timed words back into the original lines."""
    out = []
    wi = 0
    idx = 0
    for st in stanzas:
        for line in st["lines"]:
            n = len(line.split())
            wslice = lyric_words[wi:wi + n]
            wi += n
            if not wslice:
                continue
            start_s = min(w["start"] for w in wslice)
            end_s = max(w["end"] for w in wslice)
            out.append({
                "index": idx,
                "text": line,
                "section": None,            # filled below from beat sections
                "tag": st["tag"],
                "startFrame": int(round(start_s * fps)),
                "endFrame": int(round(max(end_s, start_s + 0.3) * fps)),
                "words": [
                    {"text": w["text"],
                     "startFrame": int(round(w["start"] * fps)),
                     "endFrame": int(round(max(w["end"], w["start"] + 0.1) * fps))}
                    for w in wslice
                ],
            })
            idx += 1
    return out


def tag_sections(lines, beat_data):
    secs = beat_data.get("sections") or []
    for ln in lines:
        f = ln["startFrame"]
        ln["section"] = next((s["label"] for s in secs
                              if s["startFrame"] <= f < s["endFrame"]),
                             secs[-1]["label"] if secs else "section_1")
    return lines


def main():
    ap = argparse.ArgumentParser(description="Forced-alignment lyric timing via Whisper.")
    ap.add_argument("lyrics", help="plain-text lyrics file")
    ap.add_argument("--audio", required=True, help="the song WAV/MP3")
    ap.add_argument("--beat-data", required=True, help="beat_data.json (for fps + sections)")
    ap.add_argument("-o", "--out", default="lyrics.json")
    ap.add_argument("--model", default="base",
                    help="faster-whisper model size (tiny/base/small/medium; default base)")
    ap.add_argument("--language", default="en")
    ap.add_argument("--vad", action="store_true",
                    help="enable Whisper voice-activity filter (default off; off catches sung intros)")
    args = ap.parse_args()

    beat_data = json.load(open(args.beat_data))
    fps = beat_data["fps"]
    text = open(args.lyrics).read()
    stanzas = parse_lyrics(text)
    if not any(st["lines"] for st in stanzas):
        sys.stderr.write("muzak: no lyric lines found.\n")
        sys.exit(1)

    flat = [{"text": w} for st in stanzas for line in st["lines"] for w in line.split()]

    print("muzak: transcribing with faster-whisper (%s) for word timestamps..." % args.model)
    recognized = whisper_words(args.audio, args.model, args.language, vad=args.vad)
    print("  recognized %d words; aligning to %d lyric words..." % (len(recognized), len(flat)))

    align(flat, recognized)
    lines = tag_sections(build_lines(stanzas, flat, fps), beat_data)

    data = {"version": 1, "fps": fps, "lines": lines,
            "timing_source": "whisper-forced-alignment",
            "density": density(stanzas, beat_data)}
    _title = extract_title(text)
    if _title:
        data["title"] = _title
    json.dump(data, open(args.out, "w"), indent=2)

    matched = sum(1 for w in flat if w.get("start") is not None)
    print("muzak: wrote %s" % args.out)
    print("  lines:    %d   words:  %d (%d anchored to audio, rest interpolated)"
          % (len(lines), len(flat), matched))
    print("  timing:   forced-aligned to the vocal (not a beat-grid guess)")
    dur_f = beat_data.get("durationInFrames") or (lines[-1]["endFrame"] if lines else 1)
    if lines and lines[0]["startFrame"] > 0.15 * dur_f:
        print("  WARNING: first caption at %.1fs (%.0f%% into the song). If vocals start"
              % (lines[0]["startFrame"] / fps, 100 * lines[0]["startFrame"] / dur_f))
        print("           earlier, Whisper missed the intro — re-run with a bigger --model"
              " (small/medium); leave --vad OFF.")
    for ln in lines[:6]:
        print("    f%-6d %-8s %s" % (ln["startFrame"], (ln["tag"] or ""), ln["text"][:46]))
    if len(lines) > 6:
        print("    ... (%d more)" % (len(lines) - 6))


if __name__ == "__main__":
    main()
