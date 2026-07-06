#!/usr/bin/env python3
"""Build the 'Who's Gonna Bell That Cat' STORY beat sheet — Kling start/end frames,
each storyboard composited by FLUX from up to 4 inputs (1 background + characters).

Cast assets live in PNG/:  background_v1-6, orange-cat_v1-12 (the LEAD — the cat the
mice fear), mice_v1-6 (use 2+ when mice are in a scene), black-cat_v1-6 (occasional).
One lyric line = one story beat = a FLUX-composited START frame and END frame; Kling
tweens the motion between them.
"""
import json, os

ly = json.load(open("lyrics.json")); bd = json.load(open("beat_data.json"))
fps = bd["fps"]; total_f = bd["durationInFrames"]
lines = sorted(ly["lines"], key=lambda l: l["index"])
A = "PNG/"  # asset dir

STYLE = ("Composite the inputs into ONE cohesive hand-drawn ink-and-gouache storybook "
         "illustration — unified moonlit lighting, matching linework and texture, the "
         "characters blended naturally into the scene at consistent scale. No text, no watermark.")

# per beat: (background, [character assets, <=3], start arrangement, end arrangement, kling motion)
oc = lambda n: f"{A}orange-cat_v{n}.png"
mo = lambda n: f"{A}mice_v{n}.png"
bc = lambda n: f"{A}black-cat_v{n}.png"
bg = lambda n: f"{A}background_v{n}.png"

STORY = [
 # 1 midnight meeting
 (bg(2), [mo(1),mo(2),mo(3)], "three little mice creep out along the base of the moonlit fence at night", "the three mice gather close together in a huddle to begin their secret meeting", "slow push-in as the mice scurry together"),
 (bg(3), [mo(1),mo(2),mo(3)], "the three mice sit in a tight council circle under the moon, whispering", "the mice squeak excitedly, little paws raised", "gentle bob as the mice gesture and squeak"),
 (bg(4), [oc(3),mo(1),mo(2)], "the big orange tiger-cat appears as a looming shape at the fence, two tiny mice freeze", "the orange cat creeps closer, the mice shrink back in fear", "the cat slinks forward, mice recoil"),
 (bg(5), [mo(1),mo(2)], "a little mouse clutches its chest in melodramatic terror, another beside it", "the frightened mouse swoons backward, the other catches it", "the mouse faints, caught by its friend"),
 # 2 brown back complains
 (bg(2), [mo(3),mo(1)], "a stout grumbling mouse (Brown Back) crosses its arms, fed up, another listens", "Brown Back throws its paws up in complaint", "Brown Back grumbles and gestures"),
 (bg(1), [mo(2)], "by daylight in the marigold garden a mouse darts toward a scattered crumb", "the mouse snatches the crumb and scampers away, fur ruffled", "quick dash for the crumb and away"),
 (bg(6), [oc(2),mo(1)], "the grinning fanged orange cat with golden eyes emerges huge from the shadow over one tiny mouse", "the cat looms directly over the cowering mouse, jaws wide", "the cat's grinning face pushes in"),
 (bg(3), [mo(1),mo(2),mo(3)], "the mice cluster together, suddenly resolute", "one mouse thrusts a paw to the sky to rally the others", "the mice draw together, a paw shoots up"),
 # 3 the plan
 (bg(4), [mo(4),mo(1)], "a mouse (Gray Ear) mid-suggestion, gesturing a bite-and-run", "Gray Ear mimes darting in and dashing away", "Gray Ear acts out the bite and run"),
 (bg(5), [mo(1),mo(2),mo(3)], "the mice imagine a swarm, paws spread wide", "the mice cheer the swarm idea, bouncing", "the mice get excited, bouncing"),
 (bg(2), [mo(5),mo(1),mo(2)], "a clever mouse (White Whisker) raises one paw with a bright idea, the others lean in", "the listening mice lean closer, ears perked", "White Whisker raises a paw, others lean in"),
 (bg(3), [mo(5),mo(1)], "White Whisker mimes hanging a tiny bell in the air, a small brass bell drawn glinting", "the mice stare at the imagined glinting bell, wide-eyed", "the mouse mimes hanging the bell, it glints"),
 # 4 celebration
 (bg(6), [mo(1),mo(2),mo(3)], "the mice throw their paws up cheering, a little brass bell glinting above them", "the mice leap with joy, the bell ringing over their heads", "the mice jump up cheering, bell swings"),
 (bg(4), [mo(2),mo(3),mo(4)], "a line of mice break into a joyful dance", "the mice form a little conga line, tails linked", "the mice dance into a conga line"),
 (bg(5), [mo(1),mo(2),mo(3)], "the mice twirl with glee, a tiny bell glinting", "the mice link paws and spin in a ring", "the mice twirl and link paws"),
 (bg(2), [oc(7),mo(1)], "the orange cat now wearing a little bell collar, a mouse grinning at it", "the belled cat skulks off as the mouse points and laughs", "the belled cat slinks away, mouse laughs"),
 # 5 the catch
 (bg(3), [mo(3),mo(1),mo(2)], "Brown Back raises a paw for silence, hushing the cheering mice", "the celebrating mice fall quiet, ears drooping", "Brown Back hushes them, cheer dies down"),
 (bg(6), [mo(3),mo(1)], "Brown Back speaks gravely, close, the other mouse uneasy", "the listening mouse's ears droop with dawning fear", "Brown Back speaks; the other shrinks"),
 (bg(4), [mo(3)], "Brown Back points up at the small brass bell hanging untouched", "the bell hangs silent and still as the mouse stares", "Brown Back points; the bell hangs still"),
 # 6 who? — the key question
 (bg(5), [oc(4),mo(1),mo(2)], "the great orange cat dozes turned away; two mice creep up holding the bell, hesitating", "the mice freeze and shrink back from the sleeping cat, the bell trembling", "mice inch toward the cat, then freeze"),
 # 7 excuses
 (bg(2), [mo(5),mo(1)], "White Whisker coughs and edges backward, paws up, making an excuse", "White Whisker points away, passing the job to someone else", "White Whisker backs off, points away"),
 (bg(3), [mo(5)], "White Whisker exaggerates a limp, clutching its leg", "the mouse hobbles theatrically off to the side", "the mouse fakes a limp and hobbles off"),
 (bg(6), [mo(4),mo(1)], "Gray Ear shakes its head firmly, refusing", "Gray Ear turns its back and folds its arms", "Gray Ear shakes head and turns away"),
 (bg(4), [mo(4)], "Gray Ear mimes a snapping trap and shudders at the memory", "the mouse backs away, trembling, paws up", "the mouse mimes a trap snap, shudders"),
 # 7 moral
 (bg(5), [mo(1),mo(2),mo(3)], "one by one the mice trudge away to bed in a glum line", "the mice disappear one by one into the shadows", "the mice slink off into the dark"),
 (bg(2), [oc(4)], "the small brass bell lies untouched on the ground, the orange cat asleep beyond", "a long quiet hold on the unhung bell and the sleeping cat", "slow hold on the bell and sleeping cat"),
 (bg(3), [mo(1),bc(3)], "a lone little mouse shrugs to the viewer, a black cat lurking in the far shadow", "the mouse gives a knowing look to camera", "the mouse shrugs and looks to camera"),
 (bg(6), [oc(2),bc(3)], "the grinning golden-eyed orange cat front and center, the unhung bell glinting nearby, a black cat looming behind", "the cat's grin widens as the bell hangs unhung — no mouse in sight", "slow push-in on the grinning cat, bell unhung"),
]

assert len(STORY) == len(lines), f"{len(STORY)} story beats vs {len(lines)} lyric lines"
starts = [l["startFrame"] for l in lines]
beats = []
for i, (background, chars, sp, ep, motion) in enumerate(STORY):
    sf = 0 if i == 0 else starts[i]
    ef = starts[i+1] if i+1 < len(lines) else total_f
    d = round((ef - sf)/fps, 2)
    bid = f"B{i+1:02d}"
    assets = [background] + chars
    beats.append({
        "beat_id": bid, "start_s": round(sf/fps,2), "end_s": round(ef/fps,2),
        "start_frame": sf, "end_frame": ef, "duration_s": d,
        "kind": "story", "lyric_text": lines[i]["text"],
        "video_model": "kling", "audio_slice": f"audio/{bid}.wav",
        "assets": assets,                       # FLUX composite inputs (<=4): background + characters
        "start_prompt": f"{sp}. {STYLE}",       # -> stills/story/<bid>_start.png
        "end_prompt":   f"{ep}. {STYLE}",       # -> stills/story/<bid>_end.png
        "video_prompt": f"Storybook fable: {motion}. Smooth hand-drawn animation, gentle motion, no text.",
        "raw_clip": None, "video_file": None,
    })

sheet = {"metadata": {
    "slug": "who-s-gonna-bell-that-cat", "title": "Who's Gonna Bell That Cat",
    "artist": "Parvati", "mode": "story-dance", "aspect_ratio": "9:16", "fps": fps,
    "duration_s": bd["durationInSeconds"], "duration_frames": total_f, "bpm": bd.get("bpm"),
    "audio_file": "GDWhosGonnaBellThatCatParvatiBEAN-mastered.wav", "lyrics_file": "song-11.txt",
    "beat_data": "beat_data.json", "lyrics_timing": "lyrics.json", "default_video_model": "kling",
    "cast": {"lead": "orange-cat (the cat the mice fear)", "mice": "use 2+ when mice are in a scene",
             "black-cat": "occasional second feline presence", "assets_dir": "PNG"},
    "compositing": "each storyboard frame is a FLUX composite of beat.assets (<=4 inputs: background + characters); "
                   "start_prompt -> stills/story/<beat>_start.png, end_prompt -> _end.png. Kling tweens start->end.",
    "style": STYLE,
    "counts": {"beats": len(beats)},
}, "beats": beats}

json.dump(sheet, open("beat_sheet.json","w"), ensure_ascii=False, indent=2)
prev = 0
for b in beats:
    assert b["start_frame"] == prev, f"gap at {b['beat_id']}"; prev = b["end_frame"]
    assert all(os.path.exists(a) for a in b["assets"]), f"missing asset in {b['beat_id']}: {b['assets']}"
    assert len(b["assets"]) <= 4, f"{b['beat_id']} has >4 FLUX inputs"
assert prev == total_f
print(f"wrote beat_sheet.json | {len(beats)} story beats | contiguous 0..{total_f} OK | "
      f"durations {min(b['duration_s'] for b in beats)}-{max(b['duration_s'] for b in beats)}s | all assets exist, <=4 inputs")
