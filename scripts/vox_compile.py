#!/usr/bin/env python3
"""vox_compile.py — the vox-explainer slot compiler + assembler.

Every beat on the timeline is a conformed per-beat mp4 in clips/.
Slot precedence:  media/<beat>.mp4  >  manim/<beat>.(mp4|mov)  >
                  media/<beat>.png (animated per shot.motion)  >  slate.
Rebuild recompiles ONLY slots whose input changed (sha1 manifest), then
re-concats and muxes the master audio. Annotations/captions are NOT this
script's job — they belong to the Remotion assembly plane. The --review flag
burns global timecode + per-beat id/status at assembly only; clips/ stay clean.

Text rendering is PORTABLE: slates and review labels are drawn with Pillow and
overlaid as PNGs, so this works on ffmpeg builds without the drawtext filter
(e.g. Homebrew's freetype-less bottle). If drawtext exists, a running global
timecode is added too; if not, each review label carries its time range.

Usage:
  python3 scripts/vox_compile.py reels/<slug> [--review] [--fps 24]
         [--height 720] [--audio path/to/master.(mp3|wav)] [--force]

Free/local. No API calls. ffmpeg + Pillow + Python stdlib.
"""
import argparse, hashlib, json, shutil, subprocess, sys
from collections import Counter
from pathlib import Path

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"
INK_RGB = (47, 42, 38)        # #2F2A26
CREAM_RGB = (243, 235, 221)   # #F3EBDD
LADDER_RETIME = 0.05          # retime silently within ±5%
LADDER_REFUSE = 0.15          # >15% short → loud warning (still freeze-padded)

def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.exit(f"[vox] ffmpeg failed:\n{' '.join(map(str, cmd))}\n{r.stderr[-1200:]}")
    return r

def probe_dur(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None

def probe_wh(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height", "-of", "csv=p=0",
                        str(path)], capture_output=True, text=True)
    try:
        vals = r.stdout.strip().splitlines()[0].split(",")
        return int(vals[0]), int(vals[1])
    except (ValueError, IndexError):
        return None, None

def sha1(path, extra=""):
    h = hashlib.sha1(); h.update(extra.encode())
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def has_drawtext():
    import os
    if os.environ.get("VOX_NO_DRAWTEXT"):
        return False
    r = subprocess.run([FFMPEG, "-hide_banner", "-filters"],
                       capture_output=True, text=True)
    return " drawtext " in r.stdout

def find_font():
    for p in ("/System/Library/Fonts/Supplemental/Georgia.ttf",
              "/Library/Fonts/Georgia.ttf",
              "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"):
        if Path(p).exists():
            return p
    return None

# ------------------------------------------------------------- PIL text

def _pil_font(font_path, size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def make_slate_png(out, w, h, bid, label, owner, font_path):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), INK_RGB)
    d = ImageDraw.Draw(img)
    f1 = _pil_font(font_path, int(h * 0.12))
    f2 = _pil_font(font_path, int(h * 0.045))
    f3 = _pil_font(font_path, int(h * 0.038))
    d.text((w / 2, h * 0.36), bid, font=f1, fill=CREAM_RGB, anchor="mm")
    d.text((w / 2, h * 0.53), label[:80], font=f2, fill=CREAM_RGB, anchor="mm")
    d.text((w / 2, h * 0.64), owner[:90], font=f3, fill=(211, 95, 67), anchor="mm")
    img.save(out)

def make_label_png(out, text, font_path, size):
    from PIL import Image, ImageDraw
    f = _pil_font(font_path, size)
    tmp = Image.new("RGBA", (4, 4)); tw = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=f)
    w, h = tw[2] - tw[0] + 24, tw[3] - tw[1] + 16
    img = Image.new("RGBA", (w, h), (0, 0, 0, 150))
    ImageDraw.Draw(img).text((12, 8 - tw[1]), text, font=f, fill=(255, 255, 255, 255))
    img.save(out)

# ------------------------------------------------------------- slots

def resolve_slot(folder, bid):
    for rel, status in ((f"media/{bid}.mp4", "VIDEO"), (f"manim/{bid}.mp4", "MANIM"),
                        (f"manim/{bid}.mov", "MANIM"), (f"media/{bid}.png", "STILL"),
                        (f"media/{bid}.jpg", "STILL")):
        p = folder / rel
        if p.exists():
            return p, status
    return None, "SLATE"

def vf_fit(w, h):
    return f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"

def vf_treatment(source, override=None):
    """The laundering function: desaturate + printed contrast for photographic
    sources. Manim fragments and design-system beats pass through untouched.
    Per-beat override (shot.treatment): 'none' = as generated (the one loud
    element); 'light' = keep the color, seat it in the collage — for beats
    whose color IS the information (a forge glow the narration names)."""
    if override == "none":
        return None
    if override == "light":
        return "hue=s=0.8,eq=contrast=1.06:brightness=0.005"
    if source in ("archive", "ai"):
        return "hue=s=0.25,eq=contrast=1.12:brightness=0.01"
    return None

def compile_clip(folder, beat, out, w, h, fps, font, work):
    bid, dur = beat["beat_id"], float(beat["actual_duration_s"])
    shot = beat.get("shot", {})
    src, status = resolve_slot(folder, bid)
    enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-r", str(fps), "-an", str(out)]
    treat = vf_treatment(shot.get("source", "own"), shot.get("treatment"))

    if status in ("VIDEO", "MANIM"):
        d = probe_dur(src) or dur
        vf = [vf_fit(w, h)]
        if treat and status == "VIDEO":
            vf.append(treat)
        delta = (d - dur) / dur
        if abs(delta) <= LADDER_RETIME and d > 0:          # retime to exact
            vf.append(f"setpts=PTS*{dur / d:.6f}")
        elif d < dur and d > 0:                             # slow to fit — never freeze
            ratio = dur / d
            if ratio > 3.0:
                print(f"[vox] WARNING {bid}: clip {d:.1f}s slowed {ratio:.1f}x "
                      f"into {dur:.1f}s beat — extreme slow-mo, consider a longer generation")
            else:
                print(f"[vox] {bid}: clip {d:.1f}s slowed {ratio:.2f}x to fill {dur:.1f}s beat")
            vf.append(f"setpts=PTS*{ratio:.6f}")
        # else: longer → trim (keep head) via -t below
        cmd = [FFMPEG, "-y", "-i", src, "-vf", ",".join(vf), "-t", f"{dur:.3f}"] + enc
    elif status == "STILL":
        motion = shot.get("motion", "kenburns")
        iw, ih = probe_wh(src)
        if iw and (iw < w or ih < h):
            print(f"[vox] WARNING {bid}: still {iw}x{ih} under output {w}x{h} — "
                  f"the move will reveal upscale artifacts (MOTION.md §1)")
        vf = [vf_fit(w * 2, h * 2)]                        # oversample against zoompan shimmer
        if treat:
            vf.append(treat)
        # MOTION.md §1: motivated direction. shot.focus = [fx, fy] in 0–1
        # image coords; default 0.5,0.5 reproduces the old center move.
        f_xy = shot.get("focus") or [0.5, 0.5]
        fx = min(max(float(f_xy[0]), 0.0), 1.0)
        fy = min(max(float(f_xy[1]), 0.0), 1.0)
        frames = max(2, int(round(dur * fps)))
        if motion == "hold":
            vf.append(f"scale={w}:{h}")
        elif motion == "pan":                              # pan OR zoom, never both
            ltr = int(hashlib.sha1(bid.encode()).hexdigest(), 16) % 2 == 0
            prog = (f"on/{frames - 1}" if ltr else f"(1-on/{frames - 1})")
            vf.append(f"zoompan=z='1.10':x='(iw-iw/zoom)*({prog})'"
                      f":y='(ih-ih/zoom)*{fy:.4f}':d={frames}:s={w}x{h}:fps={fps}")
        else:                                               # ken burns toward the focus
            zin = int(hashlib.sha1(bid.encode()).hexdigest(), 16) % 2 == 0
            z = (f"zoom+{0.08/frames:.6f}" if zin else f"1.08-{0.08/frames:.6f}*on")
            vf.append(f"zoompan=z='{z}':x='(iw-iw/zoom)*{fx:.4f}'"
                      f":y='(ih-ih/zoom)*{fy:.4f}':d={frames}:s={w}x{h}:fps={fps}")
        cmd = [FFMPEG, "-y", "-loop", "1", "-i", src, "-vf", ",".join(vf),
               "-t", f"{dur:.3f}"] + enc
    else:                                                   # slate (PIL — no drawtext needed)
        label = (beat.get("new_visual_element") or beat.get("narration_text", ""))[:80]
        owner = (f"YOU → drop media/{bid}.png or {bid}.mp4 (see SHOTLIST)"
                 if shot.get("source") == "archive"
                 else f"PIPELINE → render vox_graphics.py scene {bid}_*")
        png = work / f"slate-{bid}.png"
        make_slate_png(png, w, h, bid, label, owner, font)
        cmd = [FFMPEG, "-y", "-loop", "1", "-i", png, "-t", f"{dur:.3f}"] + enc
    sh(cmd)
    return src, status

def make_qc_sheet(folder, beats, clips, work, font):
    """Contact sheet: mid-frame of every beat clip, tiled + labeled. The cheap
    visual QC pass — review this one image for overflow/clipping/layout bugs."""
    from PIL import Image, ImageDraw
    tiles, tw, th = [], 480, 270
    for b in beats:
        bid, dur = b["beat_id"], float(b["actual_duration_s"])
        clip = clips / f"{bid}.mp4"
        frame = work / f"qc-{bid}.png"
        subprocess.run([FFMPEG, "-y", "-ss", f"{dur / 2:.2f}", "-i", str(clip),
                        "-frames:v", "1", "-vf", f"scale={tw}:{th}", str(frame)],
                       capture_output=True)
        if frame.exists():
            img = Image.open(frame).convert("RGB")
            d = ImageDraw.Draw(img)
            d.rectangle([0, th - 26, 150, th], fill=(0, 0, 0))
            d.text((8, th - 23), f"{bid} {b.get('shot', {}).get('type', '')}",
                   font=_pil_font(font, 16), fill=(255, 255, 255))
            tiles.append(img)
    if not tiles:
        return None
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (30, 27, 24))
    for i, img in enumerate(tiles):
        sheet.paste(img, ((i % cols) * tw, (i // cols) * th))
    out = folder / "qc-sheet.png"
    sheet.save(out)
    return out


def build_master_audio(folder, beats, cli_audio, tmp):
    """Per-beat audio/ mp3s win; else --audio master; else silence."""
    per_beat = [folder / (b.get("audio_file") or f"audio/{b['beat_id']}.mp3") for b in beats]
    if all(p.exists() for p in per_beat):
        lst = tmp / "audio.txt"
        lst.write_text("".join(f"file '{p.resolve()}'\n" for p in per_beat))
        out = tmp / "master.m4a"
        sh([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "aac", str(out)])
        return out, "per-beat narration"
    if cli_audio and Path(cli_audio).exists():
        return Path(cli_audio), "master track"
    return None, "silent"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    ap.add_argument("--review", action="store_true")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--audio", help="master audio file (music bed / narration mix)")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    folder = a.folder.resolve()
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    beats = sheet["beats"]
    ar = sheet.get("metadata", {}).get("aspect_ratio", "16:9")
    num, den = (int(x) for x in ar.split(":"))
    h = a.height; w = int(round(h * num / den / 2) * 2)
    fps, font = a.fps, find_font()
    drawtext = has_drawtext()
    clips = folder / "clips"; clips.mkdir(exist_ok=True)
    work = clips / "_work"; work.mkdir(exist_ok=True)
    (folder / "media").mkdir(exist_ok=True)
    man_path = clips / "manifest.json"
    manifest = json.loads(man_path.read_text()) if man_path.exists() else {}

    report, t0 = [], 0.0
    for b in beats:
        bid, dur = b["beat_id"], float(b["actual_duration_s"])
        out = clips / f"{bid}.mp4"
        src, status = resolve_slot(folder, bid)
        bshot = b.get("shot", {})
        key = (f"L2|{w}x{h}@{fps}|{dur:.3f}|{bshot.get('motion', '')}"
               f"|{bshot.get('focus', '')}|{bshot.get('treatment', '')}|"
               + (sha1(src) if src else "slate"))
        if a.force or manifest.get(bid) != key or not out.exists():
            src, status = compile_clip(folder, b, out, w, h, fps, font, work)
            manifest[bid] = key
            print(f"[vox] compiled {bid}  {status:6}  {dur:5.1f}s" +
                  (f"  ← {src.name}" if src else ""))
        report.append((bid, t0, dur, status, b.get("shot", {}).get("type", "?")))
        t0 += dur
    man_path.write_text(json.dumps(manifest, indent=1))

    # motion pantry lint (MOTION.md): no language carries > ~40% of beats
    def _eff_motion(b):
        s = b.get("shot", {})
        return (s.get("motion")
                or ("kenburns" if s.get("type") == "STILL"
                    else (s.get("type") or "?").lower()))
    hist = Counter(_eff_motion(b) for b in beats)
    print("[vox] motion histogram: "
          + "  ".join(f"{k}:{n}" for k, n in hist.most_common()))
    if len(beats) >= 8:
        top, n = hist.most_common(1)[0]
        if n / len(beats) > 0.40 and top != "card":
            print(f"[vox] WARNING: '{top}' carries {n}/{len(beats)} beats "
                  f"({n * 100 // len(beats)}%) — over the ~40% pantry cap; "
                  f"convert the excess to another language (MOTION.md)")

    lst = clips / "concat.txt"
    lst.write_text("".join(f"file '{(clips / (b['beat_id'] + '.mp4')).resolve()}'\n"
                           for b in beats))
    total = sum(float(b["actual_duration_s"]) for b in beats)
    audio, akind = build_master_audio(folder, beats, a.audio, clips)

    slug = sheet.get("metadata", {}).get("slug", folder.name)
    out = folder / (f"{slug}-review.mp4" if a.review else f"{slug}-cut.mp4")
    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lst]
    cmd += (["-i", str(audio)] if audio else
            ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"])
    fc = []
    if a.review:
        # per-beat label PNGs, overlaid with enable windows (portable, no drawtext)
        labels = []
        for i, (bid, ts, dur, status, stype) in enumerate(report):
            png = work / f"lbl-{bid}.png"
            make_label_png(png, f"{bid} {stype} {status} {ts:6.1f}s +{dur:.1f}s",
                           font, int(h * 0.032))
            labels.append((png, ts, dur))
        for i, (png, ts, dur) in enumerate(labels):
            cmd += ["-i", str(png)]
        prev = "0:v"
        for i, (png, ts, dur) in enumerate(labels):
            nxt = f"v{i}"
            fc.append(f"[{prev}][{i + 2}:v]overlay=16:H-h-16:"
                      f"enable='between(t,{ts:.3f},{ts + dur:.3f})'[{nxt}]")
            prev = nxt
        if drawtext:
            fc.append(f"[{prev}]drawtext=fontfile={font}:text='%{{pts\\:hms}}'"
                      f":fontcolor=white:fontsize={int(h*0.04)}:box=1"
                      f":boxcolor=black@0.55:boxborderw=8:x=w-text_w-16:y=16[vout]")
        else:
            fc.append(f"[{prev}]null[vout]")
    if fc:
        cmd += ["-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "1:a"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
            "-t", f"{total:.3f}", str(out)]
    sh(cmd)

    n_slate = sum(1 for r in report if r[3] == "SLATE")
    if a.review:
        qc = make_qc_sheet(folder, beats, clips, work, font)
        if qc:
            print(f"[vox] QC contact sheet → {qc}")
    print(f"[vox] wrote {out}  ({total:.1f}s, audio: {akind}, "
          f"drawtext: {'yes' if drawtext else 'no — PIL overlays'})")
    print(f"[vox] slots: {len(report) - n_slate}/{len(report)} filled — " +
          " ".join(f"{bid}:{st}" for bid, _, _, st, _ in report))

if __name__ == "__main__":
    main()
