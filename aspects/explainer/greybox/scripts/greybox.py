#!/usr/bin/env python3
"""
greybox.py — zero-cost scrapbook previz from a shared-schema beat_sheet.json.

Game-dev greyboxing for explainer videos: one beat = one torn-paper cutout on
a kraft-paper journal page. Deterministic (seeded by slug|beat_id), no
generative models, no paid APIs. Pure Pillow + ffmpeg.

  python greybox.py <video-folder>                # 16:9, 854x480 @ 12 fps
  python greybox.py <video-folder> --portrait     # 9:16
  python greybox.py <video-folder> --report-only  # board + report, no encode

Outputs into <folder>/greybox/:
  <slug>-greybox[-portrait].mp4   animated previz (real narration muxed if
                                  every timed beat already has its mp3)
  greybox-board.html              contact sheet, one card per beat
  greybox-report.md               pacing table + warnings
  frames/board-<beat>.jpg         board keyframes
"""

import argparse
import hashlib
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
import wave as wavemod
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    sys.exit("greybox needs Pillow:  pip install pillow")

# ---------------------------------------------------------------- constants

SKINS = {
    # visual-journal scrapbook (the greybox default)
    "journal": dict(
        paper_tones=["#E7DCC2", "#E2D4B4", "#EAE0CB"],
        card_paper="#F7F2E6", ink="#3A2F23",
        tape_rgba=(222, 198, 128, 150),
        layout="journal", torn=True, tape=True, hand_band=True,
        archival=False,
        accents=None,  # use the sheet's metadata colors
        scrap_style=("cut-paper collage illustration, torn construction-paper "
                     "edges, layered flat paper textures, kraft and cream "
                     "palette with a sky-blue accent, handmade scrapbook "
                     "journal style, soft top light, plain warm background"),
    ),
    # Vox-style editorial collage (voxbio and friends)
    "voxpaper": dict(
        paper_tones=["#FDFBF7", "#F8F3E9", "#FBF7EF"],
        card_paper="#FFFFFF", ink="#222222",
        tape_rgba=(0, 0, 0, 0),
        layout="vox", torn=False, tape=False, hand_band=False, archival=True,
        accents={"accent": "#5B7B9C", "brown": "#D35F43",
                 "highlight": "#F5D061"},
        scrap_style=("archival documentary photograph, desaturated, high "
                     "contrast crushed blacks, aged newsprint grain, early "
                     "20th-century press-photo tone, clear margins, no "
                     "modern objects"),
    ),
}
SKIN = SKINS["journal"]          # reassigned in main() via --skin

PAPER_TONES = SKINS["journal"]["paper_tones"]  # back-compat alias
CARD_PAPER = "#F7F2E6"
INK = "#3A2F23"
TAPE = (222, 198, 128, 150)
GREY_PHOTO = "#B9B2A4"


def skin(key):
    return SKIN[key]


def archivalize(img):
    """The Vox archival treatment: mostly-gray blend, contrast bump."""
    from PIL import ImageEnhance, ImageOps
    gray = ImageOps.grayscale(img).convert("RGB")
    out = Image.blend(img.convert("RGB"), gray, alpha=0.8)
    return ImageEnhance.Contrast(out).enhance(1.15)
DIM_ALPHA = 0.65          # older cutouts on a crowded page
MAX_FRESH = 3             # newest N cutouts stay full-strength
SETTLE_MAX = 0.6          # seconds of slide-in
EST_CLAMP = (1.8, 14.0)   # seconds, for word-count estimated beats
TEX_FRAMES = 4            # unique paper-texture frames per scene...
TEX_FPS = 3               # ...cycling at 3 fps: alive, not jittery
CLIP_RETIME = 0.05        # conform ladder: retime within ±5%...
CLIP_LIMIT = 0.15         # ...trim/freeze to 15%; beyond that, refuse

TYPE_COLOR_KEYS = {  # timeline ribbon; values resolved from palette at runtime
    "INTRO": "ink", "ACCUMULATE": "accent", "CUT": "brown",
    "HOLD": "grey", "ZOOM": "highlight",
}

GLYPHS = [  # (keywords, kind) — first match wins
    (("wave", "packet", "oscillat", "curve", "spectrum", "fringe", "sine"), "wave"),
    (("well", "box", "barrier", "wall", "slit", "step", "container"), "well"),
    (("arrow", "ray", "beam", "shoot", "eject", "emit"), "arrow"),
    (("graph", "axis", "axes", "plot", "histogram", "chart", "counter"), "axes"),
    (("dot", "particle", "electron", "photon", "atom", "quanta", "packet"), "dots"),
    (("light", "lamp", "glow", "sun", "bright", "bulb"), "glow"),
    (("title", "word", "text", "label", "equation", "formula", "card"), "text"),
]


SCRAP_STYLE = ("cut-paper collage illustration, torn construction-paper edges, "
               "layered flat paper textures, kraft and cream palette with a "
               "sky-blue accent, handmade scrapbook journal style, soft top "
               "light, plain warm background")


def R(*key):
    """Deterministic RNG namespaced by key parts."""
    return random.Random("|".join(str(k) for k in key))


# ------------------------------------------------------- scraps (asset ids)

def make_scrap_id(slug, beat_id, taken):
    """Deterministic 3-char alphanumeric id, first char a letter (Midjourney
    prefixes output filenames with the first prompt token, so the id maps the
    rendered asset back to its beat)."""
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz"
    alnum = letters + "23456789"
    h = hashlib.md5(f"{slug}|{beat_id}".encode()).digest()
    for bump in range(9):
        sid = (letters[h[0 + bump] % len(letters)]
               + alnum[h[3 + bump] % len(alnum)]
               + alnum[h[6 + bump] % len(alnum)])
        if sid.lower() not in taken:
            taken.add(sid.lower())
            return sid
    sid = f"Z{len(taken):02d}"
    taken.add(sid.lower())
    return sid


NAME_STOP = {
    "The", "A", "An", "In", "On", "At", "So", "Now", "Ask", "Keep", "Every",
    "Each", "That", "This", "These", "Those", "Not", "And", "But", "Or",
    "Nor", "For", "Two", "One", "Three", "Nature", "Spin", "Measuring",
    "Bear", "Notes", "Act", "Part", "Scene", "Quantum", "Mechanics",
    "Nobel", "Prize", "Physics", "University", "Institute", "Professor",
}


def detect_names(text):
    """Capitalized first+last pairs in the narration → portrait boxes.
    Whenever a person is named, the final video will show their picture;
    the previz stands one in per name."""
    import re
    out = []
    for m in re.finditer(r"\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b", text):
        a, b = m.group(1), m.group(2)
        if a in NAME_STOP or b in NAME_STOP:
            continue
        name = f"{a} {b}"
        if name not in out:
            out.append(name)
    return out


def find_scrap_file(scraps_dir, sid):
    """A dropped-in asset matches if the id appears as a filename token
    (Midjourney emits e.g. user_B1a_A_small_friendly_..._x.png)."""
    if not scraps_dir.is_dir():
        return None
    import re
    hits = []
    for f in sorted(scraps_dir.iterdir()):
        if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            tokens = re.split(r"[^0-9A-Za-z]+", f.stem.lower())
            if sid.lower() in tokens:
                hits.append(f)
    return hits[-1] if hits else None


def scrap_prompt(sid, element, ar):
    desc = element.lstrip("[").replace("]", " —", 1).strip()
    return f"{sid}, {desc}, {SKIN['scrap_style']} --ar {ar}"


def load_sources(scraps_dir):
    """Provenance sidecar: sid -> {source: generated|archive|user, url, ...}.
    Status is DERIVED from this record, never hand-edited."""
    f = scraps_dir / "sources.json"
    if f.exists():
        try:
            return json.loads(f.read_text())
        except Exception:
            print("[greybox] WARNING: scraps/sources.json unreadable — "
                  "treating all dropped images as unsourced")
    return {}


def scrap_status(kind, has_file, rec):
    """Portraits of real people demand provenance: a generated or unsourced
    image is must-replace and renders with an ink X. Elements may be
    generated freely (generic scenes), unless the record forces replacement."""
    if not has_file:
        return "todo"
    rec = rec or {}
    if rec.get("must_replace"):
        return "must-replace"
    src = rec.get("source", "")
    if kind == "portrait":
        return "approved" if src in ("archive", "user") else "must-replace"
    return "generated" if src == "generated" else "ok"


def hunt_line(name):
    return (f'search "{name} portrait" — Library of Congress FTU / '
            f"Smithsonian Open Access / Wikimedia Commons")


def stamp_standin(img, box, fonts, palette):
    """Semi-transparent ink X + STAND-IN plate over a provisional asset.
    Content stays reviewable; provisionality is unmistakable. Removed only
    by replacing the file with a sourced one."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ink = hx(palette["brown"]) + (170,)
    x0, y0, x1, y1 = box
    w = max(3, int((x1 - x0) / 40))
    d.line([(x0, y0), (x1, y1)], fill=ink, width=w)
    d.line([(x0, y1), (x1, y0)], fill=ink, width=w)
    f = fonts.get("label", max(10, int((x1 - x0) * 0.10)))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    tw = d.textlength("STAND-IN", font=f)
    d.rectangle([cx - tw / 2 - 6, cy - f.size * 0.75 - 2,
                 cx + tw / 2 + 6, cy + f.size * 0.75 - 2],
                fill=(247, 242, 230, 225), outline=ink, width=2)
    d.text((cx, cy - 2), "STAND-IN", font=f, fill=ink, anchor="mm")
    img.alpha_composite(ov)


# --------------------------------------------------- zero-cost scratch audio

def tts_engine():
    """First available FREE local TTS. macOS ships `say`; Linux often has
    espeak-ng/espeak/flite. Returns (name, synth_fn) or None."""
    def mk(cmd_builder, raw_suffix):
        def synth(text, out_wav, tmpdir):
            raw = Path(tmpdir) / (out_wav.stem + raw_suffix)
            subprocess.run(cmd_builder(text, raw), check=True,
                           capture_output=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i",
                            str(raw), "-ar", "22050", "-ac", "1",
                            "-af", "apad=pad_dur=0.3",  # breath gap, baked in
                            str(out_wav)], check=True)
        return synth
    if shutil.which("say"):  # macOS
        return "say", mk(lambda t, o: ["say", "-o", str(o), t], ".aiff")
    for exe in ("espeak-ng", "espeak"):
        if shutil.which(exe):
            return exe, mk(lambda t, o, e=exe: [e, "-s", "150", "-w", str(o), t],
                           ".wav")
    if shutil.which("flite"):
        return "flite", mk(lambda t, o: ["flite", "-t", t, "-o", str(o)], ".wav")
    return None


def ffprobe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def synth_scratch(folder, beats, engine):
    """Per-beat robo-narration; MEASURED durations replace estimates.
    Cached by text hash — re-runs are free and deterministic."""
    name, synth = engine
    cache = folder / "greybox" / "scratch"
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        for b in beats:
            text = b["narration"] or "."
            key = hashlib.md5(f"{name}|{text}".encode()).hexdigest()[:12]
            wav = cache / f"{b['id']}-{key}.wav"
            if not wav.exists():
                if b["audio"] and b["audio"].exists() and not b["est"]:
                    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i",
                                    str(b["audio"]), "-ar", "22050", "-ac", "1",
                                    str(wav)], check=True)
                else:
                    synth(text, wav, td)
            b["mux_audio"] = wav
            if b["est"]:
                b["dur"] = max(ffprobe_dur(wav), 1.2)
                b["est"], b["scratch"] = False, True


def build_click_track(beats, total, out_wav):
    """Dependency-free fallback: a tick at every beat start, a double tick on
    page turns. Pacing for the ears when no TTS engine exists."""
    sr = 22050
    n = int(total * sr) + sr // 4
    buf = bytearray(2 * n)
    def burst(t0, freq, ms, amp):
        start = int(t0 * sr)
        length = int(sr * ms / 1000)
        for i in range(length):
            if start + i >= n:
                break
            env = 1.0 - i / length
            v = int(amp * 32767 * env * math.sin(2 * math.pi * freq * i / sr))
            lo = 2 * (start + i)
            cur = int.from_bytes(buf[lo:lo + 2], "little", signed=True)
            v = max(-32767, min(32767, cur + v))
            buf[lo:lo + 2] = v.to_bytes(2, "little", signed=True)
    prev_scene = None
    for b in beats:
        if b["scene"] != prev_scene:
            burst(b["start"], 660, 70, 0.5)
            burst(b["start"] + 0.09, 880, 70, 0.5)
        else:
            burst(b["start"], 880, 40, 0.35)
        prev_scene = b["scene"]
    with wavemod.open(str(out_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(bytes(buf))


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------- fonts

FONT_FILES = {
    "hand": ["ShadowsIntoLight-Regular.ttf"],
    "label": ["ArchitectsDaughter-Regular.ttf", "ShadowsIntoLight-Regular.ttf"],
    "serif": ["EBGaramond-Regular.ttf", "EBGaramond-Medium.ttf"],
}


def font_search_dirs(folder, extra):
    here = Path(__file__).resolve()
    dirs = [Path(extra)] if extra else []
    dirs += [folder / "fonts"]
    # canonical skill home → unreal-reels/fonts ; book copy → give absolute fallback
    for up in (4, 5, 6):
        if len(here.parents) > up:
            dirs.append(here.parents[up] / "fonts")
    dirs.append(Path("/Users/nik/Documents/Cowork/unreal-reels/fonts"))
    return [d for d in dirs if d and d.is_dir()]


class Fonts:
    def __init__(self, folder, extra=None):
        self.paths, self.cache = {}, {}
        dirs = font_search_dirs(folder, extra)
        for role, names in FONT_FILES.items():
            for name in names:
                for d in dirs:
                    hits = list(d.rglob(name))
                    if hits:
                        self.paths[role] = hits[0]
                        break
                if role in self.paths:
                    break
        missing = [r for r in FONT_FILES if r not in self.paths]
        if missing:
            print(f"[greybox] WARNING: no TTF for {missing}; using PIL default "
                  f"(pass --fonts DIR for the scrapbook look)")

    def get(self, role, size):
        key = (role, size)
        if key not in self.cache:
            p = self.paths.get(role)
            self.cache[key] = (ImageFont.truetype(str(p), size) if p
                               else ImageFont.load_default())
        return self.cache[key]


def wrap(draw, text, font, maxw, max_lines=None):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: max(0, len(lines[-1]) - 1)] + "…"
    return lines


# ------------------------------------------------------------- beat model

def load_beats(folder, sheet_name, wps):
    sheet_path = folder / sheet_name
    data = json.loads(sheet_path.read_text())
    md = data.get("metadata", {})
    palette = {
        "accent": md.get("accent_color", "#58C4DD"),
        "brown": md.get("brown_color", md.get("accent_color", "#CD853F")),
        "highlight": md.get("highlight_color", "#F0E442"),
        "ink": INK, "grey": "#8A8474",
    }
    beats, t0 = [], 0.0
    for raw in data.get("beats", []):
        narration = (raw.get("narration_text") or "").replace("\n", " — ").strip()
        dur = raw.get("actual_duration_s")
        est = dur is None
        if est:
            n_words = max(1, len((raw.get("tts_normalized_text") or narration).split()))
            dur = min(max(n_words / wps, EST_CLAMP[0]), EST_CLAMP[1])
        element = (raw.get("new_visual_element") or "").strip()
        role = raw.get("role", "")
        if not role and element.startswith("["):
            role = element[1:element.find("]")] if "]" in element else ""
        audio = raw.get("audio_file")
        beats.append(dict(
            id=raw.get("beat_id", "?"), type=raw.get("beat_type", "ACCUMULATE"),
            scene=raw.get("scene_index", 0), role=role, narration=narration,
            element=element, prompt=(raw.get("video_animation_prompt") or "").strip(),
            dur=float(dur), est=est, start=t0, scratch=False, mux_audio=None,
            names=detect_names(narration) if raw.get("beat_type") != "INTRO" else [],
            viz=raw.get("viz"),
            audio=(folder / audio) if audio else None,
        ))
        t0 += beats[-1]["dur"]
    return data, md, palette, beats, t0


def glyph_kind(text):
    low = text.lower()
    for keys, kind in GLYPHS:
        if any(k in low for k in keys):
            return kind
    return "photo"


# ------------------------------------------------------------ art helpers

def torn_polygon(rng, w, h, jitter=4):
    pts, steps = [], 7
    for i in range(steps):
        pts.append((w * i / steps + rng.uniform(-jitter, jitter),
                    rng.uniform(0, jitter)))
    for i in range(steps):
        pts.append((w - rng.uniform(0, jitter),
                    h * i / steps + rng.uniform(-jitter, jitter)))
    for i in range(steps):
        pts.append((w - w * i / steps + rng.uniform(-jitter, jitter),
                    h - rng.uniform(0, jitter)))
    for i in range(steps):
        pts.append((rng.uniform(0, jitter),
                    h - h * i / steps + rng.uniform(-jitter, jitter)))
    return pts


def draw_glyph(draw, kind, box, palette, rng):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    ink, accent = hx(palette["ink"]), hx(palette["accent"])
    lw = max(2, w // 60)
    if kind == "wave":
        pts = [(x0 + w * i / 48,
                y0 + h / 2 + (h / 2.6) * math.sin(i / 48 * 4 * math.pi))
               for i in range(49)]
        draw.line(pts, fill=accent, width=lw)
    elif kind == "well":
        m = w // 6
        draw.line([(x0, y0), (x0 + m, y0), (x0 + m, y1 - lw), (x1 - m, y1 - lw),
                   (x1 - m, y0), (x1, y0)], fill=ink, width=lw)
        cx = (x0 + x1) / 2
        draw.ellipse([cx - w / 14, y1 - h / 3.2, cx + w / 14, y1 - h / 3.2 + w / 7],
                     fill=accent)
    elif kind == "arrow":
        y = (y0 + y1) / 2
        draw.line([(x0, y), (x1 - w / 5, y)], fill=accent, width=lw + 1)
        draw.polygon([(x1, y), (x1 - w / 5, y - h / 5), (x1 - w / 5, y + h / 5)],
                     fill=accent)
    elif kind == "axes":
        draw.line([(x0, y0), (x0, y1), (x1, y1)], fill=ink, width=lw)
        rr = R(rng.random())
        n = 5
        for i in range(n):
            bx = x0 + w * (i + 0.35) / n
            bh = h * rr.uniform(0.25, 0.95)
            draw.rectangle([bx, y1 - bh, bx + w / (n * 1.9), y1 - lw], fill=accent)
    elif kind == "dots":
        for _ in range(14):
            dx, dy = rng.uniform(x0, x1), rng.uniform(y0, y1)
            r = rng.uniform(w / 40, w / 16)
            draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=accent)
    elif kind == "glow":
        cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, min(w, h) / 4
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)
        for a in range(8):
            ang = a * math.pi / 4
            draw.line([(cx + (r + 4) * math.cos(ang), cy + (r + 4) * math.sin(ang)),
                       (cx + (r * 2) * math.cos(ang), cy + (r * 2) * math.sin(ang))],
                      fill=accent, width=lw)
    elif kind == "text":
        # stand-in "written lines" mark
        for k in range(3):
            y = y0 + h * (0.25 + 0.25 * k)
            draw.line([(x0 + w * 0.12, y),
                       (x1 - w * (0.12 + 0.22 * rng.random()), y)],
                      fill=ink if k else accent, width=lw + 1)
    else:  # photo placeholder
        draw.rectangle(box, fill=hx(GREY_PHOTO))
        draw.line([(x0, y0), (x1, y1)], fill=hx(CARD_PAPER), width=lw)
        draw.line([(x0, y1), (x1, y0)], fill=hx(CARD_PAPER), width=lw)
        draw.rectangle(box, outline=hx(INK), width=lw)


def make_portrait(name, sid, pw, fonts, palette, photo=None,
                  must_replace=False):
    """Polaroid-style stand-in for a person's picture: photo window
    (silhouette, or the dropped-in scrap image), name handwritten below."""
    rng = R("portrait", name)
    ph = int(pw * 1.28)
    pad = 16
    img = Image.new("RGBA", (pw + pad * 2, ph + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([pad + 4, pad + 6, pad + pw + 4, pad + ph + 6],
                                 fill=(30, 20, 10, 110))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(img)
    d.rectangle([pad, pad, pad + pw, pad + ph], fill=hx("#FBF8F0"),
                outline=(200, 188, 160, 255))
    m = int(pw * 0.09)
    win = (pad + m, pad + m, pad + pw - m, pad + m + (pw - 2 * m))
    if photo:
        p = Image.open(photo).convert("RGB")
        if SKIN["archival"]:
            p = archivalize(p)
        side = min(p.size)
        p = p.crop(((p.width - side) // 2, (p.height - side) // 2,
                    (p.width + side) // 2, (p.height + side) // 2))
        p = p.resize((win[2] - win[0], win[3] - win[1]), Image.BICUBIC)
        if SKIN["archival"]:  # vox: circular portrait crop
            mask = Image.new("L", p.size, 0)
            ImageDraw.Draw(mask).ellipse([0, 0, p.width - 1, p.height - 1],
                                         fill=255)
            img.paste(p, (win[0], win[1]), mask)
            d.ellipse(win, outline=hx(INK), width=2)
        else:
            img.paste(p, (win[0], win[1]))
            d.rectangle(win, outline=hx(INK), width=2)
        if must_replace:
            stamp_standin(img, win, fonts, palette)
    else:
        d.rectangle(win, fill=hx(GREY_PHOTO), outline=hx(INK), width=2)
        cx = (win[0] + win[2]) / 2
        wy = win[3] - win[1]
        r = wy * 0.18
        hy = win[1] + wy * 0.38
        d.ellipse([cx - r, hy - r, cx + r, hy + r], fill=hx("#F1EBDD"))
        d.pieslice([cx - r * 2.1, hy + r * 0.9, cx + r * 2.1, hy + r * 4.2],
                   180, 360, fill=hx("#F1EBDD"))
    lbl_role = "label" if SKIN["hand_band"] else "serif"
    nf = fonts.get(lbl_role, max(11, int(pw * 0.13)))
    ny = win[3] + (pad + ph - win[3]) / 2
    if SKIN["archival"]:  # vox: name on a flat golden highlight bar
        tw2 = d.textlength(name, font=nf)
        d.rectangle([pad + pw / 2 - tw2 / 2 - 5, ny - nf.size * 0.72,
                     pad + pw / 2 + tw2 / 2 + 5, ny + nf.size * 0.72],
                    fill=hx(palette["highlight"]))
    d.text((pad + pw / 2, ny), name, font=nf, fill=hx(INK), anchor="mm")
    d.text((pad + 4, pad + ph - 13), sid, font=fonts.get("label", 11),
           fill=hx(palette["brown"]))
    if SKIN["tape"]:
        tape = Image.new("RGBA", (int(pw * 0.5), 14), TAPE)
        img.alpha_composite(tape.rotate(rng.uniform(-8, 8), expand=True,
                                        resample=Image.BICUBIC),
                            (pad + int(pw * 0.25), pad - 7))
    a = 7 if SKIN["torn"] else 1.5
    return img.rotate(rng.uniform(-a, a), expand=True, resample=Image.BICUBIC)


def make_card(beat, cw, ch, fonts, palette, title_card=False,
              scrap_img=None, scrap_id=None, must_replace=False):
    """Torn-paper cutout with glyph, label, tape and beat stamp → RGBA."""
    rng = R(beat["id"], "card")
    pad = 22
    img = Image.new("RGBA", (cw + pad * 2, ch + pad * 2), (0, 0, 0, 0))
    # shadow
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    if SKIN["torn"]:
        ImageDraw.Draw(sh).polygon(
            [(x + pad + 5, y + pad + 7)
             for x, y in torn_polygon(R(beat["id"], "torn"), cw, ch)],
            fill=(30, 20, 10, 110))
    else:
        ImageDraw.Draw(sh).rectangle(
            [pad + 4, pad + 5, pad + cw + 4, pad + ch + 5],
            fill=(30, 25, 20, 80))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    # paper
    d = ImageDraw.Draw(img)
    if SKIN["torn"]:
        poly = [(x + pad, y + pad)
                for x, y in torn_polygon(R(beat["id"], "torn"), cw, ch)]
        d.polygon(poly, fill=hx(CARD_PAPER), outline=(200, 188, 160, 255))
    else:  # voxpaper: straight-edged print plate, hairline frame
        d.rectangle([pad, pad, pad + cw, pad + ch], fill=hx(CARD_PAPER),
                    outline=(216, 210, 196, 255), width=1)
    hand_role = "hand" if SKIN["hand_band"] else "serif"
    lbl_role = "label" if SKIN["hand_band"] else "serif"
    if title_card:
        tfont = fonts.get(hand_role, int(ch * 0.19))
        sfont = fonts.get(lbl_role, int(ch * 0.11))
        lines = wrap(d, beat["narration"].split(" — ")[-1], tfont, cw * 0.86, 3)
        y = pad + ch * 0.30
        d.text((pad + cw / 2, pad + ch * 0.12), "· greybox previz ·",
               font=sfont, fill=hx(palette["brown"]), anchor="mm")
        for ln in lines:
            d.text((pad + cw / 2, y + tfont.size / 2), ln, font=tfont,
                   fill=hx(INK), anchor="mm")
            y += tfont.size * 1.12
    else:
        gbox = (pad + cw * 0.14, pad + ch * 0.12, pad + cw * 0.86, pad + ch * 0.55)
        if scrap_img:
            p = Image.open(scrap_img).convert("RGB")
            if SKIN["archival"]:
                p = archivalize(p)
            gw, gh = int(gbox[2] - gbox[0]), int(gbox[3] - gbox[1])
            scale = max(gw / p.width, gh / p.height)
            p = p.resize((int(p.width * scale), int(p.height * scale)),
                         Image.BICUBIC)
            p = p.crop(((p.width - gw) // 2, (p.height - gh) // 2,
                        (p.width - gw) // 2 + gw, (p.height - gh) // 2 + gh))
            img.paste(p, (int(gbox[0]), int(gbox[1])))
            d.rectangle(gbox, outline=hx(INK), width=2)
            if must_replace:
                stamp_standin(img, gbox, fonts, palette)
        else:
            draw_glyph(d, glyph_kind(beat["element"] or beat["narration"]), gbox,
                       palette, R(beat["id"], "glyph"))
        if scrap_id:
            d.text((pad + 6, pad + ch - 16), scrap_id,
                   font=fonts.get("label", 12), fill=hx(palette["brown"]))
        lfont = fonts.get(lbl_role, max(11, int(ch * 0.105)))
        label = beat["element"].lstrip("[").replace("]", " —", 1) or beat["narration"]
        y = pad + ch * 0.62
        for ln in wrap(d, label, lfont, cw * 0.84, 3):
            d.text((pad + cw / 2, y), ln, font=lfont, fill=hx(INK), anchor="ma")
            y += lfont.size * 1.18
    if SKIN["tape"]:
        for tx in (pad + cw * 0.08, pad + cw * 0.72):
            tape = Image.new("RGBA", (int(cw * 0.24), 16), TAPE)
            img.alpha_composite(tape.rotate(rng.uniform(-14, 14), expand=True,
                                            resample=Image.BICUBIC),
                                (int(tx), pad - 8))
    if SKIN["torn"]:  # journal: ink stamp; voxpaper: quiet serif beat id
        st = Image.new("RGBA", (76, 76), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        ring = hx(palette["brown"]) + (210,)
        sd.ellipse([4, 4, 72, 72], outline=ring, width=3)
        sd.text((38, 38), beat["id"][:5], font=fonts.get("label", 17),
                fill=ring, anchor="mm")
        st = st.rotate(rng.uniform(-18, 18), expand=True,
                       resample=Image.BICUBIC)
        img.alpha_composite(st, (img.width - 74, img.height - 78))
        return img.rotate(rng.uniform(-5.5, 5.5), expand=True,
                          resample=Image.BICUBIC)
    d.text((pad + cw - 6, pad + ch - 16), beat["id"][:5],
           font=fonts.get("serif", 13), fill=hx(palette["brown"]), anchor="ra")
    return img.rotate(rng.uniform(-1.2, 1.2), expand=True,
                      resample=Image.BICUBIC)


def make_viz_card(viz, cw, ch, fonts, palette):
    """Isotype dot-grid plate (the Vox device): serif label + hairline
    underline + a grid of unit dots colored by category. Returns
    (plate_without_dots, [(x, y, color)], full_plate). The REVEAL is drawn
    per-frame by the renderer, timed from the beat's measured duration."""
    counts = viz.get("counts", [1])
    total = sum(counts)
    color_keys = viz.get("colors", ["accent", "brown", "grey"])
    seq = []
    for n, key in zip(counts, color_keys):
        seq += [hx(palette[key])] * n
    pad = 22
    plate = Image.new("RGBA", (cw + pad * 2, ch + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(plate)
    d.rectangle([pad + 4, pad + 5, pad + cw + 4, pad + ch + 5],
                fill=(30, 25, 20, 60))
    plate = plate.filter(ImageFilter.GaussianBlur(3))
    d = ImageDraw.Draw(plate)
    d.rectangle([pad, pad, pad + cw, pad + ch], fill=hx(CARD_PAPER),
                outline=(216, 210, 196, 255), width=1)
    sf = fonts.get("serif", max(13, int(ch * 0.10)))
    label = viz.get("label", "")
    d.text((pad + 14, pad + 10), label, font=sf, fill=hx(INK))
    lw = d.textlength(label, font=sf)
    d.line([(pad + 14, pad + 14 + sf.size), (pad + 14 + lw, pad + 14 + sf.size)],
           fill=hx(palette["accent"]), width=2)
    # grid geometry
    gx0, gy0 = pad + 14, pad + 20 + sf.size * 1.6
    gx1, gy1 = pad + cw - 14, pad + ch - int(ch * 0.16)
    dpr = viz.get("dots_per_row") or max(4, min(10, int(math.sqrt(total * 1.7))))
    rows = math.ceil(total / dpr)
    step = min((gx1 - gx0) / dpr, (gy1 - gy0) / max(1, rows))
    r = step * 0.30
    dots = []
    for k in range(total):
        cx = gx0 + (k % dpr) * step + step / 2
        cy = gy0 + (k // dpr) * step + step / 2
        dots.append((cx, cy, r, seq[k]))
    # legend
    legend = viz.get("legend", [])
    lf = fonts.get("serif", max(10, int(ch * 0.072)))
    lx = pad + 14
    ly = pad + ch - int(ch * 0.10)
    for key, txt in zip(color_keys, legend):
        d.ellipse([lx, ly - 5, lx + 10, ly + 5], fill=hx(palette[key]))
        d.text((lx + 16, ly), txt.upper(), font=lf, fill=hx("#4A4A4A"),
               anchor="lm")
        lx += 30 + d.textlength(txt.upper(), font=lf)
    full = plate.copy()
    fd = ImageDraw.Draw(full)
    for cx, cy, rr, col in dots:
        fd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    return plate, dots, full


def make_paper(w, h, tone, seed):
    img = Image.new("RGB", (w, h), hx(tone))
    d = ImageDraw.Draw(img)
    rng = R("paper", tone, seed)
    dark = tuple(max(0, c - 14) for c in hx(tone))
    light = tuple(min(255, c + 12) for c in hx(tone))
    for _ in range(int(w * h / 700)):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        c = dark if rng.random() < 0.5 else light
        if rng.random() < 0.25:
            ang = rng.uniform(0, math.pi)
            ln = rng.uniform(4, 14)
            d.line([(x, y), (x + ln * math.cos(ang), y + ln * math.sin(ang))],
                   fill=c, width=1)
        else:
            d.point((x, y), fill=c)
    # vignette
    vg = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vg).rectangle([w * 0.06, h * 0.06, w * 0.94, h * 0.94], fill=70)
    img.paste(Image.new("RGB", (w, h), dark), (0, 0),
              vg.filter(ImageFilter.GaussianBlur(60)).point(lambda a: 70 - a))
    return img


def ease_out(u):
    return 1 - (1 - u) ** 3


# ------------------------------------------------------------ the renderer

class Greybox:
    def __init__(self, folder, args):
        self.folder = folder
        self.args = args
        self.data, self.md, self.palette, self.beats, self.total = load_beats(
            folder, args.sheet, args.wps)
        if not self.beats:
            sys.exit("beat sheet has no beats")
        if SKIN["accents"]:  # a skin may own its accent pair (voxpaper does)
            self.palette.update(SKIN["accents"])
        self.palette["ink"] = SKIN["ink"]
        self.slug = self.md.get("slug", folder.name)
        self.W = int(args.height * (9 / 16 if args.portrait else 16 / 9))
        self.W -= self.W % 2
        self.H = args.height - (args.height % 2)
        self.fonts = Fonts(folder, args.fonts)
        self.band_h = int(self.H * 0.21)
        self.ribbon_h = 12
        self.page_rect = (0, 0, self.W, self.H - self.band_h - self.ribbon_h)
        self.out = folder / "greybox"
        (self.out / "frames").mkdir(parents=True, exist_ok=True)
        self._resolve_audio()
        t0 = 0.0
        for b in self.beats:
            b["start"] = t0
            t0 += b["dur"]
        self.total = t0
        self._plan()
        self._load_clips()

    def _load_clips(self):
        """slots/<beat_id>/clip.mp4 — a dropped/generated clip plays in place
        of the beat's cutout, CONFORMED to the beat's measured duration.
        Ladder: retime within ±5% -> trim from the HEAD (clips settle at the
        end; the settled state hands off) -> freeze-tail when short -> refuse
        beyond 15% (regenerate at the right tier; force-fitting kills sync)."""
        self.clips, self.clip_notes = {}, []
        fps = self.args.fps
        for i, b in enumerate(self.beats):
            src = self.out / "slots" / b["id"] / "clip.mp4"
            if not src.exists():
                continue
            L, T = ffprobe_dur(src), b["dur"]
            r = L / T
            ss = None
            if abs(1 - r) <= CLIP_RETIME:
                mode, vf = "retimed", f"setpts=PTS*{T / L:.6f},"
            elif L > T:
                if (L - T) / T > CLIP_LIMIT:
                    self.clip_notes.append(
                        f"`{b['id']}` clip is {L:.1f}s vs beat {T:.1f}s — "
                        f">15% long, REFUSED (regenerate shorter or respan)")
                    continue
                mode, vf, ss = "trimmed head", "", L - T
            else:
                if (T - L) / T > CLIP_LIMIT:
                    self.clip_notes.append(
                        f"`{b['id']}` clip is {L:.1f}s vs beat {T:.1f}s — "
                        f">15% short, REFUSED (regenerate longer)")
                    continue
                mode, vf = "froze tail", ""
            cw = int(self.W * 0.46)
            ch2 = int(cw * 9 / 16)
            with tempfile.TemporaryDirectory() as td:
                cmd = ["ffmpeg", "-y", "-loglevel", "error"]
                if ss:
                    cmd += ["-ss", f"{ss:.3f}"]
                cmd += ["-i", str(src),
                        "-vf", f"{vf}fps={fps},scale={cw}:{ch2}",
                        str(Path(td) / "c_%05d.jpg")]
                subprocess.run(cmd, check=True)
                frames = []
                for p in sorted(Path(td).iterdir()):
                    fr = Image.open(p).convert("RGB")
                    fr.load()
                    frames.append(fr)
            n = max(1, math.ceil(T * fps))
            frames = frames[:n] + [frames[-1]] * max(0, n - len(frames))
            self.clips[i] = frames
            self.clip_notes.append(
                f"`{b['id']}` clip conformed: {mode} ({L:.1f}s → {T:.1f}s)")

    def _resolve_audio(self):
        """Zero-cost audio ladder: real mp3s (reused) → scratch local TTS
        (measured durations replace estimates) → click track → silent."""
        if self.args.no_audio:
            self.audio_mode = "off"
            return
        if all(b["audio"] and b["audio"].exists() and not b["est"]
               for b in self.beats):
            for b in self.beats:
                b["mux_audio"] = b["audio"]
            self.audio_mode = "real narration (reused mp3s)"
            return
        eng = tts_engine()
        if eng:
            print(f"[greybox] scratch narration via '{eng[0]}' (free, local); "
                  f"measured durations replace word-count estimates")
            synth_scratch(self.folder, self.beats, eng)
            self.audio_mode = f"scratch robo-narration ({eng[0]})"
        elif SKIN["layout"] == "vox":
            # click pops read as broken in the editorial frame — stay silent
            self.audio_mode = "silent (no local TTS here; run on the Mac " \
                              "for scratch narration)"
        else:
            self.audio_mode = "click track (no local TTS engine found)"

    # ---- layout planning ------------------------------------------------
    def _plan(self):
        px0, py0, px1, py1 = self.page_rect
        cw = int(self.W * (0.34 if self.args.portrait else 0.225))
        ch = int(cw * 0.74)
        self.card_size = (cw, ch)
        cols, rows = (2, 3) if self.args.portrait else (3, 2)
        slots = []
        for r in range(rows):
            for c in range(cols):
                slots.append((px0 + (px1 - px0) * (c + 0.5) / cols,
                              py0 + (py1 - py0) * (r + 0.5) / rows))
        # per-scene: shuffled slot order, per-beat jitter
        scenes = {}
        for i, b in enumerate(self.beats):
            scenes.setdefault(b["scene"], []).append(i)
        self.scene_beats = scenes
        self.scene_tone = {s: PAPER_TONES[k % len(PAPER_TONES)]
                           for k, s in enumerate(sorted(scenes))}
        self.cards, self.pos = {}, {}
        self.scraps, self.beat_portraits, self.vizdots = [], {}, {}
        self.scrap_img_by_beat = {}
        taken, name_sids, portrait_cache = set(), {}, {}
        scraps_dir = self.out / "scraps"
        sources = load_sources(scraps_dir)
        pw = int(self.W * 0.105)
        for s, idxs in scenes.items():
            order = list(range(len(slots)))
            R(self.slug, "slots", s).shuffle(order)
            placed, scene_names = 0, set()
            for i in idxs:
                b = self.beats[i]
                adds = b["type"] in ("ACCUMULATE", "CUT") and b["element"]
                if b.get("viz"):
                    vw = int(cw * 1.5)
                    vh = int(ch * 1.5)
                    plate, dots, full = make_viz_card(b["viz"], vw, vh,
                                                      self.fonts, self.palette)
                    self.cards[i] = full
                    self.vizdots[i] = (plate, dots)
                    sx, sy = slots[order[placed % len(slots)]]
                    self.pos[i] = (sx, sy)
                    placed += 2 if placed % len(slots) < len(slots) - 1 else 1
                    continue
                if b["type"] == "INTRO":
                    tw = int(self.W * 0.62)
                    self.cards[i] = make_card(b, tw, int(tw * 0.5), self.fonts,
                                              self.palette, title_card=True)
                    self.pos[i] = ((px0 + px1) / 2, (py0 + py1) / 2)
                elif adds:
                    sid = img_file = None
                    mr = False
                    if b["role"] not in ("INTRO", "OUTRO"):
                        sid = make_scrap_id(self.slug, b["id"], taken)
                        img_file = find_scrap_file(scraps_dir, sid)
                        rec = sources.get(sid)
                        status = scrap_status("element", bool(img_file), rec)
                        mr = status == "must-replace"
                        self.scraps.append(dict(
                            sid=sid, kind="element", ref=b["id"],
                            found=bool(img_file), status=status,
                            source=(rec or {}).get("source", "—"), hunt=None,
                            prompt=scrap_prompt(sid, b["element"],
                                                self.args.scrap_ar)))
                    self.cards[i] = make_card(b, cw, ch, self.fonts,
                                              self.palette, scrap_img=img_file,
                                              scrap_id=sid, must_replace=mr)
                    self.scrap_img_by_beat[i] = img_file
                    sx, sy = slots[order[placed % len(slots)]]
                    j = R(self.slug, b["id"], "jit")
                    wrap_n = placed // len(slots)
                    self.pos[i] = (sx + j.uniform(-14, 14) + wrap_n * 10,
                                   sy + j.uniform(-10, 10) + wrap_n * 8)
                    placed += 1
                # portrait boxes: whenever a person is named, stand in a photo
                for name in b["names"]:
                    if name in scene_names:
                        continue
                    scene_names.add(name)
                    if name not in name_sids:
                        sid = make_scrap_id(self.slug, f"name:{name}", taken)
                        name_sids[name] = sid
                        img_file = find_scrap_file(scraps_dir, sid)
                        rec = sources.get(sid)
                        status = scrap_status("portrait", bool(img_file), rec)
                        portrait_cache[name] = (img_file, sid,
                                                status == "must-replace")
                        self.scraps.append(dict(
                            sid=sid, kind="portrait", ref=name,
                            found=bool(img_file), status=status,
                            source=(rec or {}).get("source", "—"),
                            hunt=hunt_line(name),
                            prompt=f"{sid}, portrait of {name}, head and "
                                   f"shoulders, {SKIN['scrap_style']} --ar 1:1"))
                    img_file, sid, mr = portrait_cache[name]
                    pimg = make_portrait(name, sid, pw, self.fonts,
                                         self.palette, photo=img_file,
                                         must_replace=mr)
                    k = sum(len(v) for j2, v in self.beat_portraits.items()
                            if self.beats[j2]["scene"] == s)
                    ppos = (px0 + pw * 0.85 + k * pw * 1.18,
                            py0 + pw * 0.95)
                    self.beat_portraits.setdefault(i, []).append((pimg, ppos))
        # paper texture loop: TEX_FRAMES seeded variants per scene, cycled at
        # TEX_FPS so the ground reads alive without jitter
        self.papers = {s: [make_paper(self.W, self.H, self.scene_tone[s],
                                      (s, k)) for k in range(TEX_FRAMES)]
                       for s in scenes}
        if SKIN["layout"] == "vox":
            self._plan_vox()

    # ---- the VOX frame: photo ground, flat annotation, narration island ----
    def _plan_vox(self):
        W, H = self.W, self.H
        self.photo_rect = (int(W * 0.05), int(H * 0.055),
                           int(W * 0.95), int(H * 0.67))
        self.panel_rect = (int(W * 0.05), int(H * 0.715),
                           int(W * 0.95), int(H * 0.945))
        pr = self.photo_rect
        pw_, ph_ = pr[2] - pr[0], pr[3] - pr[1]
        # photo layer per beat: dropped scrap > clips/<beat>.{jpg,png,mp4}
        # frame > carry the previous plate forward
        self.vox_photo, current = {}, None
        for i, b in enumerate(self.beats):
            src = self.scrap_img_by_beat.get(i)
            if not src:
                for ext in (".jpg", ".png", ".jpeg", ".webp"):
                    c = self.folder / "clips" / f"{b['id']}{ext}"
                    if c.exists():
                        src = c
                        break
                else:
                    c = self.folder / "clips" / f"{b['id']}.mp4"
                    if c.exists():
                        tmp = Path(tempfile.mkdtemp()) / "still.jpg"
                        subprocess.run(
                            ["ffmpeg", "-y", "-loglevel", "error", "-ss",
                             "1.0", "-i", str(c), "-frames:v", "1", str(tmp)],
                            check=True)
                        src = tmp
            if src:
                current = self._vox_plate(src, pw_, ph_)
            self.vox_photo[i] = current
        # quiet placeholder plate
        ph = Image.new("RGBA", (pw_, ph_), (0, 0, 0, 0))
        d = ImageDraw.Draw(ph)
        d.rectangle([0, 0, pw_ - 1, ph_ - 1], fill=hx(GREY_PHOTO),
                    outline=(180, 174, 160, 255))
        d.text((pw_ - 12, ph_ - 12), "ARCHIVAL PLATE",
               font=self.fonts.get("serif", 13), fill=(122, 116, 104),
               anchor="rs")
        self.vox_placeholder = ph
        # narration island per beat
        self.vox_panel = {}
        pnl = self.panel_rect
        for i, b in enumerate(self.beats):
            img = Image.new("RGB", (pnl[2] - pnl[0], pnl[3] - pnl[1]),
                            "#FBF7EE")
            d = ImageDraw.Draw(img)
            d.rectangle([0, 0, img.width - 1, img.height - 1],
                        outline=hx("#D8D2C4"), width=1)
            nf = self.fonts.get("serif", max(15, int(H * 0.052)))
            lines = wrap(d, b["narration"], nf, img.width - 56, 3)
            y = int(img.height / 2 - len(lines) * nf.size * 0.62)
            tw = 0
            for ln in lines:
                d.text((28, y), ln, font=nf, fill=hx(SKIN["ink"]))
                tw = max(tw, d.textlength(ln, font=nf))
                y += int(nf.size * 1.28)
            self.vox_panel[i] = (img, 28, tw)
        # card overlays (title / quote / equation / date from the sheet)
        self.vox_overlay = {}
        for i, b in enumerate(self.beats):
            raw = self.data["beats"][i].get("card") or {}
            if raw.get("kind"):
                self.vox_overlay[i] = self._vox_card(raw, pw_, ph_)
        # reposition shared elements into the frame
        for i in self.vizdots:
            self.pos[i] = (W * 0.30, H * 0.38)
        counters = {}
        pwid = int(W * 0.105)
        for i, plist in self.beat_portraits.items():
            s = self.beats[i]["scene"]
            newl = []
            for pimg, _ in plist:
                k = counters.get(s, 0)
                counters[s] = k + 1
                newl.append((pimg, (pr[2] - pwid * 0.9 - k * pwid * 1.2,
                                    pr[1] + pwid * 1.0)))
            self.beat_portraits[i] = newl

    def _vox_plate(self, src, pw_, ph_):
        """Archival-treated photo, cover-cropped, white mat + hairline."""
        p = Image.open(src).convert("RGB")
        scale = max(pw_ / p.width, ph_ / p.height)
        p = p.resize((int(p.width * scale) + 1, int(p.height * scale) + 1),
                     Image.BICUBIC)
        p = p.crop(((p.width - pw_) // 2 + 8, (p.height - ph_) // 2 + 8,
                    (p.width - pw_) // 2 + pw_ - 8,
                    (p.height - ph_) // 2 + ph_ - 8))
        p = archivalize(p)
        plate = Image.new("RGBA", (pw_, ph_), (0, 0, 0, 0))
        d = ImageDraw.Draw(plate)
        d.rectangle([2, 3, pw_ - 1, ph_ - 1], fill=(30, 25, 20, 60))
        d.rectangle([0, 0, pw_ - 3, ph_ - 3], fill="#FFFFFF")
        plate.paste(p, (8, 8))
        d.rectangle([8, 8, pw_ - 11, ph_ - 11], outline=(60, 56, 48, 90),
                    width=1)
        return plate

    def _vox_card(self, card, pw_, ph_):
        """Flat annotation from the sheet's card block, Vox grammar."""
        ov = Image.new("RGBA", (pw_, ph_), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        kind = card.get("kind")
        ink, acc = hx(SKIN["ink"]), hx(self.palette["accent"])
        hi = hx(self.palette["highlight"])
        if kind == "title":
            f1 = self.fonts.get("serif", int(ph_ * 0.17))
            f2 = self.fonts.get("serif", int(ph_ * 0.075))
            x, y = int(pw_ * 0.06), int(ph_ * 0.60)
            t = card.get("name", "")
            dates = card.get("dates", "")
            tw = d.textlength(t, font=f1)
            dh = f2.size * 1.6 if dates else 0
            d.rectangle([x - 8, y - 6, x + tw + 8, y + f1.size * 1.30 + dh],
                        fill="#FBF7EE")
            d.text((x, y), t, font=f1, fill=ink)
            d.line([(x, y + f1.size * 1.20), (x + tw, y + f1.size * 1.20)],
                   fill=acc, width=2)
            if dates:
                d.text((x + 2, y + f1.size * 1.38), dates, font=f2,
                       fill=hx("#4A4A4A"))
        elif kind in ("quote", "equation"):
            f1 = self.fonts.get("serif", int(ph_ * 0.115))
            f2 = self.fonts.get("serif", int(ph_ * 0.06))
            text = card.get("text") or card.get("tex", "")
            text = (text.replace("\\nu", "ν").replace("\\", "")
                    .replace("$", ""))
            tw = d.textlength(text, font=f1)
            cx, cy = pw_ * 0.5, ph_ * 0.42
            d.rectangle([cx - tw / 2 - 26, cy - f1.size * 1.15,
                         cx + tw / 2 + 26, cy + f1.size * 1.05],
                        fill="#FBF7EE", outline=hx("#D8D2C4"), width=1)
            if kind == "equation":
                d.rectangle([cx - tw / 2 - 4, cy + f1.size * 0.62,
                             cx + tw / 2 + 4, cy + f1.size * 0.86], fill=hi)
            d.text((cx, cy), text, font=f1, fill=ink, anchor="mm")
            lbl = card.get("label", "").upper()
            if lbl:
                lw2 = d.textlength(lbl, font=f2)
                ly = cy - f1.size * 1.65
                d.rectangle([cx - lw2 / 2 - 8, ly - f2.size * 0.85,
                             cx + lw2 / 2 + 8, ly + f2.size * 0.85],
                            fill="#FBF7EE")
                d.text((cx, ly), lbl, font=f2, fill=hx("#4A4A4A"),
                       anchor="mm")
        elif kind == "date":
            f1 = self.fonts.get("serif", int(ph_ * 0.24))
            f2 = self.fonts.get("serif", int(ph_ * 0.07))
            x, y = int(pw_ * 0.06), int(ph_ * 0.10)
            big = card.get("big", "")
            tw = d.textlength(big, font=f1)
            d.rectangle([x - 10, y + f1.size * 0.16, x + tw + 10,
                         y + f1.size * 1.06], fill=hi)
            d.text((x, y), big, font=f1, fill=ink)
            lbl = card.get("label", "").upper()
            if lbl:
                lw2 = d.textlength(lbl, font=f2)
                ly = y + f1.size * 1.22
                d.rectangle([x - 6, ly - 4, x + lw2 + 10, ly + f2.size * 1.3],
                            fill="#FBF7EE")
                d.text((x + 2, ly), lbl, font=f2, fill=hx("#4A4A4A"))
        return ov

    def _page_before(self, i, k=0, exclude=None):
        """Page with all settled cards of beat i's scene that precede i."""
        b = self.beats[i]
        img = self.papers[b["scene"]][k].copy()
        idxs = [j for j in self.scene_beats[b["scene"]]
                if j < i and j in self.cards and j != exclude]
        for rank, j in enumerate(idxs):
            card = self.cards[j]
            alpha = 1.0 if (len(idxs) - rank) <= MAX_FRESH else DIM_ALPHA
            self._paste(img, card, self.pos[j], alpha)
        for j in self.scene_beats[b["scene"]]:
            if j < i:
                for pimg, ppos in self.beat_portraits.get(j, []):
                    self._paste(img, pimg, ppos)
        return img

    def _paste(self, base, card, center, alpha=1.0, scale=1.0, dy=0):
        c = card
        if scale != 1.0:
            c = card.resize((int(card.width * scale), int(card.height * scale)),
                            Image.BICUBIC)
        x = int(center[0] - c.width / 2)
        y = int(center[1] - c.height / 2 + dy)
        if alpha >= 0.999:
            base.paste(c, (x, y), c)
        else:
            m = c.split()[3].point(lambda a: int(a * alpha))
            base.paste(c, (x, y), m)

    # ---- static per-beat chrome -----------------------------------------
    def _band(self, i):
        b = self.beats[i]
        img = Image.new("RGB", (self.W, self.band_h),
                        tuple(max(0, c - 22) for c in hx(self.scene_tone[b["scene"]])))
        d = ImageDraw.Draw(img)
        d.line([(0, 1), (self.W, 1)], fill=hx(INK), width=1)
        meta_f = self.fonts.get("label" if SKIN["hand_band"] else "serif",
                                max(11, int(self.band_h * 0.16)))
        hand_f = self.fonts.get("hand" if SKIN["hand_band"] else "serif",
                                max(14, int(self.band_h * 0.26)))
        meta = f"{b['id']}  ·  {b['type']}" + (f"  ·  {b['role']}" if b["role"] else "")
        meta += f"  ·  {b['dur']:.1f}s"
        d.text((14, int(self.band_h * 0.10)), meta, font=meta_f, fill=hx(palette_dim := INK))
        chip = "EST" if b["est"] else ("SCR" if b.get("scratch") else None)
        if chip:
            ex = 20 + d.textlength(meta, font=meta_f)
            d.rectangle([ex, self.band_h * 0.08, ex + 44, self.band_h * 0.30],
                        outline=hx(self.palette["brown"]), width=2)
            d.text((ex + 22, self.band_h * 0.19), chip, font=meta_f,
                   fill=hx(self.palette["brown"]), anchor="mm")
        y = int(self.band_h * 0.38)
        for ln in wrap(d, b["narration"], hand_f, self.W - 130, 2):
            d.text((14, y), ln, font=hand_f, fill=hx(INK))
            y += int(hand_f.size * 1.15)
        return img

    def _ribbon_base(self):
        img = Image.new("RGB", (self.W, self.ribbon_h), hx(INK))
        d = ImageDraw.Draw(img)
        for b in self.beats:
            x0 = self.W * b["start"] / self.total
            x1 = self.W * (b["start"] + b["dur"]) / self.total
            col = self.palette[TYPE_COLOR_KEYS.get(b["type"], "grey")]
            d.rectangle([x0 + 0.5, 2, x1 - 0.5, self.ribbon_h - 2], fill=hx(col))
        return img

    def _frame_vox(self, t):
        """One frame of the editorial collage: newsprint ground (baked with
        the narration island) → archival plate → flat annotation plane →
        golden progress underline. No debug chrome — the frame IS the look."""
        i = self._beat_at(t)
        b = self.beats[i]
        tl = t - b["start"]
        settle = min(SETTLE_MAX, 0.35 * b["dur"])
        u = ease_out(min(1.0, tl / settle)) if settle > 0 else 1.0
        img = self.bases[(i, int(t * TEX_FPS) % TEX_FRAMES)].copy()
        pr = self.photo_rect
        photo = self.vox_photo.get(i) or self.vox_placeholder
        prev = (self.vox_photo.get(i - 1) or self.vox_placeholder) if i else None
        if i and photo is not prev and u < 1.0:  # quick crossfade on change
            img.paste(prev, (pr[0], pr[1]), prev)
            m = photo.split()[3].point(lambda a: int(a * u))
            img.paste(photo, (pr[0], pr[1]), m)
        else:
            img.paste(photo, (pr[0], pr[1]), photo)
        scene_idxs = self.scene_beats[b["scene"]]
        # latest card annotation in this scene persists; current one fades in
        ov_j = max((j for j in scene_idxs if j <= i and j in self.vox_overlay),
                   default=None)
        if ov_j is not None:
            ov = self.vox_overlay[ov_j]
            if ov_j == i and u < 1.0:
                ov = Image.merge("RGBA", (*ov.split()[:3],
                                          ov.split()[3].point(
                                              lambda a: int(a * u))))
            img.paste(ov, (pr[0], pr[1]), ov)
        # isotype: earlier grids persist settled; the current one counts up
        for j in scene_idxs:
            if j > i or j not in self.vizdots:
                continue
            if j < i:
                self._paste(img, self.cards[j], self.pos[j])
            else:
                plate, dots = self.vizdots[j]
                window = max(0.5, b["dur"] - settle - 0.4)
                dt = window / max(1, len(dots))
                k = max(0, min(len(dots), int((tl - settle) / dt) + 1)) \
                    if tl > settle else 0
                fr = plate.copy()
                fd = ImageDraw.Draw(fr)
                for cx, cy, rr, col in dots[:k]:
                    fd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
                self._paste(img, fr, self.pos[j], alpha=u)
        # portraits: earlier ones hold, this beat's fade in
        for j in scene_idxs:
            if j > i:
                continue
            for k2, (pimg, ppos) in enumerate(self.beat_portraits.get(j, [])):
                if j == i:
                    u2 = ease_out(min(1.0, max(0.0, (tl - 0.12 * k2)
                                               / max(settle, 1e-6))))
                    self._paste(img, pimg, ppos, alpha=u2)
                else:
                    self._paste(img, pimg, ppos)
        # golden progress underline in the narration island
        _, tx, tw = self.vox_panel[i]
        d = ImageDraw.Draw(img)
        y = self.panel_rect[3] - 12
        d.rectangle([self.panel_rect[0] + tx, y,
                     self.panel_rect[0] + tx + tw * min(1.0, tl / b["dur"]),
                     y + 3], fill=hx(self.palette["highlight"]))
        return img

    # ---- one frame -------------------------------------------------------
    def frame_at(self, t):
        if SKIN["layout"] == "vox":
            return self._frame_vox(t)
        i = self._beat_at(t)
        b = self.beats[i]
        tl = t - b["start"]
        settle = min(SETTLE_MAX, 0.35 * b["dur"])
        img = self.bases[(i, int(t * TEX_FPS) % TEX_FRAMES)].copy()
        # portrait boxes for people named in this beat
        for k2, (pimg, ppos) in enumerate(self.beat_portraits.get(i, [])):
            u2 = ease_out(min(1.0, max(0.0, (tl - 0.12 * k2)
                                       / max(settle, 1e-6))))
            self._paste(img, pimg, ppos, alpha=u2,
                        dy=-(1 - u2) * self.H * 0.12)
        # animated element
        if i in self.vizdots:
            plate, dots = self.vizdots[i]
            u = ease_out(min(1.0, tl / settle)) if settle > 0 else 1.0
            window = max(0.5, b["dur"] - settle - 0.4)
            dt = window / max(1, len(dots))
            k = max(0, min(len(dots), int((tl - settle) / dt) + 1)) \
                if tl > settle else 0
            fr = plate.copy()
            fd = ImageDraw.Draw(fr)
            for cx, cy, rr, col in dots[:k]:
                fd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
            self._paste(img, fr, self.pos[i], alpha=u,
                        dy=-(1 - u) * self.H * 0.15)
        elif i in self.clips:
            frames = self.clips[i]
            fr = frames[min(int(tl * self.args.fps), len(frames) - 1)]
            plate = Image.new("RGBA", (fr.width + 24, fr.height + 24),
                              (0, 0, 0, 0))
            pd = ImageDraw.Draw(plate)
            pd.rectangle([4, 6, fr.width + 20, fr.height + 22],
                         fill=(30, 20, 10, 90))
            pd.rectangle([0, 0, fr.width + 16, fr.height + 16],
                         fill=hx(CARD_PAPER))
            plate.paste(fr, (8, 8))
            pd.rectangle([8, 8, fr.width + 8, fr.height + 8],
                         outline=hx(INK), width=2)
            pd.text((12, fr.height + 10), f"CLIP · {b['id']}",
                    font=self.fonts.get("label", 12),
                    fill=hx(self.palette["brown"]))
            px0, py0, px1, py1 = self.page_rect
            self._paste(img, plate, ((px0 + px1) / 2, (py0 + py1) / 2))
        elif i in self.cards:
            u = ease_out(min(1.0, tl / settle)) if settle > 0 else 1.0
            drop = (1 - u) * self.H * 0.25
            bob = 2.5 * math.sin(2 * math.pi * 0.4 * t + R(b["id"], "ph").uniform(0, 6)) \
                if u >= 1.0 else 0
            self._paste(img, self.cards[i], self.pos[i], alpha=u,
                        dy=-drop + bob)
        else:
            j = self._last_card_before(i)
            if j is not None:
                if b["type"] == "ZOOM":
                    sc = 1.0 + 0.3 * ease_out(min(1.0, tl / max(settle, 1e-6)))
                    self._paste(img, self.cards[j], self.pos[j], scale=sc)
                else:  # HOLD or empty — pulse marker on last cutout
                    self._paste(img, self.cards[j], self.pos[j])
                    pul = 0.5 + 0.5 * math.sin(2 * math.pi * 0.9 * tl)
                    d = ImageDraw.Draw(img)
                    cw, chh = self.cards[j].width, self.cards[j].height
                    cx, cy = self.pos[j]
                    r = 8 + 4 * pul
                    d.ellipse([cx - cw / 2 - r, cy - chh / 2 - r,
                               cx + cw / 2 + r, cy + chh / 2 + r],
                              outline=hx(self.palette["highlight"]), width=3)
        # timecode + beat progress + playhead
        d = ImageDraw.Draw(img)
        mono = self.fonts.get("label", max(11, int(self.band_h * 0.16)))
        tc = f"{int(t // 60):02d}:{int(t % 60):02d} / " \
             f"{int(self.total // 60):02d}:{int(self.total % 60):02d}"
        d.text((self.W - 14, self.H - self.band_h - self.ribbon_h +
                int(self.band_h * 0.10)), tc, font=mono, fill=hx(INK), anchor="ra")
        # per-beat progress hairline
        y = self.H - self.ribbon_h - 3
        d.line([(0, y), (self.W * min(1, tl / b["dur"]), y)],
               fill=hx(self.palette["highlight"]), width=2)
        ph = self.W * t / self.total
        d.rectangle([ph - 1.5, self.H - self.ribbon_h, ph + 1.5, self.H],
                    fill="#FFFFFF")
        return img

    def _beat_at(self, t):
        for i, b in enumerate(self.beats):
            if t < b["start"] + b["dur"]:
                return i
        return len(self.beats) - 1

    def _last_card_before(self, i):
        for j in sorted(self.scene_beats[self.beats[i]["scene"]], reverse=True):
            if j <= i and j in self.cards:
                return j
        return None

    # ---- outputs ----------------------------------------------------------
    def build_bases(self):
        if SKIN["layout"] == "vox":
            self.bases = {}
            for i, b in enumerate(self.beats):
                pimg, _, _ = self.vox_panel[i]
                for k in range(TEX_FRAMES):
                    base = self.papers[b["scene"]][k].copy()
                    base.paste(pimg, (self.panel_rect[0], self.panel_rect[1]))
                    self.bases[(i, k)] = base
            return
        ribbon = self._ribbon_base()
        self.bases = {}
        for i in range(len(self.beats)):
            band = self._band(i)
            excl = (None if i in self.cards or i in getattr(self, "clips", {})
                    else self._last_card_before(i))
            for k in range(TEX_FRAMES):
                base = Image.new("RGB", (self.W, self.H))
                base.paste(self._page_before(i, k, exclude=excl), (0, 0))
                base.paste(band, (0, self.H - self.band_h - self.ribbon_h))
                base.paste(ribbon, (0, self.H - self.ribbon_h))
                self.bases[(i, k)] = base

    def render_board(self):
        for b in self.beats:
            f = self.frame_at(min(b["start"] + 0.85 * b["dur"], self.total - 0.01))
            f.thumbnail((420, 420))
            f.save(self.out / "frames" / f"board-{b['id']}.jpg", quality=88)

    def render_video(self):
        fps = self.args.fps
        n = int(math.ceil(self.total * fps))
        tmp = Path(tempfile.mkdtemp(prefix="greybox_"))
        try:
            for k in range(n):
                self.frame_at(k / fps).save(tmp / f"f_{k:05d}.jpg", quality=90)
                if k % (fps * 20) == 0:
                    print(f"[greybox] frames {k}/{n}")
            suffix = "-portrait" if self.args.portrait else ""
            outfile = self.out / f"{self.slug}-greybox{suffix}.mp4"
            cmd = ["ffmpeg", "-y", "-loglevel", "error",
                   "-framerate", str(fps), "-i", str(tmp / "f_%05d.jpg")]
            have_audio = False
            if self.audio_mode.startswith(("real", "scratch")):
                files = [b["mux_audio"] for b in self.beats]
                if all(f and Path(f).exists() for f in files):
                    concat = tmp / "audio.txt"
                    concat.write_text("".join(
                        "file '{}'\n".format(
                            str(Path(f).resolve()).replace("'", r"'\''"))
                        for f in files))
                    cmd += ["-f", "concat", "-safe", "0", "-i", str(concat),
                            "-c:a", "aac", "-b:a", "128k", "-shortest"]
                    have_audio = True
            elif self.audio_mode.startswith("click"):
                click = tmp / "click.wav"
                build_click_track(self.beats, self.total, click)
                cmd += ["-i", str(click), "-c:a", "aac", "-b:a", "96k",
                        "-shortest"]
                have_audio = True
            cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26",
                    "-preset", "veryfast", str(outfile)]
            subprocess.run(cmd, check=True)
            print(f"[greybox] wrote {outfile} — audio: "
                  + (self.audio_mode if have_audio else "silent"))
            return outfile
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def render_report(self):
        est_n = sum(b["est"] for b in self.beats)
        warns = []
        for b in self.beats:
            wps_real = len(b["narration"].split()) / b["dur"] if b["dur"] else 0
            if b["dur"] < 1.5:
                warns.append(f"`{b['id']}` blink beat: {b['dur']:.1f}s")
            if b["dur"] > 12:
                warns.append(f"`{b['id']}` long hold: {b['dur']:.1f}s")
            # Bear Brown voice baseline ≈ 3.5 words/s; only flag real outliers,
            # and only on measured audio (estimates are wps-derived anyway).
            if not b["est"] and wps_real > 4.0:
                warns.append(f"`{b['id']}` crammed narration: {wps_real:.1f} words/s")
        for s, idxs in self.scene_beats.items():
            n_cards = sum(1 for j in idxs if j in self.cards)
            if n_cards > 6:
                warns.append(f"scene {s} overcrowds: {n_cards} cutouts on one page")
        for s in self.scraps:
            if s["status"] == "must-replace":
                warns.append(f"scrap `{s['sid']}` ({s['ref']}) is a STAND-IN "
                             f"— replace with a sourced image before final")
        for i, (plate, dots) in getattr(self, "vizdots", {}).items():
            b = self.beats[i]
            window = max(0.5, b["dur"] - min(SETTLE_MAX, 0.35 * b["dur"]) - 0.4)
            if window / max(1, len(dots)) < 0.012:
                warns.append(
                    f"`{b['id']}` isotype grid too large for its audio: "
                    f"{len(dots)} dots in {window:.1f}s — cut the grid or "
                    f"lengthen the narration")
        lines = [
            f"# Greybox report — {self.md.get('title', self.slug)}",
            "",
            f"- sheet: `{self.args.sheet}` · beats: **{len(self.beats)}** · "
            f"scenes: **{len(self.scene_beats)}** · total: "
            f"**{int(self.total // 60)}:{int(self.total % 60):02d}**",
            f"- timing: "
            f"{sum(1 for b in self.beats if not b['est'] and not b['scratch'])}"
            f" actual (mp3-measured), "
            f"{sum(b['scratch'] for b in self.beats)} scratch-TTS (measured), "
            f"{est_n} estimated at {self.args.wps} words/s",
            f"- audio: {self.audio_mode}",
            f"- scraps: {len(self.scraps)} asset prompts "
            f"({sum(s['found'] for s in self.scraps)} images dropped in) — "
            f"see `greybox-scraps.md`",
            "",
            "## Warnings" if warns else "## Warnings\n\n_None._",
        ]
        lines += [f"- {w}" for w in warns]
        if getattr(self, "clip_notes", None):
            lines += ["", "## Clips (conform ladder)", ""]
            lines += [f"- {n}" for n in self.clip_notes]
        lines += ["", "## Beats", "",
                  "| # | beat | type | role | scene | dur | t | narration |",
                  "|--:|------|------|------|------:|----:|--:|-----------|"]
        for k, b in enumerate(self.beats):
            dur = f"{b['dur']:.1f}s" + (" *(est)*" if b["est"] else "")
            t = f"{int(b['start'] // 60)}:{int(b['start'] % 60):02d}"
            narr = b["narration"][:70] + ("…" if len(b["narration"]) > 70 else "")
            lines.append(f"| {k} | {b['id']} | {b['type']} | {b['role']} | "
                         f"{b['scene']} | {dur} | {t} | {narr} |")
        (self.out / "greybox-report.md").write_text("\n".join(lines) + "\n")
        print(f"[greybox] wrote {self.out / 'greybox-report.md'}")
        return warns

    def render_scraps(self):
        """Midjourney-ready asset list. Each prompt is prefixed with its
        3-char id — Midjourney names output files from the first prompt
        token, so the filename itself maps the asset back to its beat.
        Drop finished images into greybox/scraps/ and re-run greybox."""
        if not self.scraps:
            return
        md = [f"# Greybox scraps — {self.md.get('title', self.slug)}", "",
              "One prompt per cutout/portrait. The leading 3-char id lands in "
              "Midjourney's output filename; drop the images into "
              "`greybox/scraps/` (keep the id in the filename) and re-run "
              "`greybox.py` — each image replaces its stand-in glyph.", "",
              "Provenance lives in `scraps/sources.json` "
              '(`{"<id>": {"source": "generated|archive|user", "url": "..."}}`).'
              " A portrait of a real person whose image is generated or "
              "unsourced renders with an ink X (STAND-IN) and blocks final "
              "packaging — the X is removed by replacing the file, never by "
              "editing.", "",
              "| id | kind | maps to | image | source | status |",
              "|----|------|---------|-------|--------|--------|"]
        for s in self.scraps:
            md.append(f"| {s['sid']} | {s['kind']} | {s['ref']} | "
                      f"{'✓' if s['found'] else '—'} | {s['source']} | "
                      f"{s['status']} |")
        hunts = [s for s in self.scraps if s.get("hunt")]
        if hunts:
            md += ["", "## Portraits — the honest path (real archives)", ""]
            md += [f"- **{s['ref']}** (`{s['sid']}`): {s['hunt']}"
                   for s in hunts]
        md += ["", "## Prompts (paste-ready)", "", "```"]
        md += [s["prompt"] for s in self.scraps]
        md += ["```", ""]
        (self.out / "greybox-scraps.md").write_text("\n".join(md))
        (self.out / "greybox-scraps.txt").write_text(
            "\n".join(s["prompt"] for s in self.scraps) + "\n")
        (self.out / "scraps").mkdir(exist_ok=True)
        print(f"[greybox] wrote {self.out / 'greybox-scraps.md'} "
              f"({len(self.scraps)} prompts)")

    def render_board_html(self, warns):
        cards = []
        for b in self.beats:
            est = ' <span class="est">EST</span>' if b["est"] else ""
            cards.append(f"""
  <div class="card">
    <img src="frames/board-{b['id']}.jpg" alt="{b['id']}">
    <div class="meta"><b>{b['id']}</b> · {b['type']}{' · ' + b['role'] if b['role'] else ''}
      · {b['dur']:.1f}s{est} · scene {b['scene']}</div>
    <div class="narr">{b['narration']}</div>
    <div class="elem">{b['element']}</div>
  </div>""")
        warn_html = "".join(f"<li>{w.replace('`', '')}</li>" for w in warns)
        html = f"""<!doctype html><meta charset="utf-8">
<title>greybox — {self.slug}</title>
<style>
 body{{font-family:Georgia,serif;background:#E7DCC2;color:#3A2F23;margin:24px}}
 h1{{font-size:22px}} .sum{{margin-bottom:16px}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
 .card{{background:#F7F2E6;border:1px solid #C9BC9C;padding:10px;box-shadow:2px 3px 6px #0002}}
 .card img{{width:100%;border:1px solid #C9BC9C}}
 .meta{{font-size:12px;margin:6px 0 4px}} .narr{{font-size:14px}}
 .elem{{font-size:11px;color:#7A6A50;margin-top:4px;font-style:italic}}
 .est{{background:#CD853F;color:#fff;padding:0 4px;border-radius:3px;font-size:10px}}
 ul{{font-size:13px}}
</style>
<h1>greybox previz — {self.md.get('title', self.slug)}</h1>
<div class="sum">{len(self.beats)} beats · {len(self.scene_beats)} scenes ·
 {int(self.total // 60)}:{int(self.total % 60):02d} total ·
 review artifact, never published</div>
{f'<ul>{warn_html}</ul>' if warns else ''}
<div class="grid">{''.join(cards)}</div>
"""
        (self.out / "greybox-board.html").write_text(html)
        print(f"[greybox] wrote {self.out / 'greybox-board.html'}")


# ----------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="zero-cost scrapbook previz")
    ap.add_argument("folder", type=Path)
    ap.add_argument("--sheet", default="beat_sheet.json")
    ap.add_argument("--portrait", action="store_true")
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--height", type=int, default=480)
    ap.add_argument("--wps", type=float, default=2.4,
                    help="words/sec for beats without actual_duration_s")
    ap.add_argument("--fonts", help="extra font directory")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--report-only", action="store_true")
    ap.add_argument("--scrap-ar", default="4:3",
                    help="aspect ratio for element scrap prompts (portraits are 1:1)")
    ap.add_argument("--skin", default="journal", choices=sorted(SKINS),
                    help="journal = scrapbook previz; voxpaper = editorial "
                         "collage (Vox-style)")
    args = ap.parse_args()
    global SKIN, PAPER_TONES, CARD_PAPER, INK, TAPE
    SKIN = SKINS[args.skin]
    PAPER_TONES = SKIN["paper_tones"]
    CARD_PAPER = SKIN["card_paper"]
    INK = SKIN["ink"]
    TAPE = SKIN["tape_rgba"]
    folder = args.folder.resolve()
    if not (folder / args.sheet).exists():
        sys.exit(f"no {args.sheet} in {folder}")
    gb = Greybox(folder, args)
    gb.build_bases()
    warns = gb.render_report()
    gb.render_scraps()
    gb.render_board()
    gb.render_board_html(warns)
    if not args.report_only:
        gb.render_video()
    if warns:
        print(f"[greybox] {len(warns)} warning(s) — see greybox-report.md")


if __name__ == "__main__":
    main()
