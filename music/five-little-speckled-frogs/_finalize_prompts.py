#!/usr/bin/env python3
"""Finalize five-little-speckled-frogs: derive the craft-diorama style from the
source frames (needle-felt speckled frogs on a mossy log over a still pool, giant
felt mushrooms/flowers, painterly bokeh) and write per-beat image/video prompts
pairing each chosen still with its lyric — honoring the countdown (5->4->3->2->1->0)
and the chant words (Yum yum / Glug glug / Splish splash / Ribbit ribbit)."""
import json, re

bs = json.load(open("beat_sheet.json"))
def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())

# normalized lyric -> (action tied to the words, camera)
ACT = {
 "Five little speckled frogs": ("five speckled felt frogs perched in a row along the mossy log", "slow_pan"),
 "Four little speckled frogs": ("four speckled frogs perched on the mossy log", "slow_pan"),
 "Three little speckled frogs": ("three speckled frogs perched on the mossy log", "slow_pan"),
 "Two little speckled frogs": ("two speckled frogs side by side on the mossy log", "static"),
 "One little speckled frog": ("a single speckled frog alone on the mossy log", "slow_push_in"),
 "Sat on a speckled log": ("the speckled frogs settling onto the mossy speckled log over the still pool", "static"),
 "Eating some most delicious bugs": ("a frog flicking out its long tongue to snatch a bug from the air", "slow_push_in"),
 "Yum yum!": ("a frog munching happily, cheeks full, eyes shut with delight", "slow_push_in"),
 "One jumped into the pool": ("one frog leaping off the log toward the water, caught mid-air", "tilt_down"),
 "He jumped into the pool": ("the very last frog leaping off the log toward the water, mid-air", "tilt_down"),
 "Where it was nice and cool": ("a frog sinking into the cool still water, gentle ripples spreading", "slow_push_in"),
 "Then there were four green speckled frogs": ("four frogs left on the log, one spot now empty", "slow_pan"),
 "Then there were three green speckled frogs": ("three frogs left on the log", "slow_pan"),
 "Then there were two green speckled frogs": ("two frogs left on the log", "static"),
 "Then there was one green speckled frog": ("one lonely frog left on the log", "slow_push_in"),
 "Then there were no green speckled frogs": ("the empty mossy log, only ripples in the pool below", "slow_push_in"),
 "Glug glug!": ("a stream of bubbles rising as a frog submerges in the pool", "static"),
 "Oh no more speckled frogs": ("the bare mossy log, no frogs left on it", "slow_push_in"),
 "Not one on the log": ("a close look at the empty log over the quiet pool", "slow_push_in"),
 "No more frogs to sing this song": ("the empty log with a few petals drifting down", "static"),
 "All gone!": ("the still pool and the empty log, gentle widening ripples", "slow_push_in"),
 "Each one took a dive": ("frogs diving one after another into the pool, little splashes", "tilt_down"),
 "And they're swimming feeling alive": ("frogs swimming happily just under the bright water", "slow_pan"),
 "Down in the pool oh how they thrive!": ("frogs thriving and frolicking in the bubbly pool", "slow_pan"),
 "Splish splash!": ("a big playful splash bursting up from the pool", "static"),
 "The pool is full of frogs": ("the pool crowded with cheerful swimming speckled frogs", "slow_pan"),
 "No more on the logs": ("the empty log above, frogs paddling in the water below", "tilt_down"),
 "They're happy in the water now": ("frogs blissfully floating on their backs in the pool", "static"),
 "Where they belong!": ("the frogs at home in the water, content and settled", "slow_push_in"),
 "They croak a joyful tune": ("frogs croaking, throats puffing out, singing together", "slow_push_in"),
 "Beneath the shining moon": ("the frogs in the pool beneath a big glowing moon, soft night light", "tilt_up"),
 "Singing together with a happy swoon!": ("the frogs swaying and singing together, joyful", "slow_pan"),
 "Ribbit ribbit!": ("a frog mid-ribbit, throat ballooning out round", "slow_push_in"),
 "Yum yum! Bugs in the air": ("frogs snapping at little bugs floating in the air", "static"),
 "Snapping snacks without a care": ("frogs flicking tongues at drifting bugs, carefree", "slow_pan"),
 "Glug glug! A bellyful treat": ("a frog with a round, full, happy belly", "slow_push_in"),
 "Swimming 'round with sticky feet!": ("frogs paddling around on webbed sticky feet", "slow_pan"),
 "Splish splash! They leap and play": ("frogs leaping and playing, splashing in the pool", "static"),
 "Ribbit ribbit! Night and day!": ("frogs singing out, throats puffed, day turning to starry night", "slow_pan"),
 "Yum yum! Glug glug!": ("a frog munching then bubbling under, quick and playful", "static"),
 "They hop and hug": ("two speckled frogs hopping together and hugging", "slow_push_in"),
 "Splish splash! In the bubbly bath": ("frogs splashing in a bubbly froth of pool water", "static"),
 "Ribbit ribbit! Hear them laugh!": ("frogs laughing and ribbiting together", "slow_push_in"),
 "No more logs just poolside cheer": ("the frog troupe cheering happily around the poolside", "slow_pan"),
 "Froggies singing loud and clear:": ("the whole troupe of speckled frogs singing out together", "slow_push_in"),
 "Yum yum! Glug glug! Splish splash! Yum yum! Ribbit ribbit!":
   ("a joyful finale — all the speckled frogs together munching, splashing and singing the refrain", "slow_pan"),
}
ACT = {norm(k): v for k, v in ACT.items()}

STYLE_SUFFIX = ("tactile needle-felt / craft-diorama children's-storybook style, speckled cream-and-brown "
  "felt frogs on a mossy log over a still reflective pool, oversized felt mushrooms, flowers and berries, "
  "soft painterly bokeh background, warm naturalistic woodland light, shallow depth of field, 16:9, "
  "no text, no captions, no lettering, no watermark")

for b in bs["beats"]:
    act, cam = ACT.get(norm(b["lyric_text"]),
                       ("the speckled felt frogs on the mossy log by the pool", "static"))
    b["subject"] = "frogs"; b["camera"] = cam
    src = b.get("chosen_still")
    img = (f"Image-to-image from the source still ({src}), preserving the needle-felt speckled frogs, "
           f"the mossy log and the pool diorama: {act}.")
    b["prompt_mode"] = "image-to-image"
    b["image_prompt"] = img
    b["storyboard_prompts"] = [img]
    b["video_prompt"] = (f"{act}. {cam.replace('_',' ')}; gentle stop-motion-style motion only; "
                         f"land the key moment early and hold so it cuts cleanly to the beat; "
                         f"duration {b['duration_s']}s. Style: {STYLE_SUFFIX}.")

m = bs["metadata"]
m["aspect_ratio"] = "16:9"
m["style_preset"] = "speckled-frogs-felt-diorama"
m["style_suffix"] = STYLE_SUFFIX
m["style_bible"] = {
  "visual_style": "tactile needle-felt / craft-diorama children's-storybook scene; speckled cream-and-brown "
    "felt frogs on a mossy log over a still reflective pool, in a whimsical woodland of oversized felt "
    "mushrooms, flowers and berries; soft painterly bokeh",
  "color_palette": "cream and speckled brown, mossy green, warm woodland reds and golds, soft blue water",
  "lighting_style": "warm soft naturalistic daylight; gentle moonlit blue for the night beats",
}
m["subjects"] = [{
  "name": "Frogs", "subject_key": "frogs", "driver": "described",
  "look": "a troupe of speckled cream-and-brown needle-felt frogs with dark spots and round eyes; the "
          "count thins from five to none across the verses, then the pool fills with happy frogs.",
}]
m["generation"] = {
  "still_source": "existing video frames (lyric-match)", "video_model": "minimax_hailuo (image-to-video)",
  "duration_request_s": 10,
  "rule": "each beat is image-to-video from chosen_still at 16:9; request 10s then cut to duration_s.",
}
m["counts"] = {"beats": len(bs["beats"])}

json.dump(bs, open("beat_sheet.json", "w"), ensure_ascii=False, indent=2)
prev = 0
for b in bs["beats"]:
    assert b["start_frame"] == prev; prev = b["end_frame"]
    assert b["image_prompt"] and b["video_prompt"] and b["chosen_still"]
assert prev == m["duration_frames"]
mapped = sum(1 for b in bs["beats"] if norm(b["lyric_text"]) in ACT)
print(f"finalized {len(bs['beats'])} beats | aspect 16:9 | contiguous OK | "
      f"max dur {max(b['duration_s'] for b in bs['beats'])}s")
print(f"lyric-specific actions matched: {mapped}/{len(bs['beats'])}")
