# Setup

Everything you need to install, and how to handle your service keys safely. For *what* each
service is and where to sign up, see [`services.md`](services.md).

> Unreal Reels **orchestrates** hosted AI services — it never includes, proxies, or stores them.
> You bring your own accounts and keys, read from your environment at runtime. Nothing secret
> ever lives in this repo.

---

## 1. System tools

You need: **Python 3.10+**, **Node 18+** (for Remotion assembly), **ffmpeg**, **jq**, **curl**,
**git**.

**macOS** (Homebrew):
```bash
brew install python node ffmpeg jq git
```

**Linux** (Debian/Ubuntu):
```bash
sudo apt update && sudo apt install -y python3 python3-pip nodejs npm ffmpeg jq curl git
```

**Windows:** use **WSL2** (Ubuntu) and follow the Linux steps — the shell scripts assume a
POSIX shell. Native PowerShell is not supported.

Verify:
```bash
python3 --version && node --version && ffmpeg -version | head -1 && jq --version
```

## 2. Python packages

```bash
pip install -r requirements.txt
```

Core: `requests` (ElevenLabs), `mutagen` (measure audio durations). Optional extras (Songbird
beat analysis, fal.ai, caption alignment) are noted in `requirements.txt`.

> **Intel-Mac note:** `librosa` (only needed for the Songbird music aspect) can fail to build
> `llvmlite` via pip. Install it through conda instead: `conda create -n unreal -c conda-forge
> librosa soundfile numpy`, and run the music-analysis steps from that env.

## 3. Higgsfield CLI

Install per Higgsfield's docs, then authenticate once:
```bash
higgsfield auth login
higgsfield model list          # confirm it works
```

## 4. Node / Remotion (overlay stage)

The caption/title overlay renders with Remotion. Inside a reel's Remotion project:
```bash
npm install
```
(First render downloads a headless Chromium automatically.)

---

## 5. Keys — best practices

You have a **choice** of how to provide keys. Both work; pick one. **Never** commit a key,
**never** paste one into an agent chat, and prefer per-project / per-person keys so you can
rotate or revoke without breaking everything.

### Which keys
| Service | Variable |
|---|---|
| ElevenLabs | `ELEVENLABS_API_KEY` |
| fal.ai (optional) | `FAL_KEY` |
| Higgsfield | via `higgsfield auth login` (token stored by the CLI, not an env var) |

### Option A — shell profile (persistent, simplest)
Good if you use one set of keys across all projects on this machine.
```bash
# add to ~/.zshrc (or ~/.bashrc), then: source ~/.zshrc
export ELEVENLABS_API_KEY="sk_..."
export FAL_KEY="..."
```
Pro: always available. Con: global to your user; one key for everything.

### Option B — a `.env` file (recommended for project isolation)
Keeps keys with the project and out of your global shell. **`.env` is git-ignored** — it is
never committed.
```bash
cp .env.example .env        # then edit .env with your real keys
```
Load it into the shell that runs the scripts (the scripts read the process environment):
```bash
set -a; source .env; set +a        # export everything in .env for this session
```
Or automate it with **[direnv](https://direnv.net)** so `.env` loads whenever you `cd` into the
repo:
```bash
brew install direnv                 # then hook into your shell per direnv docs
echo 'dotenv' > .envrc && direnv allow
```
Pro: per-project keys, nothing global, easy to rotate. Con: remember to `source` (or use direnv).

### Option C — per-session (most ephemeral)
```bash
ELEVENLABS_API_KEY="sk_..." python3 scripts/generate_audio.py reels/my-film
```
Pro: nothing persisted. Con: re-enter each time.

All three options are equally valid — pick whichever fits how you work. Whichever you choose:
- `.env`, `*.key`, and `higgsfield.txt` are git-ignored — keep it that way.
- Turn **off auto-recharge** on paid services, or cap spend, so a runaway loop can't drain credits.
- Rotate a key immediately if it ever appears in a log, screenshot, or chat.

---

## 6. Verify

```bash
echo "$ELEVENLABS_API_KEY" | head -c 6 ; echo " …(key present)"   # don't print the whole key
higgsfield account status          # Higgsfield authenticated
python3 scripts/generate_audio.py --help
```

If a script reports a missing key, it tells you which service — go back to step 5 (or
[`services.md`](services.md)).
