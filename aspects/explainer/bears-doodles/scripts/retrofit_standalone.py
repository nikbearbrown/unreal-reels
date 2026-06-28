#!/usr/bin/env python3
"""
retrofit_standalone.py — make existing Bear's Doodles Manim masters self-sufficient.

Older scene files render their hook/doodle beats as PLACEHOLDER boxes
("[ doodle: ... ]" / "[doodle A00 ...]"), which is fine only if you overlay art.
Under the new philosophy (Manim + voiceover is the complete video), those beats
should render real content. This rewrites the placeholder draw to a clean narration
TEXT CARD — pulled from the beat sheet — while preserving the exact per-beat timing
(so the muxed voiceover stays in sync). Idempotent; safe to re-run.

Two placeholder families are handled:
  A) self._hook(self, bid, label) / self._hook_beat(...) + self._marker()
  B) self.doodle(self, bid, label) + self.doodle_box(...)   (and the intro corner mark)

Usage:
    python retrofit_standalone.py ~/Documents/Cowork/Manim          # all videos
    python retrofit_standalone.py ~/Documents/Cowork/Manim/<folder> # one video
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CARD_A = '''_bsp = HERE / "beat_sheet.json"
_NARR = {b["beat_id"]: b.get("narration_text", "") for b in (
    __import__("json").loads(_bsp.read_text()).get("beats", []) if _bsp.exists() else [])}


def _card(s, _sz=40):
    ws = s.split()
    lines = [" ".join(ws[i:i + 6]) for i in range(0, len(ws), 6)] or [""]
    g = VGroup(*[Text(l, font=FONT, font_size=_sz, color=INK) for l in lines]).arrange(DOWN, buff=0.28)
    if g.width > 11.5:
        g.scale_to_fit_width(11.5)
    return g


'''

CARD_B = '''_NARR = {b["beat_id"]: b.get("narration_text", "") for b in SHEET.get("beats", [])}


def _card(s, _sz=40):
    ws = s.split()
    lines = [" ".join(ws[i:i + 6]) for i in range(0, len(ws), 6)] or [""]
    g = VGroup(*[txt(l, size=_sz) for l in lines]).arrange(DOWN, buff=0.28)
    if g.width > 11.5:
        g.scale_to_fit_width(11.5)
    return g


'''

HOOK_BODY = '''    def {name}(self, bid, label):
        t = dur(bid)
        card = _card(_NARR.get(bid, label))
        rt = min(1.6, t * 0.45)
        self.play(Write(card), run_time=rt)
        self.wait(max(0.2, t - rt - 0.4))
        self.play(FadeOut(card), run_time=0.4)
'''

DOODLE_BODY = '''    def doodle(self, bid, label):
        self.remove_all()
        card = _card(_NARR.get(bid, label))
        self.play(Write(card), run_time=1.0)
        self.hold(bid, 1.0)
'''


def scene_files(root: Path):
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*.py")):
        if "_svg_doodles" in p.name or p.name in ("svg_tester.py",):
            continue
        try:
            txt = p.read_text()
        except Exception:
            continue
        if "class BearsDoodlesVideo(Scene)" in txt:
            yield p


def retrofit(path: Path) -> str:
    src = path.read_text()
    if "_NARR" in src and "_card(" in src:
        return "skip (already retrofitted)"

    is_b = "def doodle(self, bid, label):" in src
    is_a = re.search(r"def _hook(?:_beat)?\(self, bid, label\):", src) is not None
    if not (is_a or is_b):
        return "skip (no known placeholder pattern)"

    # inject helper block just before the class definition
    block = CARD_B if is_b else CARD_A
    src = src.replace("class BearsDoodlesVideo(Scene):", block + "class BearsDoodlesVideo(Scene):", 1)

    if is_b:
        # rewrite the doodle() method body (keep timing via self.hold)
        src = re.sub(r"\n    def doodle\(self, bid, label\):.*?(?=\n    def |\nclass |\Z)",
                     "\n" + DOODLE_BODY.rstrip("\n"), src, count=1, flags=re.DOTALL)
        # drop the intro corner placeholder mark
        src = re.sub(r"\n[ \t]*mark = self\.doodle_box\([^\n]*", "", src)
        src = src.replace(", Create(mark)", "").replace("Create(mark), ", "").replace("Create(mark)", "")
    if is_a:
        for name in ("_hook", "_hook_beat"):
            if f"def {name}(self, bid, label):" in src:
                src = re.sub(rf"\n    def {name}\(self, bid, label\):.*?(?=\n    def |\nclass |\Z)",
                             "\n" + HOOK_BODY.format(name=name).rstrip("\n"), src, count=1, flags=re.DOTALL)

    path.write_text(src)
    return f"retrofitted ({'doodle' if is_b else 'hook'} family)"


def main(argv=None) -> int:
    root = Path((argv or sys.argv[1:])[0]).expanduser().resolve() if (argv or sys.argv[1:]) \
        else Path("~/Documents/Cowork/Manim").expanduser()
    files = list(scene_files(root))
    if not files:
        print(f"no BearsDoodlesVideo scene files under {root}")
        return 1
    for p in files:
        print(f"{p.parent.name:48} {retrofit(p)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
