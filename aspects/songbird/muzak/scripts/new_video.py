#!/usr/bin/env python3
"""
new_video.py — scaffold a muzak song project.

Creates one folder per song (named by kebab-case slug), scaffolds a blank
Remotion project inside it, copies the WAV into public/<slug>/audio.wav, and
writes song.json (the manifest the other phases read). It deliberately does NOT
generate any video content — that's what `build` is for.

Usage:
    python new_video.py --slug midnight-drive --title "Midnight Drive" \
        --wav /path/to/song.wav [--width 1920 --height 1080 --fps 30] \
        [--parent /path/to/projects]

If Remotion's scaffolder (`npm create video`) isn't available or network is
blocked, the script still creates the folder structure + a minimal package.json
so the rest of the pipeline can proceed; it prints what to run by hand.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s) or "song"


def run(cmd, cwd=None):
    print("  $ %s" % " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd).returncode


def scaffold_remotion(project_dir):
    """Best-effort Remotion scaffold. Returns True if a node project exists."""
    pkg = os.path.join(project_dir, "package.json")
    if os.path.exists(pkg):
        return True
    # Try the official blank template (no tailwind). This needs npm + network.
    code = run(
        ["npx", "--yes", "create-video@latest", ".",
         "--template", "blank", "--no-install"],
        cwd=project_dir,
    )
    if code == 0 and os.path.exists(pkg):
        return True
    # Fallback: write a minimal package.json so the pipeline isn't blocked.
    sys.stderr.write("muzak: create-video unavailable; writing minimal package.json. "
                     "Run `npm install remotion @remotion/cli @remotion/media-utils "
                     "react react-dom` in the project before rendering.\n")
    minimal = {
        "name": os.path.basename(project_dir),
        "version": "1.0.0",
        "scripts": {
            "studio": "remotion studio",
            "render": "remotion render MusicVideo out/video.mp4",
        },
        "dependencies": {
            "@remotion/cli": "^4.0.0",
            "@remotion/media-utils": "^4.0.0",
            "remotion": "^4.0.0",
            "react": "^18.0.0",
            "react-dom": "^18.0.0",
        },
    }
    with open(pkg, "w") as f:
        json.dump(minimal, f, indent=2)
    return False


def main():
    ap = argparse.ArgumentParser(description="Scaffold a muzak song project.")
    ap.add_argument("--slug", help="kebab-case slug (derived from title if omitted)")
    ap.add_argument("--title", required=True, help="song title")
    ap.add_argument("--wav", required=True, help="path to the source WAV/MP3")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--parent", default=".", help="parent dir for the project folder")
    args = ap.parse_args()

    slug = args.slug or slugify(args.title)
    project_dir = os.path.abspath(os.path.join(args.parent, slug))
    public_dir = os.path.join(project_dir, "public", slug)
    src_dir = os.path.join(project_dir, "src")
    for d in (project_dir, public_dir, src_dir,
              os.path.join(public_dir, "media"),
              os.path.join(project_dir, "design")):
        os.makedirs(d, exist_ok=True)

    # Copy the audio in (convert later if it's mp3; analyze_audio reads both,
    # but WAV in public/ is what the Remotion <Audio> references).
    if not os.path.exists(args.wav):
        sys.stderr.write("muzak: wav not found: %s\n" % args.wav)
        sys.exit(1)
    ext = os.path.splitext(args.wav)[1].lower()
    audio_dest = os.path.join(public_dir, "audio" + (ext if ext in (".wav", ".mp3") else ".wav"))
    shutil.copyfile(args.wav, audio_dest)

    has_node = scaffold_remotion(project_dir)

    manifest = {
        "slug": slug,
        "title": args.title,
        "format": {"width": args.width, "height": args.height, "fps": args.fps},
        "paths": {
            "audio": os.path.relpath(audio_dest, project_dir),
            "beatData": "beat_data.json",
            "lyrics": "lyrics.json",
            "designDoc": "design/%s.md" % slug,
        },
        "phase": "new",
    }
    with open(os.path.join(project_dir, "song.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print("\nmuzak: scaffolded '%s'" % slug)
    print("  project:   %s" % project_dir)
    print("  audio:     %s" % audio_dest)
    print("  format:    %dx%d @ %dfps" % (args.width, args.height, args.fps))
    print("  remotion:  %s" % ("ready" if has_node else "minimal package.json (run npm install)"))
    print("  next:      analyze  ->  python analyze_audio.py %s --fps %d -o %s/beat_data.json"
          % (audio_dest, args.fps, project_dir))


if __name__ == "__main__":
    main()
