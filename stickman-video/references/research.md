# Stickman video research — 50 YouTube tutorials (Oct 2026)

Source: 50 most-viewed tutorials for "stick figure / stickman / người que" video making (EN + VN), each watched by Gemini and summarised.
Full per-video notes (tools, verbatim prompts, settings): `video-notes.md` (search it by channel name or keyword).

## 1. What works (consensus across tutorials)

| Rule | Evidence (channel) |
|---|---|
| **Voice first, visuals second.** The voiceover is the timing ruler. Generate it, remove dead air, then cut one visual per sentence/beat. | zapiwala ai ("generating images first wastes 10+ h"), Ai pay you, Grow With Kaz, MAGIC AUTOMATION, Creator Now |
| **One image per sentence / beat.** Long-form: 3–6 s per image (~150 images per 10 min). Shorts: 2–4 s. | MAGIC AUTOMATION (150 sentences = 150 images), Leo Ai, Benpiaz, Syrax |
| **Static images + slow zoom/pan are enough** for explainer channels. Animate only the hook (first 5–10 scenes, ~18 s). | Money Degree, Saidox, Leo Ai ("static performs as well"), AI PIPELINE |
| **Lock the style + character text and paste it into every prompt.** One continuous paragraph, no bullet lists inside prompts. | FLOT ("Global Consistency Lock + Main Character Lock"), Jacksons AI, Mark Ai Guy |
| **Character reference sheet** (front/side/3-4/back + expressions + poses) attached as reference image to every generation. | Mark Ai Guy, Jacksons AI, AI Playbook, Hoang Labz, Earnings Blueprint |
| **No text inside AI images** (garbled letters). Put words in captions or edit overlays. Exception: 1–3 bold English words. | Hồ Mạnh Thắng, Benpiaz, Earnings Blueprint (uses short headers) |
| **Style drift guard for image-to-video:** "keep exact black-and-white line art / 2D look, static camera, no colour, no 3D, no extra limbs, no lip-sync". | Ryan Brooks, Lee Dea Hwang, AI Rush Hour ("Static camera"), Ai pay you |
| **Remove silence** from TTS (threshold ~-40 dB, keep ≤0.15–0.3 s pauses) for retention. | Lilly's Tech Tips (Audacity Truncate Silence), zapiwala ai (0.15 s) |
| **Music low:** -15 to -20 dB under voice (≈5–15 % volume), fade in/out. | almost all |
| **Captions:** bold sans, white/yellow with black stroke, lower third, not over faces. | Mark Ai Guy (CapCut "Quick"), Benpiaz |
| **Hook in first 15–30 s**, curiosity loop every 20–30 s, end with open question / CTA. | BigStepsMedia, Benpiaz, Creator Now, Nhân Lý MMO |
| **Generate TTS in small chunks** (2–3 sentences) for better pacing. | Jacksons AI (ElevenLabs v3) |
| **Mute AI video clip audio**, keep your own narration track. "Baked" voice in video models causes mouth/sync glitches. | Jacksons AI, Hồ Mạnh Thắng |

## 2. Formats and niches

- **Long-form 16:9, 8–15 min** (mid-roll ads): ancient humans / prehistoric life, dark or weird history, psychology & human behaviour, "Why do we…?", finance explainers, "What if / POV you are…". Reference channels: Zenn, Ink Explainer, Mack Explains, Axen/Axenn, Franz, The Paint Explainer, Explain in Paint, Basically Primitive, The Wealth Explainer.
- **Shorts 9:16, 30–60 s** (5–12 scenes): motivation, self-improvement, relationships, comedy (Rico Animations style), money mistakes. Reference: KnowSense, Productive Peter, The Blurb, Rico Animations, Backbench Animations.
- **Vietnamese market:** family / morals / Buddhism / personal growth (Hồ Mạnh Thắng, Đơn Như Lời), "lỗi logic của con người" satire (Nhân Lý MMO). Common VN play: localise a proven English topic, or produce in a foreign language (Korean, Spanish) for higher RPM (MAGIC AUTOMATION, Creator Now).
- Revenue claims in tutorials are SocialBlade/NexLev estimates and promo material for tools. Treat them as marketing, not data.

## 3. Visual style families (see prompt-library.md for exact text)

1. **Doodle explainer** (Zenn / Ink Explainer / Mack): flat colours, thick uniform black outline, oversized round white/cream head, dot eyes, earthy muted palette + 1 accent, cream paper bg.
2. **Rico B&W**: pure black line art on pure white, bold outlines, exaggerated expressions, no colour at all. Comedy shorts.
3. **Paper motivation** (Productive Peter / The Blurb): black ink stick figures on cream/brown paper texture, a red accent word.
4. **MS Paint satire** (The Paint Explainer): crude thin lines, pastel fills, meme sketch, googly eyes.
5. **Vintage pencil** (VN family/moral channels): pencil sketch on old paper, cinematic warm tone.
6. **Chalkboard**: white chalk figures on a black board with coloured icons.

## 4. Tool landscape (what creators use; skill replaces most of it)

| Stage | Popular tools | This skill |
|---|---|---|
| Script / prompts | ChatGPT, Claude, Gemini master prompts | Claude writes plan.json directly |
| Voice | ElevenLabs (v3, Turbo 2.5), Google AI Studio Gemini TTS, Edge-TTS, Vbee, Luvvoice | `tts` (elevenlabs / gemini / say) |
| Images | Google Flow (Nano Banana 2 / Pro), Whisk, Leonardo Flux, Reve, OpenArt | `sheet` + `images` (Gemini image API with reference sheet) |
| Animation | Flow Omni Flash, Veo 3.1 Lite, Grok Imagine, Seedance, Hailuo, Kling 3.0, Comico | manual: `export` prompts, drop clips into `clips/` |
| Edit | CapCut (+ Auto CapCut sync tools), Canva | `render` (ffmpeg Ken Burns + captions + music + loudnorm) |
| All-in-one SaaS | Vsub, TopView, Korpi, Lumina, Oloi, DomoAI, Digital Maker AI | — |

Model notes from tutorials: Seedance 1.0/2.0 is good and cheap for 2D; avoid Kling 2.6 for stickman (AI Rush Hour). Grok reproduces crude doodle style better than Veo (Winter Medal China). Veo/Flow watermark: crop ~105 % or cover with a logo. Space Veo batch jobs 30–60 s apart to avoid account locks (Hồ Mạnh Thắng).

## 5. Platform rules

- YouTube: mark "Altered or synthetic content = Yes". "Made for kids = No".
- Avoid "reused content" demonetisation: original script, real editing, not raw AI dumps or ripped frames from other channels (one VN tutorial extracts competitor frames — do NOT do that).
- Music: use licensed/royalty-free tracks only (YouTube Audio Library, Suno Pro for commercial use).
