#!/usr/bin/env python3
"""vox_outro.py — the branded outro stage for vox-explainer reels.

THE OUTRO LAW: every film ends the same way — @nikbearbrown on top, a Bear
Brown mascot variant dancing center frame, the "Next:" line below — on cream
or ink. Variant and background are chosen DETERMINISTICALLY from the reel
slug (random across reels, reproducible within one), so rebuilds are stable.

What it does (one command, rerunnable):
  1. picks bearbrown/<variant>.mp4 + light/dark ground from md5(slug)
  2. chroma-keys the green (sampled ~0x00D818), despills, scales to ~70%
  3. composites over the ground with PIL text overlays (portable: works on
     drawtext-less ffmpeg builds, same trick as vox_compile)
  4. pads the beat's narration mp3 with trailing silence to the outro length
     (audio stays the master clock — the silence is IN the clock)
  5. updates beat_sheet.json actual_duration_s, writes media/<beat>.mp4
  Then rerun vox_compile.py — only the outro slot recompiles.

Usage:
  python3 scripts/vox_outro.py reels/<slug> [--beat B16] [--bears bearbrown]
          [--force-bear 1|2|3] [--force-bg light|dark] [--tail 1.0]

Free/local. ffmpeg + Pillow + stdlib.
"""
import argparse, hashlib, json, subprocess, sys, shutil
from pathlib import Path

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"

CREAM = (243, 235, 221)   # #F3EBDD
INK = (47, 42, 38)        # #2F2A26
TERRA = (211, 95, 67)     # #D35F43
KEY_COLOR = "0x00D818"    # sampled from the bearbrown clips
W, H = 1920, 1080


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"[outro] ffmpeg failed:\n{' '.join(map(str, cmd))}\n{r.stderr[-800:]}")
    return r


def probe_dur(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def find_serif():
    for p in ("/System/Library/Fonts/Supplemental/Georgia.ttf",
              "/Library/Fonts/Georgia.ttf",
              "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"):
        if Path(p).exists():
            return p
    return None


def text_png(out, text, font_path, size, fill, underline=None, max_w=W - 240):
    """Transparent PNG of serif text, optionally with the Vox hairline."""
    from PIL import Image, ImageDraw, ImageFont
    try:
        f = ImageFont.truetype(font_path, size)
    except Exception:
        f = ImageFont.load_default()
    tmp = Image.new("RGBA", (4, 4))
    box = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=f)
    tw, th = box[2] - box[0], box[3] - box[1]
    if tw > max_w:                                  # shrink-to-fit, one line
        size = int(size * max_w / tw)
        f = ImageFont.truetype(font_path, size)
        box = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=f)
        tw, th = box[2] - box[0], box[3] - box[1]
    pad = 14
    img = Image.new("RGBA", (tw + pad * 2, th + pad * 2 + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad - box[0], pad - box[1]), text, font=f, fill=fill + (255,))
    if underline:
        y = pad + th + 8
        d.line([(pad, y), (pad + tw, y)], fill=underline + (255,), width=3)
    img.save(out)
    return img.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    ap.add_argument("--beat", default=None, help="outro beat id (default: last beat)")
    ap.add_argument("--bears", type=Path, default=Path("bearbrown"),
                    help="folder of green-screen mascot variants (bearbrown-*.mp4)")
    ap.add_argument("--handle", default="@nikbearbrown")
    ap.add_argument("--next-text", default=None,
                    help="the Next: line (default: the beat's narration_text)")
    ap.add_argument("--force-bear", type=int, default=None)
    ap.add_argument("--force-bg", choices=["light", "dark"], default=None)
    ap.add_argument("--tail", type=float, default=1.0,
                    help="silence after narration AND after the bear finishes")
    a = ap.parse_args()

    folder = a.folder.resolve()
    sheet_path = folder / "beat_sheet.json"
    sheet = json.loads(sheet_path.read_text())
    slug = sheet.get("metadata", {}).get("slug", folder.name)
    beats = sheet["beats"]
    beat = next((b for b in beats if b["beat_id"] == a.beat), beats[-1] if a.beat is None else None)
    if beat is None:
        sys.exit(f"[outro] beat {a.beat} not found")
    if beat.get("card", {}).get("silent"):
        sys.exit(f"[outro] {beat['beat_id']} is a silent endcard (shorts law) — not rebranding it")
    if beat.get("shot", {}).get("type") != "CARD":
        sys.exit(f"[outro] {beat['beat_id']} is a {beat.get('shot', {}).get('type')} beat — "
                 f"the outro law brands closing CARDs only (a film may deliberately "
                 f"end on a kicker; nothing to do here)")
    bid = beat["beat_id"]

    # frame follows the reel's aspect
    ar = sheet.get("metadata", {}).get("aspect_ratio", "16:9")
    global W, H
    W, H = (1080, 1920) if ar == "9:16" else (1920, 1080)
    aspect_tag = ar.replace(":", "x")

    seed = int(hashlib.md5(slug.encode()).hexdigest(), 16)

    # THE POOL: pre-composited bearbrown-<ground>-<aspect>-NNN.mp4 clips for
    # this aspect — no green screen. Pick is seeded (stable per film, varies
    # across films); --force-bg narrows to one ground, --force-bear to one
    # clip. Text color follows the CHOSEN clip's ground tag. Legacy keyed
    # clips (MP4/) are a last resort only if the pool is empty.
    bears_dir = a.bears.resolve()
    pool = sorted(bears_dir.glob(f"*-{aspect_tag}-[0-9]*.mp4"))
    if a.force_bg:
        pool = [p for p in pool if f"-{a.force_bg}-" in p.name] or pool
    if pool:
        mode = "base"
        bear = pool[(a.force_bear - 1) % len(pool)] if a.force_bear else pool[seed % len(pool)]
        dark = "-dark-" in bear.name
    else:
        mode = "key"
        legacy = (sorted((bears_dir / "MP4").glob("*-[0-9]*.mp4"))
                  or sorted(bears_dir.glob("*-[0-9]*.mp4")))
        if not legacy:
            sys.exit(f"[outro] no mascot clips in {bears_dir} (or MP4/)")
        bear = legacy[(a.force_bear - 1) % len(legacy)] if a.force_bear else legacy[seed % len(legacy)]
        dark = (a.force_bg == "dark") if a.force_bg else bool((seed >> 8) % 2)
    bg, fg = (INK, CREAM) if dark else (CREAM, INK)

    # --- the clock: narration + silence tail, at least as long as the bear
    mp3 = folder / (beat.get("audio_file") or f"mp3/beat-{bid}.mp3")
    if not mp3.exists():
        sys.exit(f"[outro] narration mp3 missing: {mp3} — run generate_audio.py first")
    # idempotency: pad from the pristine narration every run, never re-pad
    orig = folder / "clips" / "_work" / f"outro-orig-{bid}.mp3"
    orig.parent.mkdir(parents=True, exist_ok=True)
    if not orig.exists():
        shutil.copy(mp3, orig)
    narr = probe_dur(orig)
    bear_dur = probe_dur(bear)
    target = round(max(narr + a.tail, bear_dur + a.tail), 3)

    work = folder / "clips" / "_work"
    work.mkdir(parents=True, exist_ok=True)
    font = find_serif()

    # --- ground + text plane (PIL: portable on drawtext-less ffmpeg)
    from PIL import Image
    ground = Image.new("RGB", (W, H), bg)
    handle_png, next_png = work / "outro-handle.png", work / "outro-next.png"
    text_png(handle_png, a.handle, font, 64, fg, underline=TERRA)
    nline = a.next_text or beat.get("narration_text", "")
    text_png(next_png, nline, font, 46, fg)
    ground_png = work / "outro-ground.png"
    ground.save(ground_png)

    # --- composite + text. Two modes:
    #   base: pre-composited mascot clip IS the ground (fit, freeze-pad)
    #   key : legacy green-screen bear over the solid ground
    out = folder / "media" / f"{bid}.mp4"
    out.parent.mkdir(exist_ok=True)
    if out.is_symlink():
        out.unlink()            # NEVER write through a derivative's symlink
    if mode == "base":
        fc = (
            f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},tpad=stop_mode=clone:stop_duration={target + 0.5:.3f}[g0];"
            f"[g0][1:v]overlay=(W-w)/2:56[g1];"
            f"[g1][2:v]overlay=(W-w)/2:H-h-64"
        )
        sh([FFMPEG, "-y",
            "-i", str(bear),
            "-loop", "1", "-framerate", "24", "-i", str(handle_png),
            "-loop", "1", "-framerate", "24", "-i", str(next_png),
            "-filter_complex", fc, "-t", f"{target:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "24", "-an", str(out)])
    else:
        bh = int(H * 0.70)
        fc = (
            f"[1:v]chromakey={KEY_COLOR}:0.24:0.06,despill=type=green,"
            f"scale=-2:{bh}[bear];"
            f"[0:v][bear]overlay=(W-w)/2:(H-h)/2+40:shortest=0[g1];"
            f"[g1][2:v]overlay=(W-w)/2:56[g2];"
            f"[g2][3:v]overlay=(W-w)/2:H-h-64"
        )
        sh([FFMPEG, "-y",
            "-loop", "1", "-framerate", "24", "-i", str(ground_png),
            "-i", str(bear),
            "-loop", "1", "-framerate", "24", "-i", str(handle_png),
            "-loop", "1", "-framerate", "24", "-i", str(next_png),
            "-filter_complex", fc, "-t", f"{target:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "24", "-an", str(out)])

    # --- pad the narration mp3 to the target (silence lives IN the clock)
    padded = work / f"outro-{bid}.mp3"
    sh([FFMPEG, "-y", "-i", str(orig), "-af", f"apad=whole_dur={target:.3f}",
        "-c:a", "libmp3lame", "-q:a", "2", str(padded)])
    if mp3.is_symlink():
        mp3.unlink()            # pad a LOCAL copy — never the parent's file
    shutil.copy(padded, mp3)

    beat["actual_duration_s"] = round(probe_dur(mp3), 3)
    sheet_path.write_text(json.dumps(sheet, indent=1, ensure_ascii=False))

    print(f"[outro] {bid}: bear={bear.name}  ground={'ink' if dark else 'cream'}  "
          f"narration={narr:.1f}s  bear_clip={bear_dur:.1f}s  outro={target:.1f}s")
    print(f"[outro] wrote {out.relative_to(folder)} + padded {mp3.relative_to(folder)}")
    print(f"[outro] now: python3 scripts/vox_compile.py {folder.name if not folder.is_absolute() else folder} --review")


if __name__ == "__main__":
    main()
