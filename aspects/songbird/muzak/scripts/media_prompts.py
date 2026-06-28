#!/usr/bin/env python3
"""
media_prompts.py — chunk the song into fixed blocks and write a text-to-image +
text-to-video prompt for each, grounded in that block's lyrics and the inferred
design. These generated clips/stills become the BACKGROUND layer that the wave +
lyrics overlay on top of (Remotion composites top-to-bottom).

Each block is labeled B01, B02, ... and every prompt STARTS with that id, so the
file you generate maps straight back to its slot. Drop the result in
`public/<slug>/media/B01.mp4` (or .jpg) and add it to `media-manifest.json`.

The creative subject is yours — this writes a sensible scaffold from the lyric
phrase + the design's visual metaphor and palette, in the format:

    B02, <subject> - <description>, <style/palette>, <composition>, <motion>

Replace <subject> with whatever you actually want (e.g. "Wrought Iron Gyarados").
The block id, timing, lyric phrase, palette and motion are filled for you.

Usage:
    python media_prompts.py --beat-data beat_data.json --lyrics lyrics.json \
        --design design.json --chunk 5 -o media-prompts.md
"""

import argparse
import json

BUCKET_WORDS = {
    "warm": "warm amber, ochre and ember tones on near-black",
    "neutral": "slate, dusk-violet and muted rose tones",
    "mix": "teal and gold, cool base with warm accents",
    "cool": "cyan, ice-blue and electric highlights",
}
MOTION_WORDS = {
    "slow": "slow drifting camera, minimal motion",
    "medium": "gentle parallax push, steady motion",
    "fast": "energetic camera move, fast parallax, dynamic",
}


def words_in(lyrics, f0, f1):
    """Return the lyric phrase sung within [f0, f1) frames."""
    parts = []
    for ln in lyrics.get("lines", []):
        if ln.get("words"):
            for w in ln["words"]:
                if f0 <= w["startFrame"] < f1:
                    parts.append(w["text"])
        else:
            if f0 <= ln["startFrame"] < f1:
                parts.append(ln["text"])
    return " ".join(parts).strip()


def section_at(beat_data, frame):
    for s in beat_data.get("sections", []):
        if s["startFrame"] <= frame < s["endFrame"]:
            return s["label"]
    return (beat_data.get("sections") or [{"label": "section_1"}])[-1]["label"]


def main():
    ap = argparse.ArgumentParser(description="Per-block media prompts for the overlay background.")
    ap.add_argument("--beat-data", required=True)
    ap.add_argument("--lyrics", required=True)
    ap.add_argument("--design", required=True)
    ap.add_argument("--chunk", type=float, default=5.0, help="block length in seconds (default 5)")
    ap.add_argument("--scenes", help="JSON of authored scene descriptions per block id "
                    "({\"scenes\": {\"B01\": \"...\"}}). These DESCRIBE A SCENE — use them "
                    "instead of raw lyric fragments, which don't tell an image model anything.")
    ap.add_argument("--style", default="",
                    help="style suffix appended to every prompt, e.g. "
                    "'the style of Simon Stalenhag, cinematic --ar 16:9 --profile <id>'. "
                    "When set, replaces the auto palette/framing tail.")
    ap.add_argument("--motion", default="",
                    help="motion suffix for the VIDEO prompt only (overrides the per-section default)")
    ap.add_argument("-o", "--out", default="media-prompts.md")
    # --- Higgsfield job spec (media-jobs.json) for the generation script ---
    ap.add_argument("--hf-style", default="",
                    help="descriptive style for Higgsfield jobs (NO Midjourney --ar/--profile flags); "
                    "e.g. 'the style of Simon Stalenhag, chiaroscuro, no text'")
    ap.add_argument("--man-soulid", default="", help="Soul ID UUID for the default man")
    ap.add_argument("--woman-soulid", default="", help="Soul ID UUID for the default woman")
    ap.add_argument("--man-desc", default="", help="anchor description for the man (reinforces the Soul ID)")
    ap.add_argument("--woman-desc", default="", help="anchor description for the woman")
    ap.add_argument("--char-model", default="text2image_soul_v2", help="Higgsfield model for character beats")
    ap.add_argument("--plain-model", default="nano_banana", help="Higgsfield model for no-character beats")
    ap.add_argument("--variations", type=int, default=3, help="generations per beat (you pick the best)")
    ap.add_argument("--aspect", default="16:9", help="aspect ratio (16:9 default; 9:16 for vertical)")
    args = ap.parse_args()

    bd = json.load(open(args.beat_data))
    ly = json.load(open(args.lyrics))
    dz = json.load(open(args.design))
    fps = bd["fps"]
    total = bd["durationInFrames"]
    chunk_f = int(round(args.chunk * fps))

    pal = dz.get("palette", {})
    bucket = pal.get("temperature_bucket", "neutral")
    palette_words = BUCKET_WORDS.get(bucket, "muted cinematic tones")
    metaphor = (dz.get("visual_metaphor") or {})
    concept = metaphor.get("concept") or dz.get("visual_concept") or "the song's mood"
    impl = metaphor.get("implementation") or ""

    # authored scene descriptions (the real visual per block) override raw lyrics;
    # cast tags (man/woman/none) pick the Higgsfield model + Soul ID per block.
    scenes, cast = {}, {}
    if args.scenes:
        sc = json.load(open(args.scenes))
        if isinstance(sc, dict):
            scenes = sc.get("scenes", sc)
            cast = sc.get("cast", {})
    # section -> motion intensity from design registers
    motion_by_section = {s["name"]: s.get("motion_intensity", "medium")
                         for s in dz.get("section_registers", [])}

    blocks = []
    n = 0
    f = 0
    while f < total:
        n += 1
        f1 = min(f + chunk_f, total)
        bid = "B%02d" % n
        phrase = words_in(ly, f, f1) or "(instrumental)"
        sec = section_at(bd, f)
        motion = args.motion or MOTION_WORDS.get(motion_by_section.get(sec, "medium"), MOTION_WORDS["medium"])
        # subject priority: authored scene > lyric phrase > concept. The authored
        # scene is what makes a usable image prompt; the lyric alone is not a scene.
        subject = scenes.get(bid) or (phrase if phrase != "(instrumental)" else concept)
        # style tail: the user's --style if given (e.g. a Midjourney style + profile),
        # otherwise the auto palette + framing.
        style = args.style.strip() if args.style else ("%s, cinematic wide shot, 16:9" % palette_words)
        img = "%s, %s, %s" % (bid, subject, style)
        vid = "%s, %s" % (img, motion)

        # --- Higgsfield job: clean prompt (NO block-id, NO Midjourney flags),
        # cast picks the model + Soul ID + anchor description. ---
        c = (cast.get(bid) or "none").lower()
        if c == "man":
            soul, cdesc, model = args.man_soulid, args.man_desc, args.char_model
        elif c == "woman":
            soul, cdesc, model = args.woman_soulid, args.woman_desc, args.char_model
        else:
            soul, cdesc, model = "", "", args.plain_model
        hf_style = args.hf_style.strip()
        hf_prompt = ", ".join(p for p in [cdesc.strip(), subject, hf_style] if p)

        blocks.append({
            "id": bid,
            "startSeconds": round(f / fps, 2),
            "endSeconds": round(f1 / fps, 2),
            "startFrame": f,
            "endFrame": f1,
            "section": sec,
            "lyric": phrase,
            "cast": c,
            "image_prompt": img,           # Midjourney-style sheet (with id + flags)
            "video_prompt": vid,
            "media_file": bid + ".mp4",     # or .jpg for a still
            "hf": {                          # Higgsfield jobs
                # image keyframe (generate_images.sh)
                "model": model,
                "soul_id": soul,
                "prompt": hf_prompt,
                "aspect_ratio": args.aspect,
                "variations": args.variations,
                # text+image -> video (generate_videos.sh): per-beat prompt =
                # the same authored scene + this beat's motion. The picked still
                # carries identity/framing; this text directs the motion/action.
                "video_prompt": hf_prompt + ", " + motion,
            },
        })
        f = f1

    # write JSON sidecar
    base = args.out.rsplit(".", 1)[0]
    json.dump({"chunkSeconds": args.chunk, "fps": fps, "blocks": blocks},
              open(base + ".json", "w"), indent=2)

    # write the Higgsfield job spec consumed by generate_images.sh
    jobs = [{"id": b["id"], "cast": b["cast"], **b["hf"]} for b in blocks]
    n_char = sum(1 for b in blocks if b["cast"] in ("man", "woman"))
    json.dump({
        "variations": args.variations,
        "aspect_ratio": args.aspect,
        "char_model": args.char_model,
        "plain_model": args.plain_model,
        "jobs": jobs,
    }, open("media-jobs.json", "w"), indent=2)

    # write the human-facing prompt sheet — each prompt in its OWN fenced code
    # block on its own line, so it's a single clean copy (renderers show a copy
    # button; in a plain editor it's still one isolated line to select).
    with open(args.out, "w") as fh:
        fh.write("# Media prompts — %d blocks of %gs\n\n" % (len(blocks), args.chunk))
        fh.write("Background layer for the wave + lyrics overlay. Generate each block, "
                 "save as `public/<slug>/media/<id>.mp4` (or `.jpg`), and list delivered "
                 "files in `media-manifest.json`. Replace the **subject** (right after the "
                 "block id) with your own creative idea — id, palette, framing and motion "
                 "are pre-filled.\n\n")
        fh.write("Visual concept: %s\n\n" % concept)
        for b in blocks:
            fh.write("## %s  ·  %.1f–%.1fs  ·  %s\n" % (b["id"], b["startSeconds"], b["endSeconds"], b["section"]))
            fh.write("lyric: %s\n\n" % (b["lyric"] or "(instrumental)"))
            fh.write("image\n```\n%s\n```\n\n" % b["image_prompt"])
            fh.write("video\n```\n%s\n```\n\n" % b["video_prompt"])
            fh.write("→ save as `media/%s`\n\n" % b["media_file"])

    # write a plain paste-ready .txt — one prompt per line, blank line between
    # blocks. Triple-click any line to grab a whole prompt.
    txt = args.out.rsplit(".", 1)[0] + ".txt"
    with open(txt, "w") as fh:
        for b in blocks:
            fh.write("%s\n" % b["image_prompt"])
            fh.write("%s\n\n" % b["video_prompt"])

    print("muzak: wrote %s (+ .json, + %s, + media-jobs.json)" % (args.out, txt.split('/')[-1]))
    print("  cast: %d character beats (man/woman, Soul ID), %d plain beats (%s)"
          % (n_char, len(blocks) - n_char, args.plain_model))
    print("  %d blocks of %gs (B01..%s) over %.0fs"
          % (len(blocks), args.chunk, blocks[-1]["id"], total / fps))
    print("  each prompt starts with its block id; palette=%s, concept=%r" % (bucket, concept[:48]))
    for b in blocks[:3]:
        print("    %s %s" % (b["id"], b["image_prompt"][:90]))
    print("    ...")


if __name__ == "__main__":
    main()
