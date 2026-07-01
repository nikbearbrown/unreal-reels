#!/usr/bin/env python3
"""pick_stills.py — choose one source still per beat from extracted video frames.

Frames are extracted at a known fps (see extract_frames.sh), so a frame's index
maps to a timestamp: t = index / fps. For each beat we take the frames whose
timestamp falls in [start_s, end_s) and keep the SHARPEST (variance of the
Laplacian). Frames stay in temporal order, so beat k's still is from beat k's
moment in the song. Each frame is used at most once; if a beat's window is empty
(culled frames) we fall back to the nearest unused frame.

Writes back into beat_sheet.json:  source_still, source_frame_number,
source_frame_sharpness, and (unless --no-copy) copies the keeper to
stills/<beat_id>_v1.png and sets chosen_still + storyboard_candidates.

Usage:
    python pick_stills.py <reel_folder> [--fps 1] [--prefix NAME] [--no-copy]
"""
import argparse, glob, json, os, re, shutil
import numpy as np
from PIL import Image

def laplacian_var(path, max_side=480):
    im = Image.open(path).convert("L")
    w, h = im.size
    s = max(w, h) / max_side
    if s > 1:
        im = im.resize((int(w / s), int(h / s)))
    a = np.asarray(im, dtype=np.float64)
    lap = (-4 * a[1:-1,1:-1] + a[:-2,1:-1] + a[2:,1:-1] + a[1:-1,:-2] + a[1:-1,2:])
    return float(lap.var())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--fps", type=float, default=1.0, help="fps the frames were extracted at")
    ap.add_argument("--prefix", default=None, help="frame filename prefix (auto-detected if omitted)")
    ap.add_argument("--sheet", default="beat_sheet.json")
    ap.add_argument("--no-copy", action="store_true", help="don't copy keepers into stills/")
    args = ap.parse_args()

    f = args.folder
    frame_glob = f"*{args.prefix}*_frame_*.png" if args.prefix else "*_frame_*.png"
    paths = glob.glob(os.path.join(f, frame_glob))
    num_re = re.compile(r"_frame_(\d+)\.png$")
    frames = sorted((int(num_re.search(p).group(1)), p) for p in paths if num_re.search(p))
    if not frames:
        raise SystemExit(f"no frames matching {frame_glob} in {f}")
    print(f"frames: {len(frames)} | index range {frames[0][0]}-{frames[-1][0]} | fps={args.fps}")

    # timestamp(seconds) = index / fps
    ts = {num: num / args.fps for num, _ in frames}
    path_by_num = dict(frames)
    nums = [n for n, _ in frames]
    sharp = {n: laplacian_var(p) for n, p in frames}

    sheet_path = os.path.join(f, args.sheet)
    bs = json.load(open(sheet_path))
    beats = bs["beats"]

    if not args.no_copy:
        os.makedirs(os.path.join(f, "stills"), exist_ok=True)

    used = set()
    report = []
    for b in beats:
        s, e = b["start_s"], b["end_s"]
        cand = [n for n in nums if s <= ts[n] < e and n not in used]
        if not cand:
            mid = (s + e) / 2
            rest = [n for n in nums if n not in used]
            cand = [min(rest, key=lambda n: abs(ts[n] - mid))] if rest else \
                   [min(nums, key=lambda n: abs(ts[n] - (s + e) / 2))]
        pick = max(cand, key=lambda n: sharp[n])
        used.add(pick)
        b["source_still"] = os.path.basename(path_by_num[pick])
        b["source_frame_number"] = pick
        b["source_frame_sharpness"] = round(sharp[pick], 1)
        if not args.no_copy:
            dst = f"stills/{b['beat_id']}_v1.png"
            shutil.copyfile(path_by_num[pick], os.path.join(f, dst))
            b["chosen_still"] = dst
            b["storyboard_candidates"] = [dst]
        report.append((b["beat_id"], f"{s:.0f}-{e:.0f}s", pick,
                       round(sharp[pick]), b["lyric_text"][:44]))

    json.dump(bs, open(sheet_path, "w"), ensure_ascii=False, indent=2)
    print(f"assigned {len(used)} unique source frames to {len(beats)} beats\n")
    print(f"{'beat':4} {'window':9} {'frame':>6} {'sharp':>7}  lyric")
    for r in report:
        print(f"{r[0]:4} {r[1]:9} {r[2]:6d} {r[3]:7.0f}  {r[4]}")

if __name__ == "__main__":
    main()
