#!/usr/bin/env python3
"""vox_short.py — derive the 9:16 Shorts cut from a finished vox reel.

THE SHORTS LAW: a Short is a DERIVATIVE CUT, not a re-edit — drop the beats
that don't earn vertical time (documents, the bear outro), end on a SILENT
branded card the viewer reads (@handle + the Next: line), stay under the
3:00 Shorts cap. The film letterboxes on the newsprint ground (metadata
fit: pad); slots are symlinked from the parent reel so nothing re-renders.

Usage:
  python3 scripts/vox_short.py reels/<slug> --drop B14 B16 [--end-s 4.5]
Then:
  python3 scripts/vox_compile.py reels/<slug>/short --review --height 1920

The endcard's Next: line defaults to the narration of the LAST dropped CARD
beat (the 16:9 outro's tease), override with --next.
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
CREAM = (243, 235, 221); INK = (47, 42, 38); TERRA = (211, 95, 67)
W, H = 1080, 1920


def find_serif():
    for p in ("/System/Library/Fonts/Supplemental/Georgia.ttf",
              "/Library/Fonts/Georgia.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"):
        if Path(p).exists():
            return p
    return None


def endcard_png(out, handle, next_text, dark=True):
    from PIL import Image, ImageDraw, ImageFont
    bg, fg = (INK, CREAM) if dark else (CREAM, INK)
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    font = find_serif()

    def f(size):
        try:
            return ImageFont.truetype(font, size)
        except Exception:
            return ImageFont.load_default()

    fh = f(64)
    hb = d.textbbox((0, 0), handle, font=fh)
    hw = hb[2] - hb[0]
    d.text(((W - hw) / 2, H * 0.30), handle, font=fh, fill=fg)
    y = H * 0.30 + (hb[3] - hb[1]) + 26
    d.line([((W - hw) / 2, y), ((W + hw) / 2, y)], fill=TERRA, width=4)

    # wrap the Next: line
    fn = f(44)
    words, lines, cur = next_text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textbbox((0, 0), t, font=fn)[2] > W * 0.84 and cur:
            lines.append(cur); cur = wd
        else:
            cur = t
    lines.append(cur)
    y = H * 0.52
    for ln in lines:
        b = d.textbbox((0, 0), ln, font=fn)
        d.text(((W - (b[2] - b[0])) / 2, y), ln, font=fn, fill=fg)
        y += (b[3] - b[1]) + 22
    img.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    ap.add_argument("--drop", nargs="*", default=[], help="beat ids to cut")
    ap.add_argument("--next", dest="next_text", default=None)
    ap.add_argument("--end-s", type=float, default=4.5)
    ap.add_argument("--handle", default="@nikbearbrown")
    a = ap.parse_args()
    folder = a.folder.resolve()
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    slug = sheet["metadata"].get("slug", folder.name)

    short = folder / "short"
    for d in ("media", "manim", "mp3"):
        (short / d).mkdir(parents=True, exist_ok=True)

    kept = [b for b in sheet["beats"] if b["beat_id"] not in a.drop]
    dropped = [b for b in sheet["beats"] if b["beat_id"] in a.drop]
    next_text = a.next_text or next(
        (b["narration_text"] for b in reversed(dropped)
         if b.get("shot", {}).get("type") == "CARD"), "")

    # symlink kept slots + narration from the parent (nothing re-renders)
    for b in kept:
        bid = b["beat_id"]
        for sub in ("media", "manim"):
            for ext in (".mp4", ".mov", ".png", ".jpg"):
                src = folder / sub / f"{bid}{ext}"
                dst = short / sub / f"{bid}{ext}"
                if src.exists() and not dst.exists():
                    dst.symlink_to(Path("../..") / sub / src.name)
        mp3 = folder / (b.get("audio_file") or f"mp3/beat-{bid}.mp3")
        dst = short / "mp3" / mp3.name
        if mp3.exists() and not dst.exists():
            dst.symlink_to(Path("../..") / "mp3" / mp3.name)

    # the silent endcard: branded, read-only
    endcard_png(short / "media" / "END.png", a.handle, next_text, dark=True)
    subprocess.run([FFMPEG, "-y", "-v", "error", "-f", "lavfi",
                    "-i", "anullsrc=r=44100:cl=mono", "-t", f"{a.end_s:.2f}",
                    "-c:a", "libmp3lame", "-q:a", "9",
                    str(short / "mp3" / "beat-END.mp3")], check=True)
    kept.append({
        "beat_id": "END",
        "narration_text": "",
        "actual_duration_s": a.end_s,
        "audio_file": "mp3/beat-END.mp3",
        "shot": {"type": "CARD", "source": "own", "motion": "hold",
                 "treatment": "none"},
        "card": {"handle": a.handle, "next": next_text, "silent": True},
    })

    meta = dict(sheet["metadata"])
    meta.update({"slug": f"{slug}-short", "aspect_ratio": "9:16", "fit": "pad",
                 "derived_from": slug, "dropped_beats": a.drop,
                 "playlist_short": "Shorts"})
    total = sum(float(b["actual_duration_s"]) for b in kept)
    meta["total_estimated_duration_seconds"] = round(total, 2)
    (short / "beat_sheet.json").write_text(
        json.dumps({"metadata": meta, "beats": kept}, indent=1, ensure_ascii=False))

    cap = "OK" if total <= 180 else "⚠ OVER the 3:00 Shorts cap — drop more"
    print(f"[short] {len(kept)} beats · {total:.1f}s ({int(total//60)}:{total%60:04.1f}) {cap}")
    print(f"[short] dropped: {', '.join(a.drop) or 'none'} · silent endcard {a.end_s}s")
    print(f"[short] now: python3 scripts/vox_compile.py {folder.relative_to(folder.parents[1])}/short --review --height 1920")


if __name__ == "__main__":
    main()
