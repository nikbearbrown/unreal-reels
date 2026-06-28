#!/usr/bin/env python3
"""
assemble.py — Bear's Doodles final-cut assembler (ffmpeg).

Two assembly modes:

  --mode manim   (default)
      The Manim render already contains everything timed to the audio. This mode
      muxes the concatenated per-beat audio onto the Manim MP4 and optionally
      burns captions. Use when the whole video is one Manim scene.

  --mode clips
      Concatenate per-beat doodle clips (mp4/beat-<ID>-*.mp4) in beat order, lay
      each beat's audio onto its segment, and optionally burn captions. Use when
      the video is assembled from individual Wan 2.7 / doodle clips.

Captions: the beat's narration_text IS the caption (burned, bottom third).

Requires: ffmpeg on PATH. (brew install ffmpeg)

Usage:
    python assemble.py path/to/<slug>
    python assemble.py path/to/<slug> --mode clips --captions
    python assemble.py path/to/<slug> --manim-mp4 media/videos/foo/1080p60/BearsDoodlesVideo.mp4
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print("[ffmpeg]", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def mux(video: Path, audio: Path, out: Path, tail: float):
    """Mux audio onto video, freezing the last video frame for `tail` seconds so the
    narration never gets clipped (replaces the old -shortest, which truncated it)."""
    vf = f"[0:v]tpad=stop_mode=clone:stop_duration={tail}[v]"
    run(["ffmpeg", "-y", "-i", str(video), "-i", str(audio),
         "-filter_complex", vf, "-map", "[v]", "-map", "1:a:0",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
         "-c:a", "aac", "-b:a", "192k", str(out)])


def concat_audio(folder: Path, beats, out: Path):
    """Concatenate per-beat MP3s in order into one track."""
    listfile = folder / "mp3" / "_concat.txt"
    lines = []
    for b in beats:
        p = folder / (b.get("audio_file") or f"mp3/beat-{b['beat_id']}.mp3")
        if p.exists():
            lines.append(f"file '{p.as_posix()}'")
    listfile.write_text("\n".join(lines))
    # RE-ENCODE to AAC — copying raw MP3 frames into an .m4a (MP4) container yields
    # an audio file the mux silently drops. Re-encoding guarantees a valid track.
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c:a", "aac", "-b:a", "192k", str(out)])
    return out


def _dims(mp4: Path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(mp4)],
            capture_output=True, text=True)
        w, hgt = r.stdout.strip().split("x")
        return int(w), int(hgt)
    except Exception:
        return None


def find_manim_mp4(folder: Path, portrait: bool = False) -> Path | None:
    candidates = sorted((folder / "media" / "videos").rglob("BearsDoodlesVideo.mp4"),
                        key=lambda p: p.stat().st_mtime)
    # keep only renders matching the requested orientation (probe real dims)
    matched = []
    for c in candidates:
        d = _dims(c)
        if d is None:
            continue
        is_port = d[1] > d[0]
        if is_port == portrait:
            matched.append(c)
    pool = matched or ([] if matched else candidates)
    return pool[-1] if pool else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Assemble the final Bear's Doodles MP4.")
    ap.add_argument("folder")
    ap.add_argument("--mode", choices=["manim", "clips"], default="manim")
    ap.add_argument("--manim-mp4", default=None, help="Path to the Manim render (auto-detected if omitted)")
    ap.add_argument("--captions", action="store_true", help="Burn narration captions, bottom third")
    ap.add_argument("--tail", type=float, default=1.0,
                    help="seconds to hold the last frame after audio ends (safety; default 1.0)")
    ap.add_argument("--portrait", action="store_true",
                    help="assemble the 9:16 render (BearsDoodlesVideo at 1080x1920) → <slug>-short.mp4")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    beats = sheet["beats"]
    slug = sheet["metadata"]["slug"]
    out_dir = folder / "mp4"
    out_dir.mkdir(exist_ok=True)
    final = out_dir / (f"{slug}-short.mp4" if args.portrait else f"{slug}.mp4")

    audio_track = concat_audio(folder, beats, out_dir / "_voiceover.m4a")

    if args.mode == "manim":
        mp4 = Path(args.manim_mp4) if args.manim_mp4 else find_manim_mp4(folder, args.portrait)
        if not mp4 or not mp4.exists():
            print("[err] Manim render not found. Render first, or pass --manim-mp4.", file=sys.stderr)
            return 1
        # Mux: take video from Manim, audio from voiceover, +tail freeze-frame.
        mux(mp4, audio_track, final, args.tail)
    else:
        # clips mode: concat beat clips in order, then mux audio.
        listfile = out_dir / "_clips.txt"
        lines = []
        for b in beats:
            bid = b["beat_id"]
            matches = sorted(out_dir.glob(f"beat-{bid}-*.mp4")) + sorted(out_dir.glob(f"beat-{bid}.mp4"))
            if matches:
                lines.append(f"file '{matches[0].as_posix()}'")
        if not lines:
            print("[err] no per-beat clips found in mp4/. Generate doodle clips first.", file=sys.stderr)
            return 1
        listfile.write_text("\n".join(lines))
        silent = out_dir / "_video_only.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
             "-c", "copy", str(silent)])
        mux(silent, audio_track, final, args.tail)

    if args.captions:
        srt = out_dir / f"{slug}.srt"
        _write_srt(beats, folder, srt)
        captioned = out_dir / f"{slug}-captioned.mp4"
        style = "FontName=Arial,FontSize=18,Alignment=2,MarginV=40,BorderStyle=3,Outline=1"
        run(["ffmpeg", "-y", "-i", str(final),
             "-vf", f"subtitles={srt.as_posix()}:force_style='{style}'",
             "-c:a", "copy", str(captioned)])
        print(f"[ok] captioned → {captioned}")

    print(f"[ok] final → {final}")
    # auto-open the finished master (with sound) so it isn't confused with the
    # silent Manim render that `manim -p` previews.
    if sys.platform == "darwin":
        subprocess.run(["open", str(final)], check=False)
    return 0


def _write_srt(beats, folder, srt: Path):
    """Build an SRT from beat narration + real audio durations."""
    def ts(s):
        h = int(s // 3600); m = int((s % 3600) // 60); sec = s % 60
        return f"{h:02}:{m:02}:{sec:06.3f}".replace(".", ",")

    t = 0.0
    out = []
    for i, b in enumerate(beats, 1):
        d = b.get("actual_duration_s") or 4.0
        text = (b.get("narration_text") or "").replace("\n\n", "\n")
        out.append(f"{i}\n{ts(t)} --> {ts(t + d)}\n{text}\n")
        t += d
    srt.write_text("\n".join(out))


if __name__ == "__main__":
    sys.exit(main())
