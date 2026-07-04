# Resume prompt — lecture-video pipeline

Paste the block below into a new conversation to continue.

```
We're building a chapter → lecture-video pipeline. Read these on-disk files FIRST
(they are the source of truth — don't make me re-explain):

- /Users/nik/Documents/Cowork/unreal-reels/skills/deck-lecture/SKILL.md   (stage 3: deck → narrated video — DONE)
- /Users/nik/Documents/Cowork/unreal-reels/skills/lecture-assets/SKILL.md (stage 1: chapter → asset pool — DONE)
- /Users/nik/Documents/Cowork/unreal-reels/brutalist/DESIGN.md and EQUATIONS.md (the design system)
- /Users/nik/Documents/Cowork/computational-skepticism-for-ai/lectures/02-probability-uncertainty-and-the-confidence-illusion/assets/assets.json (a real asset pool)

PIPELINE:  chapter.md → [lecture-assets ✓] → [slide-deck ✓] → [deck-lecture ✓] → narrated mp4
(All three stages now built. slide-deck was the missing middle — see DONE.)

WHERE THINGS ARE:
- unreal-reels repo: /Users/nik/Documents/Cowork/unreal-reels (pushed to github.com:nikbearbrown/unreal-reels). All skills live in unreal-reels/skills/.
- Test book: /Users/nik/Documents/Cowork/computational-skepticism-for-ai (chapters/*.md, book figures in images/, per-chapter lectures/<slug>/assets/).
- Reference on disk: ai-for-graphs-a-practitioners-guide, brutalist-d3-x-claude (chart grammar); cajal + bears-doodles-scout skills.

DONE:
- deck-lecture (stage 3): full narrated flipped-classroom video from a .dc.html deck. Three-tier visuals (live D3 slide / bears-doodles-style doodle / auto-bullets), native SectionCard dividers, KaTeX equation tangents, karaoke captions. Chapter 7 Fairness lecture rendered + on YouTube (https://youtu.be/5RZKbSXa-E8).
- lecture-assets (stage 1): builds a POOL of candidate assets into lectures/<chapter>/assets/ (svg/ figures, charts/ live D3, doodles/ candidates, book/ imported figures), tagged in assets.json, NOTHING forced. Scripts: import_book_figures.py (Move 0), add_asset.py. Ran on ch02: 20 candidates, 10 real (4 authored + book fig-02 + jpg figs 12-16), 10 flagged placeholders (the book's ch02 SVGs are mostly stub bar charts — the skill generates the real figures).

- slide-deck (stage 2 — NEW): chapter.md + asset pool → brutalist .dc.html deck that feeds deck-lecture. Nine archetype templates (title/section/statement/concept/equation/example/chart/figure/close) in templates/archetypes.py; phase-gated build_plan.py (Phase 0 gate) → bind_assets.py (Phase 1 gap report) → emit_deck.py (Phase 2: copies runtime+_ds, folds charts/<name>.drawer.js into the data-dc-script registry, zero iframes) → verify_deck.py (Phase 3: reuses extract_slides.py, palette/notes/KaTeX/chart audit). Decisions locked: A=drawer.js contract (added lecture-assets/scripts/new_chart.py) + SVG raster fallback; B=one gate at deck_plan.json; C=re-derived Ch.7 as regression target. Round-trip PROVEN: emit → verify PASS → extract_slides parses all slides, data-chart→live, notes on every beat. Artifact: lectures/07-fairness-regen/.

NEXT TASK (options):
1. Full Ch.7 deck: build_plan.py on the ch07 chapter → author the ~39-slide deck_plan.json → emit → compare to the hand-built fairness deck.
2. Finish ch02's real figures (Venn/axioms, Markov transition, heavy-tail), run ch03's asset pass, push authored SVGs back into the book's images/.
3. Author the remaining Ch.7 chart drawers via lecture-assets/scripts/new_chart.py (compas, lipschitz, causal, gealpha, gedecomp, scaffold) so a full deck goes live end-to-end.

NON-NEGOTIABLE CONVENTIONS:
- Palette: one red #C8102E, warm ink #2a1a0e, gray #545454. No blue, grays as the only neutrals.
- Fonts: deck = Lato; overlays = Inter (local file); numbers = JetBrains Mono (local file). Load fonts INSIDE a component (useOverlayFonts hook) — NEVER call delayRender at module scope.
- Motion: ease-out-quart cubic-bezier(0.2,0.8,0.2,1); fades + small translates; no bounce.
- Assets: colorblind-safe, zero baseline, scaleSqrt radii, mono numbers, ARIA labels.
- deck-lecture render gotchas: the live deck iframe is heavy — prerender hold slides to stills (prerender_deck.py), render dividers natively (SectionCard), keep only D3 chart slides live; if ProtocolError, lower --concurrency.
- Always hand off shell commands copy-paste-ready with ABSOLUTE full paths (see unreal-reels/AGENTS.md).

Open deck-lecture thread (Chapter 7): still need to run generate_audio for the 8 equation-tangent beats (--only S05T S07T S09T S14T S16T S24T S29T S32T), re-scaffold, final render, then generate timestamped YouTube chapters.

Start by reading the files above, then propose the slide-deck skill design and confirm before building.
```
