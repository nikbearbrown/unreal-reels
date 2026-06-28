# 9:16 Shorts vs 16:9 long-form — algorithm, funnel & strategy

Research brief for Bear's Notes. Flags: **[OFFICIAL]** = first-party YouTube; **[DATA]** = published independent study; **[WEAK]** = practitioner/vendor; **[DEBUNKED]** = circulates widely, failed verification.

## The Bear's Notes model (decided)

**Two videos per concept, and only these two go to YouTube:** the **1-min 9:16 Short** (the vertical-feed piece — complete intuition) and the **2–5 min 16:9 deep** worked-example (the long-form piece). The 1-min 16:9 and the deep 9:16 are not published. The **Short's Related Video points at the deep** — which has genuinely more (the math + worked example), so the click is honest. This replaces the earlier (rejected) idea of linking a Short to its own identical 16:9 twin.

## TL;DR verdict

Shorts and long-form are ranked by **separate recommendation systems with separated watch histories** [OFFICIAL]. Shorts optimize for *not being swiped past* (viewed-vs-swiped-away, % viewed, loops); long-form optimizes for *the click + watch time* (CTR, average view duration). A Short reaches **beyond your subscribers from upload one** ("every Short is given a chance, no matter the channel"); long-form is **audience-built**. The relationship is a **one-way bridge** since 2022: Shorts *"can help with audience discovery but can't hurt your Video performance"* [OFFICIAL] — but they do **not** automatically funnel. Worse, for sub-1M channels, long-form actually **converts subscribers *better* per view than Shorts** [DATA, Galloway 2023]. So Shorts are genuinely "second-class for long-form audience building" — additive, not a pipeline — and the funnel only works through **one deliberate mechanism**: the native **Related Video** link.

## 1. Separate algorithms (official)

| Dimension | Long-form 16:9 | Shorts 9:16 |
|---|---|---|
| Entry | Viewer **clicks** a thumbnail (CTR matters) | Autoplays in feed; viewer **swipes or stays** (no click, thumbnail largely irrelevant in-feed) |
| Core metric | Watch time, avg view duration, CTR | Viewed-vs-swiped-away, % viewed, **loops/re-watches** |
| Reach for new channels | Limited until a track record exists | "Every Short is given a chance to succeed no matter the channel or number of videos" |
| Distribution | Audience/subscriber/suggested-built | Explore→exploit seed-audience expansion ("lottery"-like) |
| Watch history | Separate from Shorts | **Separated** from long-form (2022) |

Sources: [YouTube Help — Shorts search & discovery](https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts); [SEJ quoting YouTube Creator Insider, 2022](https://www.searchenginejournal.com/youtube-shorts-algorithm-explained-in-qa-format/459513/); [vidIQ on separated watch histories (Beaupré, 2022)](https://vidiq.com/blog/post/youtube-shorts-long-form-viewers-algorithm/).

## 2. Are Shorts "second-class" for the channel? Largely yes — additive, not a pipeline

- One-way bridge: *"Shorts performance doesn't negatively impact long form Video recommendations. Shorts can help with audience discovery but can't hurt your Video performance."* [OFFICIAL, [Help](https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts)]
- **Long-form converts subscribers better per 10k views than Shorts — except for 1M+ sub channels.** [DATA, [Paddy Galloway, 3.3B views / 5,400 Shorts / 33 channels, 2023](https://en.rattibha.com/thread/1646898356419981315)] Direct quote: *"on average long-form videos still convert subscribers better (per 10,000 views) than shorts."*
- Audiences barely overlap — YouTube built an **Audience Overlap** analytics card because of it; *"viewers watching Shorts aren't always the same viewers watching longer-form content."* [OFFICIAL, 2022] ~**74% of Shorts views come from non-subscribers** [WEAK, vidIQ].
- Mixed-format channels grew **faster** than long-form-only [OFFICIAL, 2022] — so Shorts are worth doing, just not as an automatic feeder.
- Separate economies: Shorts watch time does **not** count toward long-form monetization hours [OFFICIAL via TubeBuddy].

## 3. The funnel: ONE clickable path, and it's a single video — not a playlist

- **The only native clickable link from a Short is the "Related Video" attach** — one video shown below the channel handle. [OFFICIAL, [Help](https://support.google.com/youtube/answer/14075157?hl=en)] Requires advanced (verified) feature access; target must be public/unlisted.
- **You can attach exactly ONE video — there is no playlist slot.** [OFFICIAL + [TubeBuddy](https://www.tubebuddy.com/blog/youtube-shorts-related-video-manager-strategy/)] So link the **single corresponding long-form explainer**, then let *that video's* end screen + playlist escalate into the series.
- **Links in Shorts descriptions and pinned comments are NON-clickable** — *"URLs placed in YouTube Shorts comments and Shorts descriptions are non-clickable"* [OFFICIAL, [Help](https://support.google.com/youtube/answer/13748639)]. This kills the usual "pinned comment link" tactic for Shorts. The Related Video is the *only* tap-through.
- Two named link strategies: **relevance** (link the topically-matching deep-dive — vidIQ) vs **"flood method"** (point *every* Short at one flagship long-form — TubeBuddy, attributed to MrBeast/Youshaei). Relevance fits an explainer library with a 1:1 Short↔concept mapping.

**⚠️ Automation caveat:** the Related Video is set in **YouTube Studio**, and it is **not exposed by the Data API** as far as the official docs show — so attaching it is likely a **manual per-Short step**, not something `youtube_publish.py` can do. Treat the link as a manual finishing action until proven otherwise.

## 4. Metadata, timing, and the dilution trap

- **Shorts are feed-driven, not search-driven** — *"Shorts are ranked based on performance and viewer personalization"*; the feed drives ~70–90% of views [OFFICIAL + vidIQ]. So Shorts get **hook/curiosity titles**, light keywords; long-form keeps **search-intent, keyword-rich** titles.
- **Skip `#Shorts`** — since Oct 15 2024, classification is purely aspect-ratio + duration: *"videos… with a square or vertical aspect ratio up to three minutes… categorized as Shorts."* [OFFICIAL, [Help](https://support.google.com/youtube/answer/15424877)] `#Shorts` does nothing for classification now. [DEBUNKED as a requirement] A couple of *topical* hashtags are fine.
- **Timing:** publish the **long-form first or same day**; release the Short **same-day or shortly after** — never a teaser *before* the long-form exists (nothing to link, nothing for the bridge to recommend). And **don't co-post at the identical clock time**: long-form peaks mornings (~8–11am), Shorts peak evenings (~6–9pm) [WEAK, Buffer ~1.8M videos].
- **A Short must be standalone *and* a teaser** — one self-contained idea with a first-second hook and a curiosity gap the long-form fills; *not* a raw mid-video cut. [OFFICIAL repurposing playbook + vidIQ]
- **Dilution is the real risk:** off-topic Shorts pull in subscribers who never watch your long-form, so future uploads *"launch to a subscriber base that doesn't care."* [WEAK, vidIQ] **Topic alignment** is the defense — chase audience-right reach, not raw virality.

## What this means for Bear's Notes (concrete)

1. **Do publish both**, but treat the Short as **top-of-funnel reach**, not a guaranteed feeder. Mixed-format channels grow faster; just don't expect a viral Short to lift the long-form on its own.
2. **Link each Short → its single corresponding 16:9 explainer** via Related Video (manual, in Studio). No playlist slot exists; the long-form's own end screen/playlist carries viewers into the rest of the series.
3. **Publish order/timing:** long-form first (morning slot), the matching Short later the **same day** (evening slot) — not the same timestamp, and never the Short before the long-form is live.
4. **Two metadata profiles:** long-form = keyword/search title + full description + chapters + sources; Short = hook title, 2–3 topical hashtags (no `#Shorts`), short description, a spoken/on-screen "full video on the channel" CTA (the description link won't be clickable).
5. **Keep Shorts on-topic** (each maps to a concept pillar) to avoid subscriber dilution.

### Implication for `youtube_publish.py`
The earlier "pair at the same timestamp" idea is **not** optimal per the research. Better model: a `--pair` mode that, per concept, schedules the **16:9 in a morning slot and the 9:16 in an evening slot the same day** (long-form leads), keeping 3 concepts/day (6 uploads = quota). The Related-Video link stays a manual Studio step (flagged above). The script can emit a **per-concept checklist** ("set Related Video on <short> → <long-form videoId>") so the manual step isn't forgotten.

## Channel architecture & analytics (folded from a third pass)

**Playlist layer.** Organize the library into a handful of **subject playlists** (e.g. Quantum Mechanics, Modern Physics, Electromagnetism, Classical Mechanics, Thermodynamics, Optics, Astronomy, Math-for-Physics) rather than per-book. Simpler funnel, longer autoplay chains, stronger session signals. The per-concept chain:

```
Short (9:16)
  → Related Video = the corresponding long-form explainer (1:1 topical match)
     → that video's end screen + card + description → subject playlist
        → playlist autoplay chain into the series
```

**1:1 vs gateway — the choice.** Default to **1:1** (each Short links to *its own* long-form) — for a library where every Short is a vertical cut of one concept, that's the tightest relevance signal. Reserve the **"gateway video"** idea (all of a subject's Shorts point at one accessible flagship) as a **fallback** for Shorts with no clean single match, or a launch tactic. Don't make a subject gateway the default — it trades per-Short topical precision for funnel concentration.

**Content reserves.** The `physics-plus-one-*` and `*-with-llms` repos (~275 rendered videos total across the library) are candidates for gateway videos, alternative Shorts angles, and seed-audience wildcards — an unusual angle may find an audience the standard explainer doesn't, while still funneling into the same subject playlist.

**Analytics — what to actually track (priority order):**
1. **Viewed-vs-swiped-away** — hook diagnostic (rough goal 75%+; directional). [WEAK]
2. **Average % viewed** — completion (rough goal 80%+ on sub-60s; directional). [WEAK]
3. **Subscribers gained per Short** — conversion.
4. **Traffic to the long-form *from* the Short** — the real funnel-health metric (check the long-form's traffic sources for Shorts-driven traffic). If Shorts views are high but this is flat, the Related Video isn't set or the topical match is weak.

Ignore raw view counts — inflated since the Mar 2025 any-duration-counts change.

## Folklore flagged (don't cite)
- ❌ "YouTube fully decoupled Shorts in 2025" — overstated; the live Help page describes a one-way *help-not-hurt* bridge.
- ❌ "Add #Shorts so YouTube knows it's a Short / boosts it" — outdated since Oct 2024 aspect-ratio classification.
- ❌ "Pin a comment with your long-form link" — Shorts comment/description URLs are non-clickable.
- ❌ "Shorts → long-form converts 3–5× / hybrid +50% / 41% faster growth" — uncited vendor multipliers.
- ⚠️ Galloway's "50–60s Shorts win" and all swipe-rate benchmarks are 2023, pre-dating the Mar 2025 loop-counting change and 3-min Shorts — directional only.
