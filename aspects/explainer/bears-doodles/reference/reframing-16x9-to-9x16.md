# Reframing 16:9 ↔ 9:16 for Bear's Notes — research + encodable ruleset

A cited research brief on how to intelligently reformat motion graphics and vector
animations between landscape and portrait, and a concrete deterministic ruleset for
the Bear's Notes layout engine. The driving failure this fixes: naively shrinking
landscape content to the narrower portrait width leaves ~70% of the frame empty.

---

## TL;DR — the verdict

There are **two paradigms**, and we must not confuse them:

1. **Content-aware REFRAME** — crop and pan *filmed footage* to follow a tracked subject (Premiere Auto Reframe, Final Cut Smart Conform, DaVinci Smart Reframe, Google AutoFlip). Signal = saliency/face/object detection. Output = a moving crop window.
2. **Layout REFLOW** — re-arrange *discrete authored elements* (panels, labels, captions) into a new composition (After Effects/Premiere MOGRT pinning, Figma/Auto Layout constraints, responsive data-viz). Output = a different layout, not a crop.

**Bear's Notes scenes are authored vector graphics, so we are 100% in the REFLOW track.** We never crop-to-subject. The correct operations are: **scale content to fill the constrained dimension (the width, in portrait), then distribute it down the abundant axis (the height), and where two panels can't both fit, stack them (serialize) or split into sequential beats.** "Shrink to fit width and leave it floating in the middle" is the documented anti-pattern.

---

## 1. The professional tools split cleanly along the same two paradigms

The reframe tools are crop-and-pan engines driven by saliency/detection; the graphics tools are constraint/pin engines. Google **AutoFlip** is the only fully-open algorithm and is the reference design for the reframe track: histogram-delta shot detection → buffer the whole shot → run face/object detectors on a downsampled stream → fuse boxes with per-class weights and a `is_required` hard-constraint flag → pick stationary/pan/track by one motion threshold → fit an L2-smoothed low-degree-polynomial camera path → **and when required regions are "too spread out" to fit the crop, abandon cropping and letterbox/pad** ([Google Research](https://research.google/blog/autoflip-an-open-source-framework-for-intelligent-video-reframing/), [MediaPipe config](https://github.com/google/mediapipe/blob/master/docs/solutions/autoflip.md)). Premiere Auto Reframe (Adobe Sensei) keyframes clip Position to keep the main action in frame ([Adobe](https://helpx.adobe.com/premiere/desktop/add-video-effects/commonly-used-effects/auto-reframe-overview.html)); Final Cut Smart Conform picks **one static crop per clip and does not track** ([Apple](https://support.apple.com/guide/final-cut-pro/adjust-framing-with-smart-conform-ver26664d93f/mac)); DaVinci Smart Reframe tracks via its Neural Engine ([Blackmagic](https://www.blackmagicdesign.com/products/davinciresolve/whatsnew)).

The graphics tools are what matter for us. After Effects/Premiere **Responsive Design – Position** uses "Pin To" parenting so layers re-anchor to frame edges or to each other when the aspect ratio changes; **Responsive Design – Time** protects intro/outro regions from time-stretch ([Adobe Premiere](https://helpx.adobe.com/premiere-pro/using/responsive-design-features.html), [Adobe AE](https://helpx.adobe.com/after-effects/using/responsive-design.html)). Cavalry and Jitter reflow authored elements with constraint/layout systems, not pixel saliency ([Cavalry](https://docs.cavalry.scenegroup.co/nodes/shapes/forge-dynamics/constraints/)). The decisive cross-tool fact: **AutoFlip's own fallback — when the must-keep regions don't fit, stop cropping and change strategy — is exactly our trigger to stack/split instead of shrink.**

---

## 2. The reflow action menu (this is our decision space)

The authoritative source is Kim, Moritz, Hoffswell et al., *Design Patterns and Trade-Offs in Responsive Visualization for Communication* (EuroVis 2021), built on a corpus of **378 large-screen↔small-screen visualization pairs** ([ar5iv](https://ar5iv.labs.arxiv.org/html/2104.07724), [arXiv](https://arxiv.org/abs/2104.07724)), extending Hoffswell et al.'s 231-pair corpus ([CHI 2020](https://jhoffswell.github.io/website/resources/papers/2020-ResponsiveVisualization-CHI.pdf)). It defines exactly **five actions** for adapting a layout to a smaller/narrower screen:

- **Recompose** — change what exists: remove, add, replace, aggregate.
- **Rescale** — change size (e.g. to a narrower aspect ratio).
- **Transpose** — change orientation. **"Serialize" = place side-by-side elements in vertical serial order** — and it was *one of the most frequent strategies in the corpus*.
- **Reposition** — move targets (externalize/internalize, fix/fluid, relocate).
- **Compensate** — recover lost info (numbering, toggling) when something was removed.

The governing objective is the **density–message trade-off**: keep info-per-pixel manageable while preserving the takeaway; dropping non-critical information is acceptable, even good, if the message survives ([ar5iv](https://ar5iv.labs.arxiv.org/html/2104.07724)). Authors reach for cheapest-first: **rescale → serialize → recompose**, because the cheap ones automate well ([ar5iv](https://ar5iv.labs.arxiv.org/html/2104.07724)). Critically, **simple proportional rescaling is a known failure when it causes overplotting, sub-perceptual mark sizes, or overflow past one screen** — those are the triggers to *restructure* instead of *resize* ([ar5iv](https://ar5iv.labs.arxiv.org/html/2104.07724)). And one wide figure can be **split into sequential panels** ("split states into panels for SS views") ([ar5iv](https://ar5iv.labs.arxiv.org/html/2104.07724)). Caveat to encode: serializing costs *co-visibility* — stacked panels can no longer be compared at a glance, so keep must-compare panels together when possible ([ar5iv](https://ar5iv.labs.arxiv.org/html/2104.07724)).

For infographics specifically: default to **vertical orientation**; **stacking order = reading order** (most important first); and **don't reflow one giant image — build from discrete blocks that restack** ([Esri](https://www.esri.com/arcgis-blog/products/bus-analyst/sharing-collaboration/infographic-design-in-business-analyst-best-practices-for-layers-and-display-modes), [NewCity](https://www.insidenewcity.com/responsive-infographics/)). WCAG 1.4.10 makes the same point at the standard level: relocating/restacking content is *not* loss, but **slicing a graphic into stacked pieces makes it unintelligible** — treat each diagram as an *atomic block to reposition*, not to cut internally ([W3C](https://www.w3.org/WAI/WCAG21/Understanding/reflow.html)).

---

## 3. The constraint/anchor system (how to position deterministically)

Figma, iOS Auto Layout, and Android ConstraintLayout agree on the same primitives, which we can adopt directly. Each axis (x and y, independently) gets one anchor behavior:

- **PIN_START / PIN_END** — hold to the near/far edge ([Figma](https://help.figma.com/hc/en-us/articles/360039957734-Apply-constraints-to-define-how-layers-resize)).
- **STRETCH** — pin *both* opposing edges; the element grows/shrinks with the frame ([Figma](https://help.figma.com/hc/en-us/articles/360039957734-Apply-constraints-to-define-how-layers-resize), [Pond5](https://blog.pond5.com/23558-how-to-design-auto-responsive-templates-for-vertical-and-square-videos/)).
- **CENTER** — pin both edges with a **bias ∈ [0,1]** (0.5 = centered); the bias is the deterministic off-center knob ([Android](https://developer.android.com/develop/ui/views/layout/constraint-layout)).
- **SCALE** — express size *and* position as a percentage of the frame's dimensions, so the element keeps the same fractional area in any aspect ratio ([Figma](https://help.figma.com/hc/en-us/articles/360039957734-Apply-constraints-to-define-how-layers-resize)).

Distribution along an axis has three deterministic modes (Android chains): **SPREAD** (equal gaps including the ends), **SPREAD_INSIDE** (equal gaps between only), **PACKED + bias** (grouped, then shifted) ([Android](https://developer.android.com/develop/ui/views/layout/constraint-layout)). This is our anti-dead-band logic. Aspect-locked elements set *one* dimension and derive the other from a ratio — never both ([Android](https://developer.android.com/develop/ui/views/layout/constraint-layout)).

Breakpoints should key on **orientation/aspect ratio, not just width** — switch to a *different layout template* at the portrait threshold rather than scaling the landscape one ([NN/g](https://www.nngroup.com/articles/breakpoints-in-responsive-design/)). The recommended motion-graphics workflow confirms this: author the element against **distinct master frames per AR** (16:9, 1:1, 9:16) and let pin/scale constraints carry it across; full-bleed backgrounds pin to all four edges, content is centered/scaled to a reference ([Pond5](https://blog.pond5.com/23558-how-to-design-auto-responsive-templates-for-vertical-and-square-videos/)).

---

## 4. "Fill the frame" = scale to the constrained dimension, distribute on the abundant one

This is the rule my first attempt violated. It is well-supported as a *derived* rule (see confidence note): the **SCALE constraint sizes content as a fraction of a chosen dimension**, and **safe margins are per-dimension fractions** — so binding content size to the *small* dimension (width, in portrait) prevents short-axis overflow, while the *large* dimension's surplus is absorbed by edge-pins, centering, and distribution ([Figma](https://help.figma.com/hc/en-us/articles/360039957734-Apply-constraints-to-define-how-layers-resize), [eks.tv](https://eks.tv/title-safe-still-matters/)). Stated for motion design: vertical's strength is the extra height — **use the extremes of the frame** for scaled-up typography and stacked supporting elements, not a small centered island ([Mowe](https://mowe.studio/common-video-aspect-ratios/)). Vertical rhythm and negative space are *deliberate quantities* used to distribute elements evenly and avoid dead bands ([Imperavi](https://imperavi.com/books/ui-typography/principles/vertical-rhythm/), [IxDF](https://www.interaction-design.org/literature/topics/negative-space)).

Safe margins: broadcast title-safe = inner 90% (5% margin/side), action-safe = inner 93% under SMPTE ST 2046-1 ([Venera](https://www.veneratech.com/what-is-title-safe-and-why-it-still-matters-in-modern-video-production), [NAB PDF](https://www.nab.org/xert/scitech/pdfs/tv031510.pdf)). Because they're per-dimension fractions, the safe box reshapes correctly across ARs for free — **but broadcast safe ≠ social safe** (a 90% box still sits under the platform UI on a phone) ([eks.tv](https://eks.tv/title-safe-still-matters/)). Use the platform zones below, not SMPTE, for Shorts/Reels/TikTok.

---

## 5. Platform safe zones for 9:16 (1080×1920) — where content must NOT go

UI occludes the **bottom** (captions, handle, CTA, music) and the **right rail** (like/comment/share/profile); the top is lighter. **Only TikTok ships official safe-zone files, and they vary by caption length — there is no fixed pixel rectangle.** All pixel numbers below are from creator/ad-spec guides and disagree by 100–200px; treat as ranges ([TikTok Ads](https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads), [Orson Lord](https://orsonlord.com/articles/free-safe-zone-overlays-for-reels-tiktok-and-shorts), [Kreatli](https://kreatli.com/guides/tiktok-safe-zone)).

| Platform | Top clear | Bottom clear | Right clear | Notes |
|---|---|---|---|---|
| TikTok | ~130–160px | ~480px (caption+CTA+ticker) | ~120–140px | Heaviest right rail; keep faces/text out of right third |
| Instagram Reels | ~250px (14%) | ~480–670px (20–35%) | ~120px | Tightest bottom; design to Reels and it fits Stories ([Meta specs](https://www.tryvizup.com/blog/meta-ad-specs-2026-every-dimension-size-you-need)) |
| YouTube Shorts | ~180–380px | ~350–380px | ~120px (left only ~40–60px) | Lightest UI but **asymmetric** — more margin on the right |

**Universal cross-platform safe box ≈ central 840×1280px**, i.e. avoid the top ~250px, bottom ~480px, and right ~120px ([Orson Lord](https://orsonlord.com/articles/free-safe-zone-overlays-for-reels-tiktok-and-shorts)). Caption placement consensus: central 960px wide, vertically ~Y=1200–1550, clear of the bottom dead zone ([BlitzCut](https://blitzcutai.com/blog/best-caption-placement-short-form-video)). **Direct consequence for us:** our outro channel handle and any running captions must sit in the upper/middle safe band — the very bottom (where I'd normally put a URL) is the worst place on a Short.

---

## 6. Typography for vertical

Scale type **up** in portrait and accept more wrapping, because the column is narrow but tall ([Mowe](https://mowe.studio/common-video-aspect-ratios/)). Concrete targets: minimum burned-in caption size **~48–60px** bold sans-serif on a 1080-wide master ([Rev](https://www.rev.com/blog/best-open-caption-font-sizes-for-videos-on-social-media), [Sleepy Motion](https://sleepymotion.com/blog/captions-styling-motion-graphics-captions-for-impactful-videos-8l6g)). BBC sets subtitle line height to **4.5% of height for 9:16** (≈86px at 1920) vs 8% for 16:9 — the narrower column forces a smaller *relative* size so it fits the width ([BBC](https://bbc.github.io/subtitle-guidelines/), [Clevercast](https://www.clevercast.com/bbc-subtitling-guidelines/)). Line length: body text reads best at **45–75 characters** (66 sweet spot) ([UXPin](https://www.uxpin.com/studio/blog/optimal-line-length-for-readability/), [Baymard](https://baymard.com/blog/line-length-readability)); **captions far shorter — ≤~37 char/line, max 2 lines, 3–7 words** ([BBC](https://bbc.github.io/subtitle-guidelines/), [Opus](https://www.opus.pro/blog/tiktok-caption-subtitle-best-practices)). Contrast: WCAG AA **4.5:1** normal / 3:1 large; prefer white text + dark outline to survive any background ([W3C](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)). When budget forces it, **edit captions down rather than verbatim** to meet the tighter character budget ([Nimdzi](https://www.nimdzi.com/subtitling-vertical-videos-guidelines-where-art-thou/)).

---

## 7. Motion: re-path, disclose down the axis, split when needed

Repositioning elements is not enough — **motion paths must be re-computed against the new edges**, because an arc tuned to the wide frame now starts or ends off-screen or under the UI rail ([Mowe](https://mowe.studio/common-video-aspect-ratios/), [Codrops/GSAP](https://tympanus.net/codrops/2025/12/17/building-responsive-scroll-triggered-curved-path-animations-with-gsap/)). Keep the **entire arc inside the safe band**. Exploit the tall axis with **progressive disclosure** — reveal one stacked panel at a time down the column ([Decision Lab](https://thedecisionlab.com/reference-guide/design/progressive-disclosure), [Mighty Fine](https://mightyfinedesign.co/website-animation-guide/)). And when a wide two-panel tableau simply can't show both side-by-side, **split it into sequential beats** — the vertical analog of shot/reverse-shot — giving each "hero" moment its own full-width vertical frame ([Mowe](https://mowe.studio/common-video-aspect-ratios/), [Nitro](https://www.nitromediagroup.com/optimizing-your-horizontal-content-for-vertical-platforms/)). Top-level principle: **decide both aspect ratios before authoring** — adaptation bolted on after the storyboard always degrades ([Mowe](https://mowe.studio/common-video-aspect-ratios/)).

---

## 7b. Coordinate recompute, motion re-pathing, and the element table (folded-in specifics)

Three practitioner specifics sharpen the rules above. **Provenance caveat:** these come from secondary practitioner write-ups (motion-design blogs, social safe-zone guides), not primary docs — trust the *directions*, treat any specific pixel number as a candidate to confirm on a real device. (A cited "US Patent 5917549" for arc-length reparameterization could not be verified and is treated as unconfirmed.)

**Center recompute is the core bug.** An element at landscape-center `(960, 540)` in 1920×1080 lands at *upper-center* `(960, 540)` in a 1080×1920 canvas — it must be recomputed to the new center `(540, 960)`. In Manim terms: never reuse a landscape y-coordinate in portrait; **recompute every position as a fraction of the new content band**, not as an absolute offset. This is exactly why the first portrait attempt floated content in the upper-middle: it kept landscape-relative y-positions instead of re-deriving them from the portrait band.

**Motion paths distort and change apparent speed.** A horizontal move that crossed 1920px now crosses ~1080px (−44%), so at unchanged timing it *reads slower / less energetic*; and a circular path becomes elliptical under the asymmetric axis scale. So motion is **re-pathed, not translated**: shorten or re-time lateral sweeps, prefer vertical/axial entrances (which align with the portrait scan direction), and keep the whole arc inside the content band. Entrances from the **bottom must be avoided** — that's where platform UI sits and where the eye is *not* primed to look in portrait.

**Element-by-element defaults (portrait):**

| Element (landscape) | Portrait rule |
|---|---|
| Side-by-side panels | Stack top→bottom in reading order; each fills the band width |
| Horizontal bar chart / wide legend | Vertical bars, or sequence the data points; legend stacks |
| Lower-third (name bar near bottom) | Becomes an **upper-third / center overlay** — bottom ~25% is UI dead zone |
| Logo / brand in a corner, small | Move to upper-center, enlarge (corner watermark is illegible on mobile) |
| Long single-line headline | Rewrite line breaks (not word-wrap); shorten; scale up; stagger top→bottom |
| Entrance from left/right/bottom | Prefer entrance from top or center; never resolve key content in the bottom band |
| Background with edge-critical content | Redesign (a center crop loses the horizontal context) |

**Pacing:** short-form rewards a fast hook and front-loaded hierarchy; long landscape intros that build over several seconds and outros that hold should be **tightened** for the Short (the audio is shared, so this is a render/edit choice, not a re-record). Center-aligned beats beat left-aligned in portrait (the eye doesn't reset to a left margin); emphasis via scale-pulse/color reads better than positional movement in the narrow column.

## 8. The Bear's Notes ruleset (deterministic, encodable)

Synthesis into rules for `bn_layout.py`. We are always REFLOW, never crop.

**R0 — Recompute every position from the band, never reuse landscape coordinates.** Positions are expressed as a fraction of the active content band (R6), so the same logical placement resolves to the correct absolute point in either orientation. No landscape y-offset survives into portrait. (§7b center-recompute.)

**R1 — Two layout templates, switched on orientation, not one scaled.** `is_portrait()` selects a portrait composition authored against the 1080×1920 master, not a narrowed copy of the landscape one. (§3 breakpoints; §2 "restructure, don't resize".)

**R2 — Anchor model per element, per axis:** `{PIN_START, PIN_END, STRETCH, CENTER(bias), SCALE(frac, ref_axis)}`. Background/full-bleed → STRETCH both axes. Text/diagram blocks → atomic, positioned by anchors; never cut internally. (§3; WCAG atomic-graphic rule.)

**R3 — Fill the width, distribute the height.** In portrait, size each content block by SCALE bound to **width** (target **88–92% of safe width**), then place blocks down the height with a **SPREAD/SPREAD_INSIDE** distribution so there are no dead bands. This is the specific fix for the floating-island bug. (§4.)

**R4 — Dual-panel → serialize (stack), in reading order.** Side-by-side (landscape) becomes top/bottom (portrait), most-important panel first. Each stacked panel scaled to fill the width. If the two panels must be *compared simultaneously*, keep both on screen (stacked); if not, prefer R5. (§2 serialize + co-visibility caveat.)

**R5 — If stacked panels are still too cramped, split into sequential beats.** Reveal panel A full-width, then transition to panel B full-width (progressive disclosure), reusing the same audio windows. Better one clear thing than two tiny ones. (§2 split-into-panels; §7 beats.)

**R6 — Bear's Notes safe band for portrait** (stricter than SMPTE, driven by §5): usable region **x ∈ ±2.0 of 2.25** (~11% side margin) and **y ∈ [−3.0, +3.4] of ±4.0** — i.e. reserve the **bottom ~25% and top ~12%** for platform UI. Put the brand top, key content in the central band, and **the channel handle/outro in the upper-middle, never flush bottom.** Captions live ~upper-middle, not bottom. (§5.)

**R7 — Type scales up, wraps more.** Portrait captions/labels target the larger *relative* size (min ~48–60px equiv), wrap at ≤~32 characters, ≤2 lines; use `fit_text` bound to safe width. Long landscape captions get **shortened**, not shrunk to illegibility. (§6, density–message trade-off.)

**R8 — Re-path motion to the new frame.** Entry/exit/indicate arcs are recomputed against portrait edges and kept inside the R6 band; never reuse absolute landscape coordinates for motion. (§7.)

**R9 — Cheapest-first when authoring a portrait variant:** try rescale-to-fill (R3) → serialize (R4) → split into beats (R5) → recompose/trim (R7). Stop at the first that preserves the takeaway. (§2 ordering.)

**R10 — Audit both renders.** Run `manim_layout_audit.py` on the portrait render (it's aspect-aware) and additionally check the R6 band, not just the frame edge. A portrait scene passes only if content fills the height (no >~15% contiguous dead band outside intended whitespace) and nothing sits in the bottom/right UI zones.

---

## Confidence & limitations

- **"Scale to the width in portrait" (R3) is a *derived* rule** — strongly implied by the percentage-scale constraint + per-dimension safe margins + the full-bleed-vs-content split, but no single source states it verbatim. Everything else in §3–4 is quote-backed.
- **All 9:16 safe-zone pixel numbers are approximate** and vary by device, caption length, and app version. Only TikTok publishes official files, and even those are variable. Use the ranges in §5 as guidance, verify on a real device.
- **No formal CPL standard exists for vertical captions specifically** — the ≤37-char figure is borrowed from BBC TV and only informally validated for portrait.
- AutoFlip's camera-path objective is described qualitatively by Google (L2 / low-degree polynomial); the closest formal treatment is Grundmann et al.'s L1-optimal camera paths. Not load-bearing for our reflow track.

## Primary sources
- AutoFlip: [Google Research](https://research.google/blog/autoflip-an-open-source-framework-for-intelligent-video-reframing/) · [MediaPipe config](https://github.com/google/mediapipe/blob/master/docs/solutions/autoflip.md)
- Responsive viz (5 actions, density–message): [Kim/Moritz/Hoffswell EuroVis 2021](https://ar5iv.labs.arxiv.org/html/2104.07724) · [Hoffswell CHI 2020](https://jhoffswell.github.io/website/resources/papers/2020-ResponsiveVisualization-CHI.pdf)
- Constraints: [Figma](https://help.figma.com/hc/en-us/articles/360039957734-Apply-constraints-to-define-how-layers-resize) · [Android ConstraintLayout](https://developer.android.com/develop/ui/views/layout/constraint-layout) · [Apple Auto Layout](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/AutolayoutPG/WorkingwithConstraintsinInterfaceBuidler.html)
- Reflow standard: [WCAG 1.4.10](https://www.w3.org/WAI/WCAG21/Understanding/reflow.html) · breakpoints [NN/g](https://www.nngroup.com/articles/breakpoints-in-responsive-design/)
- Adobe responsive: [Premiere Pin To](https://helpx.adobe.com/premiere-pro/using/responsive-design-features.html) · [AE Responsive Time](https://helpx.adobe.com/after-effects/using/responsive-design.html) · cross-AR MOGRT [Pond5](https://blog.pond5.com/23558-how-to-design-auto-responsive-templates-for-vertical-and-square-videos/)
- Safe zones: [Orson Lord](https://orsonlord.com/articles/free-safe-zone-overlays-for-reels-tiktok-and-shorts) · [Kreatli](https://kreatli.com/guides/tiktok-safe-zone) · [Meta specs](https://www.tryvizup.com/blog/meta-ad-specs-2026-every-dimension-size-you-need) · SMPTE [Venera](https://www.veneratech.com/what-is-title-safe-and-why-it-still-matters-in-modern-video-production)
- Typography: [BBC subtitles](https://bbc.github.io/subtitle-guidelines/) · [WCAG contrast](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html) · [Rev sizes](https://www.rev.com/blog/best-open-caption-font-sizes-for-videos-on-social-media) · [line length](https://baymard.com/blog/line-length-readability)
- Motion/aspect: [Mowe](https://mowe.studio/common-video-aspect-ratios/) · [GSAP paths](https://tympanus.net/codrops/2025/12/17/building-responsive-scroll-triggered-curved-path-animations-with-gsap/) · [Nitro vertical beats](https://www.nitromediagroup.com/optimizing-your-horizontal-content-for-vertical-platforms/)
