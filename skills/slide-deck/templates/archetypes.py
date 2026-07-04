#!/usr/bin/env python3
"""
archetypes.py — the slide-template functions for the slide-deck skill (stage 2).

Each function takes one deck_plan.json slide dict and returns the exact
`<section data-label=… data-speaker-notes=… style="…brutalist inline…">…</section>`
string that (a) renders under deck-stage.js and (b) parses cleanly through
deck-lecture/scripts/extract_slides.py.

The markup is copied verbatim from the known-good fairness deck
(`Chapter 7 - Fairness Metrics.dc.html`) so an emitted deck is byte-compatible
with everything downstream. Color only via the deck's --nu-* tokens; type via
--font-sans (Lato); data numbers in the worked example via --font-mono.

Nine archetypes:
    title · section · statement · concept · equation · example · chart · figure · close

Pure stdlib. No deps.
"""
from __future__ import annotations

import html
import re


# ─────────────────────────────────────────────────────────────────────────────
# escaping helpers
# ─────────────────────────────────────────────────────────────────────────────
def attr(s: str) -> str:
    """Escape a string for use inside a double-quoted HTML attribute.

    extract_slides.py reads data-label / data-speaker-notes straight off the
    attribute, so these must never contain a raw double-quote. We keep the text
    otherwise literal (curly quotes etc. survive) — only ", &, <, > are escaped.
    """
    return (str(s or "")
            .replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def rich(s: str) -> str:
    """Body text that may legitimately contain author-inlined HTML.

    Plan fields like `headline`/`body` are allowed to carry <b>, <i>, <span>,
    <sub>, &mdash;, &ldquo; etc. (the fairness deck does this heavily). We trust
    the plan author here — this is deck copy, not user input — and pass it
    through unchanged. Use `text()` instead for fields that must be plain.
    """
    return str(s or "")


def text(s: str) -> str:
    """Plain body text: escape everything, no inline HTML honored."""
    return html.escape(str(s or ""), quote=False)


_NUM = re.compile(r"(?<![\w>])(\d[\d,\.]*\s?%?)")


def mono_numbers(s: str) -> str:
    """Wrap bare data-numbers in the mono token. Used ONLY where numbers are
    unambiguously data (equation worked examples, metric tables) — never on
    prose, so years like 2016 in a sentence are left alone by the caller.
    """
    return _NUM.sub(r'<span style="font-family:var(--font-mono);">\1</span>', str(s or ""))


# ─────────────────────────────────────────────────────────────────────────────
# small shared fragments (verbatim from the source deck)
# ─────────────────────────────────────────────────────────────────────────────
def _bar_top(h: int = 8) -> str:
    return f'<div style="position:absolute;top:0;left:0;right:0;height:{h}px;background:var(--nu-red);"></div>'


def _bar_left(w: int = 10) -> str:
    return f'<div style="position:absolute;top:0;left:0;bottom:0;width:{w}px;background:var(--nu-red);"></div>'


def _eyebrow(txt: str, *, cls: str = "rise", size: int = 22, ls: str = "0.16em",
             color: str = "var(--nu-red)") -> str:
    return (f'<div class="{cls}" style="font-size:{size}px;font-weight:700;'
            f'letter-spacing:{ls};text-transform:uppercase;color:{color};">{rich(txt)}</div>')


def _rule(cls: str = "rise", w: int = 88, h: int = 6, mt: int = 28) -> str:
    return (f'<div class="{cls}" style="width:{w}px;height:{h}px;'
            f'background:var(--nu-red);margin:{mt}px 0 0;"></div>')


def _section_open(label: str, notes: str, style: str) -> str:
    return (f'<section data-label="{attr(label)}" '
            f'data-speaker-notes="{attr(notes)}" style="{style}">')


# ─────────────────────────────────────────────────────────────────────────────
# the nine archetypes
# ─────────────────────────────────────────────────────────────────────────────
def title(s: dict) -> str:
    style = ("background:var(--nu-black);color:var(--nu-white);"
             "font-family:var(--font-sans);padding:120px 130px;"
             "display:flex;flex-direction:column;justify-content:center;")
    sub = ""
    if s.get("subtitle"):
        sub = (f'<div class="rise3" style="font-size:38px;line-height:1.3;'
               f'color:var(--nu-neutral-2);margin-top:40px;max-width:1300px;'
               f'font-weight:400;">{rich(s["subtitle"])}</div>')
    return (
        f'{_section_open(s.get("label", "Title"), s.get("speaker_notes", ""), style)}\n'
        f'  {_bar_top(10)}\n'
        f'  {_eyebrow(s.get("eyebrow", ""))}\n'
        f'  <h1 class="rise2" style="font-size:104px;line-height:1.0;font-weight:400;'
        f'margin:34px 0 0;letter-spacing:-0.02em;max-width:1560px;">{rich(s.get("headline", ""))}</h1>\n'
        f'  <div class="rise2" style="width:120px;height:8px;background:var(--nu-red);margin:46px 0 0;"></div>\n'
        f'  {sub}\n'
        f'</section>'
    )


def section(s: dict) -> str:
    """Red divider slide ("Part N"). deck-lecture renders these natively (SectionCard)."""
    style = ("background:var(--nu-red);color:var(--nu-white);"
             "font-family:var(--font-sans);padding:110px 130px;"
             "display:flex;flex-direction:column;justify-content:center;")
    sub = ""
    if s.get("subtitle"):
        sub = (f'<div class="rise3" style="font-size:34px;line-height:1.3;'
               f'color:rgba(255,255,255,0.92);margin-top:36px;max-width:1280px;">'
               f'{rich(s["subtitle"])}</div>')
    return (
        f'{_section_open(s.get("label", "Part"), s.get("speaker_notes", "Section divider."), style)}\n'
        f'  {_eyebrow(s.get("part", "Part"), size=26, ls="0.2em", color="rgba(255,255,255,0.78)")}\n'
        f'  <h2 class="rise2" style="font-size:108px;line-height:1.0;font-weight:400;'
        f'margin:26px 0 0;letter-spacing:-0.02em;">{rich(s.get("headline", ""))}</h2>\n'
        f'  {sub}\n'
        f'</section>'
    )


def statement(s: dict) -> str:
    """One large claim on black — the theorem / thesis slide."""
    style = ("background:var(--nu-black);color:var(--nu-white);"
             "font-family:var(--font-sans);padding:110px 130px;"
             "display:flex;flex-direction:column;justify-content:center;")
    body = ""
    if s.get("body"):
        body = (f'<div class="rise3" style="font-size:30px;line-height:1.4;'
                f'color:var(--nu-neutral-2);margin-top:44px;max-width:1380px;">'
                f'{rich(s["body"])}</div>')
    return (
        f'{_section_open(s.get("label", "Statement"), s.get("speaker_notes", ""), style)}\n'
        f'  {_bar_top(8)}\n'
        f'  {_eyebrow(s.get("eyebrow", ""), size=24, ls="0.18em")}\n'
        f'  <h2 class="rise2" style="font-size:72px;line-height:1.1;font-weight:400;'
        f'margin:30px 0 0;letter-spacing:-0.01em;max-width:1560px;">{rich(s.get("headline", ""))}</h2>\n'
        f'  {body}\n'
        f'</section>'
    )


def concept(s: dict) -> str:
    """White slide: eyebrow + h2 + red-marker bullet list (rise2)."""
    style = ("background:var(--nu-white);color:var(--nu-black);"
             "font-family:var(--font-sans);padding:96px 130px;"
             "display:flex;flex-direction:column;")
    items = []
    for b in s.get("bullets", []):
        items.append(
            '<div style="display:flex;align-items:flex-start;gap:22px;">'
            '<div style="width:14px;height:14px;background:var(--nu-red);'
            'margin-top:15px;flex:0 0 auto;"></div>'
            f'<div style="font-size:31px;line-height:1.42;color:var(--nu-neutral-7);">{rich(b)}</div></div>'
        )
    bullets = ""
    if items:
        bullets = ('<div class="rise2" style="display:flex;flex-direction:column;'
                   'gap:26px;margin-top:48px;max-width:1480px;">'
                   + "".join(items) + '</div>')
    return (
        f'{_section_open(s.get("label", "Concept"), s.get("speaker_notes", ""), style)}\n'
        f'  {_bar_top(8)}\n'
        f'  {_eyebrow(s.get("eyebrow", ""))}\n'
        f'  <h2 class="rise" style="font-size:66px;line-height:1.04;font-weight:400;'
        f'margin:16px 0 0;letter-spacing:-0.01em;max-width:1500px;">{rich(s.get("headline", ""))}</h2>\n'
        f'  {_rule()}\n'
        f'  {bullets}\n'
        f'</section>'
    )


def equation(s: dict) -> str:
    """White equation slide: eyebrow + title + subhead + dark KaTeX box +
    plain-terms / values-claim two-column. Supports one or several equations.

    Consumes the EQUATIONS.md fields on the slide (`plain`, `values_claim`);
    the richer tangent data (glossary, worked example) rides in s["tangent"]
    for deck-lecture's equation-tangent beats and is not rendered here.
    """
    style = ("background:var(--nu-white);color:var(--nu-black);"
             "font-family:var(--font-sans);padding:84px 130px;"
             "display:flex;flex-direction:column;")
    subhead = ""
    if s.get("subhead"):
        subhead = (f'<div class="rise" style="font-size:27px;color:var(--nu-neutral-5);'
                   f'margin-top:8px;">{rich(s["subhead"])}</div>')

    texs = s.get("texs") or ([s["tex"]] if s.get("tex") else [])
    labels = s.get("tex_labels") or []
    if len(texs) == 1 and not labels:
        box = (
            '<div class="rise2" style="background:var(--nu-neutral-7);color:#fff;'
            'padding:54px 40px;margin-top:34px;display:flex;align-items:center;justify-content:center;">'
            f'<div data-tex data-display style="font-size:42px;color:#fff;">{rich(texs[0])}</div></div>'
        )
    else:
        inner = []
        for i, tx in enumerate(texs):
            if i < len(labels) and labels[i]:
                mt = "margin-top:6px;" if i else ""
                inner.append(
                    f'<div style="font-size:16px;letter-spacing:0.14em;text-transform:uppercase;'
                    f'color:var(--nu-red);font-weight:700;{mt}">{rich(labels[i])}</div>')
            inner.append(f'<div data-tex data-display style="font-size:34px;color:#fff;">{rich(tx)}</div>')
        box = (
            '<div class="rise2" style="background:var(--nu-neutral-7);color:#fff;'
            'padding:40px 40px;margin-top:28px;display:flex;flex-direction:column;gap:22px;'
            'align-items:center;justify-content:center;">' + "".join(inner) + '</div>'
        )

    plain = (f'<div style="flex:1;border:1px solid var(--nu-neutral-1);padding:30px 34px;">'
             f'<div style="font-size:18px;font-weight:700;letter-spacing:0.14em;'
             f'text-transform:uppercase;color:var(--nu-red);">In plain terms</div>'
             f'<div style="font-size:29px;line-height:1.4;color:var(--nu-neutral-7);'
             f'margin-top:14px;">{rich(s.get("plain", ""))}</div></div>')
    vclaim = (f'<div style="flex:0 0 360px;border:1px solid var(--nu-neutral-1);'
              f'padding:30px 34px;background:var(--nu-red-tint);">'
              f'<div style="font-size:18px;font-weight:700;letter-spacing:0.14em;'
              f'text-transform:uppercase;color:var(--nu-red);">Values claim</div>'
              f'<div style="font-size:25px;line-height:1.4;color:var(--nu-neutral-7);'
              f'margin-top:14px;">{rich(s.get("values_claim", ""))}</div></div>')
    cols = (f'<div class="rise3" style="display:flex;gap:28px;margin-top:34px;'
            f'align-items:stretch;">{plain}{vclaim}</div>')

    return (
        f'{_section_open(s.get("label", "Equation"), s.get("speaker_notes", ""), style)}\n'
        f'  {_bar_top(8)}\n'
        f'  {_eyebrow(s.get("eyebrow", "Equation"))}\n'
        f'  <h2 class="rise" style="font-size:58px;line-height:1.05;font-weight:400;'
        f'margin:14px 0 0;letter-spacing:-0.01em;">{rich(s.get("headline", ""))}</h2>\n'
        f'  {subhead}\n'
        f'  {box}\n'
        f'  {cols}\n'
        f'</section>'
    )


def example(s: dict) -> str:
    """White worked/real-world example: left red bar + big h2 + prose paragraphs."""
    style = ("background:var(--nu-white);color:var(--nu-black);"
             "font-family:var(--font-sans);padding:96px 130px;"
             "display:flex;flex-direction:column;justify-content:center;")
    paras = s.get("paragraphs", [])
    body = ""
    if paras:
        body += (f'<div class="rise2" style="font-size:32px;line-height:1.45;'
                 f'color:var(--nu-neutral-7);margin-top:38px;max-width:1480px;">{rich(paras[0])}</div>')
    if len(paras) > 1:
        body += (f'<div class="rise3" style="font-size:28px;line-height:1.4;'
                 f'color:var(--nu-neutral-5);margin-top:30px;max-width:1480px;'
                 f'border-top:1px solid var(--nu-neutral-1);padding-top:26px;">{rich(paras[1])}</div>')
    return (
        f'{_section_open(s.get("label", "Example"), s.get("speaker_notes", ""), style)}\n'
        f'  {_bar_left(10)}\n'
        f'  {_eyebrow(s.get("eyebrow", "Real-world example"))}\n'
        f'  <h2 class="rise" style="font-size:62px;line-height:1.06;font-weight:400;'
        f'margin:16px 0 0;letter-spacing:-0.01em;max-width:1500px;">{rich(s.get("headline", ""))}</h2>\n'
        f'  {body}\n'
        f'</section>'
    )


def chart(s: dict) -> str:
    """Live D3 slide: eyebrow + h2 + a [data-chart="NAME"] mount. The drawer for
    NAME is folded into the deck's script registry by emit_deck.py. The presence
    of [data-chart] is what makes extract_slides tag this beat visual_mode=live.
    """
    style = ("background:var(--nu-white);color:var(--nu-black);"
             "font-family:var(--font-sans);padding:64px 110px 56px;"
             "display:flex;flex-direction:column;")
    align = ""
    if s.get("center", True):
        style += "align-items:center;"
        align = "align-self:flex-start;"
    w = s.get("chart_w", 1480)
    h = s.get("chart_h", 600)
    name = s["chart"]
    return (
        f'{_section_open(s.get("label", "Chart"), s.get("speaker_notes", ""), style)}\n'
        f'  {_bar_top(8)}\n'
        f'  <div class="rise" style="{align}font-size:22px;font-weight:700;'
        f'letter-spacing:0.16em;text-transform:uppercase;color:var(--nu-red);">{rich(s.get("eyebrow", ""))}</div>\n'
        f'  <h2 class="rise" style="{align}font-size:50px;line-height:1.04;font-weight:400;'
        f'margin:12px 0 0;letter-spacing:-0.01em;">{rich(s.get("headline", ""))}</h2>\n'
        f'  <div data-chart="{attr(name)}" style="width:{w}px;height:{h}px;margin-top:10px;"></div>\n'
        f'</section>'
    )


def figure(s: dict) -> str:
    """White slide holding a static asset (SVG/PNG/JPG) from the pool.

    `src` is the path the deck will reference (emit_deck copies the asset into
    the deck folder's assets/ and rewrites src to the copied location).
    """
    style = ("background:var(--nu-white);color:var(--nu-black);"
             "font-family:var(--font-sans);padding:72px 110px 56px;"
             "display:flex;flex-direction:column;align-items:center;")
    caption = ""
    if s.get("caption"):
        caption = (f'<div class="rise3" style="font-size:24px;line-height:1.36;'
                   f'color:var(--nu-neutral-5);margin-top:20px;max-width:1400px;'
                   f'text-align:center;">{rich(s["caption"])}</div>')
    img = (f'<img class="rise2" src="{attr(s.get("src", ""))}" '
           f'alt="{attr(s.get("alt", s.get("headline", "")))}" '
           f'style="max-width:{s.get("img_w", 1400)}px;max-height:{s.get("img_h", 720)}px;'
           f'margin-top:18px;object-fit:contain;" />')
    return (
        f'{_section_open(s.get("label", "Figure"), s.get("speaker_notes", ""), style)}\n'
        f'  {_bar_top(8)}\n'
        f'  <div class="rise" style="align-self:flex-start;font-size:22px;font-weight:700;'
        f'letter-spacing:0.16em;text-transform:uppercase;color:var(--nu-red);">{rich(s.get("eyebrow", "Figure"))}</div>\n'
        f'  <h2 class="rise" style="align-self:flex-start;font-size:50px;line-height:1.04;'
        f'font-weight:400;margin:12px 0 0;letter-spacing:-0.01em;">{rich(s.get("headline", ""))}</h2>\n'
        f'  {img}\n'
        f'  {caption}\n'
        f'</section>'
    )


def close(s: dict) -> str:
    style = ("background:var(--nu-black);color:var(--nu-white);"
             "font-family:var(--font-sans);padding:120px 130px;"
             "display:flex;flex-direction:column;justify-content:center;")
    body = ""
    if s.get("body"):
        body = (f'<div class="rise3" style="font-size:30px;line-height:1.4;'
                f'color:var(--nu-neutral-2);margin-top:38px;max-width:1440px;">{rich(s["body"])}</div>')
    nxt = ""
    if s.get("next"):
        nxt = (f'<div class="rise3" style="font-size:24px;color:var(--nu-neutral-4);'
               f'margin-top:40px;">{rich(s["next"])}</div>')
    return (
        f'{_section_open(s.get("label", "Close"), s.get("speaker_notes", ""), style)}\n'
        f'  {_bar_top(10)}\n'
        f'  {_eyebrow(s.get("eyebrow", ""))}\n'
        f'  <h2 class="rise2" style="font-size:84px;line-height:1.04;font-weight:400;'
        f'margin:28px 0 0;letter-spacing:-0.02em;max-width:1560px;">{rich(s.get("headline", ""))}</h2>\n'
        f'  <div class="rise3" style="width:120px;height:8px;background:var(--nu-red);margin:42px 0 0;"></div>\n'
        f'  {body}\n'
        f'  {nxt}\n'
        f'</section>'
    )


ARCHETYPES = {
    "title": title,
    "section": section,
    "statement": statement,
    "concept": concept,
    "equation": equation,
    "example": example,
    "chart": chart,
    "figure": figure,
    "close": close,
}


def render_slide(slide: dict) -> str:
    fn = ARCHETYPES.get(slide.get("archetype"))
    if fn is None:
        raise ValueError(f"unknown archetype: {slide.get('archetype')!r} "
                         f"(slide label={slide.get('label')!r})")
    return fn(slide)
