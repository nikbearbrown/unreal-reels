#!/usr/bin/env python3
"""
extract_slides.py — turn an HTML slide deck (.dc.html) into a beat_sheet.json
that the deck-lecture pipeline (and the existing generate_audio.py) can drive.

One slide = one beat. Each beat carries:
  - beat_id        S01, S02, ...           (stable id; mp3 is mp3/beat-S01.mp3)
  - slide_index    0-based DOM order        (the deck's location.hash #<index>)
  - label          data-label              (slide title chip)
  - speaker_notes  data-speaker-notes      (the SEED the script writer expands)
  - on_slide_text  visible text, collapsed (used for the discuss-don't-read guard)
  - narration_text ""                      (filled in Phase 1; what gets spoken)

The output is schema-compatible with bears-doodles/scripts/generate_audio.py:
it has metadata.voice_id and a `beats` array whose text comes from
narration_text — so Phase 2 audio reuses that script with no adapter.

Usage:
    python extract_slides.py "path/to/Deck.dc.html" -o path/to/lecture_folder
    python extract_slides.py "path/to/Deck.dc.html"          # writes next to deck

Pure stdlib (html.parser). No deps.
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOICE_ID_DEFAULT = "TyW6NH39JcFb5M3xdIIk"  # Bear's clone (repo default)


class SlideParser(HTMLParser):
    """Collect top-level <section> slides, their attrs, and their visible text.

    Slides are <section> elements that carry a data-label (every authored slide
    in the deck format has one). Nested <section>s are folded into their parent's
    text rather than treated as separate slides.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides = []
        self._depth = 0          # <section> nesting depth
        self._cur = None         # current slide dict being built
        self._skip_text = 0      # inside <script>/<style>: ignore text

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and "data-label" in a:
            if self._depth == 0:
                self._cur = {
                    "label": a.get("data-label", "").strip(),
                    "speaker_notes": (a.get("data-speaker-notes") or "").strip(),
                    "_text": [],
                    "_chart": False,   # set if any descendant has data-chart (live D3)
                }
            self._depth += 1
        elif tag in ("script", "style"):
            self._skip_text += 1
        # A [data-chart] element anywhere in the slide means the deck renders a live
        # D3 visual here (see the deck's slidechange handler) -> keep it live.
        if self._cur is not None and "data-chart" in a:
            self._cur["_chart"] = True

    def handle_endtag(self, tag):
        if tag == "section" and self._depth > 0:
            self._depth -= 1
            if self._depth == 0 and self._cur is not None:
                text = re.sub(r"\s+", " ", " ".join(self._cur["_text"])).strip()
                self.slides.append({
                    "label": self._cur["label"],
                    "speaker_notes": self._cur["speaker_notes"],
                    "on_slide_text": text,
                    "has_chart": self._cur["_chart"],
                })
                self._cur = None
        elif tag in ("script", "style") and self._skip_text > 0:
            self._skip_text -= 1

    def handle_data(self, data):
        if self._cur is not None and self._skip_text == 0:
            chunk = data.strip()
            if chunk:
                self._cur["_text"].append(chunk)


# fields carried over from an existing beat_sheet on re-extraction (so editing the
# deck and re-running never clobbers human work downstream of Phase 0)
PRESERVE = ("narration_text", "tts_normalized_text", "actual_duration_s", "audio_file")


def build_sheet(deck_path: Path, voice_id: str, fps: int, existing: dict | None = None) -> dict:
    html = deck_path.read_text(encoding="utf-8", errors="replace")
    p = SlideParser()
    p.feed(html)
    if not p.slides:
        sys.exit("[err] no <section data-label=...> slides found — is this a .dc.html deck?")

    prev = {}
    if existing:
        prev = {b["beat_id"]: b for b in existing.get("beats", [])}

    beats = []
    for i, s in enumerate(p.slides):
        bid = f"S{i + 1:02d}"
        beat = {
            "beat_id": bid,
            "slide_index": i,
            "label": s["label"],
            "speaker_notes": s["speaker_notes"],
            "on_slide_text": s["on_slide_text"],
            # "live" = slide has a D3 chart, keep it on-screen the whole slide;
            # "doodle" = hold the slide ~slide_hold_s, then cut to a doodle clip.
            "visual_mode": "live" if s["has_chart"] else "doodle",
            "narration_text": "",          # Phase 1 fills this (expand speaker_notes)
        }
        for k in PRESERVE:                  # carry over prior work if re-extracting
            if bid in prev and prev[bid].get(k):
                beat[k] = prev[bid][k]
        beats.append(beat)

    meta = (existing or {}).get("metadata", {})
    meta.update({
        "skill": "deck-lecture",
        "source_deck": deck_path.name,
        "voice_id": meta.get("voice_id", voice_id),
        "fps": meta.get("fps", fps),
        "tail_padding_s": meta.get("tail_padding_s", 0.4),
        "crossfade_frames": meta.get("crossfade_frames", 0),
        "slide_hold_s": meta.get("slide_hold_s", 3.5),   # live-slide hold before doodle
        "tts_voice_settings": meta.get("tts_voice_settings",
                                       {"stability": 0.45, "similarity_boost": 0.8, "style": 0.0}),
    })
    n_live = sum(1 for b in beats if b["visual_mode"] == "live")
    return {
        "metadata": meta,
        "counts": {"slides": len(beats), "live_d3": n_live, "doodle": len(beats) - n_live},
        "beats": beats,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck", help="Path to the .dc.html slide deck")
    ap.add_argument("-o", "--out", default=None,
                    help="Lecture folder to write beat_sheet.json into (default: deck's folder)")
    ap.add_argument("--voice-id", default=VOICE_ID_DEFAULT)
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()

    deck_path = Path(args.deck).expanduser()
    if not deck_path.exists():
        sys.exit(f"[err] deck not found: {deck_path}")

    out_dir = Path(args.out).expanduser() if args.out else deck_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    out = out_dir / "beat_sheet.json"
    existing = json.loads(out.read_text()) if out.exists() else None  # preserve prior work
    sheet = build_sheet(deck_path, args.voice_id, args.fps, existing)
    out.write_text(json.dumps(sheet, indent=2, ensure_ascii=False))

    c = sheet["counts"]
    print(f"[ok] wrote {out}{'  (merged, preserved prior narration)' if existing else ''}")
    print(f"[ok] {c['slides']} slides | {c['live_d3']} live-D3 · {c['doodle']} doodle "
          f"| voice {sheet['metadata']['voice_id']}")
    missing = [b["beat_id"] for b in sheet["beats"] if not b["speaker_notes"]]
    if missing:
        print(f"[warn] no data-speaker-notes on: {', '.join(missing)} "
              f"(script writer must work from on_slide_text for these)")
    print("[next] Phase 1: fill each beat's narration_text by EXPANDING speaker_notes "
          "(discuss the slide, don't read it).")


if __name__ == "__main__":
    main()
