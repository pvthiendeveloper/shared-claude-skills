# stickman-video: Claude Code skill làm video người que

This skill turns a topic into a finished faceless stick-figure (người que) video. You get an MP4 file (16:9 YouTube or 9:16 Shorts/TikTok). The pipeline has 6 stages:

**script → voice → character sheet → one AI image per sentence → AI clips for key scenes → free motion for the rest → captions → MP4**

The skill is built from 50 YouTube tutorials on stickman channels (Zenn, Ink Explainer, Rico Animations, The Paint Explainer…).

## Kết quả mẫu
- A 2-minute video has about 32–35 scenes. Each scene shows one image while the narrator reads one sentence.
- **Cheapest mix** (default):
  - The first 5 scenes and every 4th scene after that use an AI video clip. That is about 11–12 clips.
  - All other scenes use the AI image with zoom/pan and a hand-drawn "line boil" effect. This part is free.
- Sample cost: about 11 Kling 3.0 clips ≈ 50 Higgsfield credits. Images and voice are billed by Gemini and ElevenLabs.

## Cài đặt
1. Copy the `stickman-video/` folder to `~/.claude/skills/`:
   ```bash
   cp -r stickman-video ~/.claude/skills/
   ```
2. Install the tools:
   - Python 3.10 or later and Pillow: `pip install pillow`.
   - `ffmpeg` with libass: `brew install ffmpeg`.
   - Google Chrome. You need it only to draw images with code (`svgdraw.py`). On Linux, set `CHROME_PATH`.
3. Set the API keys as environment variables. Never write keys in code.
   - `GEMINI_API_KEY` (required): images (Nano Banana 2), Gemini TTS voice, and Veo clips.
   - `ELEVENLABS_API_KEY` (optional): better Vietnamese voice. Set `voice.engine=elevenlabs` and `voice.voice_id` in `plan.json`.
4. (Optional) For Kling/Seedance clips: connect the **Higgsfield MCP** in Claude Code.
5. (Optional) Set a caption font with Vietnamese glyphs: `STICKMAN_FONT="Be Vietnam Pro"` and `STICKMAN_FONT_DIR=/path/to/fonts`. Default: Arial.

## Cách dùng
In Claude Code, type a request like:
> làm video người que về chủ đề chó pug

Claude runs these steps:
1. Writes the script and `plan.json`.
2. Generates the voice.
3. Draws the character sheet and checks it.
4. Draws one image per scene and checks the contact sheets.
5. Tells you the number of AI clips and their credit cost, then **waits for your approval**.
6. Renders the final MP4 in `~/stickman-videos/<slug>/final/`.

Manual commands (see `python3 scripts/stickman.py --help`):
```bash
S=~/.claude/skills/stickman-video/scripts/stickman.py
python3 $S init ~/stickman-videos/my-topic --aspect 16:9 --lang vi
python3 $S check  ~/stickman-videos/my-topic     # after writing plan.json
python3 $S tts    ~/stickman-videos/my-topic
python3 $S sheet  ~/stickman-videos/my-topic
python3 $S images ~/stickman-videos/my-topic
python3 $S aiplan ~/stickman-videos/my-topic     # which scenes need AI clips + credit estimate
python3 $S render ~/stickman-videos/my-topic --ai-hook 5 --ai-every 4
```

## Nội dung gói
| File | Purpose |
|---|---|
| `SKILL.md` | Workflow and rules for Claude |
| `scripts/stickman.py` | Pipeline: init, check, tts, sheet, images, contact, aiplan, render |
| `scripts/veo.py` | Image-to-video with Gemini Veo 3.1 Lite (API) |
| `scripts/svgdraw.py` | Code-drawn stickmen and pug, free and offline, for when no image API is available |
| `references/prompt-library.md` | Style presets, character locks, scene and motion prompt rules |
| `references/research.md` | Summary of 50 tutorials: what works, niches, tools, platform rules |
| `examples/cho-pug/` | Sample `plan.json` (35 scenes) and `draw_scenes.py` |

## Lưu ý
- Gemini AI Studio Tier 1 allows only about **10 Veo clips per day** (2 per minute). Generate clips one at a time.
- YouTube: set "Altered or synthetic content = Yes". Use original scripts. Do not copy frames or scripts from other channels.
- Every image and clip costs money. The skill always reports the cost before it generates paid clips.
