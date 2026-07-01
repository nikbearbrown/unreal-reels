#!/usr/bin/env python3
"""make_shotlist.py — a paste-ready shot list for hand-generating a mixed dance reel
on the web (Kling start/end, unlimited) with the few Seedance beats flagged.

Writes <reel>/SHOTLIST.md: one block per beat, in order, with the model, duration,
the exact image files to upload, and the prompt in a copy-block. Kling beats first
(the fast upload-upload-paste run), Seedance beats called out separately.

Usage:  python make_shotlist.py <reel_folder>
"""
import json, os, sys

f = sys.argv[1] if len(sys.argv) > 1 else "."
d = json.load(open(os.path.join(f, "beat_sheet.json")))
m = d["metadata"]; beats = d["beats"]

def block(b):
    model = b.get("video_model", "kling")
    out = [f"### {b['beat_id']}  ·  {model}  ·  {b['duration_s']}s  ({b['start_s']:.1f}–{b['end_s']:.1f}s)"]
    if b.get("lyric_text"): out.append(f"_lyric:_ {b['lyric_text']}")
    if model == "kling":
        out.append(f"- **slot A (start frame):** `{b.get('storyboard_start','— MISSING —')}`")
        out.append(f"- **slot B (end frame):** `{b.get('storyboard_end','— MISSING —')}`")
        out.append(f"- settings: Kling 3.0, 5s, 720p, Unlimited mode")
    else:
        out.append(f"- **start frame:** `{b.get('storyboard_start') or b.get('chosen_still','— MISSING —')}`")
        out.append(f"- **audio:** `{b.get('audio_slice','—')}`  ·  Seedance 2.0, {min(15,int(b['duration_s'])+1)}s, audio-enhanced")
    out.append("\n_prompt:_\n```\n" + (b.get("video_prompt","").rsplit(". Duration",1)[0]) + "\n```")
    return "\n".join(out)

kling = [b for b in beats if b.get("video_model","kling") == "kling"]
seed = [b for b in beats if b.get("video_model","kling") != "kling"]

md = [f"# {m.get('title','reel')} — shot list",
      f"{len(beats)} beats · {len(kling)} Kling · {len(seed)} Seedance · aspect {m.get('aspect_ratio')} · "
      f"audio `{m.get('audio_file')}`",
      "\nUpload each beat's frame(s), paste the prompt, generate, download to "
      "`video/<beat_id>.mp4`. Then run the local assembly (`generate_video_seedance.sh FINAL=1` "
      "or the assemble step) — it stitches whatever clips are present and muxes the master track.\n",
      "---\n## Kling beats (web, Unlimited — fast run)\n"]
md += [block(b) + "\n" for b in kling]
if seed:
    md += ["---\n## Seedance beats (audio-enhanced — the ones that earned it)\n"]
    md += [block(b) + "\n" for b in seed]

open(os.path.join(f, "SHOTLIST.md"), "w").write("\n".join(md))
print(f"wrote SHOTLIST.md | {len(beats)} beats ({len(kling)} kling, {len(seed)} seedance)")
