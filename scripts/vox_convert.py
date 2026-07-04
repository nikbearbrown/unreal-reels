#!/usr/bin/env python3
"""vox_convert.py — convert an existing video folder (bears-doodles / brownblue
physics format) into a vox-explainer reel.

WHAT CARRIES OVER (free, by default):
  - narration_text / tts_normalized_text per beat, the generated mp3s and their
    measured actual_duration_s — for every beat you KEEP. Rewriting lines into
    Vox register is expected: flip that beat's "narration" to "rewrite" and
    regenerate only those beats (generate_audio.py <reel> --only <IDs>); the
    compile re-clocks them automatically.
WHAT IS RE-PLANNED (the point of the conversion):
  - every visual. Old Manim scenes are NOT ported — each beat gets a vox shot
    type (STILL/FOOTAGE/DOCUMENT/GRAPHIC/COMPOSITE/CARD) by heuristic, marked
    needs_review, and the SHOTLIST carries seeds (old visual description +
    archive queries). The human/agent rewrites visuals in the vox grammar;
    the QC gates audit ONLY what survives conversion.

Usage:
  python3 scripts/vox_convert.py physics/<slug> [--dest reels/vox-<slug>]
"""
import argparse, json, re, shutil, sys
from pathlib import Path

VOX_META = {
    "aspect_ratio": "16:9",
    "style_preset": "vox-editorial",
    "isotype_mark": "square",
    "accents": {"data": ["#BF3339", "#3D5A80"], "annotation": "#D35F43",
                "highlighter": "#F5D061"},
    "ground": "#F3EBDD",
    "style_bible": {
        "visual_style": "editorial paper collage on real newsprint scan; desaturated "
                        "archival plates; flat annotation plane; serif labels with "
                        "hairline underlines; one hand-drawn annotation per graphic max",
        "color_palette": "cream ground, charcoal serif type, two accents max, "
                         "terracotta/yellow as the single editor's-pen voice",
        "lighting_style": "flat print, no digital effects",
    },
    "accent_color": "#BF3339", "brown_color": "#D35F43", "highlight_color": "#F5D061",
}

RULES = [  # (keywords, type, source, motion) — first match wins
    (("title", "card", "logo", "outro", "end card"), "CARD", "own", "hold"),
    (("quote", "said", "“"), "DOCUMENT", "archive", "highlight"),
    (("photo", "photograph", "archival", "portrait", "historical"), "STILL", "archive", "kenburns"),
    (("footage", "b-roll", "broll", "clip", "film"), "FOOTAGE", "archive", "clip"),
    (("equation", "formula", "graph", "plot", "axes", "curve", "chart", "grid",
      "histogram", "spectrum", "wave", "packet", "distribution", "diagram",
      "energy level", "well", "barrier", "slit", "orbital"), "GRAPHIC", "own", "manim"),
    (("experiment", "apparatus", "lab", "detector", "laser", "oven", "screen",
      "sun", "star", "atom", "electron beam"), "STILL", "ai", "kenburns"),
]

def classify(beat):
    text = " ".join(str(beat.get(k, "")) for k in
                    ("new_visual_element", "scene_description",
                     "video_animation_prompt", "image_prompt",
                     "narration_text")).lower()
    for kws, t, s, m in RULES:
        if any(k in kws[0] or k in text for k in kws if k in text):
            return t, s, m
    return "GRAPHIC", "own", "manim"   # physics-explainer default

def archive_queries(beat, slug):
    words = re.sub(r"[^a-z ]", "", (beat.get("new_visual_element") or
                                    beat.get("narration_text", "")).lower())
    terms = "+".join([w for w in words.split() if len(w) > 4][:4]) or slug
    return [
        f"https://www.loc.gov/free-to-use/?q={terms}",
        f"https://commons.wikimedia.org/w/index.php?search={terms}&title=Special:MediaSearch",
        f"https://archive.org/search?query={terms}",
    ]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("--dest", type=Path, default=None)
    a = ap.parse_args()
    src = a.src.resolve()
    sheet = json.loads((src / "beat_sheet.json").read_text())
    slug = sheet.get("metadata", {}).get("slug", src.name)
    dest = (a.dest or Path("reels") / f"vox-{src.name}").resolve()
    if dest.exists():
        sys.exit(f"[convert] {dest} already exists — remove it or pass --dest")
    dest.mkdir(parents=True)
    (dest / "media").mkdir()
    (dest / "manim").mkdir()

    smd = sheet.get("metadata", {})
    md = dict(VOX_META)
    md.update(slug=f"vox-{src.name}", title=smd.get("title", src.name),
              voice_id=smd.get("voice_id"),
              clock="narration reused from source (already measured)",
              converted_from=str(src),
              purpose="CONVERTED from bears-doodles/brownblue format — every "
                      "visual re-planned in vox grammar; audio carried over.")

    have_audio = (src / "mp3").is_dir()
    if have_audio:
        shutil.copytree(src / "mp3", dest / "mp3")

    beats_out, report, histo = [], [], {}
    for b in sheet.get("beats", []):
        bid = b.get("beat_id", "?")
        t, s, m = classify(b)
        histo[t] = histo.get(t, 0) + 1
        old_visual = (b.get("new_visual_element") or
                      b.get("scene_description") or "").strip()
        nb = {
            "beat_id": bid,
            "narration_text": b.get("narration_text", ""),
            "tts_normalized_text": b.get("tts_normalized_text"),
            "actual_duration_s": b.get("actual_duration_s"),
            "audio_file": b.get("audio_file"),  # kept even if mp3/ not yet copied —
                                                # compile goes silent until files arrive
            "shot": {"type": t, "source": s, "motion": m},
            "narration": "keep",   # flip to "rewrite" when you change the line —
                                   # then regenerate ONLY those beats:
                                   #   generate_audio.py <reel> --only <IDs>
            "needs_review": True,
            "source_visual": old_visual or None,
            "new_visual_element": f"[{t}] TODO — was: {old_visual[:60]}" if old_visual
                                  else f"[{t}] TODO",
            "chosen_media": None,
        }
        if s == "archive":
            nb["archive_queries"] = archive_queries(b, src.name)
        beats_out.append(nb)
        report.append((bid, t, s, old_visual[:70]))

    json.dump({"metadata": md, "beats": beats_out},
              open(dest / "beat_sheet.json", "w"), indent=2)

    # scaffold for this reel's own Manim fragments (vox_run picks it up)
    (dest / "vox_scenes.py").write_text(
        '"""Per-reel vox Manim fragments — import the shared library and write\n'
        'one Scene per GRAPHIC beat, named <BEATID>_<Name>(Scene), rendered to\n'
        "the beat's measured duration. QC gates audit these on every run.\"\"\"\n"
        "import sys, pathlib\n"
        "sys.path.insert(0, str(pathlib.Path(__file__).resolve()"
        ".parents[2] / 'aspects/explainer/vox-explainer/manim'))\n"
        "from vox_graphics import *   # noqa: F401,F403 — tokens + mobjects\n\n"
        "# TODO: one scene per GRAPHIC beat below.\n")

    lines = [f"# SHOTLIST — {md['slug']} (CONVERTED — every beat needs_review)",
             "", f"Source: {src}", f"Audio: {'reused mp3/' if have_audio else 'MISSING — generate'}",
             "", "## Shot-type histogram (heuristic first pass — retype freely)",
             "", " · ".join(f"{k} {v}" for k, v in sorted(histo.items())), "",
             "## Beats — old visual → assigned type", ""]
    for bid, t, s, old in report:
        lines.append(f"- **{bid}** → {t}/{s} — was: {old or '(none)'}")
    lines += ["", "## Conversion contract",
              "- Per-beat narration: `keep` reuses the source mp3 + duration (free); "
              "`rewrite` means you changed the line — regenerate just those beats "
              "(`generate_audio.py <reel> --only <IDs>`) and the compile re-clocks. "
              "Rewrites into Vox register (cold opens, quote beats) are EXPECTED.",
              "- Old Manim scenes are NOT ported. Write vox fragments in "
              "vox_scenes.py for GRAPHIC beats; fill archive/ai slots via media/.",
              "- Run `bash scripts/vox_run.sh <this reel>` — QC gates audit only "
              "what survives conversion."]
    (dest / "SHOTLIST.md").write_text("\n".join(lines) + "\n")

    print(f"[convert] {src.name} → {dest}")
    print(f"[convert] {len(beats_out)} beats · audio {'reused' if have_audio else 'MISSING'}"
          f" · types: " + " ".join(f"{k}:{v}" for k, v in sorted(histo.items())))
    print(f"[convert] every beat is needs_review=true — retype in SHOTLIST.md, "
          f"then write vox_scenes.py fragments")

if __name__ == "__main__":
    main()
