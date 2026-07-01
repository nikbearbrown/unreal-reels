#!/usr/bin/env python3
"""Turn the solo 9:16 Cookie stills into 16:9 Cookie+Grover DUET prompts.

Each beat keeps its preserved vertical Cookie still (now in stills/916/) as the
image-to-image base, extends it to a wide 16:9 frame, and adds Grover as a second
felt puppet beside Cookie. Only ONE plays (Cookie keeps the banjo from the source
still); Grover is the non-playing partner, reacting to the lyric. Grover's side
alternates beat to beat so the duet doesn't feel static. The generated 16:9 image
overwrites stills/<beat_id>_v1.png; the 9:16 original is preserved in stills/916/.
"""
import json, re

bs = json.load(open("beat_sheet.json"))
def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())

# Cookie's lyric-tied action (he is the player, carried from the source still)
COOKIE = {
 "On Sesame Street,where the cookies crumble,": "busking on the clay street corner, strumming",
 "Cookie Monster sings,his voice a humble": "head tilted, humble open-mouthed note, strumming",
 "Five-note wonder,a simple song,": "plucking a simple five-note phrase, wool notes drifting up",
 "Where cookies and melodies belong.": "cozy and content over the banjo, a bowl of cookies at his feet",
 '"C is for cookie," that\'s good enough for me,': "taking a big happy bite of a cookie mid-strum, crumbs flying",
 "Five little notes in a cookie melody.": "strumming brightly, cookie-shaped felt notes floating",
 "A monster's voice,deep and true,": "eyes closed, head tipped back, belting a deep soulful note",
 "Singing the blues,'bout cookies too.": "bluesy slouch over the banjo, wistful and sweet",
 "No ballads here,just crunchy treats,": "bouncing upbeat, crumbs flying, lively strum",
 "On the stage,he feels the beats.": "tapping a felt foot, leaning into the rhythm",
 "Grover might join,a duet they'd try,": "turning with a delighted grin to welcome his bandmate, strumming",
 "Sounds like a cookie-filled battle cry.": "banjo raised high, mouth wide in a playful whoop",
 "Bill Sherman laughs,says it's quite a show,": "grinning wide, performing showman-style",
 "With growls and gargles,the tunes they flow.": "a comical open-mouthed growl mid-strum",
 '"Arrggh" they sing,not always on key,': "an exaggerated off-key wail, banjo akimbo",
 "But in Cookie's world,it's perfect harmony.": "blissful, eyes closed, gentle harmonious strum",
 "So if you wander down Sesame Street,": "busking down the clay street, mid-strum",
 "And a singing monster you happen to meet.": "greeting the camera warmly, banjo in paw",
 "Remember it's Cookie,with his charming range,": "a charming wink mid-note",
 "Five notes of joy,and none would change.": "a satisfied final strum, content",
}
# Grover's lyric-tied reaction (the partner, NOT playing)
GROVER = {
 "On Sesame Street,where the cookies crumble,": "ambling into frame to join in",
 "Cookie Monster sings,his voice a humble": "leaning in to listen, a paw cupped to his ear",
 "Five-note wonder,a simple song,": "nodding along, counting the notes on his fingers",
 "Where cookies and melodies belong.": "happily holding up a cookie",
 '"C is for cookie," that\'s good enough for me,': "clapping with delight",
 "Five little notes in a cookie melody.": "bouncing to the tune",
 "A monster's voice,deep and true,": "swaying with eyes closed, harmonizing",
 "Singing the blues,'bout cookies too.": "snapping along in a bluesy sway",
 "No ballads here,just crunchy treats,": "munching a cookie, crumbs flying",
 "On the stage,he feels the beats.": "stomping a felt foot to the beat",
 "Grover might join,a duet they'd try,": "stepping right up beside Cookie, thrilled to join the duet",
 "Sounds like a cookie-filled battle cry.": "throwing both lanky arms up in a playful cheer",
 "Bill Sherman laughs,says it's quite a show,": "laughing and gesturing grandly to the audience",
 "With growls and gargles,the tunes they flow.": "gargling a comic note, tongue out",
 '"Arrggh" they sing,not always on key,': "wailing an off-key 'arrgh', wobbly googly eyes spinning",
 "But in Cookie's world,it's perfect harmony.": "blissful, swaying in perfect harmony",
 "So if you wander down Sesame Street,": "waving a big hello down the street",
 "And a singing monster you happen to meet.": "tipping an imaginary hat in friendly greeting",
 "Remember it's Cookie,with his charming range,": "a charmed grin, a paw over his heart",
 "Five notes of joy,and none would change.": "beaming as little felt notes float between them",
}
COOKIE = {norm(k): v for k, v in COOKIE.items()}
GROVER = {norm(k): v for k, v in GROVER.items()}

GROVER_LOOK = ("Grover — a lanky teal-blue needle-felt monster with a long magenta nose and big "
               "wobbly googly eyes, same handmade claymation folk style as Cookie")
STYLE_SUFFIX = ("tactile needle-felt / claymation stop-motion folk-art duet, two felt puppets sharing "
  "one warm clay diorama set, handmade wool textures, ochre and cobalt palette, soft cozy storybook "
  "light, shallow depth of field, wide 16:9, no text, no captions, no lettering, no watermark")

for i, b in enumerate(bs["beats"]):
    k = norm(b["lyric_text"])
    cookie_act = COOKIE.get(k, "strumming his banjo, googly eyes bright")
    grover_act = GROVER.get(k, "swaying along beside him")
    cookie_side, grover_side = ("left", "right") if i % 2 == 0 else ("right", "left")
    src = f"stills/916/{b['beat_id']}_v1.png"
    b["duet_source_916"] = src
    b["grover_side"] = grover_side
    b["subject"] = "duet"
    img = (f"Image-to-image: take the vertical still ({src}) of the blue felt Cookie monster and "
           f"extend it into a wide 16:9 frame. Keep Cookie exactly as-is on the {cookie_side}, "
           f"still the only one playing — {cookie_act}. On the {grover_side}, add {GROVER_LOOK}, "
           f"{grover_act}, not playing. A two-puppet felt duet on one clay diorama set, consistent lighting.")
    b["prompt_mode"] = "image-to-image (outpaint to 16:9 + add Grover)"
    b["image_prompt"] = img
    b["storyboard_prompts"] = [img]
    b["video_prompt"] = (f"A felt-puppet duet: on the {cookie_side} Cookie is {cookie_act}; on the "
                         f"{grover_side} Grover is {grover_act}. {b['camera'].replace('_',' ')}; gentle "
                         f"stop-motion motion only; only Cookie plays; land the key moment early and hold "
                         f"so it cuts cleanly to the beat; duration {b['duration_s']}s. Style: {STYLE_SUFFIX}.")

m = bs["metadata"]
m["aspect_ratio"] = "16:9"
m["style_preset"] = "cookie-grover-felt-duet"
m["style_suffix"] = STYLE_SUFFIX
m["style_bible"]["visual_style"] = ("tactile needle-felt / claymation stop-motion folk-art DUET; a blue "
  "googly-eyed Cookie-Monster-style felt creature busking with a banjo, joined by Grover, a lanky teal-blue "
  "felt monster with a long magenta nose; two puppets per frame, one clay diorama set")
m["subjects"] = [
  {"name": "Cookie", "subject_key": "cookie", "driver": "described",
   "look": "blue googly-eyed needle-felt Cookie-Monster-style creature in an ochre felt vest, plays the banjo; the player in every shot."},
  {"name": "Grover", "subject_key": "grover", "driver": "described",
   "look": "lanky teal-blue needle-felt monster, long magenta nose, big wobbly googly eyes; the non-playing duet partner, added when widening to 16:9."},
]
m["generation"] = {
  "still_source": "16:9 outpaint from the preserved 9:16 Cookie stills in stills/916/, adding Grover",
  "image_model": "nano_banana_2_shots or flux_2 (image-to-image, aspect 16:9)",
  "video_model": "minimax_hailuo (image-to-video)", "duration_request_s": 10,
  "rule": "every 16:9 shot is a Cookie+Grover duet; only Cookie plays; Grover's side alternates per beat. "
          "9:16 originals kept in stills/916/ for the vertical cut.",
}
m["counts"] = {"beats": len(bs["beats"]), "duet_beats": len(bs["beats"])}

json.dump(bs, open("beat_sheet.json", "w"), ensure_ascii=False, indent=2)
print("duetized", len(bs["beats"]), "beats -> 16:9 | aspect", m["aspect_ratio"])
print("Grover sides:", "".join("L" if b["grover_side"]=="left" else "R" for b in bs["beats"]))
print("sample B11:", bs["beats"][10]["image_prompt"][:200])
