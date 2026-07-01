#!/usr/bin/env python3
"""build_dance_beatsheet.py — DANCE-mode beat sheet (songbird-dance).

Cuts a song into 10-15s segments, each ending on a musical downbeat and never over
Seedance's 15s cap. One segment = one solo dance shot: a character still + the beat's
audio slice (drives on-beat motion) + a four-part prompt
(CHARACTER + CHOREOGRAPHY + CAMERA + short style tag). Character stills are cycled;
move + camera vary per beat. Optional lyrics are attached per segment for captions only.

Usage:
  python build_dance_beatsheet.py <reel_folder> --audio song.wav --title "Boogeyman" \
      --character "A tall lanky grinning rubber-hose puppet" \
      [--style-tag "..."] [--aspect 9:16] [--stills-dir stills] [--slug boogeyman] \
      [--lyrics song.txt] [--moves-json moves.json]
"""
import argparse, glob, json, os, re

# default 1930s vernacular dance vocabulary — solo-friendly, beat-readable
DEFAULT_MOVES = [
 ("a loose-limbed Cab Calloway strut", "gliding side to side, head bobbing and snapping a finger on every downbeat"),
 ("a rubber-hose shimmy", "shoulders shaking fast on the off-beats, hips wobbling in time"),
 ("a soft-shoe shuffle", "feet sliding and tapping out the rhythm, upper body loose and swaying"),
 ("a Charleston", "knees swinging in and out, legs flapping loosely, heels flicking on the beat"),
 ("a Truckin' shuffle", "one index finger pointed high, shuffling sideways across the frame in time"),
 ("a spin-and-freeze", "whirling around then snapping to a sharp pose exactly on the downbeat"),
 ("the Black Bottom", "slapping the hips and rocking forward and back, stomping on the beat"),
 ("a rubber-hose melt", "body drooping like wax then snapping bolt upright on the musical hit"),
 ("a Lindy-hop air kick", "big leggy kicks and little hops, arms loose, landing on the beat"),
 ("a traveling conga hop", "hop-hop-kick bouncing across the frame on each beat"),
 ("a grand finale strut", "a big showboating strut into a deep bow, hitting the final beat hard"),
]
DEFAULT_CAMERAS = [
 "locked-off wide, slight low angle, full body in frame", "slow push-in from wide to medium",
 "slow orbit drifting around the character", "side-tracking dolly following the dance",
 "wide shot with a dutch tilt", "high overhead looking down", "low hero angle tilting up",
 "static wide, character dead-center", "slow pull-back from medium to wide",
 "gentle handheld sway, full body", "punch-in to a medium on the downbeat then hold",
 "wide locked-off for the big finish",
]
DEFAULT_STYLE_TAG = ("exaggerated and loose, motion locked to the beat; single character, full body, "
                     "no text, no captions, no extra characters, no watermark")

def segment_downbeats(db, dur, maxlen=15.0, minlen=10.0):
    bounds = [0.0]; cur = 0.0
    while cur < dur - 0.5:
        cands = [t for t in db if cur + 1.0 < t <= cur + maxlen]
        if cands:
            good = [t for t in cands if t >= cur + minlen]
            nxt = good[-1] if good else cands[-1]
        else:
            nxt = min(cur + maxlen, dur)
        if dur - nxt < 5.0 and (dur - cur) <= maxlen:
            nxt = dur
        nxt = min(nxt, dur); bounds.append(round(nxt, 3)); cur = nxt
    if bounds[-1] < dur:
        bounds.append(dur)
    return bounds

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--character", required=True, help="short character description")
    ap.add_argument("--style-tag", default=DEFAULT_STYLE_TAG)
    ap.add_argument("--background", default="Background: a plain dark backdrop, no extra scenery, no spotlight, no stage",
                    help="EXPLICIT background — vague wording makes the model invent stages/confetti")
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--stills-dir", default="stills")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--artist", default="")
    ap.add_argument("--lyrics", default=None)
    ap.add_argument("--lyrics-timing", default="lyrics.json")
    ap.add_argument("--beat-data", default="beat_data.json")
    ap.add_argument("--moves-json", default=None, help="JSON [[move,detail],...] to override defaults")
    ap.add_argument("--model", default="kling", help="default per-beat video model: kling (5s, start+end frames) or seedance_2_0 (15s, audio)")
    ap.add_argument("--beat-max", type=float, default=None, help="max segment seconds (default 5 for kling, 15 for seedance)")
    ap.add_argument("--beat-min", type=float, default=None, help="min segment seconds")
    args = ap.parse_args()
    # profile defaults: Kling is unlimited at 5s; Seedance caps at 15s
    if args.beat_max is None: args.beat_max = 5.0 if args.model == "kling" else 15.0
    if args.beat_min is None: args.beat_min = 3.5 if args.model == "kling" else 10.0

    f = args.folder
    bd = json.load(open(os.path.join(f, args.beat_data)))
    fps = bd["fps"]; dur = bd["durationInSeconds"]; total_f = bd["durationInFrames"]
    db = bd.get("downbeatTimestamps") or bd.get("beatTimestamps") or []
    slug = args.slug or re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")

    MOVES = [tuple(x) for x in json.load(open(args.moves_json))] if args.moves_json else DEFAULT_MOVES
    stills = sorted(glob.glob(os.path.join(f, args.stills_dir, "*.png")) +
                    glob.glob(os.path.join(f, args.stills_dir, "*.jpg")))
    if not stills:
        raise SystemExit(f"no character stills in {os.path.join(f, args.stills_dir)}")
    stills = [os.path.relpath(s, f) for s in stills]

    lines = []
    lp = os.path.join(f, args.lyrics_timing)
    if os.path.exists(lp):
        lines = sorted(json.load(open(lp)).get("lines", []), key=lambda l: l["index"])
    def lyrics_in(a_s, b_s):
        return " / ".join(l["text"] for l in lines if a_s <= l["startFrame"]/fps < b_s)

    bounds = segment_downbeats(db, dur, maxlen=args.beat_max, minlen=args.beat_min)
    beats = []
    for i in range(len(bounds) - 1):
        s, e = bounds[i], bounds[i+1]
        sf, ef = int(round(s*fps)), int(round(e*fps))
        if i == len(bounds) - 2:
            ef = total_f; e = ef/fps
        d = round((ef - sf)/fps, 2)
        move, detail = MOVES[i % len(MOVES)]
        camera = DEFAULT_CAMERAS[i % len(DEFAULT_CAMERAS)]
        bid = f"B{i+1:02d}"
        beats.append({
            "beat_id": bid, "start_s": round(s,2), "end_s": round(e,2),
            "start_frame": sf, "end_frame": ef, "duration_s": d,
            "kind": "dance", "subject": slug, "dance_move": move, "camera": camera,
            "lyric_text": lyrics_in(s, e),
            "chosen_still": stills[i % len(stills)],
            "audio_slice": f"audio/{bid}.wav",
            "video_model": args.model, "generate_audio": False,
            "video_prompt": f"{args.character}. Dance: {move} — {detail}. Camera: {camera}. {args.background}. {args.style_tag}. Duration {d}s.",
            "raw_clip": None, "video_file": None,
        })

    sheet = {"metadata": {
        "slug": slug, "title": args.title, "artist": args.artist, "mode": "dance",
        "aspect_ratio": args.aspect, "fps": fps, "duration_s": dur, "duration_frames": total_f,
        "bpm": bd.get("bpm"), "audio_file": os.path.basename(args.audio),
        "lyrics_file": (os.path.basename(args.lyrics) if args.lyrics else None),
        "beat_data": args.beat_data, "lyrics_timing": args.lyrics_timing if lines else None,
        "segmentation": f"downbeat-aligned dance segments, {args.beat_min:g}-{args.beat_max:g}s each",
        "default_video_model": args.model,
        "character": args.character, "background": args.background, "style_suffix": args.style_tag, "cameras": DEFAULT_CAMERAS,
        "generation": {"default_video_model": args.model, "beat_max_s": args.beat_max, "generate_audio": False,
            "rule": "PER-BEAT video_model routes generation. kling -> Kling start+end frames (web, unlimited, 5s); "
                    "seedance_2_0 -> single frame + audio_slice (audio-enhanced, <=15s). Storyboard + slicer + "
                    "assembly all read video_model. Two-pass: build all Kling, then promote_to_seedance the sections that earn it."},
        "counts": {"beats": len(beats), "kling": sum(1 for b in beats if b["video_model"]=="kling"),
                   "seedance": sum(1 for b in beats if b["video_model"]!="kling")},
    }, "beats": beats}

    json.dump(sheet, open(os.path.join(f, "beat_sheet.json"), "w"), ensure_ascii=False, indent=2)
    prev = 0
    cap = max(15.0, args.beat_max)
    for b in beats:
        assert b["start_frame"] == prev, f"gap at {b['beat_id']}"; prev = b["end_frame"]
        assert b["duration_s"] <= cap + 0.5, f"{b['beat_id']} > {cap}s"
    assert prev == total_f
    print(f"wrote beat_sheet.json | {len(beats)} dance beats ({args.model}) | contiguous 0..{total_f} OK | "
          f"max {max(b['duration_s'] for b in beats)}s | stills cycled: {len(stills)}")

if __name__ == "__main__":
    main()
