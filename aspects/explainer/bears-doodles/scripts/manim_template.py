#!/usr/bin/env python3
"""
manim_template.py — Bear's Notes Manim scene scaffold.

Copy this into a video folder, rename to <slug_underscored>.py, and fill in one
draw method per `render: manim` beat (named draw_<BEAT_ID>, e.g. draw_A00).

What the scaffold gives you for free:
  • reads beat_sheet.json + mp3/timings.json from the folder it runs in
  • white background, Shadows Into Light for text, metadata colors (Warm Slate
    accent, red forbidden)
  • an INTRO title card ("Bear's Notes" + title)
  • per-beat timing pulled from the REAL audio durations (timings.json)
  • automatic self.add_sound("mp3/beat-<ID>.mp3") at the start of each beat
  • CUT = fade everything out; HOLD = hold the static scene; INTRO/none beats
    just play their audio over the current frame

Render:
    ai                                  # activate the ~/ai venv
    manim -pqh <slug_underscored>.py BearsDoodlesVideo      # 1080p
    manim -pql <slug_underscored>.py BearsDoodlesVideo      # fast preview

Output: media/videos/<file>/<quality>/BearsDoodlesVideo.mp4
"""
import json
from pathlib import Path

from manim import *  # noqa: F401,F403

HERE = Path(__file__).resolve().parent
SHEET = json.loads((HERE / "beat_sheet.json").read_text())
TIMINGS_PATH = HERE / "mp3" / "timings.json"
TIMINGS = json.loads(TIMINGS_PATH.read_text()) if TIMINGS_PATH.exists() else {}

META = SHEET["metadata"]
INK = "#1a1a1a"
ACCENT = META.get("accent_color", "#5A5653")
FORBIDDEN = META.get("forbidden_color", "#C0392B")
FONT = META.get("text_font", "Shadows Into Light")
TITLE = META.get("title", "")


def dur(beat_id: str, fallback: float = 4.0) -> float:
    """Real audio duration for a beat; falls back if timings.json is missing it."""
    return float(TIMINGS.get(beat_id, fallback))


def label(text: str, size: int = 36, color: str = INK):
    return Text(text, font=FONT, font_size=size, color=color)


def _wrap(text: str, words_per_line: int = 6):
    """Split a sentence into ~equal lines for a multi-line text card."""
    words = text.split()
    return [" ".join(words[i:i + words_per_line]) for i in range(0, len(words), words_per_line)] or [""]


class BearsDoodlesVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        for beat in SHEET["beats"]:
            bid = beat["beat_id"]
            btype = beat["beat_type"]
            audio = beat.get("audio_file") or f"mp3/beat-{bid}.mp3"
            if (HERE / audio).exists():
                self.add_sound(str(HERE / audio))

            if btype == "INTRO":
                self._intro(dur(bid, 3.0))
                continue
            if btype == "CUT":
                # clear the canvas to white before the new scene's first element
                if self.mobjects:
                    self.play(FadeOut(*self.mobjects), run_time=0.4)
                    self.wait(0.1)

            method = getattr(self, f"draw_{bid}", None)
            if method is not None:
                method(dur(bid))
            elif btype == "HOLD":
                self.wait(dur(bid, 2.0))
            else:
                # No bespoke draw method (e.g. a hook beat): render a real, on-brand
                # text card from the narration so Manim + voiceover stands alone.
                # An SVG icon / hand doodle can be overlaid on this window later, but
                # nothing here is a placeholder — it is finished content.
                self._text_card(beat.get("narration_text", ""), dur(bid))

    # ── narration text card (default for beats without a draw_<ID> method) ─────
    def _text_card(self, text: str, t: float):
        text = " ".join((text or "").split())
        card = label(text, size=40, color=INK)
        if card.width > 11.5:                      # wrap long lines to the safe area
            card = Paragraph(*_wrap(text, 6), font=FONT, font_size=38, color=INK,
                             alignment="center", line_spacing=0.8)
            if card.width > 11.5:
                card.scale_to_fit_width(11.5)
        self.play(Write(card), run_time=min(1.8, t * 0.45))
        self.wait(max(0.2, t - min(1.8, t * 0.45) - 0.3))
        self.play(FadeOut(card), run_time=0.3)

    # ── INTRO title card ─────────────────────────────────────────────────────
    def _intro(self, t: float):
        brand = label("Bear's Notes", size=54)
        title = label(TITLE, size=38, color=ACCENT).next_to(brand, DOWN, buff=0.5)
        self.play(Write(brand), run_time=min(1.6, t * 0.4))
        self.play(Write(title), run_time=min(1.6, t * 0.4))
        self.wait(max(0.2, t - 3.2))
        self.play(FadeOut(brand, title), run_time=0.4)

    # ─────────────────────────────────────────────────────────────────────────
    # FILL IN ONE METHOD PER manim BEAT. Each receives `t` = real audio duration.
    # Use self.play(..., run_time=...) and self.wait(...) so total ≈ t.
    # Keep new content centered in the middle third of frame to avoid edge warp.
    #
    # Worked example (delete if not "particle in a box"):
    #
    # def draw_A00(self, t):
    #     left = Line([-3.5, 1.5, 0], [-3.5, -1.5, 0], color=INK, stroke_width=6)
    #     right = Line([3.5, 1.5, 0], [3.5, -1.5, 0], color=INK, stroke_width=6)
    #     dot = Dot([0, 0, 0], color=INK)
    #     self.play(Create(left), Create(right), run_time=t * 0.6)
    #     self.play(GrowFromCenter(dot), run_time=t * 0.2)
    #     self.wait(max(0.1, t * 0.2))
    # ─────────────────────────────────────────────────────────────────────────
