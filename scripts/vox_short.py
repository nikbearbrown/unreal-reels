#!/usr/bin/env python3
"""vox_short.py — derive the 9:16 Shorts cut from a finished vox reel.

THE SHORTS LAW: a Short is a DERIVATIVE CUT, not a re-edit — drop the beats
that don't earn vertical time (documents, the bear outro), end on a SILENT
branded card the viewer reads (@handle + the Next: line), stay under the
3:00 Shorts cap.

THE REFORMAT RULE (16:9 → 9:16): you ONLY cut captured/generated media
(media/*.mp4|png) — center-cut biased by shot.focus, written beside the
source as <beat>-916.* (inspectable, replaceable; --recut regenerates).
GENERATED GRAPHICS ARE NEVER CUT: Manim/Remotion beats are RE-LAID-OUT for
portrait in the short's own vox_scenes.py and rendered by vox_run on the
short/ folder (the runner prefers a reel-local scenes file). A hand-made
<beat>-916.mp4|png in media/ or manim/ always wins over both paths.

Usage:
  python3 scripts/vox_short.py reels/<slug> --drop B14 B16 [--end-s 4.5] [--recut]
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
    ap.add_argument("--recut", action="store_true",
                    help="regenerate auto -916 cuts (never touches hand-made ones you added while no auto-cut existed)")
    ap.add_argument("--no-endcard", action="store_true",
                    help="end on the last kept beat (e.g. the bio kicker) instead of the silent branded card")
    a = ap.parse_args()
    folder = a.folder.resolve()
    sheet = json.loads((folder / "beat_sheet.json").read_text())
    slug = sheet["metadata"].get("slug", folder.name)

    short = folder / "short"
    for d in ("media", "manim", "mp3"):
        (short / d).mkdir(parents=True, exist_ok=True)

    # a derivative inherits the parent's fact-check (Gate F)
    fc = short / "FACTCHECK.md"
    if (folder / "FACTCHECK.md").exists() and not fc.exists():
        fc.symlink_to(Path("..") / "FACTCHECK.md")

    kept = [b for b in sheet["beats"] if b["beat_id"] not in a.drop]
    dropped = [b for b in sheet["beats"] if b["beat_id"] in a.drop]
    next_text = a.next_text or next(
        (b["narration_text"] for b in reversed(dropped)
         if b.get("shot", {}).get("type") == "CARD"), "")

    # resolve each kept slot to a 9:16 source: explicit -916 override wins,
    # else auto-cut the 16:9 winner (focus-aware) into <bid>-916.* beside it
    for b in kept:
        bid = b["beat_id"]
        # narration link FIRST — every kept beat needs its audio regardless of
        # how (or whether) its visual slot resolves; the compiler is all-or-silent
        mp3 = folder / (b.get("audio_file") or f"mp3/beat-{bid}.mp3")
        mdst = short / "mp3" / mp3.name
        if mp3.exists() and not mdst.exists():
            mdst.symlink_to(Path("../..") / "mp3" / mp3.name)
        fx = float((b.get("shot", {}).get("focus") or [0.5, 0.5])[0])
        override = None
        for sub, exts in (("media", (".mp4", ".png", ".jpg")),
                          ("manim", (".mp4",))):
            for ext in exts:
                p = folder / sub / f"{bid}-916{ext}"
                if p.exists():
                    override = (sub, p, ext)
                    break
            if override:
                break
        if override is None:
            # the parent slot's winner, per compile precedence
            src = None
            for sub, ext in (("media", ".mp4"), ("manim", ".mp4"),
                             ("manim", ".mov"), ("media", ".png"),
                             ("media", ".jpg")):
                p = folder / sub / f"{bid}{ext}"
                if p.exists():
                    src = (sub, p, ".mp4" if ext == ".mov" else ext)
                    break
            if src is None:
                continue                        # slate — nothing to cut
            sub, p, ext = src
            if sub == "manim":                  # NEVER cut generated graphics
                print(f"[short] {bid}  GENERATED — no cut; needs a portrait "
                      f"scene in short/vox_scenes.py (render via vox_run) or "
                      f"a hand-made manim/{bid}-916.mp4")
                continue
            cut = folder / sub / f"{bid}-916{ext}"
            if a.recut or not cut.exists():
                if ext == ".mp4":
                    vf = (f"crop='min(iw,ih*9/16)':ih:"
                          f"'max(0,min(iw-ow,iw*{fx:.4f}-ow/2))':0")
                    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(p),
                                    "-vf", vf, "-c:v", "libx264", "-preset",
                                    "veryfast", "-crf", "20", "-an", str(cut)],
                                   check=True)
                else:
                    from PIL import Image
                    im = Image.open(p)
                    w, h = im.size
                    cw = min(w, int(h * 9 / 16))
                    x = max(0, min(w - cw, int(fx * w - cw / 2)))
                    im.crop((x, 0, x + cw, h)).save(cut)
                print(f"[short] {bid}  cut 16:9 -> {sub}/{cut.name} (focus x={fx:.2f})")
            override = (sub, cut, ext)
        sub, p, ext = override
        dst = short / sub / f"{bid}{ext}"
        if dst.is_symlink() or dst.exists():
            dst.unlink()
        dst.symlink_to(Path("../..") / sub / p.name)

    # the silent endcard: branded, read-only (unless the film ends on a beat)
    if not a.no_endcard:
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
    meta.update({"slug": f"{slug}-short", "aspect_ratio": "9:16", "fit": "crop",
                 "reformat": "center-cut, focus-aware; -916 overrides honored",
                 "derived_from": slug, "dropped_beats": a.drop,
                 "playlist_short": "Shorts"})
    total = sum(float(b["actual_duration_s"]) for b in kept)
    meta["total_estimated_duration_seconds"] = round(total, 2)
    (short / "beat_sheet.json").write_text(
        json.dumps({"metadata": meta, "beats": kept}, indent=1, ensure_ascii=False))

    cap = "OK" if total <= 180 else "⚠ OVER the 3:00 Shorts cap — drop more"
    print(f"[short] {len(kept)} beats · {total:.1f}s ({int(total//60)}:{total%60:04.1f}) {cap}")
    tail_note = ("ends on the last beat (no endcard)" if a.no_endcard
                 else f"silent endcard {a.end_s}s")
    print(f"[short] dropped: {', '.join(a.drop) or 'none'} · {tail_note}")
    print(f"[short] now: python3 scripts/vox_compile.py {folder.relative_to(folder.parents[1])}/short --review --height 1920")


if __name__ == "__main__":
    main()
