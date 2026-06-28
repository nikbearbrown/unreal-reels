# Songbird — music & lyric videos

The music-video aspect. Turns **mastered audio + lyrics** into a beat-synced video — performance
shots, lyric/karaoke captions, and audiogram motion graphics — then hands off to the shared engine.

## What's different from the base engine

- **Music is the master clock, not narration.** Beat timing comes from an offline beat/onset
  analysis of the actual track (librosa), and lyrics are force-aligned to the vocal so captions
  hit on the sung word.
- **Captions + audiogram are the spine;** generated stills/clips are the garnish, dropped only
  where a moment needs them.
- **Look** leans on the audiogram/karaoke presets rather than `cinematic-netflix`.

## Authoring → `beat_sheet.json`

Lyrics → key moments/verses → per-beat scene prompts, with beat timing from the track. Then the
shared stages take over: references → storyboard → video → overlay (the overlay here is the
karaoke + waveform Remotion layer).

## Source skills to fold in

From the existing work: **`muzak`** (analyze_audio, align_lyrics / forced alignment,
infer_design, the Remotion music-video templates) and **`muzak-overlay`** (lay karaoke lyrics +
audiogram over an existing finished video). These provide the beat analysis, forced alignment,
and the Remotion caption/waveform layer.

> _Mapping to confirm/adjust:_ Bear to decide exactly which `muzak` scripts move into the shared
> `scripts/` (audio analysis, alignment) vs. stay Songbird-specific (audiogram look, lyric layer).

## Publish convention

Songbird videos publish as early-stage tests: titles include the test tag, descriptions lead with
"this is ONE STEP, not the finished video," and end with the channel/playlist links. Each song ships
in three forms — YouTube (full), Substack note (short), LinkedIn (process framing).
