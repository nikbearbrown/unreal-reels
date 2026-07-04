# SHOTLIST — vox-the-ultraviolet-catastrophe (editorial pass DONE)

Converted from `physics/the-ultraviolet-catastrophe`. 15 beats · ~77s at old
timings (re-clocks after TTS). Narration: **11 keep · 4 rewrite** (INTRO, H02,
A08, A12 — rewritten into Vox register; all 15 regenerate in one TTS pass since
no mp3s exist on this machine).

## Shot types after the pass

GRAPHIC 9 (A02–A07, A09–A11 — all scenes written in `vox_scenes.py`, gate-checked)
· CARD 2 (INTRO, OUTRO — scenes written) · STILL/archive 2 (H01, A12)
· COMPOSITE/archive 1 (H02) · DOCUMENT/archive 1 (A08)

## YOUR slots (4) — everything else renders from code

**H01 — glowing metal / campfire, archival still** (`media/H01.png` + `H01.source.txt`)
- https://www.loc.gov/free-to-use/?q=steel+foundry+molten
- https://www.si.edu/openaccess?edan_q=blacksmith%20forge%20glowing
- https://commons.wikimedia.org/w/index.php?search=foundry+molten+iron+photograph&title=Special:MediaSearch

**H02 — same plate, crimson runaway ink line on the annotation plane** — reuses
H01's image; the hand-drawn curve sweeps up and off-frame on the word
"infinite" (Remotion annotation layer; slate until H01 lands).

**A08 — Planck's 1900/1901 paper scan** (`media/A08.png` + sidecar) — zoom to the
quantum-hypothesis passage, crimson chip "Energy comes in chunks."
- https://commons.wikimedia.org/w/index.php?search=Planck+1901+Annalen+der+Physik&title=Special:MediaSearch
- https://www.biodiversitylibrary.org/search?searchTerm=annalen+der+physik+1901

**A12 — Max Planck portrait, archival, very slow push-in** (`media/A12.png` + sidecar)
- https://commons.wikimedia.org/w/index.php?search=Max+Planck+portrait&title=Special:MediaSearch
- Fallback if no portrait: the `A12_Fuse` scene (terracotta chunk ringed on the
  finished curve) renders automatically until `media/A12.png` exists.

## The graphic arc (one continuous chart, vox grammar)

A02 axes → A03 few wave-patterns → A04 patterns pack in (+f² ghost) →
A05 equal terracotta shares (isotype) → A06 crimson runaway "prediction:
infinite ultraviolet" → A07 navy measured curve vs ghost → A09 chunk staircase
+ price chip → A10 high-f patterns grey out → A11 runaway TRANSFORMS into the
Planck curve (the payoff cut).

## Order of operations

1. `generate_audio.py` (all 15, final script) → 2. `vox_run.sh` (gates → render
→ compile, narration muxed automatically) → 3. drop the 3 archive images in
`media/` whenever — only those slots recompile.
