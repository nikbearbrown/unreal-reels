# Visualizer & lyric look options (incl. the audiogram)

All look choices flow through one `theme` object (`src/theme.ts`), generated from
`design.json`. The mechanical components read only from it. This file documents the
options so `build` and a design doc can set them by name.

## Visualizer types (`theme.visualizerType`)

| Value | Look | Component |
|---|---|---|
| **`audiogram`** | dense oscilloscope waveform across the **whole** video — the captioned-audiogram reference look. Global: overrides the per-section map. | `Waveform` |
| `waveform` | smooth thin waveform line | `Waveform` |
| `spectrum` / `bars` | mirrored FFT bar chart, bottom band | `SpectrumBars` |
| `ring` / `hybrid` | currently fall back to spectrum (no dedicated component) | `SpectrumBars` |

Lyric-forward songs default to **`audiogram`** (set by `infer_design.py` when the
song has lyrics and isn't rapid-fire). In `MusicVideo.tsx`, `audiogram` short-circuits
`SectionVisualizer` to render `Waveform` on every section.

### Audiogram tuning (`AudioVisualizer.tsx` → `Waveform`)

| Knob | Default | Effect |
|---|---|---|
| `numberOfSamples` | 512 | trace density — higher = finer/busier |
| `windowInSeconds` | 2.5 | seconds of audio shown at once — bigger = more oscillation across the width. A tiny window (1/fps) gives a flat sliver — don't. |
| `normalize` | true | scale each window to fill the band; false keeps quiet passages quieter |
| `mid` | `height * 0.88` | baseline position — **higher number = lower on screen** |
| `amp` | `height * 0.09` | band height — bigger = taller peaks |
| `theme.waveformStroke` | 3 | line thickness |
| `theme.accent` | — | line color |

Lyric vertical position: `LyricLayer.tsx` outer `AbsoluteFill` `paddingBottom`
(default `8%`; smaller = lower). The lyrics sit ON the waveform band near the bottom.

## Lyric styles (`theme.lyricStyle`)

| Value | Behavior |
|---|---|
| **`karaoke`** | word highlight: current word brightest (1.0), upcoming dim (0.5), sung (0.85). Needs real per-word timings from `align_lyrics_audio.py`; falls back to an even stagger without them. |
| `per-word-pop`, `word-by-word` | same code path as karaoke |
| `fade-beat` | whole line fades with a beat-scale pop |
| `line-wipe`, `instant` | line-level, for dense/rapid lyrics |

Highlight opacities live in `LyricLayer.tsx` (`wordOpacity`). Chorus/hook lines
(detected from the `[Chorus]` tag) auto-render at `hookSize` in `accent2`.

## Beat reactions

- `theme.flashColor` / `flashMax` — beat flash (cap from dynamic range; never raise for drama).
- `theme.beatScalePulseMax` — spring "thud" scale cap.
- `theme.springDamping` / `springStiffness` / `easingCharacter` — feel, from BPM.

## Ink-on-white look (stick figures)

For stick-figure videos (white frames, black ink) use the **ink** look: white
background, black audiogram + black text. Generate it with
`infer_design.py --look ink`, which sets `background:#FFFFFF`, `accent:#141414`,
`textColor:#141414`, `flashColor:#141414` (low `flashMax`), `bgSat:0`, and
`bgLumRange:[96,99]`. The `Background` component reads `theme.bgLumRange`, so the
energy gradient stays near-white instead of dark. Pair with the `stick-figures`
skill: cast every beat `none`, and pass the stick-figure style lock as `--hf-style`.

## Background gradient

`theme.bgHueRange` + `bgSat` drive the energy-reactive background behind everything
(shows through where no per-beat media exists).

## Precedence

A hand-written `design/[slug].md` outranks the inferred `design.json`, which outranks
`default-look.md`. Whatever wins is flattened into `theme.ts`; never raise a computed
cap (`flashMax`, `beatScalePulseMax`) — those are fidelity guarantees from the audio.
