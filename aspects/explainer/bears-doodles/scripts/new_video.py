#!/usr/bin/env python3
"""
new_video.py — scaffold a Bear's Doodles video folder.

Creates <root>/<slug>/ with mp3/ mp4/ frames/ media/ and a beat_sheet.json
skeleton pre-filled with the series metadata defaults. Idempotent: refuses to
clobber an existing beat_sheet.json unless --force.

Usage:
    python new_video.py "Why a Particle in a Box Cannot Sit Still"
    python new_video.py "Born's Rule" --root ~/Documents/Cowork/Manim --aspect 9:16
    python new_video.py "Quantum Tunneling" --slug quantum-tunneling
"""
import argparse
import json
import re
import sys
from pathlib import Path

DEFAULTS = {
    "series": "Bears Doodles",
    "voice_id": "",
    "accent_color": "#5A5653",
    "forbidden_color": "#C0392B",
    "text_font": "Shadows Into Light",
}

# Only the smallest articles are dropped, to keep slugs predictable and close to
# the title. Pass --slug to set the canonical slug explicitly.
DROP = {"a", "an", "the"}


def slugify(title: str) -> str:
    words = re.sub(r"[^a-z0-9\s-]", "", title.lower()).split()
    kept = [w for w in words if w not in DROP]
    return "-".join(kept or words)


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a Bear's Doodles video folder.")
    ap.add_argument("title", help="Human title of the video")
    ap.add_argument("--root", default=".", help="Parent directory for the video folder (default: cwd)")
    ap.add_argument("--slug", default=None, help="Override the derived kebab-case slug")
    ap.add_argument("--aspect", default="16:9", choices=["16:9", "9:16"])
    ap.add_argument("--source", default="", help="Chapter path or candidate this is built from")
    ap.add_argument("--force", action="store_true", help="Overwrite an existing beat_sheet.json")
    args = ap.parse_args()

    slug = args.slug or slugify(args.title)
    root = Path(args.root).expanduser().resolve()
    folder = root / slug

    for sub in ("mp3", "mp4", "frames", "media"):
        (folder / sub).mkdir(parents=True, exist_ok=True)

    sheet_path = folder / "beat_sheet.json"
    if sheet_path.exists() and not args.force:
        print(f"[skip] {sheet_path} already exists (use --force to overwrite)")
        print(f"[ok]   folder ready: {folder}")
        return 0

    sheet = {
        "metadata": {
            "slug": slug,
            "title": args.title,
            "series": DEFAULTS["series"],
            "source": args.source,
            "aspect_ratio": args.aspect,
            "voice_id": DEFAULTS["voice_id"],
            "accent_color": DEFAULTS["accent_color"],
            "forbidden_color": DEFAULTS["forbidden_color"],
            "text_font": DEFAULTS["text_font"],
            "thing": "",
            "total_estimated_duration_seconds": 0,
        },
        # The intro beat is always present. The script/beats commands append A00.. .
        "beats": [
            {
                "beat_id": "INTRO",
                "beat_type": "INTRO",
                "scene_index": 0,
                "render": "none",
                "narration_text": "Bear's Doodles\n\n" + args.title,
                "tts_normalized_text": "Bear's Doodles\n\n" + args.title,
                "accumulated_scene_state": [],
                "new_visual_element": "title card",
                "tts_voice_settings": {
                    "model_id": "eleven_multilingual_v2",
                    "stability": 0.80,
                    "similarity_boost": 0.75,
                    "style": 0.00,
                    "speed": 0.92,
                },
                "audio_file": None,
                "actual_duration_s": None,
                "approval_status": "pending",
            }
        ],
    }
    sheet_path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False))
    print(f"[ok] created {folder}")
    print(f"[ok] wrote   {sheet_path}")
    print(f"[ok] slug    {slug}   aspect {args.aspect}")
    print("Next: run the `script` command to fill in the narration beats.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
