"""
bio_max_planck.py  —  Bear's Notes "bio" pipeline prototype (Max Planck).
16:9, SILENT; assemble.py muxes Bear's voiceover.

The cut ALTERNATES (audio-first): render:"manim" beats are clean DARK cinematic cards
(title / equation / date); render:"clip" beats are full-frame Higgsfield footage, shown
here as a labeled PLACEHOLDER until composite_clips.py drops the real footage in.

TIMING CONTRACT: every beat's on-screen time (fade-out included) equals its narration
length dur(bid) EXACTLY — so the master timeline matches the audio, and the footage
windows composite_clips computes from the same durations land on the right cuts. Do not
add animation time on top of a beat's budget.

Palette: white on near-black, grey for secondary. No accent colour. Montserrat throughout.

Run:
    ai
    python ../../bears-doodles/scripts/generate_audio.py .
    manim -qh bio_max_planck.py BearsDoodlesVideo
    python ../../bears-doodles/scripts/composite_clips.py .
    python ../../bears-doodles/scripts/assemble.py . --mode manim --manim-mp4 mp4/_composited.mp4
"""
import json
from pathlib import Path

from manim import *

import bn_layout as BL                         # orientation engine (16:9 + 9:16)
from bn_layout import is_portrait, band, fit

try:
    import manimpango
except Exception:
    manimpango = None


def _reframe(*mobs):
    """In portrait, scale+center the card into the safe band (cards reflow, never crop).
    Landscape keeps the designed layout. Footage cropping is handled by composite_clips."""
    if is_portrait():
        fit(VGroup(*mobs), band(), 0.95)

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"

BG    = "#0E0E12"
INK   = "#F2F0EC"      # primary — white on black
DIM   = "#8A8780"      # secondary — grey
RULE  = "#F2F0EC"      # divider lines: white (no blue)
FONT  = "Montserrat"

if manimpango is not None:
    for _f in ("Montserrat-Bold.ttf", "Montserrat-Medium.ttf",
               "Montserrat-Regular.ttf", "Montserrat-Light.ttf"):
        try:
            manimpango.register_font(str(FONTS / _f))
        except Exception:
            pass

_BS = json.loads((HERE / "beat_sheet.json").read_text())
_BEATS = _BS["beats"]
_tp = HERE / "mp3" / "timings.json"
_T = json.loads(_tp.read_text()) if _tp.exists() else {}
_FB = {b["beat_id"]: float(b.get("actual_duration_s", 4.0)) for b in _BEATS}


def dur(bid):
    return float(_T.get(bid, _FB.get(bid, 4.0)))


def txt(s, size, color=INK, weight="MEDIUM"):
    return Text(s, font=FONT, weight=weight, font_size=size, color=color)


def wrap(s, max_chars=34):
    """Greedy word-wrap into lines (Manim Text has no auto-wrap)."""
    words, lines, cur = s.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def tracked(s, size, color, weight="BOLD", track=0.22):
    groups = []
    em = size / 100.0
    for w in s.split(" "):
        g = VGroup(*[Text(c, font=FONT, weight=weight, font_size=size, color=color) for c in w])
        em = max((l.height for l in g), default=size / 100.0) / 0.7
        g.arrange(RIGHT, buff=track * em)
        groups.append(g)
    return VGroup(*groups).arrange(RIGHT, buff=track * em * 3.0)


class BearsDoodlesVideo(Scene):
    def construct(self):
        self.camera.background_color = BG
        for b in _BEATS:
            t = dur(b["beat_id"])
            if b.get("render") == "clip":
                self._placeholder(b, t)
            else:
                getattr(self, f"_card_{b['card']['kind']}")(b["card"], t)

    # ── clip placeholder (covered by footage in composite) ────────────────────
    def _placeholder(self, b, t):
        fade = 0.35
        frame = DashedVMobject(
            Rectangle(width=11.4, height=6.0, color=DIM, stroke_width=2).move_to([0, 0.3, 0]),
            num_dashes=64)
        tag = tracked("FOOTAGE", 30, INK, "BOLD").move_to([0, 1.4, 0])
        holes = VGroup(*[Square(0.18, color=DIM, stroke_width=2).move_to([x, 1.4, 0])
                         for x in (-2.6, -2.2, 2.2, 2.6)])
        shot = txt(b.get("shot", ""), 24, INK, "MEDIUM")
        if shot.width > 9.5:
            shot.scale_to_fit_width(9.5)
        shot.move_to([0, -0.1, 0])
        src = txt(f"[{b.get('clip_source','clip')}]", 20, DIM, "MEDIUM").move_to([0, -1.4, 0])
        grp = VGroup(frame, tag, holes, shot, src)
        _reframe(grp)
        r1 = min(0.7, t * 0.2)
        r2 = min(0.8, t * 0.22)
        self.play(Create(frame), FadeIn(tag), FadeIn(holes), run_time=r1)
        self.play(FadeIn(shot, shift=UP * 0.1), FadeIn(src), run_time=r2)
        self.wait(max(0.1, t - r1 - r2 - fade))
        self.play(FadeOut(grp), run_time=fade)

    # ── cards ─────────────────────────────────────────────────────────────────
    def _card_title(self, c, t):
        fade = 0.4
        name = tracked(c["name"], 64, INK, "BOLD").move_to([0, 0.5, 0])
        if name.width > 12:
            name.scale_to_fit_width(12)
        rule = Line([-name.width / 2, -0.25, 0], [name.width / 2, -0.25, 0], color=RULE, stroke_width=3)
        dates = txt(c["dates"], 30, DIM, "LIGHT").move_to([0, -0.95, 0])
        _reframe(name, rule, dates)
        r1 = min(1.3, t * 0.4)
        r2 = min(1.0, t * 0.28)
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.15) for g in name], lag_ratio=0.08), run_time=r1)
        self.play(Create(rule), FadeIn(dates), run_time=r2)
        self.wait(max(0.2, t - r1 - r2 - fade))
        self.play(FadeOut(name, rule, dates), run_time=fade)

    def _card_equation(self, c, t):
        fade = 0.4
        label = txt(c.get("label", "").upper(), 24, DIM, "MEDIUM").move_to([0, 1.4, 0])
        eq = MathTex(c["tex"], color=INK).scale(2.4).move_to([0, -0.1, 0])
        if eq.width > 11:
            eq.scale_to_fit_width(11)
        _reframe(label, eq)
        r1 = min(0.7, t * 0.22)
        r2 = min(1.5, t * 0.4)
        self.play(FadeIn(label, shift=DOWN * 0.1), run_time=r1)
        self.play(Write(eq), run_time=r2)
        self.wait(max(0.2, t - r1 - r2 - fade))
        self.play(FadeOut(label, eq), run_time=fade)

    def _card_quote(self, c, t):
        fade = 0.4
        label = txt(c.get("label", "").upper(), 24, DIM, "MEDIUM").move_to([0, 1.7, 0])
        body = wrap(c.get("text", ""), c.get("wrap", 34))
        quote = Text(body, font=FONT, weight="LIGHT", font_size=40, color=INK,
                     line_spacing=0.8).move_to([0, -0.1, 0])
        if quote.width > 11:
            quote.scale_to_fit_width(11)
        if quote.height > 4.4:
            quote.scale_to_fit_height(4.4)
        _reframe(label, quote)
        r1 = min(0.7, t * 0.22)
        r2 = min(1.5, t * 0.4)
        self.play(FadeIn(label, shift=DOWN * 0.1), run_time=r1)
        self.play(Write(quote), run_time=r2)
        self.wait(max(0.2, t - r1 - r2 - fade))
        self.play(FadeOut(label, quote), run_time=fade)

    def _card_date(self, c, t):
        fade = 0.4
        big = tracked(c["big"], 96, INK, "BOLD").move_to([0, 0.55, 0])
        rule = Line([-2.2, -0.5, 0], [2.2, -0.5, 0], color=RULE, stroke_width=3)
        label = txt(c.get("label", "").upper(), 26, DIM, "MEDIUM").move_to([0, -1.2, 0])
        _reframe(big, rule, label)
        r1 = min(1.0, t * 0.36)
        r2 = min(0.9, t * 0.28)
        self.play(FadeIn(big, scale=1.08), run_time=r1)
        self.play(Create(rule), FadeIn(label), run_time=r2)
        self.wait(max(0.2, t - r1 - r2 - fade))
        self.play(FadeOut(big, rule, label), run_time=fade)
