#!/usr/bin/env python3
"""
prerender_deck.py — screenshot each deck slide to a still PNG, so the Remotion
render can show <Img> instead of loading the live deck iframe per frame (the
iframe reloads caused the ProtocolError crashes + the slow, jittery export).

Runs on YOUR machine (needs a real browser + the deck's CDN assets: d3, katex).
Only the "hold" slides end up shown as stills in the video; the 8 D3 chart slides
stay live, so their animations are preserved. Prerendering all slides anyway is
cheap and lets DeckBackground choose per slide.

Setup (once):
    pip install playwright
    playwright install chromium

Usage:
    python prerender_deck.py <folder> --deck "<deck>.dc.html"
    python prerender_deck.py <folder> --deck "<deck>" --only 4 6 8   # specific slide indices

Writes <folder>/deck-stills/slide-<index>.png (0-based, matching slide_index).
"""
import argparse
import re
from pathlib import Path


def slide_count(deck_html: str) -> int:
    return len(re.findall(r'<section\b[^>]*data-label="', deck_html))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--deck", required=True)
    ap.add_argument("--only", nargs="*", type=int, help="specific 0-based slide indices")
    ap.add_argument("--wait", type=int, default=1400, help="ms to let each slide settle")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit(
            "deck-lecture: Playwright not installed. On your machine:\n"
            "    pip install playwright\n"
            "    playwright install chromium\n"
            "then re-run this script."
        )

    folder = Path(args.folder).expanduser().resolve()
    # Resolve a relative --deck against the LECTURE FOLDER first, then the CWD.
    deck_arg = Path(args.deck).expanduser()
    if not deck_arg.is_absolute() and (folder / deck_arg).exists():
        deck = (folder / deck_arg).resolve()
    else:
        deck = deck_arg.resolve()
    if not deck.exists():
        raise SystemExit(f"[err] deck not found: {args.deck} (tried {folder / deck_arg} and {deck_arg.resolve()})")
    out = folder / "deck-stills"
    out.mkdir(parents=True, exist_ok=True)

    n = slide_count(deck.read_text(encoding="utf-8", errors="replace"))
    indices = args.only if args.only else list(range(n))
    file_url = deck.as_uri()  # file:///…/Deck.dc.html

    print(f"[i] deck has {n} slides; rendering {len(indices)} still(s) at {args.width}x{args.height}")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": args.width, "height": args.height},
                                device_scale_factor=1)
        # hide the deck's presenter rail before it initialises
        page.add_init_script("try{localStorage.setItem('deck-stage.railVisible','0')}catch(e){}")
        for i in indices:
            # about:blank forces a real reload each time so deck-stage re-reads #index
            page.goto("about:blank")
            page.goto(f"{file_url}#{i}", wait_until="networkidle")
            try:
                page.evaluate("document.fonts && document.fonts.ready")
            except Exception:
                pass
            page.wait_for_timeout(args.wait)  # let KaTeX / D3 / the rise settle
            dest = out / f"slide-{i}.png"
            page.screenshot(path=str(dest), clip={"x": 0, "y": 0, "width": args.width, "height": args.height})
            print(f"    slide {i:>2} -> {dest.name}")
        browser.close()

    print(f"[ok] wrote {len(indices)} stills to {out}")
    print("[next] re-scaffold to copy them into the Remotion project, then render.")


if __name__ == "__main__":
    main()
