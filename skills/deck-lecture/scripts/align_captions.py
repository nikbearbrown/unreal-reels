#!/usr/bin/env python3
"""
align_captions.py — per-slide karaoke captions via forced alignment.

Same mechanism as the music-video pipeline (aspects/songbird/muzak/scripts/
align_lyrics_audio.py): the narration TEXT is already known (it's what we sent to
ElevenLabs), so we don't transcribe blind. faster-whisper supplies word-level
TIMING from the generated mp3; we sequence-align the KNOWN words onto those
timestamps; words Whisper missed get interpolated between anchors. Every caption
word therefore lands on the real moment it is spoken — exact text, no drift.

Reads <folder>/beat_sheet.json (after Phase 2 audio, so each beat has
narration_text + audio_file) and writes <folder>/captions.json:

    {
      "fps": 30,
      "slides": {
        "S01": {"lines": [
          {"text": "...", "startFrame": 0, "endFrame": 54,
           "words": [{"text": "Three", "startFrame": 0, "endFrame": 9}, ...]}
        ]}
      }
    }

Frames are LOCAL to each slide (slide-local frame 0 = start of that slide's
audio), which is what the Remotion <Sequence> for that slide expects.

Usage:
    python align_captions.py path/to/lecture_folder [--model base] [--max-line-words 9]

faster-whisper is an optional dep:  pip install faster-whisper
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


def norm(tok: str) -> str:
    tok = unicodedata.normalize("NFKD", tok)
    tok = "".join(c for c in tok if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", tok.lower())


def split_lines(text: str, max_words: int):
    """Break narration into readable caption lines: sentence-first, then wrap
    long sentences at ~max_words on clause boundaries."""
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?;:])\s+", text)
    lines = []
    for sent in sentences:
        words = sent.split()
        if not words:
            continue
        i = 0
        while i < len(words):
            chunk = words[i:i + max_words]
            lines.append(" ".join(chunk))
            i += max_words
    return [ln for ln in lines if ln.strip()]


def whisper_words(audio_path: str, model_size: str, language: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit(
            "deck-lecture: faster-whisper not installed. Install it (CPU is fine):\n"
            "    pip install faster-whisper\n"
            "(pulls ctranslate2 + downloads a small model on first run)."
        )
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, language=language, word_timestamps=True)
    out = []
    for seg in segments:
        for w in (seg.words or []):
            t = w.word.strip()
            if t:
                out.append((t, float(w.start), float(w.end)))
    return out


def align_words(lyric_words, recognized):
    """Map each known word (list of {text}) onto (start,end) seconds from the
    recognized stream via sequence matching + neighbour interpolation."""
    from difflib import SequenceMatcher
    for w in lyric_words:
        w["start"] = w["end"] = None
    a = [norm(w["text"]) for w in lyric_words]
    b = [norm(r[0]) for r in recognized]
    sm = SequenceMatcher(a=a, b=b, autojunk=False)
    for ai, bi, size in sm.get_matching_blocks():
        for k in range(size):
            lyric_words[ai + k]["start"] = recognized[bi + k][1]
            lyric_words[ai + k]["end"] = recognized[bi + k][2]

    anchors = [i for i, w in enumerate(lyric_words) if w["start"] is not None]
    if not anchors:
        # No alignment at all — fall back to even spread across the clip later.
        return None
    first, last = anchors[0], anchors[-1]
    for i in range(first):
        lyric_words[i]["start"] = lyric_words[first]["start"]
        lyric_words[i]["end"] = lyric_words[first]["start"]
    for i in range(last + 1, len(lyric_words)):
        lyric_words[i]["start"] = lyric_words[last]["end"]
        lyric_words[i]["end"] = lyric_words[last]["end"]
    for idx in range(len(anchors) - 1):
        a0, a1 = anchors[idx], anchors[idx + 1]
        gap = a1 - a0
        if gap <= 1:
            continue
        t0 = lyric_words[a0]["end"]
        t1 = lyric_words[a1]["start"]
        span = max(t1 - t0, 0.0)
        for j in range(1, gap):
            t = t0 + span * (j / gap)
            lyric_words[a0 + j]["start"] = t
            lyric_words[a0 + j]["end"] = t0 + span * ((j + 0.9) / gap)
    return lyric_words


def even_spread(lyric_words, duration_s):
    n = len(lyric_words)
    per = duration_s / max(n, 1)
    for i, w in enumerate(lyric_words):
        w["start"] = i * per
        w["end"] = (i + 0.9) * per
    return lyric_words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="Lecture folder (has beat_sheet.json + mp3/)")
    ap.add_argument("--model", default="base", help="faster-whisper model size")
    ap.add_argument("--language", default="en")
    ap.add_argument("--max-line-words", type=int, default=9)
    ap.add_argument("--only", nargs="*", help="only these beat_ids")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser()
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    fps = sheet["metadata"].get("fps", 30)

    out_path = folder / "captions.json"
    captions = {"fps": fps, "slides": {}}
    if out_path.exists():
        captions = json.loads(out_path.read_text())
        captions["fps"] = fps

    for beat in sheet["beats"]:
        bid = beat["beat_id"]
        if args.only and bid not in args.only:
            continue
        # Captions DISPLAY the correctly-spelled narration_text, never the
        # respelled tts_normalized_text. Word order/count match (respelling is an
        # in-place token swap), so this still aligns against the spoken audio.
        text = (beat.get("narration_text") or beat.get("tts_normalized_text") or "").strip()
        audio_rel = beat.get("audio_file")
        if not text or not audio_rel:
            print(f"[skip] {bid}: no narration_text/audio yet")
            continue
        audio_path = folder / audio_rel
        if not audio_path.exists():
            print(f"[skip] {bid}: missing {audio_rel}")
            continue

        dur = float(beat.get("actual_duration_s", 0.0))
        lines_text = split_lines(text, args.max_line_words)
        # flat word list across all lines, remembering line boundaries
        line_lens = [len(ln.split()) for ln in lines_text]
        flat = [{"text": w} for ln in lines_text for w in ln.split()]

        recognized = whisper_words(str(audio_path), args.model, args.language)
        timed = align_words(flat, recognized) if recognized else None
        if timed is None:
            timed = even_spread(flat, dur)

        # regroup into lines, convert seconds -> slide-local frames
        lines = []
        wi = 0
        for ln_text, n in zip(lines_text, line_lens):
            ws = timed[wi:wi + n]
            wi += n
            words = [{
                "text": w["text"],
                "startFrame": max(0, round(w["start"] * fps)),
                "endFrame": max(0, round(w["end"] * fps)),
            } for w in ws]
            lines.append({
                "text": ln_text,
                "startFrame": words[0]["startFrame"] if words else 0,
                "endFrame": words[-1]["endFrame"] if words else round(dur * fps),
                "words": words,
            })
        captions["slides"][bid] = {"lines": lines}
        print(f"[ok] {bid}: {len(lines)} caption lines, {len(flat)} words aligned")

    out_path.write_text(json.dumps(captions, indent=2, ensure_ascii=False))
    print(f"[ok] wrote {out_path}")


if __name__ == "__main__":
    main()
