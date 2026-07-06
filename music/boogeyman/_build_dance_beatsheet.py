#!/usr/bin/env python3
"""Build a DANCE beat sheet for boogeyman — 15-second segments (Seedance's cap),
not per-lyric-line beats. Each segment is a solo dance shot: image-to-video from a
boogeyman still + the beat's audio slice driving on-beat motion, in 1930s Fleischer
rubber-hose / Cab Calloway style. Segment boundaries snap to musical downbeats and
never exceed 15s. Lyric lines are attached per segment for optional captions only."""
import json, math

bd = json.load(open("beat_data.json"))
ly = json.load(open("lyrics.json"))
fps = bd["fps"]; dur = bd["durationInSeconds"]; total_f = bd["durationInFrames"]
db = bd.get("downbeatTimestamps") or []

MAXLEN, MINLEN = 15.0, 10.0
# greedy downbeat segmentation: each segment 10-15s, cut on a downbeat, <=15s
bounds = [0.0]; cur = 0.0
while cur < dur - 0.5:
    cands = [t for t in db if cur + 1.0 < t <= cur + MAXLEN]
    if cands:
        good = [t for t in cands if t >= cur + MINLEN]
        nxt = good[-1] if good else cands[-1]
    else:
        nxt = min(cur + MAXLEN, dur)
    if dur - nxt < 5.0 and (dur - cur) <= MAXLEN:  # absorb a tiny tail if it stays <=15s
        nxt = dur
    nxt = min(nxt, dur)
    bounds.append(round(nxt, 3)); cur = nxt
if bounds[-1] < dur:
    bounds.append(dur)

# dance vocabulary cycled across segments (solo, on-beat, fits the lanky rubber-hose Boogeyman)
MOVES = [
 ("a loose-limbed Cab Calloway strut", "gliding side to side, head bobbing and one long finger snapping on every downbeat"),
 ("a rubber-hose shimmy", "shoulders and spiky collar shaking fast on the off-beats, hips wobbling in time"),
 ("a soft-shoe shuffle", "twiggy feet sliding and tapping out the rhythm, upper body loose and swaying"),
 ("a Charleston", "knees swinging in and out, long legs flapping like rubber, heels flicking on the beat"),
 ("a Truckin' shuffle", "one long index finger pointed high, shuffling sideways across the frame in time"),
 ("a spin-and-freeze", "whirling around then snapping to a sharp grinning pose exactly on the downbeat"),
 ("the Black Bottom", "slapping his hips and rocking forward and back, stomping on the beat"),
 ("a rubber-hose melt", "body drooping and oozing like candle wax then snapping bolt upright on the musical hit"),
 ("a Lindy-hop air kick", "big leggy kicks and little hops, arms flailing loosely, landing on the beat"),
 ("a traveling conga hop", "hop-hop-kick bouncing across the frame, collar bouncing on each beat"),
 ("a grand finale strut", "a big showboating strut into a deep grinning bow, hitting the final beat hard"),
]

lines = sorted(ly["lines"], key=lambda l: l["index"])
def lyrics_in(a_s, b_s):
    out = [l["text"] for l in lines if a_s <= l["startFrame"]/fps < b_s]
    return " / ".join(out)

# Prompt = simple CHARACTER + CHOREOGRAPHY + CAMERA + short STYLE tag (per-beat camera varies).
CHAR = ("A tall lanky grinning rubber-hose Boogeyman puppet — spiky black collar, wide toothy grin, "
        "red cravat, long jointless twig-like limbs")
BACKGROUND = ("Background: a spooky desaturated monochrome-grey hall in deep shadow. AT MOST TWO spectral "
  "spirit-creatures drift and DANCE in the background — silvery-white, luminescent and semi-transparent, each "
  "glowing like a Patronus — and they RESEMBLE THE BOOGEYMAN HIMSELF: the same lanky, spiky-collared, grinning, "
  "twig-limbed silhouette, his eerie Tim Burton-style demon kin. They dance along loosely in time, echoing his "
  "moves, casting faint cold light; soft fog. Never more than two at once. NO spotlight, NO stage, NO confetti")
STYLE_TAG = ("rubber-hose 1930s Fleischer cartoon style, exaggerated and loose, motion locked to the beat; "
  "single character, full body, no text, no captions, no extra characters, no watermark")
CAMERAS = [
 "locked-off wide, slight low angle, full body in frame",
 "slow push-in from wide to medium",
 "slow orbit drifting around him",
 "side-tracking dolly following the dance",
 "wide shot with a dutch tilt",
 "high overhead looking down",
 "low hero angle tilting up",
 "static wide, character dead-center",
 "slow pull-back from medium to wide",
 "gentle handheld sway, full body",
 "punch-in to a medium on the downbeat, then hold",
 "wide locked-off for the big finish",
]

NSTILLS = 7
beats = []
for i in range(len(bounds) - 1):
    s, e = bounds[i], bounds[i+1]
    sf, ef = int(round(s*fps)), int(round(e*fps))
    if i == len(bounds) - 2:
        ef = total_f; e = ef/fps
    d = round((ef - sf)/fps, 2)
    move, detail = MOVES[i % len(MOVES)]
    camera = CAMERAS[i % len(CAMERAS)]
    still = f"stills/boogeyman_v{(i % NSTILLS) + 1}.png"
    bid = f"B{i+1:02d}"
    beats.append({
        "beat_id": bid,
        "start_s": round(s,2), "end_s": round(e,2),
        "start_frame": sf, "end_frame": ef, "duration_s": d,
        "kind": "dance",
        "subject": "boogeyman",
        "dance_move": move,
        "camera": camera,
        "lyric_text": lyrics_in(s, e),
        "chosen_still": still,
        "audio_slice": f"audio/{bid}.wav",
        "video_model": "seedance_2_0",
        "generate_audio": False,
        "video_prompt": (f"{CHAR}. Dance: {move} — {detail}. Camera: {camera}. {BACKGROUND}. {STYLE_TAG}. Duration {d}s."),
        "raw_clip": None, "video_file": None,
    })

sheet = {
  "metadata": {
    "slug": "boogeyman", "title": "Boogeyman", "artist": "Mayfield King",
    "mode": "dance", "aspect_ratio": "9:16", "fps": fps,
    "duration_s": dur, "duration_frames": total_f, "bpm": bd.get("bpm"),
    "key": f'{bd["features"].get("key")} {bd["features"].get("mode")}' if bd.get("features") else None,
    "audio_file": "BoogeymanMayfieldGD-mastered.wav", "lyrics_file": "song-09.txt",
    "beat_data": "beat_data.json", "lyrics_timing": "lyrics.json",
    "segmentation": "downbeat-aligned dance segments, 10-15s each (Seedance 15s cap)",
    "style_preset": "boogeyman-rubberhose-dance",
    "character": CHAR, "background": BACKGROUND, "style_suffix": STYLE_TAG, "cameras": CAMERAS,
    "subjects": [{"name": "Boogeyman", "subject_key": "boogeyman", "driver": "reference",
                  "reference_dir": "stills",
                  "look": "a tall lanky folk-art Boogeyman puppet: spiky black collar, wide grinning toothy "
                          "mask, red cravat, long jointless twig-like rubber-hose limbs; 7 reference stills cycled."}],
    "generation": {
      "video_model": "seedance_2_0", "duration_s_max": 15, "generate_audio": False,
      "rule": "each beat is image-to-video on Seedance 2.0: --image chosen_still + --audio audio_slice "
              "(drives on-beat motion) + --prompt video_prompt, --duration = beat duration (<=15s), "
              "generate_audio false (mux the master track at assembly). Test beat-match before full run.",
    },
    "counts": {"beats": len(beats)},
  },
  "beats": beats,
}
json.dump(sheet, open("beat_sheet.json","w"), ensure_ascii=False, indent=2)

# verify
prev = 0
for b in beats:
    assert b["start_frame"] == prev, f"gap at {b['beat_id']}"
    prev = b["end_frame"]
    assert b["duration_s"] <= 15.0, f"{b['beat_id']} exceeds 15s: {b['duration_s']}"
assert prev == total_f
print(f"wrote beat_sheet.json | {len(beats)} dance beats | contiguous 0..{total_f} OK")
print(f"durations: {[b['duration_s'] for b in beats]}")
print(f"all <=15s: {all(b['duration_s']<=15 for b in beats)} | max {max(b['duration_s'] for b in beats)}s")
