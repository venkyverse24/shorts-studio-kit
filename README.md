# Shorts Studio Kit

Skills, agents and small scripts for making YouTube Shorts with [Claude Code](https://claude.com/claude-code). You give it a one-line topic. It researches, writes and scores the script, builds the video, makes the sound, checks the result and prepares the upload files. It never uploads anything itself.

```
/short How does a zip lock together?
```

## Install (pick one)

You need Claude Code and Python 3. Blender and ffmpeg are only needed if you build 3D videos or mix audio.

### Option 1: one command, no git (recommended for most people)

Open a terminal in your (empty) studio folder and run one line. It downloads the kit, installs it, and cleans up after itself.

**Windows (PowerShell)**
```powershell
irm https://raw.githubusercontent.com/venkyverse24/shorts-studio-kit/main/bootstrap.ps1 | iex
```

**macOS, Linux, Git Bash**
```bash
curl -fsSL https://raw.githubusercontent.com/venkyverse24/shorts-studio-kit/main/bootstrap.sh | bash
```

Piping a script from the internet into your shell is a trust decision. The script only downloads this kit's zip and runs the kit's own installer, and you can read it first: download `bootstrap.ps1` or `bootstrap.sh`, open it, then run it. To install a fixed version, set `KIT_REF=v1.0.0` first. To install from a fork, set `KIT_REPO=your-name/your-fork`.

### Option 2: Claude Code plugin

```bash
claude plugin marketplace add venkyverse24/shorts-studio-kit
claude plugin install shorts@shorts-studio-kit --scope project
```
Run these inside your studio folder (use `--scope user` to enable it in every project). Then open Claude Code there and type `/shorts:setup`. Plugin skills carry the plugin name, so the main command is `/shorts:short <topic>`.

Notes on the plugin route:
- Plugins cannot run setup by themselves, so `/shorts:setup` creates `brand.md`, `shorts-kit.json`, the helper scripts in `tools/` and the queue and results files, and helps you fill them in.
- The plugin's skill and agent names add about 1,100 tokens to every session where it is enabled. Prefer `--scope project` so it is only on for your studio.
- Updates: `claude plugin marketplace update shorts-studio-kit`, then `claude plugin update shorts@shorts-studio-kit`.

### Option 3: clone and run the installer

```powershell
git clone https://github.com/venkyverse24/shorts-studio-kit shorts-studio-kit
cd shorts-studio-kit
.\install.ps1 -Target C:\path\to\your-studio
```
```bash
git clone https://github.com/venkyverse24/shorts-studio-kit shorts-studio-kit
cd shorts-studio-kit
./install.sh /path/to/your-studio
```

All three routes install the same things. The installer routes (1 and 3):
- copy 14 skills and 7 agents into `<studio>/.claude/` (commands are `/short`, `/shorts-hooks` and so on)
- copy 5 scripts into `<studio>/tools/`
- create `brand.md`, `shorts-kit.json`, `notes/queue.md` and `analytics/results.csv` only if they do not exist
- add a short section to `<studio>/CLAUDE.md` (once) and put `shorts-kit.json` in `.gitignore`
- never overwrite a kit file you edited (use `--force` / `-Force` to update), and never touch your own files

### After installing
1. Fill in `brand.md` (voice, closing line, disclosures, tools) and `shorts-kit.json` (your private terms). `/shorts:setup` walks you through it.
2. Open Claude Code in the studio folder and type `/short <topic>` (or `/shorts:short <topic>` for the plugin).

You can also paste this into Claude Code: *"Install the Shorts Studio Kit from `venkyverse24/shorts-studio-kit` into this folder."*

## What you get

| Piece | What it does |
|---|---|
| `/short` | Runs the six production agents in order and stops with a report |
| `short-researcher` | Sourced research notes with dates and open items |
| `short-scriptwriter` | Five hooks, scored; humanised scene-by-scene script |
| `short-director` | Builds visuals (Blender 3D rules included), previews, silent final |
| `short-sound` | Narration, effects, mix, subtitles |
| `short-qc` | Read-only PASS/FAIL gate: specs, facts, privacy, disclosures, credits |
| `short-publisher` | Title, description, tags, thumbnail, notes; never uploads |
| `channel-analyst` | After publishing: results log, retention drops, queue refresh, comment drafts |

Skills hold the rules so prompts stay short: `shorts-setup`, `shorts-voice`, `shorts-hooks`, `shorts-seo`, `shorts-3d`, `shorts-sound`, `shorts-earshot`, `shorts-openverse`, `shorts-publish`, `shorts-qc`, `shorts-analytics`, `shorts-plan`, `shorts-comments`.

Scripts (standard library only, no keys):

| Script | Use |
|---|---|
| `tools/hookscore.py` | Lint hook options: open question, puzzle, viewer, specifics, spoken length, clean wording (a lint, not a view predictor) |
| `tools/titlecheck.py` | Lint title, thumbnail text and hashtags together |
| `tools/ytsuggest.py` | What people type into YouTube search (public autocomplete) |
| `tools/openverse.py` | Find openly licensed sounds and images, with a licence and credit log |
| `tools/analytics.py` | Results log, ranking against your median, retention drops mapped to scenes |

## Privacy

- The kit's scripts need no account or API key and upload nothing. Claude Code itself runs on your own Claude login or API key, as usual. The only network calls are web search and two read-only lookups (YouTube autocomplete and Openverse).
- Put your own name, usernames, hostnames and similar terms in `shorts-kit.json`. Hooks, titles, thumbnails and the QC skill block them. Emails, IP addresses and home-folder paths are always blocked.
- The installer adds `shorts-kit.json` to your `.gitignore`. Do not commit it.
- This repo contains no personal data, channel names or credentials. Run your own search before you publish a fork.

## Safety and limits

Read this before you rely on the kit.

### Enforced by code
- Claude Code's own permission prompts for running commands and writing files. Keep them on.
- `titlecheck.py` fails titles with clickbait phrases, profit promises, private terms, emails or IP addresses. `hookscore.py` penalises private terms and greetings.
- The installers never overwrite your edited files or your `brand.md`, and they stop before copying anything if the kit is incomplete.
- `shorts-kit.json` (your private terms) is added to your `.gitignore`.
- `openverse.py` refuses any licence except cc0, pdm and by, and logs a credit line for every download.
- No script in the kit can upload, log in to YouTube or post anything.

### Instructions Claude follows (strong, but not locks)
- Never upload, schedule, post or reply. Never create accounts or API keys. Never use paid services. Never overwrite a finished export.
- Run the agents one at a time. The script is the single source of truth for the spoken words.
- A read-only QC step checks specs, claims against the research note, privacy, disclosures and credits before the publish pack.
- Comments and pinned comments are drafts for you to post.

Instructions can fail. If you connect a browser tool, a social-media tool or any upload tool to Claude Code, nothing in this kit technically stops it from using them. Do not connect upload tools to a studio folder, and keep permission prompts on.

### What the kit does not cover
- **Whether your sources are right.** QC checks claims against your research note, not the note's sources. If a source cannot be opened, the research stage should say so.
- **Platform rules.** YouTube's synthetic-content label, copyright of any assets you add, and sponsorship rules are yours to handle. The kit only reminds you to disclose.
- **Private terms you forget.** The block list is only as good as what you put in `shorts-kit.json`.
- **Cost.** A full `/short` is many agent runs on your Claude plan or API key. The scripts themselves are free.

### Known limits
- **The hook scorer is a lint, not a predictor.** It catches greetings, digits, missing questions, long hooks and private terms. Hooks that rely on the picture can score low and still work, and a high score never means the claims are true.
- **Tested on Windows only.** The shell installer ran under Git Bash on Windows, not on macOS or Linux.
- **Run end to end once**, on a single topic, with Pillow-drawn visuals and a local text-to-speech tool. `shorts-3d` (Blender), `shorts-openverse`, `shorts-earshot`, `shorts-comments` and `shorts-plan` are covered by tests or reading only, not by a real run.
- **Retention reading is tested on made-up data.** Real YouTube Studio exports vary, and the parser says plainly when it cannot find the columns.
- **Small samples mislead.** Rankings from fewer than about ten videos are hints.
- **The YouTube suggestions endpoint is unofficial** and can stop working. Web search is the fallback.
- **Claude cannot log in to YouTube Studio.** You bring numbers, exports and comments.
- **The kit includes no renderer or text-to-speech engine.** Name yours in `brand.md`.
- **Earshot is optional, third-party and not bundled.** `shorts-earshot` explains how to review and install it yourself.

## Tests

```
python tests/run_tests.py
```
Checks the structure (names match, tools listed), the scripts' behaviour (forbidden terms blocked, scoring, analytics), and runs without network access.

## Update

Pull the repo and run the installer again. Files you edited are kept and listed; add `--force` to take the new version.

## Uninstall

Plugin route: `claude plugin uninstall shorts@shorts-studio-kit`. Installer routes: delete the 13 `shorts-*` folders and `short` from `<studio>/.claude/skills/`, the 7 agent files from `<studio>/.claude/agents/`, the five scripts from `<studio>/tools/`, and the marked block in `CLAUDE.md`.

## Credits

- `tools/hookscore.py` was inspired by the idea of a small hook lint with a weakest-link guard, as seen in the MIT-licensed [youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) repository. The checks, scoring rule, thresholds, word lists, layout and code here are written independently for this kit and share no code with it.
- [Earshot](https://github.com/Leonxlnx/earshot) (MIT, by Leon Lin) is referenced by `shorts-earshot` but not included. Install it yourself after reviewing it.
- Openverse and YouTube's public autocomplete are used through their public web interfaces. Follow their terms.
- Other tools named as examples (Blender, ffmpeg, Kokoro, faster-whisper) are third-party and not bundled.

## License

MIT. See `LICENSE`.
