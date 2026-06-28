#!/usr/bin/env python3
"""
package_video.py — generate the publish-time artifacts for a Bear's Notes video.

From beat_sheet.json it writes two files into the video folder:

  <slug>-youtube.md      — title, description (built from the narration), hashtags.
  <slug>-doodles-todo.md — per doodle beat: a starter Midjourney image prompt and a
                           stroke-by-stroke animation prompt, with checkboxes. These
                           are STARTERS — edit freely.

Both are drafts: the description reads back the spoken script as prose, and the
doodle prompts come straight from the beat sheet. Polish by hand as you like.

Usage:
    python package_video.py <video-folder>
"""
import argparse
import json
import re
import sys
from pathlib import Path

# beats that carry the spoken explanation (exclude bookends + bracketed labels)
def is_content(b):
    return b["beat_id"] not in ("INTRO", "OUTRO")


def subject_of(frame_prompt: str) -> str:
    m = re.search(r"\[DOODLE OBJECT\s*=\s*(.+?)\]\s*$", (frame_prompt or "").strip())
    return m.group(1).strip() if m else ""


def full_image_prompt(template: str, subject: str) -> str:
    if "[DOODLE OBJECT]" in template:
        return template.replace("[DOODLE OBJECT]", subject)
    return f"{subject}, {template}"


def write_youtube(folder: Path, sheet: dict):
    m = sheet["metadata"]
    beats = sheet["beats"]
    title = m.get("title", "")
    series = m.get("series", "Bears Notes")
    channel = m.get("channel_url", "youtube.com/@NikBearBrown")
    tags = m.get("hashtags", ["#BearsNotes"])

    content = [b["narration_text"] for b in beats if is_content(b) and b.get("narration_text")]
    # hook = the first 1–2 content sentences; body = the rest
    hook = " ".join(content[:2])
    body = " ".join(content[2:])

    out = folder / f"{m['slug']}-youtube.md"
    lines = [
        f"# {title} | Bear's Notes",
        "",
        "## Title",
        f"{title} — Bear's Notes",
        "",
        "## Description",
        hook,
        "",
        body,
        "",
        f"🐻 More Bear's Notes: {channel}",
        "",
        " ".join(tags),
    ]
    out.write_text("\n".join(lines))
    print(f"[ok] {out.name}")


def write_doodle_todo(folder: Path, sheet: dict):
    m = sheet["metadata"]
    template = sheet.get("doodle_prompt_template", "[DOODLE OBJECT]")
    out = folder / f"{m['slug']}-doodles-todo.md"
    lines = [f"# {m.get('title','')} — Doodle TODO", "",
             "Starter prompts (edit freely). For each doodle: generate the image, then",
             "animate it stroke-by-stroke. Save where noted, then overlay in your editor.", ""]

    n = 0
    for b in sheet["beats"]:
        if b.get("render") != "doodle":
            continue
        n += 1
        bid = b["beat_id"]
        subj = subject_of(b.get("end_frame_prompt", "")) or subject_of(b.get("start_frame_prompt", "")) \
            or b.get("new_visual_element", "")
        img = full_image_prompt(template, subj)
        anim = b.get("video_animation_prompt", "")
        save = "mp4/doodle-INTRO.mp4 (random from shared pool — or hand-make)" if bid == "INTRO" \
            else f"mp4/src-{bid}.mp4"
        lines += [
            f"## {bid} — {b.get('new_visual_element','')}",
            f"_Narration:_ \"{b.get('narration_text','').strip()}\"",
            "",
            "- [ ] Image (Midjourney):",
            "```",
            img,
            "```",
            "- [ ] Stroke-by-stroke (animation):",
            "```",
            anim,
            "```",
            f"- [ ] Save as `{save}`",
            "",
        ]
    if n == 0:
        lines.append("_No doodle beats in this video._")
    out.write_text("\n".join(lines))
    print(f"[ok] {out.name}  ({n} doodle beat(s))")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate YouTube description + doodle TODO.")
    ap.add_argument("folder")
    args = ap.parse_args()
    folder = Path(args.folder).expanduser().resolve()
    sheet_path = folder / "beat_sheet.json"
    if not sheet_path.exists():
        print(f"[err] no beat_sheet.json in {folder}", file=sys.stderr)
        return 1
    sheet = json.loads(sheet_path.read_text())
    write_youtube(folder, sheet)
    write_doodle_todo(folder, sheet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
