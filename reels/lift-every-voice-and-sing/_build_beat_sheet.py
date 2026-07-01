#!/usr/bin/env python3
"""Assemble lift-every-voice-and-sing/beat_sheet.json from beat_data.json (real
librosa beat grid = the master clock) + lyrics.json (beat-grid seed timing) +
authored scene prompts.

Style bible is DERIVED FROM the existing "Lift Every Voice and Sing | Mayfield
King" music video in this folder: a young Black singer in a warm sun-flared
studio, intercut with high-contrast black-and-white and sepia portraits of Black
ancestors, elders, and everyday people (Frederick Douglass-era figures, a grand
piano and top hats, double-exposure street montages). The reel mirrors that
intercut: the SINGER carries the "lift every voice" hook and the dawn/victory
turns; ARCHIVE portraits carry the dark-past / stony-road / weary-years lines.

One beat = one lyric line = one scene. Beats tile the song contiguously (no gaps),
so every line ends exactly where the next begins; the last beat runs to song end.
Lyric TEXT is verbatim (it drives the caption overlay); image prompts are visual
scenes only and never contain the lyric words.
"""
import json

bd = json.load(open("beat_data.json"))
ly = json.load(open("lyrics.json"))
fps = bd["fps"]
lines = {l["index"]: l for l in ly["lines"]}

# Reference frames extracted from the source music video, used to lock the look
# per subject (the still generator can use these as reference plates).
SRC = "Lift Every Voice and Sing _ Mayfield King_frame_%06d.png"
REF_SINGER_PROFILE = SRC % 5     # tight warm profile, window light + flare
REF_SINGER_OVERHEAD = SRC % 90   # overhead studio, vintage mic + guitars
REF_PORTRAIT_WOMAN = SRC % 70    # B&W afro-haired woman, chiaroscuro
REF_PORTRAIT_DOUGLASS = SRC % 110  # Frederick Douglass-style B&W elder
REF_PORTRAIT_ELDER = SRC % 150   # white-afro elder, dramatic B&W against black
REF_SEPIA_PIANO = SRC % 140      # sepia grand piano + top-hatted figures
REF_DOUBLE_EXPOSURE = SRC % 35   # double-exposure street montage, monochrome

# Per-line: (subject, reference_frame, camera, image_prompt, alt_prompt)
# subject "singer" = the contemporary artist; "archive" = monochrome/sepia ancestor imagery.
SCENES = {
 0:("singer", REF_SINGER_PROFILE, "slow_push_in",
    "tight profile of a young Black male singer in a warm sunlit studio, a single lantern-warm window flare behind him, deep amber and shadow, shallow depth of field",
    "close-up of a hand cupping a small warm flame like a lantern at dawn, sun-flare, amber and black, cinematic"),
 1:("singer", REF_SINGER_PROFILE, "static",
    "extreme close-up of the singer's lips and breath as he begins to sing, warm rim light, a fine mote of dust catching the sun like a drifting seed, charcoal background",
    "macro of a single seed held between dark fingers, backlit by golden window light, shallow focus"),
 2:("singer", REF_SINGER_OVERHEAD, "slow_push_in",
    "the singer head tilted back mid-note at a vintage studio microphone, warm low light, guitars and an old radio softly out of focus behind, lens flare",
    "overhead studio shot of the singer at the mic, arms loose, warm wood floor, sunlit"),
 3:("archive", REF_SEPIA_PIANO, "slow_pan",
    "sepia archival tableau of a Black gospel choir in close harmony around a grand piano, soft period daylight, early-1900s dress, grain",
    "sepia close-up of hands on a grand piano keyboard, dust and warm light, vintage"),
 4:("singer", REF_SINGER_PROFILE, "tilt_up",
    "the singer lifting his face toward a bright window, eyes rising, blown-out warm sky beyond the glass, hopeful golden light, shallow focus",
    "low angle of the singer against a luminous sunrise window, silhouette edged in gold"),
 5:("archive", REF_DOUBLE_EXPOSURE, "slow_push_in",
    "high-contrast monochrome of weathered Black hands stacking stone, a long low wall vanishing toward the sea, overcast silver light, documentary grain",
    "sepia wide of figures building a stone wall along a shore, a grey sea of mist behind them"),
 6:("archive", REF_PORTRAIT_DOUGLASS, "slow_push_in",
    "dramatic black-and-white studio portrait of a dignified Black elder, Frederick Douglass-era, single-source chiaroscuro against pure black, silver highlights, deep faith in the eyes",
    "B&W portrait of an old Black man, weathered face, hard side light, black background"),
 7:("singer", REF_SINGER_OVERHEAD, "static",
    "the singer in morning light, a faint smile of hope, warm amber studio glow, guitar and radio behind, soft flare",
    "the singer by the window as new daylight floods the room, dust in the sunbeam"),
 8:("singer", REF_SINGER_PROFILE, "tilt_up",
    "silhouette of the singer turning to face a rising sun through the studio window, intense golden backlight and flare, his form rimmed in fire-gold",
    "the singer's profile against a blazing sunrise, warm lens flare, just-begun morning"),
 9:("archive", REF_DOUBLE_EXPOSURE, "slow_pan",
    "high-contrast monochrome of a column of marchers moving forward on a road, banners blurred, hard daylight, dust, determined stride, documentary",
    "B&W double-exposure of marching feet and a distant horizon, grain, forward motion"),
 10:("archive", REF_DOUBLE_EXPOSURE, "slow_push_in",
    "sepia low-angle of a long stony road climbing into haze, a lone barefoot traveller small upon it, harsh flat light, dust, grain",
    "monochrome close-up of bare feet on sharp stones, dust, hard shadow"),
 11:("archive", REF_PORTRAIT_ELDER, "static",
    "stark black-and-white portrait of a defiant Black elder with a white afro, brow furrowed against an unseen weight, single hard key light, black void background",
    "B&W portrait, an old face refusing to break, light fighting deep shadow"),
 12:("archive", REF_DOUBLE_EXPOSURE, "slow_pan",
    "monochrome of weary feet walking in steady rhythm along a dim path, motion-blur of stride, low underexposed light, grain",
    "B&W of legs and worn shoes marching to a steady beat, hard side light"),
 13:("archive", REF_PORTRAIT_ELDER, "slow_push_in",
    "tender black-and-white portrait of an aged Black elder asleep or dreaming, lit by one warm sliver against deep night-black, the face of someone who dreamed this day",
    "B&W close-up of an elder's closed eyes, a single soft catchlight in the dark"),
 14:("archive", REF_PORTRAIT_WOMAN, "static",
    "intimate black-and-white close-up of a Black woman's face, a single tear catching the light, chiaroscuro against black, immense quiet dignity",
    "B&W close-up of brimming eyes, one bright catchlight, deep shadow"),
 15:("archive", REF_SEPIA_PIANO, "slow_push_in",
    "sombre sepia interior, a single candle burning beside an old hymnal, the slaughtered years felt in the dark around it, grain, low warm flame",
    "sepia still life of a candle and worn hymnbook in heavy shadow, vintage"),
 16:("archive", REF_DOUBLE_EXPOSURE, "tilt_up",
    "monochrome silhouette stepping out of a black doorway toward a faint grey opening, the gloomy past behind, a sliver of light ahead, grain",
    "B&W of a figure emerging from darkness into a thin shaft of light"),
 17:("singer", REF_SINGER_PROFILE, "slow_push_in",
    "the singer standing where a single gleam of light breaks through cloud onto his face, warm and silver mixing, the first relief after long dark, shallow focus",
    "a beam of sun breaking through grey cloud onto an upturned face, gold against slate"),
 18:("archive", REF_PORTRAIT_DOUGLASS, "static",
    "sepia close-up of an old Black man's clasped weathered hands in prayer, soft period window light, decades of weary years in the skin, grain",
    "B&W portrait, an elder's bowed head, hands folded, single soft light"),
 19:("archive", REF_PORTRAIT_WOMAN, "slow_push_in",
    "black-and-white close-up of a Black woman's face in silent grief, no sound, one slow tear, hard chiaroscuro against black",
    "B&W of downcast eyes glistening, deep shadow, a held breath"),
 20:("archive", REF_DOUBLE_EXPOSURE, "slow_pan",
    "tender monochrome double-exposure of generations layered together — an elder, a mother, a child — carried along one continuous road, grain, soft overlap",
    "B&W double-exposure of three generations of faces dissolving into one another"),
 21:("singer", REF_SINGER_PROFILE, "tilt_up",
    "the singer rising into a flood of warm window light, led upward, gold flare filling the frame, eyes open toward the brightness",
    "low angle of the singer lifting into a blaze of golden light, arms beginning to open"),
 22:("archive", REF_SEPIA_PIANO, "static",
    "sepia tableau of a congregation's clasped hands in a row of pews, heads bowed in prayer, soft church daylight, early-1900s, grain",
    "sepia of many hands joined in prayer along a wooden pew, warm dim light"),
 23:("archive", REF_DOUBLE_EXPOSURE, "slow_push_in",
    "monochrome low shot of bare feet planted firm on dark ground, refusing to stray, hard shadow, grain, quiet resolve",
    "B&W of feet rooted on the earth, a faint path leading away, deep contrast"),
 24:("singer", REF_SINGER_PROFILE, "static",
    "earnest close-up of the singer, eyes steady and true to the camera, warm key light against shadow, a vow in the gaze, shallow focus",
    "close-up of the singer's open, honest face, warm rim light, black background"),
 25:("archive", REF_PORTRAIT_ELDER, "slow_push_in",
    "stark black-and-white portrait, a face turned half from temptation's glow, resisting the wine of the world, hard side light against black",
    "B&W portrait, eyes turned from a warm distracting light, holding firm in shadow"),
 26:("singer", REF_SINGER_OVERHEAD, "static",
    "the singer with eyes closed, drawing near, hands lightly to his chest, warm intimate studio glow, soft flare, very shallow focus",
    "close-up of the singer, eyes shut, leaning toward an unseen warmth, amber light"),
 27:("archive", REF_DOUBLE_EXPOSURE, "slow_pan",
    "monochrome of figures standing together beneath a great shaft of light reaching down like a sheltering hand, small and unbowed, grain",
    "B&W of a gathered crowd under one vast beam of light, silhouettes, awe"),
 28:("archive", REF_PORTRAIT_DOUGLASS, "static",
    "reverent black-and-white portrait of a Black elder, face lifted, true and unwavering, single warm key against black, silver highlights",
    "B&W portrait, an upturned faithful face, light from above, deep shadow"),
 29:("archive", REF_SEPIA_PIANO, "slow_pan",
    "sepia wide of a warm horizon over open land at golden hour, a lone figure facing the homeland light, period grain, hopeful stillness",
    "sepia landscape, golden fields under a low sun, a single small figure facing it"),
 30:("singer", REF_SINGER_PROFILE, "tilt_up",
    "the singer turning fully into a brilliant sunrise that floods the window, gold and white light, lens flare blooming, a dawn that will not dim",
    "the singer's face bathed in full sunrise, radiant gold flare, eyes wide with hope"),
 31:("singer", REF_SINGER_OVERHEAD, "slow_push_in",
    "triumphant final shot of the singer at the mic bathed in warm gold light, head high as victory calls, flare and glow filling the room, the look held",
    "the singer lit in full golden triumph at the studio mic, radiant, the last note ringing"),
}

# --- contiguous tiling: each beat ends where the next begins ----------------
order = sorted(SCENES.keys())
starts = {i: lines[i]["startFrame"] for i in order}
beats = []
for n, i in enumerate(order):
    start = 0 if n == 0 else starts[i]
    end = starts[order[n + 1]] if n + 1 < len(order) else bd["durationInFrames"]
    dur = round((end - start) / fps, 2)
    subject, ref, cam, pa, pb = SCENES[i]
    section = next((s["label"] for s in bd["sections"]
                    if s["startFrame"] <= start < s["endFrame"]), bd["sections"][-1]["label"])
    bid = f"B{n+1:02d}"
    beats.append({
        "beat_id": bid,
        "start_s": round(start / fps, 2), "end_s": round(end / fps, 2),
        "start_frame": start, "end_frame": end, "duration_s": dur,
        "section": section,
        "kind": "vocal",
        "subject": subject,
        "line_indices": [i],
        "lyric_text": lines[i]["text"],
        "reference_frame": ref,
        "image_prompt": pa,
        "storyboard_prompts": [pa, pb],
        "camera": cam,
        "video_prompt": f"{pa}. {cam.replace('_', ' ')}; subtle natural motion only; "
                        f"land the key moment early and hold so it cuts cleanly to the beat; duration {dur}s.",
        "clip_tier": 6 if dur <= 6 else 10,
        "images_per_beat": 2,
        "storyboard_candidates": [],
        "chosen_still": None,
        "raw_clip": None,
        "video_file": None,
    })

sheet = {
  "metadata": {
    "slug": "lift-every-voice-and-sing",
    "title": "Lift Every Voice and Sing",
    "artist": "Mayfield King",
    "aspect_ratio": "16:9", "fps": fps,
    "duration_s": bd["durationInSeconds"], "duration_frames": bd["durationInFrames"],
    "bpm": bd["bpm"], "key": f'{bd["features"]["key"]} {bd["features"]["mode"]}',
    "audio_file": "LifteveryvoiceandsingMayfieldGDMusinique-mastered.wav",
    "lyrics_file": "song-06.txt",
    "beat_data": "beat_data.json", "lyrics_timing": "lyrics.json",
    "source_video": "Lift Every Voice and Sing _ Mayfield King.mp4",
    "timing_source": "librosa beat grid (master clock) + beat-grid seed lyric timing "
                     "(faster-whisper forced alignment unavailable in this sandbox — "
                     "review/nudge anchors at the overlay gate)",
    "language": "en",
    "style_preset": "mayfield-king-soul-portrait",
    "style_bible": {
      "visual_style": "soulful contemporary music-video portraiture intercut with archival-style "
        "monochrome and sepia portraits, derived from the Mayfield King 'Lift Every Voice and Sing' "
        "video: a young Black singer in a warm sun-flared studio crossfading with high-contrast "
        "black-and-white and sepia portraits of Black elders, ancestors and everyday people; "
        "cinematic shallow depth of field, dramatic single-source chiaroscuro, gentle double-exposure transitions",
      "color_palette": "warm amber and gold studio light with lens flare; rich charcoal-black and "
        "silver monochrome; sepia archival browns",
      "lighting_style": "warm low window light and golden lens flare in the studio; hard single-source "
        "chiaroscuro against pure black for the portraits; soft sepia daylight for the period tableaux"
    },
    "style_suffix": "in the style of the Mayfield King 'Lift Every Voice and Sing' video — soulful "
      "cinematic portrait look, warm amber studio with lens flare intercut with high-contrast B&W and "
      "sepia archival portraits, shallow depth of field, film grain, no text, no captions, no watermark",
    "subjects": [
      {"name": "Singer", "subject_key": "singer", "driver": "described",
       "reference_frames": [REF_SINGER_PROFILE, REF_SINGER_OVERHEAD],
       "look": "a young Black male singer with short cropped hair in a blue button-up shirt, in a warm "
               "sunlit studio with a vintage microphone, acoustic guitars and an old radio; lit by golden "
               "window light and lens flare. Carries the hook and the dawn/victory beats."},
      {"name": "Archive", "subject_key": "archive", "driver": "described",
       "reference_frames": [REF_PORTRAIT_DOUGLASS, REF_PORTRAIT_WOMAN, REF_PORTRAIT_ELDER,
                            REF_SEPIA_PIANO, REF_DOUBLE_EXPOSURE],
       "look": "high-contrast black-and-white and sepia portraits and tableaux of Black ancestors, "
               "elders and everyday people — Frederick Douglass-era dignitaries, a grand piano and "
               "top hats, congregations, marchers, a stony road, double-exposure street montages. "
               "Carries the dark-past / stony-road / weary-years beats."}
    ],
    "generation": {
      "still_backend": "TBD (Higgsfield Soul / FLUX.2 or nano_banana); use the listed reference_frame "
                       "per beat to match the source-video look",
      "images_per_beat": 2, "video_model": "minimax (image-to-video)",
      "rule": "image_prompt is a visual scene only — never the lyric text; the singer and archive looks "
              "come from the source-video reference frames. Cut each generated clip to its beat duration "
              "(all beats <= 6s -> clip_tier 6)."
    },
    "counts": {
      "beats": len(beats),
      "singer_beats": sum(1 for b in beats if b["subject"] == "singer"),
      "archive_beats": sum(1 for b in beats if b["subject"] == "archive"),
    },
    "design_signals": {
      "brightness": bd["features"]["brightness"],
      "dynamic_range_db": bd["features"]["dynamic_range_db"],
      "density": ly.get("density", {}),
      "note": "dark/warm brightness + moderate dynamics support the amber-and-black palette; "
              "moderate lyric density (~1.5 w/s) allows word-by-word caption animation."
    }
  },
  "beats": beats
}

json.dump(sheet, open("beat_sheet.json", "w"), ensure_ascii=False, indent=2)

# --- verification -----------------------------------------------------------
print("wrote beat_sheet.json | beats:", len(beats),
      "| singer:", sheet["metadata"]["counts"]["singer_beats"],
      "| archive:", sheet["metadata"]["counts"]["archive_beats"])
print("max beat dur:", max(b["duration_s"] for b in beats), "s",
      "| min:", min(b["duration_s"] for b in beats), "s")
assert all(b["duration_s"] <= 10.0 for b in beats), "a beat exceeds the 10s clip cap"
over6 = [(b["beat_id"], b["duration_s"]) for b in beats if b["duration_s"] > 6.05]
print("beats over 6s (would need clip_tier 10):", over6 or "none")
# contiguous coverage 0..durationInFrames
prev = 0
for b in beats:
    assert b["start_frame"] == prev, f"gap/overlap at {b['beat_id']}: {prev} vs {b['start_frame']}"
    prev = b["end_frame"]
assert prev == bd["durationInFrames"], f"last beat ends at {prev}, song is {bd['durationInFrames']}"
print(f"coverage 0..{bd['durationInFrames']} frames contiguous: OK")
# every beat carries a lyric line and a reference frame
assert all(b["lyric_text"] and b["reference_frame"] for b in beats)
print("every beat has lyric_text + reference_frame: OK")
