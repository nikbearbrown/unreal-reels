#!/usr/bin/env python3
"""Pick one source still per beat from the extracted music-video frames.

The frames were extracted at ~1 fps (blurry/dupe frames already culled, hence the
gaps), so a frame's number == its timestamp in seconds. For each of the 32 beats
we take the frames whose timestamp falls in that beat's [start_s, end_s) window
and keep the SHARPEST one (variance of the Laplacian). Frames stay in temporal
order, so beat k's still comes from beat k's moment in the song.
"""
import json, glob, re, os
import numpy as np
from PIL import Image

FRAME_RE = re.compile(r"_frame_(\d+)\.png$")

def laplacian_var(path, max_side=480):
    im = Image.open(path).convert("L")
    w, h = im.size
    s = max(w, h) / max_side
    if s > 1:
        im = im.resize((int(w / s), int(h / s)))
    a = np.asarray(im, dtype=np.float64)
    # 3x3 Laplacian kernel via numpy slicing
    lap = (-4 * a[1:-1,1:-1] + a[:-2,1:-1] + a[2:,1:-1] + a[1:-1,:-2] + a[1:-1,2:])
    return float(lap.var())

frames = []
for p in glob.glob("*_frame_*.png"):
    m = FRAME_RE.search(p)
    if m:
        frames.append((int(m.group(1)), p))
frames.sort()
print("frames:", len(frames), "| number range", frames[0][0], "-", frames[-1][0])

# timestamp(seconds) == frame number
sharp = {}
for num, p in frames:
    sharp[num] = laplacian_var(p)

bs = json.load(open("beat_sheet.json"))
beats = bs["beats"]
nums = [n for n, _ in frames]
path_by_num = dict(frames)

used = set()
report = []
for b in beats:
    s, e = b["start_s"], b["end_s"]
    # candidate frames in this beat's window
    cand = [n for n in nums if s <= n < e and n not in used]
    if not cand:                      # window had no frame -> nearest unused
        cand = [n for n in nums if n not in used]
        if cand:
            mid = (s + e) / 2
            cand = [min(cand, key=lambda n: abs(n - mid))]
    if not cand:                      # everything used -> nearest overall
        mid = (s + e) / 2
        cand = [min(nums, key=lambda n: abs(n - mid))]
    pick = max(cand, key=lambda n: sharp[n])
    used.add(pick)
    b["source_still"] = path_by_num[pick]
    b["source_frame_number"] = pick
    b["source_frame_sharpness"] = round(sharp[pick], 1)
    report.append((b["beat_id"], f"{s:.0f}-{e:.0f}s", pick, round(sharp[pick],0),
                   b["subject"], b["lyric_text"][:40]))

json.dump(bs, open("beat_sheet.json", "w"), ensure_ascii=False, indent=2)
print(f"assigned {len(used)} unique source frames to {len(beats)} beats\n")
print(f"{'beat':4} {'window':9} {'frame':>5} {'sharp':>7}  {'subj':7} lyric")
for r in report:
    print(f"{r[0]:4} {r[1]:9} {r[2]:5d} {r[3]:7.0f}  {r[4]:7} {r[5]}")
