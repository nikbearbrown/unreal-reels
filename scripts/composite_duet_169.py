#!/usr/bin/env python3
"""composite_duet_169.py — make 16:9 Cookie+Grover duet stills WITHOUT a model.

Deterministic: take each beat's 9:16 Cookie still and a 9:16 Grover still, place
them side by side (Grover on beat.grover_side), and crop to 16:9. Every character
keeps EXACTLY the look from its source frame — nothing is regenerated. Motion is
added later in the video step.

Cookie stills:  --cookie-dir (default stills/916), file <beat_id>_v1.png
Grover stills:  --grover-dir — paired by <beat_id>_v1.png if present; otherwise the
                folder's images are cycled across beats. Or --grover one image reused.

Output: stills/<beat_id>_v1.png  (overwrites the ruined model duets; 9:16 originals
        stay in stills/916/)

Modes:
  --mode crop  (default) each half is cover-cropped to fill — fullest frame, may clip
               top/bottom; use --vanchor 0..1 to bias (0.4 keeps heads).
  --mode pad   each still is fully contained on a blurred backdrop — nothing clipped.

Usage:
  python composite_duet_169.py <reel_folder> --grover-dir stills/grover
  python composite_duet_169.py <reel_folder> --grover path/to/grover.png --mode pad
"""
import argparse, glob, json, os, re
from PIL import Image, ImageFilter

def load_grovers(reel, grover_dir, grover_single, beats):
    if grover_single:
        g = Image.open(os.path.join(reel, grover_single) if not os.path.isabs(grover_single) else grover_single).convert("RGB")
        return {b["beat_id"]: g for b in beats}
    d = os.path.join(reel, grover_dir)
    out = {}
    # 1:1 pairing by beat id if those files exist
    if all(os.path.exists(os.path.join(d, f"{b['beat_id']}_v1.png")) for b in beats):
        for b in beats:
            out[b["beat_id"]] = Image.open(os.path.join(d, f"{b['beat_id']}_v1.png")).convert("RGB")
        return out
    # else cycle whatever images are in the folder, in name order
    pool = sorted(glob.glob(os.path.join(d, "*.png")) + glob.glob(os.path.join(d, "*.jpg")))
    if not pool:
        raise SystemExit(f"no Grover images in {d} (and no --grover single image given)")
    for i, b in enumerate(beats):
        out[b["beat_id"]] = Image.open(pool[i % len(pool)]).convert("RGB")
    return out

def cover_crop(im, tw, th, vanchor=0.5):
    w, h = im.size
    s = max(tw / w, th / h)
    nw, nh = int(round(w * s)), int(round(h * s))
    im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = int(round((nh - th) * vanchor))
    return im.crop((x, y, x + tw, y + th))

def contain_pad(im, tw, th):
    bg = cover_crop(im.copy(), tw, th).filter(ImageFilter.GaussianBlur(40))
    w, h = im.size
    s = min(tw / w, th / h)
    nw, nh = int(round(w * s)), int(round(h * s))
    fg = im.resize((nw, nh), Image.LANCZOS)
    bg.paste(fg, ((tw - nw) // 2, (th - nh) // 2))
    return bg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--cookie-dir", default="stills/916")
    ap.add_argument("--grover-dir", default="stills/grover")
    ap.add_argument("--grover", default=None, help="single Grover image reused for every beat")
    ap.add_argument("--mode", choices=["crop", "pad"], default="crop")
    ap.add_argument("--height", type=int, default=1080, help="output height (16:9 -> width = height*16/9)")
    ap.add_argument("--vanchor", type=float, default=0.4, help="crop mode vertical anchor 0..1 (lower keeps heads)")
    ap.add_argument("--sheet", default="beat_sheet.json")
    ap.add_argument("only", nargs="*", help="optional beat IDs to composite (default: all)")
    args = ap.parse_args()

    reel = args.folder
    bs = json.load(open(os.path.join(reel, args.sheet)))
    beats = bs["beats"]
    if args.only:
        want = set(args.only)
        beats = [b for b in beats if b["beat_id"] in want]
    H = args.height; W = H * 16 // 9; half = W // 2
    grovers = load_grovers(reel, args.grover_dir, args.grover, beats)
    os.makedirs(os.path.join(reel, "stills"), exist_ok=True)

    place = cover_crop if args.mode == "crop" else (lambda im, tw, th: contain_pad(im, tw, th))
    n = 0
    for b in beats:
        ck = os.path.join(reel, args.cookie_dir, f"{b['beat_id']}_v1.png")
        if not os.path.exists(ck):
            print("skip", b["beat_id"], "- no cookie still", ck); continue
        cookie = Image.open(ck).convert("RGB")
        grover = grovers[b["beat_id"]]
        if args.mode == "crop":
            ch = cover_crop(cookie, half, H, args.vanchor); gh = cover_crop(grover, half, H, args.vanchor)
        else:
            ch = contain_pad(cookie, half, H); gh = contain_pad(grover, half, H)
        canvas = Image.new("RGB", (W, H))
        if b.get("grover_side", "right") == "right":
            canvas.paste(ch, (0, 0)); canvas.paste(gh, (half, 0))   # cookie left, grover right
        else:
            canvas.paste(gh, (0, 0)); canvas.paste(ch, (half, 0))   # grover left, cookie right
        out = os.path.join(reel, "stills", f"{b['beat_id']}_v1.png")
        canvas.save(out); n += 1
    print(f"composited {n} duet stills -> {os.path.join(reel,'stills')} ({W}x{H}, mode={args.mode})")
    print("9:16 originals untouched in stills/916/")

if __name__ == "__main__":
    main()
