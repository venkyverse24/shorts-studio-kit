---
name: shorts-openverse
description: Find openly licensed sound effects and images with Openverse (no key), keep a licence and credit log, and put the credits in the description. Use when a Short needs a real recorded sound or a photo the synth tools and Blender cannot make.
---

# Openverse

Helper: `tools/openverse.py` (Python standard library only, no account or key).

```
python tools/openverse.py search audio "door closing" --n 8
python tools/openverse.py search images "city street" --n 8
python tools/openverse.py get audio <id> --dir assets/sfx/<project> --log projects/<project>/publish/attribution.json
```

## Rules
- Allowed licences by default: `cc0`, `pdm`, `by`. The search excludes non-commercial and no-derivatives items. Share-alike and everything else stay out unless you decide otherwise. `get` refuses other licences.
- Mature content filter stays on.
- Listen to or look at every pick before using it. Many audio results are MP3 previews from Freesound: convert to 48 kHz stereo WAV and check for noise and clipping before mixing.
- No faces of real people, logos or brand marks from image results. Photos are reference or background only.
- Every download is written to `attribution.json` with title, creator, licence, source page and a ready credit line. Nothing is used without a log entry.
- Anonymous use is rate limited. Search a few times, pick, download. Do not loop or bulk download.

## Credits go in the description
Add a "Sound and image credits" block with one line per `credit` in the log. CC0 and public-domain items still list the source. If nothing from Openverse is used, leave the block out.
