#!/usr/bin/env python3
"""
infer_design.py — derive a design brief from the audio + lyric features.

This is muzak's design-GUIDANCE engine. Rather than wait for a human to write a
design doc, it reads the analyzed features (brightness, dynamic range, key/mode,
BPM, lyric density, sections) and emits design.json: a starting design spec where
every *mechanical* and *safety* decision is already made and constrained.

What the script decides deterministically (so the model can't violate it):
  - beat-hit caps from dynamic range  (compressed tracks must not strobe)
  - spring easing from BPM
  - allowed lyric animation styles from density (fast lyrics can't char-spring)
  - visualizer FORM from brightness
  - a curated starting palette from brightness + mode bias (no #ff0000 placeholders)
  - section registers covering the whole song with no gaps

What it leaves for the `design` phase to reason out (semantic, not algorithmic):
  - visual_concept and visual_metaphor (null TODOs — read the lyrics)
  - palette refinement within the temperature bucket

The mapping rules and their rationale live in references/design-inference.md;
this script is their executable, constraint-enforcing form. design.json is the
top-ranked source for theme.ts at build time, below only a hand-written design doc.

Usage:
    python infer_design.py --beat-data beat_data.json --lyrics lyrics.json -o design.json
"""

import argparse
import json

# --- curated palettes per brightness (color-temperature) bucket -------------
# Considered hexes, not placeholders. The mode bias nudges accent_secondary
# warmer (major) or cooler (minor); the model may refine within the bucket.
PALETTES = {
    "warm": {        # brightness 0.00–0.30 — dark/warm timbre
        "background": "#1A0E08", "accent_primary": "#F5A623",
        "accent_secondary": "#C1440E", "accent_warm": "#FFB347",
        "beat_flash": "#FFE3B3",
    },
    "neutral": {     # 0.30–0.55
        "background": "#15121F", "accent_primary": "#C9B8E8",
        "accent_secondary": "#8E6CCF", "accent_warm": "#D9A066",
        "beat_flash": "#EDE7F6",
    },
    "mix": {         # 0.55–0.75 — cool/warm mix
        "background": "#0E1518", "accent_primary": "#2EC4B6",
        "accent_secondary": "#FFB703", "accent_warm": "#FF9F1C",
        "beat_flash": "#E0FBFC",
    },
    "cool": {        # 0.75–1.00 — bright/cool
        "background": "#08121A", "accent_primary": "#7CE0F2",
        "accent_secondary": "#4A90E2", "accent_warm": "#9AD7E0",
        "beat_flash": "#EAF6FF",
    },
}


def palette_bucket(brightness):
    if brightness < 0.30:
        return "warm"
    if brightness < 0.55:
        return "neutral"
    if brightness < 0.75:
        return "mix"
    return "cool"


def spring_from_bpm(bpm):
    if bpm < 80:
        return ("heavy", 20, 80)
    if bpm < 110:
        return ("smooth", 16, 120)
    if bpm < 140:
        return ("crisp", 12, 160)
    return ("snappy", 8, 220)


def beat_hits_from_dr(dr):
    # (flash_opacity_max, scale_pulse_max, style note)
    if dr < 6:
        return (0.15, 1.08, "subtle glow pulse, no full-screen flash")
    if dr <= 12:
        return (0.25, 1.15, "standard flash + ring pulse")
    return (0.40, 1.30, "full dramatic flash, strong spring overshoot")


def typography_from_density(cls):
    table = {
        "sparse":   (["character-spring", "word-spring"], "character-spring", 8, 6, 20),
        "moderate": (["word-by-word", "line-wipe"],       "word-by-word",     8, 6, 18),
        "dense":    (["line-wipe", "instant"],            "line-wipe",        6, 4, 22),
        "rapid":    (["instant"],                          "instant",          0, 0, 16),
    }
    return table.get(cls, table["moderate"])


def visualizer_from_brightness(brightness, palette):
    if brightness < 0.35:
        form, pos = "bars", "bottom-third"
    elif brightness < 0.65:
        form, pos = "ring", "center"
    else:
        form, pos = "hybrid", "lower-center"  # waveform path + thin bar ring
    return {
        "type": form,
        "sample_count": 64,          # power of two
        "position": pos,
        "logarithmic": True,
        "gradient_start": palette["accent_primary"],
        "gradient_end": palette["accent_secondary"],
    }


def section_registers(beat_data):
    energy = beat_data.get("energyPerFrame", [])
    regs = []
    secs = beat_data.get("sections") or []
    for i, s in enumerate(secs):
        seg = energy[s["startFrame"]:s["endFrame"]] or [0.0]
        mean_e = sum(seg) / len(seg)
        if mean_e < 0.2:
            dens, sat, motion = "sparse", 0.5, "slow"
        elif mean_e < 0.55:
            dens, sat, motion = "moderate", 0.8, "medium"
        else:
            dens, sat, motion = "full", 1.0, "fast"
        regs.append({
            "name": s["label"],            # design phase renames to verse/chorus/etc.
            "start_seconds": s["start"],
            "end_seconds": s["end"],
            "mean_energy": round(mean_e, 3),
            "element_density": dens,
            "saturation_multiplier": sat,
            "motion_intensity": motion,
            "active_components": ["BackgroundLayer", "SectionVisualizer", "LyricLayer"],
            "notes": None,                 # design phase fills (semantic)
        })
    return regs


def build_design(beat_data, lyrics, look="dark"):
    f = beat_data.get("features", {})
    brightness = f.get("brightness", 0.5)
    dr = f.get("dynamic_range_db", 9.0)
    bpm = beat_data.get("bpm", 120.0)
    mode = f.get("mode")
    mode_conf = f.get("mode_confidence", 0.0)
    dens = (lyrics.get("density") or {}).get("density_class", "moderate")

    bucket = palette_bucket(brightness)
    palette = dict(PALETTES[bucket])
    # mode is a *weak* bias, only applied when reasonably confident
    if mode == "major" and mode_conf >= 0.05:
        mode_bias = "warmer"
    elif mode == "minor" and mode_conf >= 0.05:
        mode_bias = "cooler"
    else:
        mode_bias = "neutral"

    easing, damping, stiffness = spring_from_bpm(bpm)
    flash_cap, scale_cap, hit_note = beat_hits_from_dr(dr)
    allowed, default_style, entry, exit_, hold = typography_from_density(dens)

    # Lyric-forward default = the captioned-audiogram look: a dense oscilloscope
    # waveform across the whole video + karaoke word-highlighting. Applied when the
    # song has lyrics and isn't rapid-fire (where per-word highlighting can't keep up).
    has_lyrics = bool((lyrics.get("lines") or []))
    viz = visualizer_from_brightness(brightness, palette)
    if has_lyrics and dens != "rapid":
        default_style = "karaoke"
        if "karaoke" not in allowed:
            allowed = ["karaoke"] + allowed
        viz["type"] = "audiogram"

    return {
        "version": 1,
        "source": "inferred",   # vs "human" if a person edits this
        "look": look,           # "dark" or "ink" (white bg, black ink — stick figures)
        "derived_from": {
            "brightness": brightness, "dynamic_range_db": dr, "bpm": round(bpm, 1),
            "key": f.get("key"), "mode": mode, "mode_confidence": mode_conf,
            "lyric_density_class": dens,
            "lyric_words_per_second": (lyrics.get("density") or {}).get("words_per_second"),
        },

        # SEMANTIC — left for the `design` phase to reason from the lyrics.
        "visual_concept": None,
        "visual_metaphor": {"concept": None, "implementation": None, "lyric_basis": None},

        "palette": {
            **palette,
            "temperature_bucket": bucket,
            "mode_bias": mode_bias,
            "rationale": ("brightness %.2f -> %s bucket; mode '%s' (conf %.2f) biases %s. "
                          "Refine within this temperature, do not jump buckets."
                          % (brightness, bucket, mode, mode_conf, mode_bias)),
        },

        "typography": {
            "title_font": "Inter",
            "lyric_font": "Inter",
            "lyric_animation_style": default_style,
            "allowed_animation_styles": allowed,   # HARD constraint from density
            "animation_rationale": ("density '%s' allows %s; '%s' chosen as default."
                                    % (dens, allowed, default_style)),
            "entry_frames": entry, "exit_frames": exit_, "readable_hold_frames": hold,
        },

        "motion_vocabulary": {
            "easing_character": easing,
            "spring_damping": damping,
            "spring_stiffness": stiffness,
            "beat_flash_opacity_max": flash_cap,   # HARD cap from dynamic range
            "beat_scale_pulse_max": scale_cap,     # HARD cap from dynamic range
            "rationale": ("BPM %.0f -> %s easing (damping %d/stiffness %d); "
                          "dynamic range %.1f dB -> %s (flash<=%.2f, scale<=%.2f)."
                          % (bpm, easing, damping, stiffness, dr, hit_note, flash_cap, scale_cap)),
        },

        "visualizer": viz,

        "section_registers": section_registers(beat_data),

        "negative_space_strategy": None,           # design phase fills
        "proof_of_concept_note": None,             # design phase fills (which chorus 8-10s)
    }


def to_theme_ts(design):
    """Emit a theme.ts the mechanical components read. design.json is the brief;
    theme.ts is its machine form. Build keeps these in sync."""
    p = design["palette"]; m = design["motion_vocabulary"]
    t = design["typography"]; v = design["visualizer"]
    samples = v["sample_count"] if (v["sample_count"] & (v["sample_count"] - 1)) == 0 else 64
    # "ink" look (stick figures): white background, black audiogram + black text.
    ink = design.get("look") == "ink"
    if ink:
        bg, acc, acc2, txt, flash = "#FFFFFF", "#141414", "#444444", "#141414", "#141414"
        flash_max = min(0.08, m["beat_flash_opacity_max"]); bg_sat = 0; bg_lum = "[96, 99]"
    else:
        bg, acc, acc2, txt = p["background"], p["accent_primary"], p["accent_secondary"], "#FFFFFF"
        flash = p["beat_flash"]; flash_max = m["beat_flash_opacity_max"]; bg_sat = 45; bg_lum = "[8, 16]"
    return f"""// theme.ts — GENERATED from design.json by infer_design.py.
// Mechanical components read ONLY from here. Re-run infer_design (or hand-edit a
// design doc) to change the look; timing/structure are untouched.
export const theme = {{
  // palette (color-temperature bucket: {p['temperature_bucket']}, mode bias: {p['mode_bias']})
  background: "{bg}",
  accent: "{acc}",
  accent2: "{acc2}",
  accentWarm: "{p['accent_warm']}",
  textColor: "{txt}",
  flashColor: "{flash}",
  flashMax: {flash_max},          // HARD cap from dynamic range
  beatScalePulseMax: {m['beat_scale_pulse_max']},   // HARD cap from dynamic range

  // motion vocabulary (from BPM)
  easingCharacter: "{m['easing_character']}",
  springDamping: {m['spring_damping']},
  springStiffness: {m['spring_stiffness']},

  // type
  fontFamily: "{t['lyric_font']}, system-ui, sans-serif",
  lyricSize: 56,
  hookSize: 88,
  fontWeight: 700,
  lyricStyle: "{t['lyric_animation_style']}",       // must be in allowed list
  lyricInFrames: {t['entry_frames']},
  lyricOutFrames: {t['exit_frames']},
  readableHoldFrames: {t['readable_hold_frames']},

  // visualizer (form from brightness)
  visualizerType: "{v['type']}",
  spectrumSamples: {samples},
  spectrumMaxHeight: 240,
  waveformStroke: 3,
  waveformMid: 0.78,
  waveformAmp: 0.15,
  bgHueRange: [222, 268] as [number, number],
  bgSat: {bg_sat},
  bgLumRange: {bg_lum} as [number, number],
}};
"""


def main():
    ap = argparse.ArgumentParser(description="Infer a design brief from audio + lyric features.")
    ap.add_argument("--beat-data", required=True)
    ap.add_argument("--lyrics", required=True)
    ap.add_argument("-o", "--out", default="design.json")
    ap.add_argument("--emit-theme", help="also write a theme.ts to this path")
    ap.add_argument("--look", choices=["dark", "ink"], default="dark",
                    help="dark (default) or ink (white bg + black audiogram/text, for stick figures)")
    args = ap.parse_args()

    beat_data = json.load(open(args.beat_data))
    lyrics = json.load(open(args.lyrics))
    if "features" not in beat_data:
        raise SystemExit("muzak: beat_data.json has no 'features' block — re-run analyze_audio.py.")

    design = build_design(beat_data, lyrics, look=args.look)
    json.dump(design, open(args.out, "w"), indent=2)

    if args.emit_theme:
        with open(args.emit_theme, "w") as fh:
            fh.write(to_theme_ts(design))

    p = design["palette"]; m = design["motion_vocabulary"]; t = design["typography"]
    print("muzak: wrote %s" % args.out)
    print("  palette:     %s bucket (%s), bias %s  bg %s / %s / %s"
          % (p["temperature_bucket"], design["derived_from"]["key"], p["mode_bias"],
             p["background"], p["accent_primary"], p["accent_secondary"]))
    print("  motion:      %s  (spring %d/%d)  flash<=%.2f scale<=%.2f"
          % (m["easing_character"], m["spring_damping"], m["spring_stiffness"],
             m["beat_flash_opacity_max"], m["beat_scale_pulse_max"]))
    print("  type:        %s  (allowed: %s)  from density '%s'"
          % (t["lyric_animation_style"], ", ".join(t["allowed_animation_styles"]),
             design["derived_from"]["lyric_density_class"]))
    print("  visualizer:  %s @ %s" % (design["visualizer"]["type"], design["visualizer"]["position"]))
    print("  TODO (design phase): visual_concept, visual_metaphor, section notes,")
    print("       negative_space_strategy, proof_of_concept_note  — reason these from the lyrics.")


if __name__ == "__main__":
    main()
