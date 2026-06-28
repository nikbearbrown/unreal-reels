#!/usr/bin/env python3
"""
enhance_suggest.py — the OPTIONAL "enhance" pass for Bear's Notes.

Reads a video folder's beat_sheet.json and writes ONE markdown file —
`<folder>/enhance/Enhance.md` — that SUGGESTS where a real-looking asset (a still,
a short clip, or a Soul-ID character moment) might teach better than flat-doodle
Manim geometry. For each candidate it gives the beat, why it was flagged, the
suggested asset, a ready-to-paste Higgsfield command, and the target filename in
`enhance/`.

It NEVER:
  - generates anything (you run the Higgsfield commands yourself),
  - edits the Manim scene or the beat sheet,
  - forces a suggestion (most beats stay pure Manim; if nothing qualifies it says so).

The flat-doodle library stays style-locked. `enhance/` is the quarantined,
photoreal-allowed exception layer. See reference/enhance.md.

Usage:
    python scripts/enhance_suggest.py <video-folder>
    python scripts/enhance_suggest.py <video-folder> --image-model nano_banana_2 --clip-model seedance_2_0
"""
import argparse
import json
import re
import sys
from pathlib import Path

# ── curated detectors (high precision — suggest, don't nag) ──────────────────
# Named scientists/mathematicians worth a shout-out (Soul-ID character moment).
SCIENTISTS = {
    "planck", "einstein", "bohr", "heisenberg", "schrodinger", "schrödinger",
    "de broglie", "broglie", "born", "dirac", "pauli", "fermi", "feynman",
    "godel", "gödel", "tonomura", "rayleigh", "jeans", "wien", "boltzmann",
    "compton", "davisson", "germer", "young", "maxwell", "newton", "curie",
    "hawking", "turing", "shannon", "bell", "everett", "wheeler", "dyson",
    "rutherford", "thomson", "millikan", "stern", "gerlach", "aspect",
    "darwin", "mendel", "watson", "crick", "franklin", "pasteur", "koch",
    "hodgkin", "huxley", "krebs", "mcclintock", "margulis",
}

# Nameable physical/biological objects the viewer must RECOGNIZE — things flat
# Manim geometry can't draw convincingly. (Concepts/relationships stay Manim.)
OBJECTS = {
    # physics / astro
    "satellite", "telescope", "microscope", "prism", "nebula", "galaxy",
    "supernova", "comet", "crystal", "filament", "lightbulb", "light bulb",
    "vacuum tube", "cloud chamber", "accelerator", "detector",
    # biology
    "neuron", "synapse", "bacteriophage", "phage", "virus", "bacterium",
    "bacteria", "mitochondria", "mitochondrion", "ribosome", "chromosome",
    "chloroplast", "membrane", "cell membrane", "blood vessel", "capillary",
    "artery", "alveoli", "alveolus", "nephron", "muscle fiber", "muscle fibre",
    "antibody", "receptor", "enzyme", "tumor", "tumour", "cilia", "flagellum",
}

# Possessive-law pattern: "Planck's idea", "Wien's law", etc. (secondary signal)
LAW_RE = re.compile(
    r"\b([A-ZÖÄ][a-zöä]+)(?:'s|’s)\s+"
    r"(law|idea|rule|principle|equation|constant|effect|theorem|model|relation|hypothesis|law)\b"
)
HOOK_IDS = {"INTRO", "H01", "H02", "H03"}


def _scientists_in(text):
    low = text.lower()
    hits = []
    for name in sorted(SCIENTISTS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(name) + r"\b", low):
            hits.append(name)
    # possessive-law names not already in the curated set
    for m in LAW_RE.finditer(text):
        nm = m.group(1).lower()
        if nm not in {h.split()[-1] for h in hits} and len(nm) > 2:
            hits.append(nm)
    # collapse names contained in a longer matched name ("broglie" ⊂ "de broglie")
    hits = [h for h in hits if not any(h != b and h in b for b in hits)]
    # de-dupe, title-case for display
    seen, out = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h)
            out.append(h.title())
    return out


def _objects_in(text):
    low = text.lower()
    out = []
    for obj in sorted(OBJECTS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(obj) + r"\b", low):
            out.append(obj)
    # collapse near-duplicates already contained in a longer match
    out = [o for o in out if not any(o != b and o in b for b in out)]
    return out


def _scientist_prompt(name):
    return (f"portrait of {name}, an early-20th-century scientist, in a tweed suit "
            f"and round wire glasses, standing at a chalkboard covered in equations, "
            f"natural light, period documentary photograph, consistent character, "
            f"shallow depth of field")


def _scientist_clip_prompt(name):
    return (f"{name}, an early-20th-century scientist in a tweed suit and round glasses, "
            f"writing equations on a university chalkboard, subtle natural movement, "
            f"period documentary look, 5 seconds")


def _object_prompt(obj):
    return (f"a single {obj}, clean diagrammatic illustration, centered on a plain "
            f"white background, clear and recognizable, soft shading")


def _hook_prompt(nar):
    nar = re.sub(r'["“”]', "", nar.replace("\n", " ")).strip()
    return (f"a short hand-drawn scene-setter: {nar[:80]}, minimal, "
            f"bold ink lines on white, 3 seconds")


def build(folder: Path, image_model: str, clip_model: str, soul_model: str):
    bs_path = folder / "beat_sheet.json"
    if not bs_path.exists():
        print(f"[err] no beat_sheet.json in {folder}", file=sys.stderr)
        return 2
    bs = json.loads(bs_path.read_text())
    meta = bs.get("metadata", {})
    beats = bs.get("beats", [])
    title = meta.get("title", folder.name)
    slug = meta.get("slug", folder.name)

    # Dedupe across beats: one block per scientist / per object (one Soul ref or
    # still serves all its placements); hooks stay per-beat (distinct moments).
    scientists, objects, hooks = {}, {}, []
    for b in beats:
        bid = b.get("beat_id", "?")
        nar = (b.get("narration_text") or "").replace("\n", " ").strip()
        sci = _scientists_in(nar)
        objs = _objects_in(nar)
        for name in sci:
            scientists.setdefault(name, {"beats": [], "nar": nar})["beats"].append(bid)
        for obj in objs:
            objects.setdefault(obj, {"beats": [], "nar": nar})["beats"].append(bid)
        if bid in HOOK_IDS and not sci and not objs:
            hooks.append((bid, nar))
    n_cands = len(scientists) + len(objects) + len(hooks)

    out = []
    out.append(f"# Enhance — {title}")
    out.append("")
    out.append("> **OPTIONAL. Suggestions only.** This pass generates nothing, edits no "
               "scene, and forces nothing. The flat-doodle Manim base and the "
               "style-locked doodle library are unchanged. Enhance assets are the "
               "*quarantined, photoreal-allowed exception* — they live only in this "
               "`enhance/` folder. Pick the few that help; ignore the rest.")
    out.append("")
    out.append("**Decision rule:** does the narration name a real thing the viewer must "
               "*recognize* (a scientist, a physical/biological object)? If yes, a real-looking "
               "asset may beat geometry. If it's a concept, process, or relationship — keep it Manim.")
    out.append("")
    out.append("**Soul-ID note:** for a recurring invented character (an on-brand, "
               "copyright-safe \"scientist\" who stays the same person across shots), train a "
               "Soul ref once (`higgsfield soul-id --help`) and attach it to the commands below "
               "(the ref flag is shown by `higgsfield generate create --help`). Check cost first "
               "with `higgsfield generate cost`; video models cost more than stills.")
    out.append("")

    if n_cands == 0:
        out.append("## No enhance candidates detected")
        out.append("")
        out.append("Nothing in this script names a recognizable object or person, so pure "
                   "Manim doodle is the right call. No assets needed.")
        _write(folder, out)
        print(f"[enhance] no candidates — wrote {folder/'enhance'/'Enhance.md'}")
        return 0

    out.append(f"## {n_cands} suggestion(s)  ·  "
               f"{len(scientists)} scientist · {len(objects)} object · {len(hooks)} hook")
    out.append("")
    bridge = ("- **Bridge (optional):** to keep a photoreal insert from clashing with the "
              "flat-ink doodles, frame it (hand-drawn border) and/or duotone it in the "
              "channel palette so it reads as intentional, not pasted-in.")

    for who, info in scientists.items():
        beats_s = ", ".join(info["beats"])
        out.append(f"### Scientist shout-out: {who}  ·  beats {beats_s}")
        out.append(f"> \"{info['nar']}\"")
        out.append("")
        out.append(f"- **Why:** the narration names **{who}** — a 3–5s Soul-ID character "
                   f"moment (or a still) lands the human behind the idea. Appears at: {beats_s} "
                   f"— one Soul ref covers every placement.")
        out.append(f"- **Suggested:** Soul-ID still **or** ~4–5s clip of an invented "
                   f"period-scientist character. Photoreal is fine here (quarantined).")
        out.append(f"- **Still:** `enhance/{_safe(who)}.png`")
        out.append("  ```")
        out.append(f"  higgsfield generate create {soul_model} --prompt \"{_scientist_prompt(who)}\"  # + your Soul ref flag")
        out.append("  ```")
        out.append(f"- **Clip (~5s):** `enhance/{_safe(who)}.mp4`")
        out.append("  ```")
        out.append(f"  higgsfield generate create {clip_model} --prompt \"{_scientist_clip_prompt(who)}\"  # + your Soul ref flag")
        out.append("  ```")
        out.append("")
        out.append(bridge)
        out.append("")

    for obj, info in objects.items():
        beats_s = ", ".join(info["beats"])
        out.append(f"### Nameable object: {obj}  ·  beats {beats_s}")
        out.append(f"> \"{info['nar']}\"")
        out.append("")
        out.append(f"- **Why:** the narration names **{obj}** — something Manim can't draw "
                   f"convincingly and the viewer needs to recognize.")
        out.append(f"- **Suggested:** a clean still. For *biology*, prefer a diagrammatic "
                   f"style (Illustrae / Midjourney diagram mode) to stay closer to the "
                   f"doodle aesthetic; for *phenomena*, photoreal is fine (quarantined).")
        out.append(f"- **Still:** `enhance/{_safe(obj)}.png`")
        out.append("  ```")
        out.append(f"  higgsfield generate create {image_model} --prompt \"{_object_prompt(obj)}\"")
        out.append("  ```")
        out.append("")
        out.append(bridge)
        out.append("")

    for bid, nar in hooks:
        out.append(f"### {bid} — hook beat (optional scene-setter)")
        out.append(f"> \"{nar}\"")
        out.append("")
        out.append("- **Why:** a hook beat — a quick hand-drawn moment can set the scene "
                   "better than a text card. Lowest priority; skip freely.")
        out.append(f"- **Suggested:** a short doodle clip overlaid at this beat by "
                   f"`composite_doodles.py`.")
        out.append(f"- **Clip:** `enhance/{bid}-hook.mp4`")
        out.append("  ```")
        out.append(f"  higgsfield generate create {clip_model} --prompt \"{_hook_prompt(nar)}\"")
        out.append("  ```")
        out.append("")
        out.append(bridge)
        out.append("")

    out.append("---")
    out.append("")
    out.append("### How an asset wires back in (only once you've made and vetted it)")
    out.append("")
    out.append("- **Still (PNG):** drop in `enhance/`, load in the scene with "
               "`ImageMobject(\"enhance/<file>.png\")` at that beat (animate move/scale/fade). "
               "Transparent or white background; must survive a move/scale/fade test.")
    out.append("- **Clip (MP4):** name it for its beat and let `composite_doodles.py` overlay it "
               "at that beat's window — same path the optional doodle overlays already use. "
               "Manim never ingests mp4.")
    out.append("- Nothing here is required to ship: the `assemble` master is already complete.")
    out.append("")

    _write(folder, out)
    print(f"[enhance] {n_cands} suggestion(s) → {folder/'enhance'/'Enhance.md'}")
    return 0


def _safe(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _write(folder: Path, lines):
    edir = folder / "enhance"
    edir.mkdir(exist_ok=True)
    (edir / "Enhance.md").write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Optional enhance suggestions (no generation).")
    ap.add_argument("folder", help="video folder containing beat_sheet.json")
    ap.add_argument("--image-model", default="nano_banana_2", help="Higgsfield model for stills")
    ap.add_argument("--clip-model", default="seedance_2_0", help="Higgsfield model for short clips")
    ap.add_argument("--soul-model", default="text2image_soul_v2", help="Higgsfield Soul-ID image model")
    args = ap.parse_args()
    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"[err] not a folder: {folder}", file=sys.stderr)
        sys.exit(2)
    sys.exit(build(folder, args.image_model, args.clip_model, args.soul_model))


if __name__ == "__main__":
    main()
