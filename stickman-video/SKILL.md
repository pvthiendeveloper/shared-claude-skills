---
name: stickman-video
description: Make a complete faceless stick-figure (người que / stickman / doodle explainer) video from a topic — script, voiceover, consistent character sheet, one AI image per sentence, Ken Burns motion, captions, music — rendered to MP4 (16:9 long-form or 9:16 Shorts/TikTok). Built from 50 YouTube tutorials (Zenn / Ink Explainer / Rico / The Paint Explainer styles). Use when the user says "làm video người que", "video stickman", "video hoạt hình người que", "phim người que", "stick figure video", "doodle explainer", "kênh người que", or asks to turn a topic/script into a stick-figure video. Also for revisions of a stickman project ("đổi ảnh cảnh s05", "đổi giọng", "thêm nhạc").
---

# Stickman video (người que)

Pipeline script: `S=~/.claude/skills/stickman-video/scripts/stickman.py` (Python stdlib + ffmpeg + PIL). Run `python3 $S --help`.
References (read when needed):
- `references/prompt-library.md`: style presets, character locks, scene/motion prompt rules, script rules. **Read before writing plan.json.**
- `references/research.md`: what works, niches, tools, platform rules (from 50 tutorials).
- `references/video-notes.md`: raw per-video notes with verbatim prompts (grep by channel or keyword).

Projects live in `${STICKMAN_HOME:-~/stickman-videos}/<slug>/` (one folder per video):
`plan.json` (source of truth) · `audio/` · `refs/` (character sheets) · `images/` · `clips/` (optional animated clips) · `work/` · `final/<slug>.mp4 + .srt` · `prompts.md`.

Reply to the user in Vietnamese, short STE sentences. Run autonomously with sensible defaults; ask only for the topic if none is given.

## Defaults (override when the user says so)

| Item | Default |
|---|---|
| Format | 16:9 long-form. "short", "tiktok", "reels" → 9:16 |
| Length | long-form 3–5 min for a first test; Shorts 30–45 s |
| Language | Vietnamese |
| Voice | Gemini TTS `Charon` (works for vi and en). Better Vietnamese: ElevenLabs `eleven_v3` with a Vietnamese voice: set `voice.engine=elevenlabs` and `voice.voice_id` in plan.json. Preview/fallback: `{"engine":"say","voice_name":"Linh"}` (offline macOS) |
| Style | `doodle` preset; comedy → `rico-bw`; motivation → `paper`; satire → `mspaint`; family/moral VN → `pencil` |
| Images | `gemini-3.1-flash-image` (Nano Banana 2). `--model gemini-3-pro-image` for higher quality |
| Music | none unless asked or a track is given (`--music`, -20 dB under voice). Use licensed / royalty-free tracks only and keep their credit lines. |

## Steps

1. **Init.** `python3 $S init <proj> --aspect 16:9|9:16 --lang vi|en`.
2. **Write plan.json** (you, Claude). Read `prompt-library.md` first.
   - `title`, `slug`, `style` (preset text), `characters: [{id, lock}]` (or `{id, ref: "<image path>"}` to use the user's own character image), `voice`, `captions`.
   - `scenes[]`: `{id: "s01", narration, image_prompt, chars: [ids], motion, image_text?, motion_prompt?, pause?}`.
   - Write the script **voice-first**: one sentence or beat per scene. Long-form 3–6 s per scene (≈10–20 words vi). Shorts ≤ 12–15 words.
   - Hook in the first 1–3 scenes. Open question every 20–30 s. Simple words.
   - `image_prompt` = one frozen moment, English, one paragraph. No text in images unless `image_text` (1–3 English words).
   - Add a no-character establishing shot every 4–6 scenes. Alternate `motion`.
   - ElevenLabs v3 accepts audio tags in narration (`[curious]`, `[whispers]`, `[laughs]`). They are removed from captions automatically.
3. **Check.** `python3 $S check <proj>`. Split every scene the script flags as long.
4. **Voice.** `python3 $S tts <proj>`. This writes per-scene wav files with edge silence trimmed, plus `timing.json`. Listen to 1–2 files (`afplay`) only if the user asks. Redo one scene with `--only s07`.
5. **Character sheets.** `python3 $S sheet <proj>`, then `python3 $S contact <proj> --refs`. **Look at the sheet image.** Re-roll with `--force` if the views do not match, have extra limbs, or the wrong style.
6. **Scene images.** `python3 $S images <proj>`, then `python3 $S contact <proj>`. **Look at every contact sheet.**
   - Re-roll a bad scene: edit its `image_prompt` if needed, then `images <proj> --only s05,s12`.
   - Bad means: wrong character design, garbled text, extra limbs, duplicate character, off-style (3D or photo), or the image does not match the narration.
6b. **No image API? Draw the images yourself (free, offline).** `scripts/svgdraw.py` is a code-drawn doodle library. It has these parts:
   - `stickman()`: 19 poses, expressions, outfits, hair, hats (crown, tiara, bicorne, mask…), dress.
   - `pug()`: sit, stand, lie, back.
   - About 40 props: furniture, sun, moon, ship, castle, pagoda, fridge, bowl…
   - Backgrounds: room, outdoor, dusk, night, palace, sea, plain.
   - PNG output via headless Chrome.

   Write `<proj>/draw_scenes.py` with one function per scene. Example: `examples/cho-pug/draw_scenes.py`. Run it, then check the result with `contact`.
   - Close-up of a sitting pug at scale s: pass `y ≈ 560 + 123*s` so the head stays in frame.
   - Add new characters or props to `svgdraw.py` when a topic needs them.
7. **AI motion: use the cheapest mix by default.** The first 5 scenes plus every 4th scene get an AI clip. All other scenes use the Gemini still with free Ken Burns and line boil.
   - Tested and not recommended: AI clips for every scene (a 2-minute video cost ~130 Kling credits). Code-drawn canvas animation looked too plain. Local Wan 2.2 on an M3 Pro was broken and slow.
   - Run `python3 $S aiplan <proj>` (`--hook 5 --every 4`). It lists the scenes that get an AI clip: the first 5, then every 4th scene. It also prints the credit estimate. For 35 scenes that is 12 clips: ~24 credits on Seedance 2.0 Mini 480p, or ~45 on Kling 3.0 at 3–4 s.
   - **Before any paid generation, tell the user the clip count and the total credit cost. Wait for a clear yes.**
   - All other scenes get free motion in `render`: Ken Burns plus hand-drawn "line boil" (3 warped copies cycled at 8 fps).
   - Render the mix: `render <proj> --ai-hook 5 --ai-every 4`. Without `--ai-hook`, every clip present is used.
   - Model prices (Higgsfield, 16:9, silent):

     | Model | Setting | Credits |
     |---|---|---|
     | Seedance 2.0 Mini | 480p, 4 s | 2 |
     | Seedance 1.5 | 480p | 2.4 |
     | Grok Imagine 1.5 Lite | 480p, 3 s | 3 |
     | Kling 3.0 std | 3 s | 3.75 |
     | Kling 3.0 std | 4 s | 5 |
     | Kling 3.0 std | 6 s | 7.5 |

     Kling 3.0 is proven on this style. Seedance Mini is untested; test 1 clip first.
   - Local models on this Mac (M3 Pro 36 GB) were tested and rejected. Wan 2.2 TI2V-5B GGUF took 16 min for a 2 s clip at 832×480, and moving parts broke into blocks. Do not reinstall.
   - Use the Gemini API (reliable, ~35–45 s per clip): `VEO_DUR=4 python3 scripts/veo.py images/<id>.png "<motion_prompt + style-lock tail>" clips/<id>.mp4`.
   - `VEO_DUR` is 4 or 6 (scene ≤ 4 s → 4). Model: veo-3.1-lite-generate-preview.
   - Run clips **one at a time**. Parallel requests hit HTTP 429 quota. On a 429, wait 60 s and retry.
   - Google Flow in Chrome also works but is slow, and its agent asks for 10 credits per clip. Click **Approve**, never "Always approve".
   - Manual alternative: The user may want motion in the first 5–10 scenes.
   - Run `python3 $S export <proj>` to write `prompts.md`.
   - The user animates those scenes in Google Flow / Veo / Grok (start frame = `images/<id>.png`).
   - The user saves the clips as `clips/<id>.mp4`. `render` uses them automatically. Video audio is dropped.
8. **Render.** `python3 $S render <proj> --ai-hook 5 --ai-every 4 [--music <file>] [--music-db -20] [--no-captions]`.
   - Then extract 4 frames and look at them: `ffmpeg -ss <t> -i final/<slug>.mp4 -frames:v 1 work/f.png`.
9. **Deliver.** Give the user these items:
   - The path to `final/`.
   - The duration.
   - What you chose: style, voice, scene count.
   - A YouTube title, a description and 3–5 hashtags.
   - A reminder to set "Altered or synthetic content = Yes".
   - Offer to deliver the file through any messaging or file-sharing tool the user has.

## Revisions

- Change one scene's text: edit `narration`, then run `tts --only <id>` and `render`.
- Change one picture: edit `image_prompt`, then run `images --only <id>` and `render`.
- Change the voice: edit `voice`, then run `tts --force` and `render`.
- Change the style: edit `style`, then run `sheet --force`, `images --force` and `render`. This re-pays for every image, so tell the user first.

## Rules

- Original scripts only. Never rip frames or scripts from other channels (reused-content demonetisation).
- Keys come only from env (`GEMINI_API_KEY`, `ELEVENLABS_API_KEY`). Never print them.
- Failures:
  - HTTP 402 or 429 from Gemini, or 401 from ElevenLabs: stop. Tell the user that the key or credits need attention. You may offer the `say` voice as a preview.
  - Never loop on retries.
- Cost: every image is one paid API call. A 10 min video is about 150 images. Before a long-form run over 60 scenes, tell the user the scene count.
- Captions are timed by character share inside each scene, not by forced alignment. Timing is accurate per scene but approximate inside the scene.
