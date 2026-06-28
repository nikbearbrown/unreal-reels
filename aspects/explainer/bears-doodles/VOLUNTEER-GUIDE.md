# Bear's Notes — Volunteer Guide

How to make the quantum videos with Cowork. You don't need to know Python or physics. Your job is to **ask Cowork to build a video, run one command to render it, watch it, and report back.** Cowork (the assistant) does the building; you do the watching.

Each topic becomes **two videos**: a **1-minute vertical Short** (9:16, for phones) and a **2–5 minute wide deep version** (16:9, with the worked math).

---

## One-time setup (do this once)

1. Open the **Cowork** app and the **Terminal** app (both are on the Mac).
2. In Terminal, type this and press Return — it switches on the video tools:
   ```
   ai
   ```
3. That's it. If a video ever fails with a "LaTeX" error, tell Cowork — a one-time install may be needed.

---

## The loop — repeat this for each video

### Step 1 — Ask Cowork what's next
In the Cowork chat, type:
```
What's the next video to build?
```
Cowork will name the topic (e.g. "v1.04 — atom-and-laser") and start building it. **Wait** until Cowork says it's done and gives you a command to run.

### Step 2 — Copy the command Cowork gives you
Cowork will hand you a command that looks like this (the topic name changes each time):
```
python ~/Documents/Cowork/bears-doodles/scripts/bn_pipeline.py run <topic-name> --render
```
**Copy it exactly.** Don't type it from scratch.

### Step 3 — Run it in Terminal
1. Click the Terminal window.
2. If you haven't already this session, type `ai` and press Return.
3. Paste the command and press Return.
4. **Wait.** It makes two videos. The short one (vertical) finishes first and pops open. The deep one (wide) takes longer — **wait for the second video to pop open too.** This can take a few minutes; that's normal.

### Step 4 — Watch both videos
Two video windows will open. Watch each one and ask:
- Does the **text** sit cleanly, not overlapping other text or lines?
- Does the **picture** fill the frame (not tiny in the middle)?
- Does the **voice** match what's on screen?

### Step 5 — Report back to Cowork
**If both look good**, type in Cowork:
```
Both look great. Next.
```
Cowork moves on to the next topic.

**If something looks off**, tell Cowork what you saw. The most helpful thing is to **paste the problem**:
- If Terminal showed an **error** (red text / "Traceback"), copy that text and paste it into Cowork.
- If a **video looks wrong**, take a screenshot of the bad moment (press **Cmd + Shift + 4**, drag a box) and drop the image into Cowork.

Cowork will fix it and give you a new command to run. Repeat Step 3.

---

## Starting a new book — use Scout first

When you've finished a book (or Nik points you at a brand-new one), the topics for the new book don't exist yet. Before you can build any videos, Cowork needs to **scout** the book — read its chapters and write up a list of candidate video ideas.

### Step 1 — Ask Cowork to scout the new book
In the Cowork chat, type:
```
Scout the new book for video ideas.
```
Tell Cowork which book if it asks (e.g. "quantum-mechanics-vol2"). Cowork reads the chapters and writes a list of candidate topics. **You don't build anything in this step** — Cowork is just finding the good ideas.

### Step 2 — Nik picks the winners
Scout produces a list of candidates with scores. **Nik (not you) decides which ones to make.** Once the good ones are picked, they get added to the build queue.

### Step 3 — Back to the normal loop
After scouting and picking, go back to **"What's the next video to build?"** above. The new book's approved topics now flow through the same ask → run → watch → report loop.

So: **new book = scout first, then build as usual.** You never have to figure out the topics yourself — Cowork scouts, Nik picks, you build.

---

## Publishing (only when told)

Don't publish anything yourself. When a batch of videos is approved, Nik (or Cowork) handles uploading them to YouTube on a schedule. Your job stops at "looks great."

---

## Good to know

- **You can't break anything.** If a command errors, nothing is harmed — just paste the error to Cowork.
- **It's normal to wait.** The deep (wide) video always takes longer than the short.
- **Don't edit the code or files.** If something needs changing, describe it to Cowork and let it make the change.
- **One topic at a time.** Finish (or report) the current one before asking for the next.

## If you get stuck — copy/paste these to Cowork

- "The command gave an error — here it is: [paste the red text]"
- "The vertical video has a problem — here's a screenshot: [drop image]"
- "Nothing popped up after a few minutes — what should I check?"
- "Which command do I run again?"

That's the whole job: **ask → run → watch → report.** Cowork does the rest.
