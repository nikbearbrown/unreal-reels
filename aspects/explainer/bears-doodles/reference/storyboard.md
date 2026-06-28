# Storyboard Rules — Script & Beat Sheet

Condensed from the full production guide. These are the laws the `script` and
`beats` commands obey.

## Format: MinutePhysics, not RSA Animate

No visible hand. Script written first. White background. Hard cuts between scenes.
Tight narration-to-beat sync. (A drawing hand causes anatomical warping in AI
video and is banned — see negative prompt.)

## One sentence = one visual beat

Every narration sentence introduces exactly **one** new visual element. The
grammatical **subject** of the sentence is the thing being drawn. Test: can you
draw exactly one thing while this sentence is spoken? If "two" or "nothing
specific" — rewrite.

## Script rules

- **Word count:** 6–20 words/sentence. Target 10–16. Hard max 20 (split anything longer).
- **Active voice only.** No "it can be shown that…".
- **No equations read symbol-by-symbol.** Speak the concept; show the notation as a handwritten label.
- **Narrative arc:** Hook (no visual) → Accumulation (the bulk) → Reveal → Implication. The proportions hold whether the video runs 1 minute or 5; the arc scales, the order doesn't change.
- **Length:** size to the concept, not to a clock. "One-minute" is the *style*, not a duration — 1 min is the floor, 2–3 is typical, up to 5 for genuinely multi-stage ideas. A tight idea ≈ 8–12 sentences (~1–2 min); most concepts 20–40 (~2–3 min); complex ones up to ~70 (~5 min). One sentence = one beat throughout. Teaching the concept clearly always outranks hitting a target length: never pad to fill time, never rush or amputate a step to beat a clock.
- **First sentence** creates curiosity and needs no visual. First element appears on sentence 2.

### Failure modes → fix

| Failure | Fix |
|---|---|
| Too abstract ("The concept of…") | Make a physical entity the subject |
| Too dense (multiple elements in one sentence) | Split into beats |
| Wrong order (effect before cause) | Reorder: cause → effect |
| Passive ("It can be shown…") | Rewrite active |

## Beat types

| Type | Duration | Rule | When |
|---|---|---|---|
| `ACCUMULATE` | 3–8s | `START(n)=END(n-1)`; draw one new element | Default |
| `CUT` | 3–8s | Reset to white `#FFFFFF`; draw first element of new scene | >5–6 elements, or new sub-topic |
| `HOLD` | 1–3s | Static scene; narration continues; **no video render** | Emphasis pause / final line |
| `ZOOM` | 2–4s | Push into existing element; no new drawing | Detail focus |

Default to ACCUMULATE. HOLD/ZOOM are rare.

## State invariant (most error-prone part)

```
START_FRAME(n) = END_FRAME(n-1)      — for every ACCUMULATE beat
END_FRAME(n)   = START_FRAME(n) + exactly one new element
On CUT: state resets to empty white.
```

An accumulated-state error at beat 3 propagates through every later beat. Track
`accumulated_scene_state` as an explicit list per beat.

## Scene capacity

Max **5–6** elements per scene before a CUT. Count everything: each shape, each
label, each arrow = one element.

## Prompt templates

**Positive (image/video):**
```
A minimalist, clean black line art illustration on a flat, solid white background
(#FFFFFF). The black lines representing [NEW_ELEMENT] draw themselves stroke-by-stroke
onto the canvas with a smooth, consistent vector-style growth. All existing black line
elements, including [ACCUMULATED_STATE], remain perfectly static, sharp, and locked in
position. The camera remains fixed. No hand, no pencil, no drawing tool is visible.
```

**Negative (apply to every image + video generation):**
```
hand, fingers, arm, pencil, pen, marker, stylus, writing tool, shadow, paper texture,
yellowing, gradient, photorealistic, 3D render, gray shading, color, brush, eraser,
artifacts, distortion, camera movement, zoom, pan, wiggle, blur
```

"Lines draw themselves" (positive framing) makes a hand impossible; negative-only
constraints are less reliable. "Remain perfectly static, sharp, and locked in
position" fights drift.

## Audio-first timing

Generate ElevenLabs TTS before any render. Use the real MP3 duration (mutagen) as
the render length. Add a 0.5s silence buffer at the end of each clip so working
memory can consolidate. `generate_audio.py` handles both.

## Math symbol normalization (before TTS)

ψ→"psi", ℏ→"h-bar", |ψ|²→"psi squared", ∫→"integral of", →→"goes to",
≥→"greater than or equal to", Δx→"delta x", Δp→"delta p", ∞→"infinity",
E₀→"E sub zero", n=1→"n equals one". Keep both the display `narration_text`
(with symbols, used for captions) and `tts_normalized_text` (spoken form).

## Accumulation order (draw framework → subjects → relationships → annotations)

| Concept | Order |
|---|---|
| Potential well | walls → floor → wavefunction → labels |
| Energy levels | lowest level → up → labels |
| Wavefunction | axes → curve → labels |
| Probability density | axes → curve → shaded region → boundary labels |
| Hydrogen orbitals | central point → lobes → labels |
| Tunneling | left wall → right wall → incident wave → reflection → decay inside → transmitted wave → P=0 label |

Never draw an annotation before the thing it annotates, or an effect before its cause.

## Quality checklist (run before presenting a beat sheet)

**Script:** every sentence 6–20 words · one new element each · subject = drawn
thing · active voice · no equations read aloud · hook needs no visual · cause
before effect.

**Beat sheet:** ACCUMULATE start = previous end · no scene >5–6 elements before
CUT · every video prompt has "lines draw themselves, no hand visible, no drawing
hand" · negative prompt on every generation · HOLD beats have no element and no
render · beat IDs sequential.

**The clarity test (run at any length):** audio-only — the narration is a self-contained argument
without visuals; visual-only — a STEM-literate viewer can follow the arc on mute.
If either breaks, the script or beat sheet is wrong.
