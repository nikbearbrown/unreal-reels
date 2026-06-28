# The reference library

Characters are locked by reference **images**, not by describing them in prompts. You build a
small library once and reuse it across every beat (and every reel that shares the cast).

## Layout (per reel)

```
reels/<slug>/references/
  candidates/                 generate_references.sh drops 10 plates/character here
  characters/
    hero/    hero plate(s)    <- you move your keepers here, by ref_key
    beast/   beast plate(s)
```

`ref_key` is set per character in `beat_sheet.json` → `metadata.characters[].ref_key`.

## Building a reference (stage 3)

1. `bash scripts/generate_references.sh reels/<slug>` → 10 SoulID plates per character into
   `candidates/`, named `<ref_prefix>-<ref_key>-NN.png`. Clean recipe (front/¾, even light,
   plain background, full costume) is appended automatically — these read cleanest into FLUX.
2. **Curate:** delete the bad ones; the survivors are "good enough."
3. Move keepers into `characters/<ref_key>/`.

Generate 10; if none are *great*, generate 10 more. Free SoulID credits make this cheap. If ~30
yield nothing great, the **prompt** (wardrobe/`look`) is off — fix it, don't reroll.

## How the storyboard runner uses it

For each beat, for each character in `characters_present`, it takes up to **2** plates from that
character's folder (more angles = stronger lock), capped at **4 references/scene** total. So:

- **One plate** in a folder → locked to exactly that image.
- **Several** → the runner draws on a couple of them. Trim to your top 1–2 if you want strict control.
- **`MAXPERCHAR=1`** forces single-reference.

## "Great" means great *as a reference*

Pick for legibility, not drama: face clear, costume complete, **plain background** (a busy
background bleeds into every scene FLUX generates from it). Save the moody shots for the actual beats.

## Wardrobe states & shared casts

- A real costume change (rags → gown) is its **own `ref_key`/folder**; the beat selects it via
  `characters_present`. That's how you get the right *look* per shot — not by prompt.
- A cast reused across stories (a recurring narrator, a creature) is curated **once** and copied
  into each reel's `characters/`. Curate once; copy the files.

## Non-character references

- **Props:** only reference a *recurring hero object* that must look identical across shots
  (a specific locket, a mirror). Text renders ordinary props (a basket, an axe) fine — don't
  over-reference.
- **Locations:** a recurring setting can be a reference too, for place consistency.
