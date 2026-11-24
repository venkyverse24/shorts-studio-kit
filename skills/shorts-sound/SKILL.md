---
name: shorts-sound
description: Narration, sound effects, mixing and subtitles for Shorts. Load before generating or mixing any audio. The narration tool comes from brand.md.
---

# Sound

## Voice
- Use the narration tool in `brand.md`. Write one audio file per scene plus `audio/timing.json` (scene lengths and word times) so the picture can be timed to real speech.
- Speak exactly what `storyboard/script.md` says. If the script must change (too long or too short, a word the voice garbles), change the script first, through the script stage, so research can check the new claims and QC compares like with like. Never ship narration that differs from the script.
- Do not regenerate narration that already exists or that costs paid credits without asking.
- If the transcript check (faster-whisper / ctranslate2) crashes or runs out of memory on a machine with plenty of free RAM, set the environment variable `CT2_USE_MKL=0` and rerun. It fixed this once; do not apply it unless the crash happens. Never run the transcript check while a render is running.
- Text-to-speech often garbles digits: write numbers as words, then transcribe the final audio (for example with faster-whisper) and compare it with the script.

## Music and effects
- Default: voice only. Add music or effects only when `brand.md` or the film's style asks.
- Sound sources, in order: Earshot (`shorts-earshot`, synthesised, no licence work), Openverse (`shorts-openverse`, real recordings, credits required), then any generator the project already has.
- Place each effect on a real picture moment (a cut, a hit, a door closing), not on a timer. Keep effects below the voice.
- If any music is present, export two audio versions: with music and without.

## Mix and delivery
- Stereo, 48 kHz (re-encode other rates), loudness about -14 LUFS unless `brand.md` says otherwise, true peak under -1 dB.
- Video H.264 with AAC audio, 1080x1920, 30 fps, length within the Shorts limit stated in `brand.md` (default 3:00).
- Subtitles: burned in at the bottom inside the safe area, at most two rows of about 33 characters, plus a separate `.srt`.
- Put the AI-voice disclosure in the description (and on screen if `brand.md` says so).
