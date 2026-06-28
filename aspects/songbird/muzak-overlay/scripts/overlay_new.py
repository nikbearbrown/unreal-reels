#!/usr/bin/env python3
"""
overlay_new.py — turn an EXISTING finished video + its lyrics into a Remotion
project that overlays synced karaoke lyrics and an audiogram waveform on top.

This is the "overlay" sibling of the muzak pipeline. Muzak BUILDS a video from a
WAV (generated backgrounds, per-block media). Overlay does the opposite: the video
is already done (e.g. an AI-generated music video); we only add the lyric +
visualizer layer the other Songbird videos have — without re-rendering or touching
the original footage beyond compositing over it.

What it does, in order:
  1. ffmpeg-extracts the audio from the source video -> audio.wav (the picture and
     the analyzed audio therefore stay perfectly in sync).
  2. ffprobe reads the video's width/height/fps so the composition matches the
     source exactly (no rescale, no letterboxing).
  3. analyze_audio.py (librosa) -> beat_data.json  (duration, fps, energy, sections).
  4. lyric timing -> lyrics.json:
       - default: align_lyrics.py beat-grid SEED (no extra deps; even spacing).
       - --whisper: align_lyrics_audio.py FORCED ALIGNMENT (faster-whisper) for
         true per-word karaoke timing locked to the vocal. Recommended for the
         final; needs faster-whisper + a model download.
  5. Stamps the templates/ Remotion project into <dir>/<slug>/ with the slug and
     real dimensions substituted, and drops the JSON + assets where Remotion wants.

It does NOT render. Rendering needs headless Chromium and minutes of compute; the
script prints the exact `npm install` + render commands to finish locally.

Usage:
    python overlay_new.py --mp4 "Strange Brothers.mp4" --lyrics song-03.txt \\
        --slug strange-brothers --dir .
    # then, for accurate timing:
    python overlay_new.py ... --whisper --model small

Re-runnable: pass --force to overwrite an existing project folder's generated
files (keeps node_modules).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
TEMPLATES = SKILL / "templates"
# muzak's analysis/alignment scripts are the single source of truth; reuse them.
DEFAULT_MUZAK_SCRIPTS = (SKILL.parent / "muzak" / "scripts").resolve()


def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def safe_copy(src: Path, dst: Path):
    """Copy src -> dst, but skip when they are the same file (idempotent re-runs:
    e.g. --mp4 already points at the project's own source.mp4)."""
    src, dst = Path(src), Path(dst)
    if dst.exists() and src.resolve() == dst.resolve():
        return
    shutil.copy2(src, dst)


def ffprobe_dims(mp4: Path):
    """Return (width, height, fps_int) of the first video stream."""
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-of", "json", str(mp4),
    ])
    st = json.loads(out)["streams"][0]
    w, h = int(st["width"]), int(st["height"])
    num, den = (st.get("r_frame_rate") or "30/1").split("/")
    fps = round(float(num) / float(den)) if float(den) else 30
    return w, h, fps


# Files that carry the user's hand-tuned look / config: once they exist in a
# project, re-stamping must NOT clobber them. The mechanical components (the .tsx
# wiring) are always refreshed so template fixes propagate.
PRESERVE_IF_EXISTS = {"src/theme.ts", "package.json"}


def stamp_templates(dst: Path, slug: str, w: int, h: int):
    """Copy templates/ -> dst, substituting __SLUG__ / __WIDTH__ / __HEIGHT__.
    Files in PRESERVE_IF_EXISTS are skipped when they already exist, so re-runs
    keep the user's theme/config edits."""
    subs = {"__SLUG__": slug, "__WIDTH__": str(w), "__HEIGHT__": str(h)}
    for src in TEMPLATES.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(TEMPLATES)
        out = dst / rel
        if rel.as_posix() in PRESERVE_IF_EXISTS and out.exists():
            print(f"overlay: keeping your existing {rel.as_posix()} (not overwritten)")
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text()
        for k, v in subs.items():
            text = text.replace(k, v)
        out.write_text(text)


def main():
    ap = argparse.ArgumentParser(description="Overlay synced lyrics + audiogram on an existing video.")
    ap.add_argument("--mp4", required=True, help="the finished source video")
    ap.add_argument("--lyrics", required=True, help="plain-text lyrics (TITLE: convention)")
    ap.add_argument("--slug", required=True, help="kebab-case project name, e.g. strange-brothers")
    ap.add_argument("--dir", default=".", help="parent dir to create <slug>/ inside (default .)")
    ap.add_argument("--fps", type=int, default=0, help="override fps (default: probe the video)")
    ap.add_argument("--whisper", action="store_true",
                    help="forced-align lyrics with faster-whisper (accurate karaoke timing)")
    ap.add_argument("--model", default="small", help="whisper model size (tiny/base/small/medium)")
    ap.add_argument("--muzak-scripts", default=str(DEFAULT_MUZAK_SCRIPTS),
                    help="path to muzak's scripts/ (analyze_audio.py + align_lyrics*.py)")
    ap.add_argument("--analyze-python", default="",
                    help="python to run the librosa analyze step (e.g. the conda 'muzak' env's "
                         "python). Default: the same python running this script. Use this when "
                         "librosa lives in a different env than faster-whisper (Intel-Mac llvmlite).")
    ap.add_argument("--skip-analyze", action="store_true",
                    help="reuse an existing beat_data.json instead of re-running librosa. Safe when "
                         "the audio hasn't changed — avoids needing librosa at all.")
    ap.add_argument("--force", action="store_true", help="overwrite generated files if present")
    args = ap.parse_args()

    mp4 = Path(args.mp4).expanduser().resolve()
    lyrics = Path(args.lyrics).expanduser().resolve()
    mscripts = Path(args.muzak_scripts).expanduser().resolve()
    if not mp4.is_file():
        sys.exit(f"overlay: source video not found: {mp4}")
    if not lyrics.is_file():
        sys.exit(f"overlay: lyrics not found: {lyrics}")
    for s in ("analyze_audio.py", "align_lyrics.py", "align_lyrics_audio.py"):
        if not (mscripts / s).is_file():
            sys.exit(f"overlay: missing {s} in --muzak-scripts ({mscripts})")

    proj = Path(args.dir).expanduser().resolve() / args.slug
    pub = proj / "public" / args.slug
    src = proj / "src"
    pub.mkdir(parents=True, exist_ok=True)
    src.mkdir(parents=True, exist_ok=True)
    (proj / "out").mkdir(exist_ok=True)

    w, h, vfps = ffprobe_dims(mp4)
    fps = args.fps or vfps
    print(f"overlay: source {w}x{h} @ {vfps}fps  ->  composition {w}x{h} @ {fps}fps")

    # 1. assets: copy the video + extract its audio
    src_mp4 = proj / "source.mp4"
    audio = proj / "audio.wav"
    if args.force or not src_mp4.exists():
        safe_copy(mp4, src_mp4)
    print("overlay: extracting audio.wav ...")
    run(["ffmpeg", "-y", "-i", src_mp4, "-vn", "-ac", "2", "-ar", "44100",
         "-c:a", "pcm_s16le", audio, "-loglevel", "error"])
    safe_copy(src_mp4, pub / "source.mp4")
    safe_copy(audio, pub / "audio.wav")

    # 2. beat analysis (skippable / delegable to a librosa-capable env)
    beat = proj / "beat_data.json"
    if args.skip_analyze:
        if not beat.is_file():
            sys.exit(f"overlay: --skip-analyze but no existing {beat}. Run analyze once first.")
        print("overlay: --skip-analyze -> reusing existing beat_data.json")
    else:
        apy = args.analyze_python or sys.executable
        print(f"overlay: analyzing beats (librosa, via {apy}) ...")
        run([apy, mscripts / "analyze_audio.py", audio, "--fps", fps, "-o", beat])

    # 3. lyric timing
    ly = proj / "lyrics.json"
    if args.whisper:
        print("overlay: forced-aligning lyrics (faster-whisper, model=%s) ..." % args.model)
        run([sys.executable, mscripts / "align_lyrics_audio.py", lyrics,
             "--audio", audio, "--beat-data", beat, "-o", ly, "--model", args.model],
            cwd=mscripts)  # align_lyrics_audio imports align_lyrics from its own dir
    else:
        print("overlay: seeding lyric timing from the beat grid ...")
        run([sys.executable, mscripts / "align_lyrics.py", lyrics, "--beat-data", beat, "-o", ly],
            cwd=mscripts)

    # 4. stamp the Remotion project and drop JSON into src/
    print("overlay: stamping Remotion project ...")
    stamp_templates(proj, args.slug, w, h)
    safe_copy(beat, src / "beat_data.json")
    safe_copy(ly, src / "lyrics.json")
    safe_copy(lyrics, proj / lyrics.name)

    print("\noverlay: project ready ->", proj)
    print("  finish locally (needs Node + Chromium):")
    print(f"    cd {proj}")
    print("    npm install")
    print("    npm run studio       # preview / nudge timing in Remotion Studio")
    print("    npm run render       # -> out/%s.mp4" % args.slug)
    if not args.whisper:
        print("\n  timing is a beat-grid SEED. For accurate karaoke locked to the vocal, re-run:")
        print(f"    python {Path(__file__).name} --mp4 {mp4.name} --lyrics {lyrics.name} "
              f"--slug {args.slug} --dir {args.dir} --whisper --model small --force")


if __name__ == "__main__":
    main()
