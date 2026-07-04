#!/usr/bin/env python3
"""
scaffold_remotion.py — assemble the Remotion project that renders the lecture.

Given a lecture folder (with beat_sheet.json + captions.json + mp3/) and the
source deck, it builds <folder>/remotion/:

  remotion/
    package.json  tsconfig.json  remotion.config.ts
    src/ (index, Root, Lecture, DeckBackground, Captions, theme)
    src/data/beats.json      <- copy of beat_sheet.json
    src/data/captions.json   <- copy of captions.json
    public/deck/             <- deck.html (rail hidden) + support.js + deck-stage.js + _ds/
    public/mp3/              <- per-slide narration

Then: cd remotion && npm i && npm run studio   (preview gate — approve, THEN `npm run render`)

Usage:
    python scaffold_remotion.py path/to/lecture_folder \
        --deck "path/to/Deck.dc.html" [--slug fairness-lecture]
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates" / "remotion"

# inject right after <head ...> so it runs before deck-stage.js initialises
RAIL_HIDE = (
    "<script>try{localStorage.setItem('deck-stage.railVisible','0');}"
    "catch(e){}</script>\n"
)


def copy_deck(deck_path: Path, public_deck: Path):
    """Copy deck.html (renamed) + its sibling JS/CSS deps so relative paths
    (./support.js, ./deck-stage.js, _ds/...) still resolve under public/deck/."""
    public_deck.mkdir(parents=True, exist_ok=True)
    src_dir = deck_path.parent

    html = deck_path.read_text(encoding="utf-8", errors="replace")
    # hide the presenter rail/chrome in the render
    m = re.search(r"<head[^>]*>", html, re.IGNORECASE)
    if m:
        html = html[: m.end()] + "\n" + RAIL_HIDE + html[m.end():]
    else:
        html = RAIL_HIDE + html
    (public_deck / "deck.html").write_text(html, encoding="utf-8")

    # sibling assets the deck references
    for name in ("support.js", "deck-stage.js"):
        p = src_dir / name
        if p.exists():
            shutil.copy2(p, public_deck / name)
        else:
            print(f"[warn] deck dependency not found: {name}")
    # design-system / asset folders referenced via relative paths
    for d in ("_ds", "assets", "images"):
        p = src_dir / d
        if p.is_dir():
            shutil.copytree(p, public_deck / d, dirs_exist_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="Lecture folder (beat_sheet.json, captions.json, mp3/)")
    ap.add_argument("--deck", required=True, help="Path to the source .dc.html deck")
    ap.add_argument("--slug", default=None)
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    # Resolve a relative --deck against the LECTURE FOLDER first, then the CWD.
    # (A bare filename like "01-x.dc.html" almost always means "in the folder".)
    deck_arg = Path(args.deck).expanduser()
    if not deck_arg.is_absolute() and (folder / deck_arg).exists():
        deck_path = (folder / deck_arg).resolve()
    else:
        deck_path = deck_arg.resolve()
    if not deck_path.exists():
        sys.exit(f"[err] deck not found: {args.deck} (tried {folder / deck_arg} and {deck_arg.resolve()})")
    slug = args.slug or folder.name

    sheet_path = folder / "beat_sheet.json"
    if not sheet_path.exists():
        sys.exit(f"[err] no beat_sheet.json in {folder} (run extract_slides.py first)")
    sheet = json.loads(sheet_path.read_text())
    caps_path = folder / "captions.json"
    mp3_dir = folder / "mp3"

    proj = folder / "remotion"
    (proj / "src" / "data").mkdir(parents=True, exist_ok=True)
    (proj / "public").mkdir(parents=True, exist_ok=True)

    # 1) config files (slug-substituted)
    for name in ("package.json", "tsconfig.json", "remotion.config.ts"):
        txt = (TEMPLATES / name).read_text().replace("__SLUG__", slug)
        (proj / name).write_text(txt)

    # 2) src/*
    for src_file in (TEMPLATES / "src").glob("*"):
        if src_file.is_file():
            shutil.copy2(src_file, proj / "src" / src_file.name)

    # 2b) bundled static assets shipped with the skill (e.g. public/fonts/*.ttf —
    #     the overlay typeface, loaded from a real file rather than the CDN).
    tpl_public = TEMPLATES / "public"
    if tpl_public.is_dir():
        shutil.copytree(tpl_public, proj / "public", dirs_exist_ok=True)

    # 3) data
    shutil.copy2(sheet_path, proj / "src" / "data" / "beats.json")
    if caps_path.exists():
        shutil.copy2(caps_path, proj / "src" / "data" / "captions.json")
    else:
        (proj / "src" / "data" / "captions.json").write_text(
            json.dumps({"fps": 30, "slides": {}}, indent=2))
        print("[warn] no captions.json yet — rendering without captions "
              "(run align_captions.py, then re-scaffold)")

    # 4) public assets
    copy_deck(deck_path, proj / "public" / "deck")
    if mp3_dir.is_dir():
        shutil.copytree(mp3_dir, proj / "public" / "mp3", dirs_exist_ok=True)
    else:
        print("[warn] no mp3/ folder — narration audio missing (run generate_audio.py)")

    # 4b) doodle specs (Remotion-native): <folder>/doodles.json is a map
    #     { beat_id: {title?, elements:[...]} }. Lecture.tsx draws the spec on for
    #     exactly the doodle slides that have a non-empty elements list; the rest
    #     stay live. No video files — the doodle is rendered inside Remotion.
    doodle_spec_path = folder / "doodles.json"
    spec = json.loads(doodle_spec_path.read_text()) if doodle_spec_path.exists() else {}
    (proj / "src" / "data" / "doodles.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    authored = [bid for bid, s in spec.items() if s.get("elements")]
    n_doodle_slides = sum(1 for b in sheet["beats"] if b.get("visual_mode") == "doodle")
    print(f"[ok] doodle specs wired: {len(authored)}/{n_doodle_slides} doodle slides "
          f"({'none yet — slides stay live until specs exist' if not authored else ', '.join(authored)})")

    # 4c) bullets specs (auto fallback for doodle slides without a doodle)
    bullets_path = folder / "bullets.json"
    bspec = json.loads(bullets_path.read_text()) if bullets_path.exists() else {}
    (proj / "src" / "data" / "bullets.json").write_text(json.dumps(bspec, indent=2, ensure_ascii=False))

    # 4c-fig) progressive-figure specs: reveal an authored SVG's parts in sync with
    #     narration. <folder>/figures.json is { beat_id: {file, title?} }; we embed
    #     the SVG text (so no runtime fetch) and count its reveal groups (pf-N).
    fig_path = folder / "figures.json"
    figraw = json.loads(fig_path.read_text()) if fig_path.exists() else {}
    figout = {}
    for bid, f in figraw.items():
        svgp = (folder / f["file"]).resolve()
        if not svgp.exists():
            print(f"[warn] figure svg not found for {bid}: {svgp}")
            continue
        txt = svgp.read_text(encoding="utf-8")
        idxs = [int(m) for m in re.findall(r"pf-(\d+)", txt)]
        groups = (max(idxs) + 1) if idxs else 1
        figout[bid] = {"svg": txt, "groups": groups, "title": f.get("title")}
    (proj / "src" / "data" / "figures.json").write_text(json.dumps(figout, ensure_ascii=False))
    fig_summary = ", ".join("%s:%dg" % (b, v["groups"]) for b, v in figout.items()) or "none"
    print("[ok] progressive figures wired: %d (%s)" % (len(figout), fig_summary))

    # 4d) equation-tangent specs (the 5-zone explainer after each equation slide)
    tang_path = folder / "tangents.json"
    tspec = json.loads(tang_path.read_text()) if tang_path.exists() else {}
    (proj / "src" / "data" / "tangents.json").write_text(json.dumps(tspec, indent=2, ensure_ascii=False))
    n_tang = sum(1 for b in sheet["beats"] if b.get("visual_mode") == "equation")
    print(f"[ok] equation tangents wired: {len([k for k in tspec])} authored, {n_tang} beats")

    # 4e) native section cards (title / dividers / close) — no deck iframe
    sect_path = folder / "sections.json"
    sect = json.loads(sect_path.read_text()) if sect_path.exists() else {}
    (proj / "src" / "data" / "sections.json").write_text(json.dumps(sect, indent=2, ensure_ascii=False))
    print(f"[ok] native section cards: {len(sect)} (no iframe reload at dividers)")

    # 4f) prerendered deck stills (from prerender_deck.py) — hold slides show these
    #     PNGs instead of a live iframe. Manifest lists which slide indices exist.
    stills_src = folder / "deck-stills"
    still_idx = []
    if stills_src.is_dir():
        (proj / "public" / "deck-stills").mkdir(parents=True, exist_ok=True)
        for png in stills_src.glob("slide-*.png"):
            shutil.copy2(png, proj / "public" / "deck-stills" / png.name)
            m = re.match(r"slide-(\d+)\.png", png.name)
            if m:
                still_idx.append(int(m.group(1)))
    (proj / "src" / "data" / "deck-stills.json").write_text(json.dumps(sorted(still_idx)))
    print(f"[ok] deck stills wired: {len(still_idx)} "
          f"({'none yet — hold slides stay live until you run prerender_deck.py' if not still_idx else 'hold slides use PNGs'})")
    bulleted = [bid for bid, s in bspec.items() if s.get("bullets") and bid not in authored]
    still_live = [b["beat_id"] for b in sheet["beats"]
                  if b.get("visual_mode") == "doodle"
                  and b["beat_id"] not in authored and b["beat_id"] not in bulleted
                  and b["beat_id"] not in figout]  # progressive-figure slides aren't "live"
    print(f"[ok] bullet specs wired: {len(bulleted)} slides "
          f"| still falling back to live: {len(still_live)}")

    print(f"[ok] scaffolded {proj}")
    print("[next] preview first — NEVER auto-render. The human approves in Studio, then renders.")
    print(f"    cd {proj}")
    print("    npm install")
    print("    npm run studio     # <- STOP HERE: preview all beats, audio, captions, charts")
    print("    # only if it looks good, YOU render it:")
    print("    npm run render     # -> remotion/out/{}.mp4".format(slug))


if __name__ == "__main__":
    main()
