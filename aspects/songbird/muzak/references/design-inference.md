# Design inference — deriving the look from the song

muzak does not wait for a human to hand it a palette. It **infers** a design from
the audio and lyrics, because design decisions aren't arbitrary — they're responses
to musical and semantic signals. Bright timbre wants cool color. A compressed master
can't support a strobing flash without looking incoherent. Fast lyrics physically
can't animate character-by-character. These are rules, and the `design` phase applies
them to produce `design.json`, the brief that skins the build.

Two kinds of decision live here, and they're handled differently:

- **Mechanical / safety decisions are computed and constrained** by
  `scripts/infer_design.py` — caps, easing, allowed animation styles, visualizer
  form, a starting palette, section registers. The model must not loosen these.
- **Semantic decisions are reasoned by you** in the `design` phase — the visual
  concept, the dominant metaphor, section notes, negative space, the proof-of-concept
  moment, and palette refinement *within* the chosen temperature. These need judgment
  about what the song is *about*; no table can supply them.

So the flow is: run `infer_design.py` to get the constrained skeleton, then fill the
null/semantic fields by reading the lyrics — never overriding a computed cap.

## The signals (from `beat_data.json.features` + `lyrics.json.density`)

| Signal | Field | What it drives |
|---|---|---|
| Brightness (spectral centroid, 0..1) | `features.brightness` | color **temperature** + visualizer **form** |
| Mode (major/minor) + confidence | `features.mode`, `features.mode_confidence` | weak warm/cool **bias** on the palette |
| Dynamic range (dB) | `features.dynamic_range_db` | **caps** on beat-flash opacity + scale pulse |
| Tempo | `bpm` | **spring** easing vocabulary |
| Lyric density (words/sec) | `density.density_class` | **allowed** lyric animation styles |
| Section energy | `energyPerFrame` per section | per-section density / saturation / motion |

## The mapping rules (these are what `infer_design.py` encodes)

### Color temperature ← brightness
| Brightness | Palette direction |
|---|---|
| 0.00–0.30 | Warm — amber, ochre, deep red, burgundy |
| 0.30–0.55 | Neutral — mid-purple, dusty rose, slate |
| 0.55–0.75 | Cool/warm mix — teal + gold, indigo + amber |
| 0.75–1.00 | Cool — cyan, ice white, electric blue, mint |

### Mode bias ← mode (weak, gated by confidence ≥ 0.05)
Major nudges ~10–15% **warmer**; minor ~10–15% **cooler**. It's a *modifier on the
brightness bucket, never an override*: a bright minor track stays cool, the bias just
keeps it from going full ice-white. Below the confidence gate, ignore mode entirely.

### Beat-hit caps ← dynamic range (HARD — do not exceed)
| Dynamic range | flash opacity max | scale pulse max | style |
|---|---|---|---|
| < 6 dB (compressed) | **0.15** | **1.08×** | subtle glow pulse, no full-screen flash |
| 6–12 dB (moderate) | **0.25** | **1.15×** | standard flash + ring pulse |
| > 12 dB (wide) | **0.40** | **1.30×** | full dramatic flash, strong spring overshoot |

A flash that punches harder than the audio reads as fake. These caps are written
into `theme.flashMax` / `theme.beatScalePulseMax`; the build must respect them.

### Spring easing ← BPM
| BPM | character | spring hint |
|---|---|---|
| < 80 | heavy, slow | `damping 20, stiffness 80` |
| 80–110 | smooth | `damping 16, stiffness 120` |
| 110–140 | crisp, punchy | `damping 12, stiffness 160` |
| > 140 | snappy, elastic | `damping 8, stiffness 220` |

### Allowed lyric animation ← density (HARD compatibility)
| Density (w/s) | Allowed styles | Exit |
|---|---|---|
| sparse < 1.5 | character-spring, word-spring (bounce) | slow fade / scale-out |
| moderate 1.5–2.5 | word-by-word, wipe reveal | slide / fade |
| dense 2.5–3.5 | line-wipe, instant + fade | hard cut / fast fade |
| rapid > 3.5 | instant, opacity only | instant cut |

`lyric_animation_style` MUST be in `allowed_animation_styles`. Choosing
character-spring on a dense track means lines never finish animating before they
must leave — it's not a taste call, it's a timing impossibility.

### Visualizer form ← brightness
| Brightness | Form |
|---|---|
| 0.00–0.35 | horizontal bars, bottom-anchored, warm gradient |
| 0.35–0.65 | circular ring, 48–64 bars, mixed-temperature gradient |
| 0.65–1.00 | waveform path + thin bar ring, cool gradient, glow-heavy |

## The semantic pass (you, in the `design` phase)

After `infer_design.py` writes the skeleton, read the **lyrics** and fill the nulls.
Every choice must trace to something concrete — a feature value or a specific lyric
line — not to a default aesthetic.

1. **`visual_concept`** — one sentence: what is this video about, visually?
2. **`visual_metaphor`** — one dominant idea (a *metaphor*, not an aesthetic), plus
   how to express it in Remotion and which lyric lines anchor it. Examples:
   isolation → negative space, single centered element; transformation → morphing
   shapes, color shift across sections; connection → converging particles, expanding
   rings; memory → grain texture, desaturated warm highlights; technology → geometric
   grids, monospace type.
3. **Section `notes`** — rename the generic `section_N` labels to verse/chorus/drop/etc.
   from the lyric tags, and say what makes each section visually distinct.
4. **`negative_space_strategy`**, **`proof_of_concept_note`** — where the frame stays
   intentionally empty, and which 8–10s chorus moment best proves the look at peak state.
5. **Palette refinement** — adjust hexes *within* the temperature bucket for taste;
   apply the mode bias. Do not jump buckets and do not use unconsidered colors.

## Constraints (carry these into `build`)

- Every design decision traces to a feature value or a lyric line.
- Do **not** default to synthwave / vaporwave / lo-fi unless the features support it.
- No placeholder colors; all hexes aesthetically considered.
- `section_registers` cover the whole duration with no gaps.
- `lyric_animation_style` ∈ `allowed_animation_styles`.
- `beat_flash_opacity_max` ≤ the dynamic-range cap. Never raise it for drama.

## When a human design doc exists

A hand-written `design/[slug].md` outranks the inferred brief — see the precedence
chain in `default-look.md`. In that case, treat `infer_design.py`'s output as a
*reference* (it still computes the safety caps worth honoring) but let the human doc
drive palette, type, and metaphor. The inference exists to give a strong, defensible
starting point — not to overrule a person who knows exactly what they want.

## Explainer-mode note (bears-doodles / cajal handoff)

If muzak is ever pointed at narration instead of a song, the dominant timing signal
is the **vocal/script rhythm**, not the beat grid: run the density analysis on the
*script*, set `readable_hold_frames` conservatively (reading needs more time than a
hook), and treat sentence boundaries as candidate `<Sequence>` cuts. Beat-sync then
only flavors transitions and background reactivity.
