#!/usr/bin/env python3
"""Finalize c-is-for-cookie beats: derive the style bible from the source
"C is for Cookie | Sing-a-Long" frames (a single needle-felt / claymation blue
Cookie-Monster-style creature busking with a banjo, folk-blues Americana), set a
single recurring subject, and write a per-beat image_prompt/video_prompt that
pairs each beat's chosen still with its lyric line. Image-to-image: keep the felt
monster + clay diorama; push pose/expression toward the lyric. Source frames are
vertical, so aspect is 9:16."""
import json, re

bs = json.load(open("beat_sheet.json"))

def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())

# distinct lyric line -> (action/expression tied to the words, camera move)
ACT = {
 "On Sesame Street,where the cookies crumble,":
   ("an establishing shot of the felt monster busking on a cozy clay Sesame-Street corner, a few cookies crumbling at his feet", "slow_push_in"),
 "Cookie Monster sings,his voice a humble":
   ("the monster tilting his shaggy blue head, mouth gently open in a humble opening note, googly eyes soft", "static"),
 "Five-note wonder,a simple song,":
   ("the monster strumming a simple chord on the felt banjo, a few little wool music-notes drifting up", "slow_push_in"),
 "Where cookies and melodies belong.":
   ("the monster cozy and content, a clay bowl of cookies at his feet, warm storybook glow", "static"),
 '"C is for cookie," that\'s good enough for me,':
   ("the monster taking a big happy bite of a cookie mid-strum, googly eyes wide with delight, crumbs flying", "slow_push_in"),
 "Five little notes in a cookie melody.":
   ("the monster strumming brightly, five little cookie-shaped felt notes floating from the banjo", "slow_pan"),
 "A monster's voice,deep and true,":
   ("the monster eyes closed, head tipped back, belting a deep soulful note, chest puffed", "slow_push_in"),
 "Singing the blues,'bout cookies too.":
   ("the monster in a bluesy slouch over the banjo, wistful and sweet, warm low light", "static"),
 "No ballads here,just crunchy treats,":
   ("the monster bouncing upbeat, crumbs and cookie bits flying, lively", "slow_pan"),
 "On the stage,he feels the beats.":
   ("the monster tapping a felt foot, leaning into the rhythm, banjo swinging", "static"),
 "Grover might join,a duet they'd try,":
   ("the monster glancing hopefully to the side as if inviting a bandmate, banjo held out", "slow_pan"),
 "Sounds like a cookie-filled battle cry.":
   ("the monster mouth wide in a playful whoop, banjo raised high, full of gusto", "slow_push_in"),
 "Bill Sherman laughs,says it's quite a show,":
   ("the monster grinning wide and performing to an unseen delighted audience, showman energy", "static"),
 "With growls and gargles,the tunes they flow.":
   ("the monster in a comical open-mouthed growl, googly eyes crossed, mid-gargle", "slow_push_in"),
 '"Arrggh" they sing,not always on key,':
   ("the monster letting out an exaggerated off-key wail, googly eyes askew, banjo akimbo", "static"),
 "But in Cookie's world,it's perfect harmony.":
   ("the monster blissful, eyes closed, a contented smile, strumming gently, everything in harmony", "slow_push_in"),
 "So if you wander down Sesame Street,":
   ("a wider establishing shot of the clay Sesame-Street corner, the little monster busking down the way", "slow_pan"),
 "And a singing monster you happen to meet.":
   ("the monster greeting the camera warmly, a friendly little wave with one felt paw, banjo in the other", "slow_push_in"),
 "Remember it's Cookie,with his charming range,":
   ("the monster giving a charming wink mid-note, head cocked, endearing", "static"),
 "Five notes of joy,and none would change.":
   ("the monster joyful and settled, little cookie-notes floating, a satisfied final strum", "slow_push_in"),
}
ACT = {norm(k): v for k, v in ACT.items()}

STYLE_SUFFIX = ("tactile needle-felt / claymation stop-motion folk-art, a blue googly-eyed "
  "Cookie-Monster-style felt creature busking with a banjo, handmade wool-felt textures, warm clay "
  "diorama set, ochre and cobalt palette, soft cozy storybook light, shallow depth of field, vertical "
  "9:16, no text, no captions, no lettering, no watermark")

for b in bs["beats"]:
    act, cam = ACT.get(norm(b["lyric_text"]),
                       ("the felt blue monster strumming his banjo, googly eyes bright", "static"))
    b["subject"] = "cookie"
    b["camera"] = cam
    src = b.get("chosen_still")
    primary = (f"Image-to-image from the source still ({src}), preserving the felt blue "
               f"banjo-playing Cookie monster, his ochre felt vest and the clay diorama set: {act}.")
    b["prompt_mode"] = "image-to-image"
    b["image_prompt"] = primary
    b["storyboard_prompts"] = [primary]
    b["video_prompt"] = (f"{act}. {cam.replace('_',' ')}; gentle stop-motion-style motion only; "
                         f"land the key moment early and hold so it cuts cleanly to the beat; "
                         f"duration {b['duration_s']}s. Style: {STYLE_SUFFIX}.")

m = bs["metadata"]
m["aspect_ratio"] = "9:16"
m["style_preset"] = "cookie-felt-folk"
m["style_bible"] = {
  "visual_style": "tactile needle-felt / claymation stop-motion folk-art; a single blue googly-eyed "
    "Cookie-Monster-style felt creature busking with a banjo; handmade wool-felt textures, clay diorama "
    "sets, shallow depth of field",
  "color_palette": "denim and cobalt-blue felt, warm ochre and terracotta, cream, muted clay backdrops",
  "lighting_style": "soft warm diffuse studio light, gentle shadows, cozy storybook glow",
}
m["style_suffix"] = STYLE_SUFFIX
m["subjects"] = [{
  "name": "Cookie", "subject_key": "cookie", "driver": "described",
  "look": "a blue googly-eyed needle-felt Cookie-Monster-style creature in a patterned ochre felt vest, "
          "playing a banjo, often a cookie in its mouth and a bowl of cookies at its feet; the only "
          "recurring character.",
}]
m["generation"] = {
  "still_source": "existing vertical video frames (lyric-match)",
  "video_model": "minimax_hailuo (image-to-video)", "duration_request_s": 10,
  "rule": "each beat is image-to-video from chosen_still at 9:16; request 10s then cut to duration_s.",
}
m["counts"] = {"beats": len(bs["beats"]), "cookie_beats": len(bs["beats"])}

json.dump(bs, open("beat_sheet.json", "w"), ensure_ascii=False, indent=2)

# verify
prev = 0
for b in bs["beats"]:
    assert b["start_frame"] == prev; prev = b["end_frame"]
    assert b["image_prompt"] and b["video_prompt"] and b["chosen_still"]
assert prev == m["duration_frames"]
print("finalized", len(bs["beats"]), "beats | aspect", m["aspect_ratio"],
      "| max dur", max(b["duration_s"] for b in bs["beats"]), "s | contiguous OK")
mapped = sum(1 for b in bs["beats"] if norm(b["lyric_text"]) in ACT)
print(f"lyric-specific actions matched: {mapped}/{len(bs['beats'])}")
