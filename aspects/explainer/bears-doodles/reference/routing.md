# Tool Routing & Cost

Per beat, decide the render path from the `render` field in `beat_sheet.json`.

## Manim vs. doodle

- **`render: manim`** — precise math: exact curves, boundary conditions, labeled axes, equations, energy levels, geometry that must be correct. Rendered locally, free, pixel-precise, white background. This is the default for quantum-mechanics diagram beats.
- **`render: doodle`** — intuition, metaphor, characters, loose sketches (a sun drawing itself in, a wolf, a balance scale). Goes through the image→video doodle path below.

A single video mixes both. Manim frames can also be **exported as PNGs and fed to
the doodle path** ("doodlize") when you want the precise geometry in napkin-art
register — Nano Banana preserves the geometry while restyling.

## Doodle path — image then animate

### 1. Generate the still (start/end frames)

| Beat content | Tool | Why |
|---|---|---|
| Character / abstract metaphor | **Midjourney** + Bear's Doodles profile suffix (see style.md) | House style, character consistency via profile ID |
| Geometry-critical (from an existing diagram) | **Nano Banana 2** via Higgsfield MCP, with the diagram as image reference | Preserves orbital lobes / curves / energy levels while applying doodle look |
| Plain text / equation still | `gpt_image_2` via Higgsfield, or Manim `MathTex` | Clean typeset |

Nano Banana doodlize prompt (URL first, then description, then style):
```
[IMAGE_URL], [geometry description], flat vector art, thick black lines,
white background, bold lines, simple details, black and white,
napkin art doodle style, Handwritten TEXT
```
GitHub Pages serves companion diagrams (raw.githubusercontent.com blocks hotlinking; use Pages):
`https://nikbearbrown.github.io/<repo>/images/companion-<name>.png`

### 2. Animate (stroke-by-stroke)

| Need | Tool | Access |
|---|---|---|
| **Preserve doodle look + start/end frame interpolation** | **Wan 2.7** | WaveSpeedAI REST (`/api/v3/alibaba/wan-2.7/image-to-video`) — primary |
| Preserve doodle, no interpolation | Higgsfield Sketch-to-Video (Sora 2), **preserve** mode | Higgsfield MCP |
| Photoreal presenter (Soul ID) | `cinematic_studio_video` / `kling3_0` + Soul ID UUID | Higgsfield MCP |

**"Photorealizes"** = the model turns the doodle into a photo, keeping geometry but
destroying the sketch look. Kling 3.0 / Seedance do this to sketch start-frames —
**wrong** for Bear's Doodles. Use Wan 2.7 (preserve) for sketch accumulation beats.

The MinutePhysics accumulation pattern in practice: start frame = scene without the
new element, end frame = scene with it. Prompt describes only the new element
"appears stroke by stroke … no hand visible". Static camera. The accumulation *is*
the animation — nothing else moves.

### 3. Persist assets

Midjourney CDN URLs expire. After the human picks a frame, upload it to Higgsfield
(`higgsfield upload --file ...` → UUID) and store the **UUID** in the beat record.
Never put an expiring CDN URL in `beat_sheet.json`.

## Phase gates (cost control)

1. Script approved (free).
2. Beat sheet approved (free).
3. Audio generated (~$0.02/clip) — durations confirmed.
4. Start/end frames generated + approved (Nano Banana ~$0.07, Midjourney cheap) — iterate freely here, it's cheap.
5. Video generated **one shot at a time**, approve before queuing the next. AI video is generate-10-pick-1; 10 × $0.50 ≈ $5/beat on Wan via WaveSpeedAI.

Never queue video blind. Iterate on the cheap stages first.

## Cost

Do not quote dollar figures. The user's accounts carry ample credits (millions of
ElevenLabs characters, thousands of generator credits), so cost is not a gating
concern and should not appear in the beat-sheet summary. Manim beats render free
locally. If a real budget question ever comes up, ask the user for their actual
plan/rates rather than inventing numbers — never fabricate pricing.

When the **AICR B200 cluster** is online, the doodle-animation step can point at a
local ComfyUI endpoint (`http://127.0.0.1:8188/prompt`) instead of a hosted API —
same start/end/prompt inputs, nothing else in the pipeline changes.
