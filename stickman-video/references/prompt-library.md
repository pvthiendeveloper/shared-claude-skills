# Prompt library (proven text from the 50 tutorials, adapted)

Put the chosen STYLE text in `plan.json → style`. Put each CHARACTER LOCK in `characters[].lock`. The script appends both to every scene prompt, attaches the reference sheet, and adds the no-text / no-3D rules. Prompts stay in **English** even for Vietnamese videos (image models follow English better; Nhân Lý MMO tip).

## STYLE presets

**doodle** (default, long-form explainer; Zenn / Ink Explainer / Mack):
> Hand-drawn 2D doodle stickman explainer cartoon, like a marker-drawn web comic. Thick uniform black outlines with rounded ends, flat solid colours, no shading, no gradients, no texture on characters. Muted earthy palette (tan, warm brown, sage green, dusty grey, cream) with one warm orange or yellow accent. Simple flat background with few props and plenty of empty space, soft cream paper tone.

**rico-bw** (comedy shorts):
> Rico Animation-style illustration: clean black-and-white vector-style line drawing with bold outlines, expressive exaggerated facial features and a minimalistic background. Black characters and objects on a pure white background. No colours, no gradients, no shading, no grey fills.

**paper** (motivation, Productive Peter / The Blurb):
> Minimal hand-drawn black ink stick figures on an off-white crumpled vintage paper texture. Thin confident marker lines, almost no colour except one dark red accent object. Lots of empty paper space, centred composition, calm motivational mood.

**mspaint** (satire, The Paint Explainer):
> MS Paint style doodle cartoon, simple meme sketch, deliberately low-effort drawing. Thin wobbly black lines, flat pastel fills, exaggerated sarcastic expressions, googly eyes when shocked. Plain white background with only the props needed for the joke.

**pencil** (VN family / moral stories):
> Classic pencil sketch illustration on aged warm vintage paper, fine expressive graphite strokes with light watercolour washes, cinematic warm lighting, gentle and emotional mood, high detail on props but simple stick-figure people.

**chalk**:
> White chalk stick-figure drawings on a dark charcoal blackboard, slightly rough chalk texture, a few coloured chalk accents (yellow, light blue, pink) for key objects, educational lecture feel.

**flat-color** (finance / modern life; Jacksons AI, AI Rush Hour):
> Clean 2D flat vector cartoon, minimal style, thick clean black outlines, solid flat colours with no shading or gradients, simple geometric shapes, solid pale beige background with minimal room decor.

## CHARACTER LOCK examples (one paragraph, every visible trait fixed)

- Modern guy: `a stickman with a large pure-white round head, two small solid black oval eyes, short thick black eyebrows, tiny curved line mouth, messy spiky brown hair, olive-green hoodie, dark grey jeans, dark grey sneakers, thin black stick arms and legs, solid black mitten hands.`
- Caveman: `a caveman stickman with a large round white head, two big solid black oval eyes, small curved mouth, messy dark-brown hair, ragged brown animal-hide tunic, thin black stick arms and legs, small black oval hands and feet.`
- Vietnamese narrator: `a stickman with a large round cream head, black dot eyes, short black side-parted hair, plain light-blue polo shirt, navy trousers, thin black stick limbs.`
- Rico style: `A stick figure named Bob: round head, two dot eyes, thick black eyebrows, short spiky hair, plain black outline body, no clothes detail.` (prefix names with "a stick figure named …" — Rico tutorials)

Tips: give each character 1 fixed accessory (scarf, cap, colour) so the model keeps identity. Never describe the character differently between scenes. For crowds write "simple background stick figures without faces".

## Scene image_prompt (what Claude writes per scene)

Describe ONE frozen moment: who, pose, facial expression, 1–4 props, setting, camera (wide / medium / close-up). Visual metaphors beat literal text: a clock melting = wasted time, a heavy backpack labelled-free = burden. Examples:

- `The modern guy slumps on a sofa scrolling his phone at night, dull tired eyes, empty snack bags around him, a wall clock showing 2 AM. Medium shot.`
- `Infographic frame: a large blue smartphone icon next to the guy's silhouette, a simple counter reaching 100. No other characters.` (+ `image_text: "100 CHECKS / DAY"`)
- `Wide establishing shot of a prehistoric savannah at sunset, three tiny caveman stickmen walking in a line carrying spears. No close-up characters.`
- Variety rule (AI Rush Hour): every 4–6 scenes add one no-character establishing or detail shot.

## motion (render Ken Burns)

`zoom_in` (default, focus/tension), `zoom_out` (reveal/conclusion), `pan_left`, `pan_right` (journey, comparison), `pan_up`, `pan_down`, `static`. Alternate them; do not use the same move 3 times in a row.

## motion_prompt (optional, only for scenes you will animate in Flow/Veo/Grok)

Short, simple, 1–2 actions, under 4 s of action. `export` adds the style-lock tail automatically. Examples:
- `The stickman slowly turns his head toward the phone and blinks twice.`
- `He drops the toothbrush in surprise, then scratches his head.`
- `The campfire flickers; the caveman leans forward and rubs his hands.`

## Script prompts (Claude follows these itself)

- Hook (first 1–3 sentences): a surprising claim or question. "Bạn có biết người tiền sử chưa từng đánh răng, nhưng răng lại tốt hơn chúng ta?"
- Structure (BigStepsMedia): cold open → reveal → backstory → turning point → escalation → climax → takeaway.
- Plant an open question every 20–30 s ("Nhưng điều kỳ lạ nhất chưa phải là ở đó…").
- Simple words (grade-10 level), short sentences, light humour, one idea per sentence.
- Shorts: 30 s ≈ 5–8 scenes, each line ≤ 12–15 words so a scene is ≤ 5 s.
- Long-form VN: ~150 words/min. 8 min ≈ 1,200 words ≈ 100–130 scenes.

## Thumbnail (manual, after render)

16:9, one big expressive stickman, one object, 2–4 word title in bold yellow with thick black stroke (Bungee / Anton), high contrast. Reuse the character sheet as reference.
