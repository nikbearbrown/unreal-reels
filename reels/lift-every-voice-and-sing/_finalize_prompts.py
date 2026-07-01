#!/usr/bin/env python3
"""Finalize each beat's storyboard prompt by pairing the ACTUAL chosen source
frame (what I viewed) with the beat's lyric line. The source frame is the
image-to-image INPUT; the prompt preserves its subject + composition and pushes
expression/light toward the lyric, in the unified Mayfield King grade. Also
corrects subject tags to match what the chosen frame really shows."""
import json

bs = json.load(open("beat_sheet.json"))

# beat_id -> (subject, frame_description, lyric_direction)
P = {
 "B01": ("singer",
   "the young Black singer in profile in a warm sunlit studio, city skyline in the window behind him, short cropped hair, blue striped shirt",
   "first light catches his face like a lantern at dawn; calm, gathering the first breath to sing; warm amber glow and a soft flare"),
 "B02": ("archive",
   "a high-contrast black-and-white portrait of an older bearded Black man, eyes lowered, lit by a single hard source against deep black",
   "he holds something precious and unspoken within, like a seed about to rise; quiet gravity, a held breath; chiaroscuro"),
 "B03": ("singer",
   "the singer at a vintage studio microphone, blue shirt, mid-phrase, recording gear around him, warm color",
   "full-voiced, head lifting into the note as the room rings; warm light, gentle lens flare"),
 "B04": ("archive",
   "a black-and-white early-1900s studio portrait of two young Black men in pinstripe suits and ties, one standing close behind the other",
   "two voices joined in harmony, dignified and composed; soft period light, silver tones, fine grain"),
 "B05": ("archive",
   "a sepia early-1900s portrait of two elegantly dressed Black men in three-piece suits, one seated, one standing adjusting his tie",
   "quiet pride rising, chins lifting toward a listening sky; warm sepia, period grain"),
 "B06": ("archive",
   "a sepia portrait of two well-dressed Black men in an early-1900s parlor, one seated and one standing",
   "the steady dignity of people who built something lasting, stone by stone; warm sepia stillness"),
 "B07": ("archive",
   "a black-and-white civil-rights rally: a woman in cat-eye sunglasses singing into a vintage microphone, fist raised, a man beside her holding a portrait placard, crowd behind",
   "song as testimony forged by the dark past; raised fist, open mouth, fierce faith; hard documentary daylight"),
 "B08": ("archive",
   "a tighter black-and-white frame of the same woman singing passionately into the silver microphone at the rally, white shawl",
   "her face full of the hope of a new day; bright hard daylight, motion in the moment"),
 "B09": ("archive",
   "a tender dramatic black-and-white portrait of an elderly Black person with soft grey curls and wide expressive eyes, hand resting on the cheek, knit sweater, against black",
   "the wonder of one who lived to face a rising sun and a morning just begun; a soft light dawning across the face"),
 "B10": ("archive",
   "a black-and-white portrait of a Black photographer holding a large vintage press camera, moustache, direct gaze",
   "the witness who records the march forward; steady, resolute, unblinking; hard key light"),
 "B11": ("archive",
   "a warm black-and-white street close-up of an older Black man in a flat cap, smiling with deep creased joy",
   "a face that has walked the stony road and still smiles; weathered warmth, soft street light"),
 "B12": ("archive",
   "a black-and-white shot of a muscular shirtless Black man shadow-boxing on a porch, his fist blurred in motion",
   "the body that took the bitter rod and fought to keep its light; tension, motion, defiance; hard daylight"),
 "B13": ("archive",
   "a sepia period music room: a double bass and empty chairs, a figure in a plumed bicorne hat reading sheet music at a stand, a pianist seated",
   "the steady rehearsal of endurance, music carrying weary feet onward; soft sepia, grain"),
 "B14": ("archive",
   "a luminous black-and-white glamour portrait of a Black woman with a full afro and a radiant open smile",
   "the realized dream made flesh, the joy elders imagined in the night; soft glowing light"),
 "B15": ("archive",
   "a black-and-white early-1900s scene of two men in suits, one gently offering something into the other's open cupped hands",
   "an offering passed between generations along a way watered with tears; solemn period light"),
 "B16": ("archive",
   "an intense black-and-white portrait of a Black man in a pinstripe suit, hand to his chin, brooding, in a brick alley",
   "the weight of the slaughtered years held in a steady jaw; deep shadow, hard side light"),
 "B17": ("archive",
   "a dramatic black-and-white portrait of an elder with a white halo of hair and a goatee, glasses, against pure black",
   "emerging out of the gloomy past, the face beginning to lift toward light; chiaroscuro against black"),
 "B18": ("singer",
   "an overhead studio shot of the singer leaning forward in a blue shirt, surrounded by guitars, a microphone and an old radio, warm color",
   "a gleam of warm light breaking across him from above at last; relief and arrival; gentle flare"),
 "B19": ("archive",
   "a sepia-toned early-1900s portrait of a Black woman in a beaded gown with a warm smile and opera-singer poise",
   "grace carried through long weary years; warm period light, soft grain"),
 "B20": ("archive",
   "a sepia period music room, a figure in a plumed bicorne hat reading at a music stand, a pianist, a double bass",
   "music made in quiet, silent sorrow, heads bowed to the page; hushed sepia light"),
 "B21": ("archive",
   "the same sepia music-room tableau, the plumed figure at the stand and the pianist seated",
   "the long accompaniment of faith that carried us thus far; warm sepia, stillness"),
 "B22": ("archive",
   "a black-and-white Frederick Douglass-style portrait of a dignified Black elder with white hair and beard in a formal coat",
   "the patriarch who led by might into the light; strong key light building on the face"),
 "B23": ("archive",
   "a black-and-white portrait of a young Black man in a black turtleneck in a doorway, protest posters behind him, 1960s",
   "the next generation keeping its steps in the path; quiet prayerful resolve, soft window light"),
 "B24": ("archive",
   "the same young Black man in the black turtleneck in the doorway, posters behind",
   "rooted, refusing to let his feet stray from the ground; steady level gaze, flat daylight"),
 "B25": ("archive",
   "a black-and-white Sojourner Truth-style portrait of an older Black woman in a shawl and white cap, seated, 1800s",
   "the very embodiment of truth held firm; plain hard light, period stillness"),
 "B26": ("archive",
   "a sepia portrait of two men in top hats and tails beside a grand piano, elegant, early 1900s",
   "worldly finery and the wine of the world, yet a call not to forget; warm sepia, refined light"),
 "B27": ("archive",
   "the same sepia top-hat-and-tails duo at the grand piano",
   "drawn close around the music, kept near; intimate sepia glow"),
 "B28": ("archive",
   "a dramatic black-and-white portrait of the white-haired elder against black, steady unflinching gaze",
   "standing unbowed, shadowed beneath a sheltering hand; single hard light against black"),
 "B29": ("archive",
   "the same white-haired elder portrait, fierce and faithful",
   "unwavering faith, true to God, in the eyes; hard key light, deep black"),
 "B30": ("singer",
   "a warm color close-up of the singer at the vintage microphone, earnest, studio light",
   "devotion, true to his native land and people; warm gold light, steady gaze"),
 "B31": ("singer",
   "a color close-up of the singer, blue shirt, mid-line at the microphone",
   "the light rising and holding on his face like a dawn that refuses to dim; growing warm glow, flare blooming"),
 "B32": ("singer",
   "a color close-up of the singer, mouth open on the final note at the microphone",
   "the last triumphant note as victory calls his name; full voice, radiant gold, the look held"),
}

SUFFIX = bs["metadata"]["style_suffix"]
for b in bs["beats"]:
    subject, desc, direction = P[b["beat_id"]]
    b["subject"] = subject
    src = b["source_still"]
    primary = (f"Image-to-image from the source frame ({src}), preserving its subject, "
               f"pose and composition: {desc}. {direction}.")
    alt = (f"Same subject and framing as the source frame, regraded for the reel: {desc}; "
           f"push the expression and light toward — {direction}.")
    b["prompt_mode"] = "image-to-image"
    b["image_prompt"] = primary
    b["storyboard_prompts"] = [primary, alt]
    b["video_prompt"] = (f"{desc}. {b['camera'].replace('_',' ')}; subtle natural motion only; "
                         f"land the key moment early and hold so it cuts cleanly to the beat; "
                         f"duration {b['duration_s']}s. Style: {SUFFIX}.")

bs["metadata"]["counts"] = {
    "beats": len(bs["beats"]),
    "singer_beats": sum(1 for b in bs["beats"] if b["subject"] == "singer"),
    "archive_beats": sum(1 for b in bs["beats"] if b["subject"] == "archive"),
}
bs["metadata"]["generation"]["rule"] = (
    "Each beat is image-to-image: the source_still (a sharp frame from the original "
    "Mayfield King video, chosen within the beat's time window) is the input; image_prompt "
    "preserves its subject/composition and pushes expression + light toward the lyric, in the "
    "shared style_suffix grade. Generate images_per_beat candidates, pick chosen_still at the gate. "
    "All beats <= 6s -> clip_tier 6.")

json.dump(bs, open("beat_sheet.json", "w"), ensure_ascii=False, indent=2)
print("finalized prompts for", len(bs["beats"]), "beats")
print("counts:", bs["metadata"]["counts"])
print("\nspot check:")
for b in bs["beats"][:2] + bs["beats"][6:8] + bs["beats"][-1:]:
    print(f"\n{b['beat_id']} [{b['subject']}] frame {b['source_frame_number']} | {b['lyric_text']}")
    print("  ", b["image_prompt"][:155], "...")
