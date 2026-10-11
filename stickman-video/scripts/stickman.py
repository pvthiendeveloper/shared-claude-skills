#!/usr/bin/env python3
"""Stickman (người que) video pipeline: plan.json -> voice -> character sheets -> scene images -> MP4.

Subcommands (all take the project dir):
  init <dir> [--aspect 16:9|9:16] [--lang vi|en]   create dir + plan.json skeleton
  check <dir>                                    validate plan.json, print word/duration estimates
  tts <dir> [--only s01,s02] [--force]           voice per scene -> audio/<id>.wav (+ timing.json)
  sheet <dir> [--force]                          character reference sheets -> refs/<CHAR>.png
  images <dir> [--only ...] [--force] [--model M] scene images -> images/<id>.png
  render <dir> [--music file] [--no-captions]    final/<slug>.mp4 (+ final/<slug>.srt)
         [--ai-hook 5 --ai-every 4]            use AI clips only for those scenes; others get free zoom/pan + line boil
         [--no-boil] [--suffix _mix]
  aiplan <dir> [--hook 5 --every 4]              which scenes need AI clips + credit estimate (cheapest mix)
  contact <dir> [--refs] [--only ...]            contact sheet(s) work/contact_*.jpg for visual QA
  export <dir>                                   prompts.md (image + motion prompts) for manual Flow/Veo/Grok use
  status <dir>                                   asset table
Optional: put an animated clip at clips/<id>.mp4 and render uses it instead of the still (loops/trims to fit).
Keys come from env: GEMINI_API_KEY, ELEVENLABS_API_KEY. Never print them.
"""
import argparse, base64, concurrent.futures as cf, json, os, re, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

FPS = 30
GAP = 0.20          # silence after each scene's line
TAIL = 0.8          # extra hold on the last scene
IMG_MODEL = "gemini-3.1-flash-image"
TTS_MODEL = "gemini-3.8-flash-tts"
FONT_DIR = os.environ.get("STICKMAN_FONT_DIR", str(Path.home() / "Library/Fonts"))
FONT = os.environ.get("STICKMAN_FONT", "Arial")            # caption font (must contain Vietnamese glyphs)
FONT_FILE = os.environ.get("STICKMAN_FONT_FILE", "")      # optional .ttf for contact-sheet labels
NO_TEXT = ("Single image only, not a grid, not a sheet. No text, no letters, no captions, no speech bubbles, "
           "no watermark, no logo. No 3D, no photorealism, no gradients, no realistic human anatomy.")

def die(msg): print("ERROR:", msg, file=sys.stderr); sys.exit(1)
def load(d): return json.loads((Path(d) / "plan.json").read_text())
def size(aspect): return (1920, 1080) if aspect == "16:9" else (1080, 1920)
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: die(" ".join(map(str, cmd[:6])) + " ...\n" + r.stderr[-1500:])
    return r
def dur(f): return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]).stdout.strip())
def words(t): return len(re.sub(r"\[[^\]]*\]", "", t).split())

def http(url, body=None, headers=None, raw=False, tries=4):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json", **(headers or {})}
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, data, h), timeout=300).read()
            return r if raw else json.loads(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")[:400]
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1: time.sleep(8 * (i + 1)); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError) as e:
            if i < tries - 1: time.sleep(5); continue
            raise RuntimeError(str(e))

def gemini(model, parts, gen):
    key = os.environ.get("GEMINI_API_KEY") or die("GEMINI_API_KEY not set")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    r = http(url, {"contents": [{"parts": parts}], "generationConfig": gen})
    try: return r["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError): raise RuntimeError("no content: " + json.dumps(r)[:300])

def pick(scenes, only):
    if not only: return scenes
    ids = set(only.split(","))
    return [s for s in scenes if s["id"] in ids]

# ---------------- init / check / status ----------------
SKELETON = {
    "title": "", "slug": "", "lang": "vi", "aspect": "16:9",
    "voice": {"engine": "gemini", "voice_name": "Charon", "style_prompt": "Đọc giọng kể chuyện ấm áp, rõ ràng:"},
    "style": "", "characters": [], "captions": True, "scenes": []
}

def cmd_init(a):
    d = Path(a.dir); (d / "audio").mkdir(parents=True, exist_ok=True)
    for sub in ("refs", "images", "work", "final"): (d / sub).mkdir(exist_ok=True)
    p = d / "plan.json"
    if p.exists() and not a.force: die(f"{p} exists (use --force)")
    sk = dict(SKELETON, aspect=a.aspect, lang=a.lang, slug=d.name)
    if a.lang != "vi": sk["voice"] = {"engine": "gemini", "voice_name": "Charon", "style_prompt": "Read in a calm, curious documentary storyteller tone:"}
    # ElevenLabs: {"engine": "elevenlabs", "voice_id": "<id>", "model": "eleven_v3", "stability": 0.45, "similarity_boost": 0.8, "style": 0.4}
    p.write_text(json.dumps(sk, ensure_ascii=False, indent=2)); print("created", p)

def cmd_check(a):
    pl = load(a.dir); errs = []
    for k in ("title", "style", "scenes"):
        if not pl.get(k): errs.append(f"missing {k}")
    cids = {c["id"] for c in pl.get("characters", [])}
    total = 0; wps = 2.6 if pl.get("lang") == "vi" else 2.5   # spoken words/sec estimate
    lim = 16 if pl.get("aspect") == "9:16" else 24
    seen = set()
    for s in pl.get("scenes", []):
        if s["id"] in seen: errs.append(f"dup id {s['id']}")
        seen.add(s["id"])
        for c in s.get("chars", []):
            if c not in cids: errs.append(f"{s['id']}: unknown char {c}")
        w = words(s.get("narration", "")); est = w / wps; total += est + GAP
        flag = "  <-- long, split it" if w > lim else ""
        print(f"{s['id']:>5} {w:3d}w ~{est:4.1f}s {s.get('motion','zoom_in'):9} {s.get('narration','')[:60]}{flag}")
    print(f"scenes={len(pl.get('scenes', []))}  est. length ~{total/60:.1f} min")
    if errs: die("; ".join(errs))
    print("plan OK")

def cmd_status(a):
    d = Path(a.dir); pl = load(d)
    t = json.loads((d / "timing.json").read_text()) if (d / "timing.json").exists() else {}
    for c in pl.get("characters", []): print("ref", c["id"], "OK" if (d / "refs" / f"{c['id']}.png").exists() else "--")
    for s in pl["scenes"]:
        i = s["id"]
        print(f"{i:>5} audio:{'OK' if (d/'audio'/f'{i}.wav').exists() else '--'} img:{'OK' if (d/'images'/f'{i}.png').exists() else '--'} {t.get(i,0):5.2f}s")
    print("final:", *(p.name for p in (d / "final").glob("*.mp4")))

# ---------------- TTS ----------------
def tts_eleven(v, text, out_mp3):
    key = os.environ.get("ELEVENLABS_API_KEY") or die("ELEVENLABS_API_KEY not set")
    body = {"text": text, "model_id": v.get("model", "eleven_v3"),
            "voice_settings": {k: v[k] for k in ("stability", "similarity_boost", "style") if k in v}}
    audio = http(f"https://api.elevenlabs.io/v1/text-to-speech/{v['voice_id']}?output_format=mp3_44100_128",
                 body, {"xi-api-key": key, "Accept": "audio/mpeg"}, raw=True)
    Path(out_mp3).write_bytes(audio)

def tts_gemini(v, text, out_raw):
    prompt = (v.get("style_prompt", "") + " " + text).strip()
    parts = gemini(v.get("model", TTS_MODEL), [{"text": prompt}], {
        "responseModalities": ["AUDIO"],
        "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v.get("voice_name", "Charon")}}}})
    b = base64.b64decode(next(p for p in parts if "inlineData" in p)["inlineData"]["data"])
    if b[:4] != b"RIFF":   # raw L16 PCM 24 kHz mono -> wrap
        Path(out_raw + ".pcm").write_bytes(b)
        run(["ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", out_raw + ".pcm", out_raw]); os.remove(out_raw + ".pcm")
    else: Path(out_raw).write_bytes(b)

def tts_say(v, text, out_raw):
    """Offline macOS voice (preview / fallback). vi: Linh, en: Samantha."""
    aiff = out_raw + ".aiff"
    run(["say", "-v", v.get("voice_name", "Linh"), "-r", str(v.get("rate", 185)), "-o", aiff, re.sub(r"\[[^\]]*\]", "", text)])
    run(["ffmpeg", "-y", "-i", aiff, out_raw]); os.remove(aiff)

ENGINES = {"elevenlabs": tts_eleven, "gemini": tts_gemini, "say": tts_say}

TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")

def cmd_tts(a):
    d = Path(a.dir); pl = load(d); v = pl["voice"]; (d / "audio").mkdir(exist_ok=True); (d / "work").mkdir(exist_ok=True)
    todo = [s for s in pick(pl["scenes"], a.only) if a.force or a.only or not (d / "audio" / f"{s['id']}.wav").exists()]
    def one(s):
        raw = str(d / "work" / f"{s['id']}_raw") + (".mp3" if v["engine"] == "elevenlabs" else ".wav")
        ENGINES[v["engine"]](v, s["narration"], raw)
        run(["ffmpeg", "-y", "-i", raw, "-af", TRIM, "-ar", "48000", "-ac", "1", str(d / "audio" / f"{s['id']}.wav")])
        return s["id"]
    with cf.ThreadPoolExecutor(3) as ex:
        for f in cf.as_completed([ex.submit(one, s) for s in todo]):
            try: print("tts", f.result(), flush=True)
            except Exception as e: print("tts FAIL", e, flush=True)
    timing = {s["id"]: round(dur(d / "audio" / f"{s['id']}.wav"), 3) for s in pl["scenes"] if (d / "audio" / f"{s['id']}.wav").exists()}
    (d / "timing.json").write_text(json.dumps(timing, indent=1))
    print(f"voice total {sum(timing.values())/60:.2f} min, {len(timing)}/{len(pl['scenes'])} scenes")

# ---------------- images ----------------
SHEET = ("Create a single full character reference sheet on a plain clean cream background, in three clearly separated rows. "
         "Top row: the same character in four full-body neutral standing views: front, side, three-quarter, back. "
         "Middle row: five head-only expressions of the same character: happy, neutral, surprised, worried, angry. "
         "Bottom row: five full-body poses of the same character: waving, thinking, pointing, walking, shrugging. "
         "Character: {lock} Art style: {style} Keep proportions, colours and line weight identical in every view. "
         "Flat colours only, no shading, no gradients, no 3D.")

def img_parts(refs, text):
    parts = []
    for r in refs:
        parts.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(Path(r).read_bytes()).decode()}})
    return parts + [{"text": text}]

def gen_image(model, aspect, refs, text, out):
    parts = gemini(model, img_parts(refs, text), {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}})
    p = next((p for p in parts if "inlineData" in p), None)
    if not p: raise RuntimeError("no image returned: " + json.dumps(parts)[:200])
    tmp = str(out) + ".src"; Path(tmp).write_bytes(base64.b64decode(p["inlineData"]["data"]))
    run(["ffmpeg", "-y", "-i", tmp, str(out)]); os.remove(tmp)

def cmd_sheet(a):
    d = Path(a.dir); pl = load(d); (d / "refs").mkdir(exist_ok=True)
    for c in pl.get("characters", []):
        out = d / "refs" / f"{c['id']}.png"
        if out.exists() and not a.force: print("sheet exists", c["id"]); continue
        if c.get("ref"):   # user-supplied reference image
            run(["ffmpeg", "-y", "-i", os.path.expanduser(c["ref"]), str(out)]); print("sheet copied", c["id"]); continue
        gen_image(a.model, "16:9", [], SHEET.format(lock=c["lock"], style=pl["style"]), out); print("sheet", c["id"], out)

def scene_prompt(pl, s):
    chars = {c["id"]: c for c in pl.get("characters", [])}
    lines = [pl["style"], "", "Scene: " + s["image_prompt"]]
    if s.get("chars"):
        lines += ["", "The attached image(s) are CHARACTER REFERENCES ONLY: copy each character's look (head, face, clothes, colours, line weight) "
                  "but NEVER copy the reference layout, grid, rows or multiple poses. Draw ONE new scene in which each character appears exactly ONCE:"]
        lines += [f"- {c}: {chars[c]['lock']}" for c in s["chars"]]
    if s.get("image_text"): lines += ["", f'Only text allowed: bold black hand-lettered words "{s["image_text"]}".']
    frame = "Horizontal 16:9 widescreen frame." if pl["aspect"] == "16:9" else "Vertical 9:16 portrait frame, subject centred in the middle third."
    lines += ["", frame, NO_TEXT if not s.get("image_text") else NO_TEXT.replace("No text, no letters, no captions, ", "No other text, ")]
    return "\n".join(lines)

def cmd_images(a):
    d = Path(a.dir); pl = load(d); (d / "images").mkdir(exist_ok=True)
    todo = [s for s in pick(pl["scenes"], a.only) if a.force or a.only or not (d / "images" / f"{s['id']}.png").exists()]
    def one(s):
        refs = [next((f for f in (d / "refs" / f"{c}_single.png", d / "refs" / f"{c}.png") if f.exists()), None) for c in s.get("chars", [])]
        refs = [r for r in refs if r]   # refs/<C>_single.png (one clean view cropped from the sheet) beats the full sheet
        gen_image(a.model, pl["aspect"], refs, scene_prompt(pl, s), d / "images" / f"{s['id']}.png"); return s["id"]
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for f in cf.as_completed([ex.submit(one, s) for s in todo]):
            try: print("img", f.result(), flush=True)
            except Exception as e: print("img FAIL", e, flush=True)
    miss = [s["id"] for s in pl["scenes"] if not (d / "images" / f"{s['id']}.png").exists()]
    print("missing images:", ",".join(miss) if miss else "none")

def cmd_contact(a):
    """Grid of all scene images (or refs) with ids, for visual review."""
    from PIL import Image, ImageDraw, ImageFont
    d = Path(a.dir); pl = load(d)
    items = [(c["id"], d / "refs" / f"{c['id']}.png") for c in pl.get("characters", [])] if a.refs else \
            [(s["id"], d / "images" / f"{s['id']}.png") for s in pick(pl["scenes"], a.only)]
    items = [(i, f) for i, f in items if f.exists()]
    if not items: die("no images")
    tw = 480; cols = 4
    th = int(tw * (9 / 16 if pl["aspect"] == "16:9" or a.refs else 16 / 9))
    sheets = [items[i:i + a.per] for i in range(0, len(items), a.per)]
    try: font = ImageFont.truetype(FONT_FILE, 30) if FONT_FILE else ImageFont.load_default(30)
    except Exception: font = ImageFont.load_default()
    for k, part in enumerate(sheets):
        rows = (len(part) + cols - 1) // cols
        im = Image.new("RGB", (cols * tw, rows * th), "white"); dr = ImageDraw.Draw(im)
        for j, (i, f) in enumerate(part):
            t = Image.open(f).convert("RGB"); t.thumbnail((tw, th))
            x, y = (j % cols) * tw, (j // cols) * th; im.paste(t, (x, y))
            dr.rectangle([x, y, x + 80, y + 40], fill="black"); dr.text((x + 8, y + 2), i, fill="yellow", font=font)
        out = d / "work" / f"contact_{'refs' if a.refs else 'scenes'}_{k+1}.jpg"; im.save(out, quality=85); print(out)

def cmd_export(a):
    """prompts.md for manual tools (Google Flow / Veo / Grok): image prompt + motion prompt per scene."""
    d = Path(a.dir); pl = load(d); lines = [f"# {pl['title']} — prompts\n"]
    for c in pl.get("characters", []): lines += [f"## Character sheet {c['id']}\n", SHEET.format(lock=c["lock"], style=pl["style"]), ""]
    for s in pl["scenes"]:
        lines += [f"## {s['id']}", f"Narration: {s['narration']}", "", "IMAGE:", scene_prompt(pl, s).replace("\n", " ").strip(), ""]
        if s.get("motion_prompt"):
            lines += ["MOTION:", f"{s['motion_prompt']} Static camera, no zoom, no pan. Keep the exact 2D stickman look, line weight, "
                      "colours and background unchanged. No spoken dialogue, no lip-sync, no text, no music, no morphing, no extra limbs.", ""]
    (d / "prompts.md").write_text("\n".join(lines)); print(d / "prompts.md")

# ---------------- render ----------------
def ease(t): return f"(({t})*({t})*(3-2*({t})))"

def motion_vf(kind, W, H, n, d=None):
    t = ease(f"min(on/{max(n-1,1)},1)")
    Z = 0.12
    z, x, y = "1", "0", "0"
    cx, cy = "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"
    if kind == "zoom_in": z, x, y = f"1+{Z}*{t}", cx, cy
    elif kind == "zoom_out": z, x, y = f"{1+Z}-{Z}*{t}", cx, cy
    elif kind == "pan_left": z, x, y = f"{1+Z}", f"(iw-iw/zoom)*(1-{t})", cy
    elif kind == "pan_right": z, x, y = f"{1+Z}", f"(iw-iw/zoom)*{t}", cy
    elif kind == "pan_up": z, x, y = f"{1+Z}", cx, f"(ih-ih/zoom)*(1-{t})"
    elif kind == "pan_down": z, x, y = f"{1+Z}", cx, f"(ih-ih/zoom)*{t}"
    up = 3   # supersample before zoompan to avoid jitter
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},scale={W*up}:{H*up}:flags=lanczos,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={d or n}:s={W}x{H}:fps={FPS},setsar=1,format=yuv420p")

def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60); return f"{int(h)}:{int(m):02d}:{s:05.2f}"
def srt_ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def chunks(text, n):
    w = re.sub(r"\[[^\]]*\]", "", text).split(); out = []; cur = []
    for x in w:
        cur.append(x)
        if len(cur) >= n or (len(cur) >= max(3, n - 2) and re.search(r"[,.!?;:…]$", x)): out.append(" ".join(cur)); cur = []
    if cur: out.append(" ".join(cur))
    return out

def ai_scenes(scenes, hook=5, every=4):
    """Scenes that get an AI video clip: the first `hook`, then every `every`-th scene after it. The rest use free motion."""
    return [s["id"] for k, s in enumerate(scenes, 1) if k <= hook or (every and (k - hook) % every == 0)]

def boil_frames(img, outdir, W, H, k=3, amp=1.8, cell=60, seed=0):
    """Hand-drawn 'line boil': k slightly warped copies of the still, cycled at ~8 fps. Free, keeps the exact art."""
    import random
    from PIL import Image
    outdir.mkdir(parents=True, exist_ok=True)
    im = Image.open(img).convert("RGB"); r = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((l, t, l + W, t + H))
    nx, ny = W // cell + 1, H // cell + 1
    for v in range(k):
        rnd = random.Random(seed * 31 + v)
        pts = [[(min(W, i * cell) + (rnd.uniform(-amp, amp) if 0 < i < nx else 0),
                 min(H, j * cell) + (rnd.uniform(-amp, amp) if 0 < j < ny else 0)) for j in range(ny + 1)] for i in range(nx + 1)]
        mesh = []
        for i in range(nx):
            for j in range(ny):
                x0, y0, x1, y1 = i * cell, j * cell, min(W, (i + 1) * cell), min(H, (j + 1) * cell)
                if x0 >= W or y0 >= H: continue
                ul, ll, lr, ur = pts[i][j], pts[i][j + 1], pts[i + 1][j + 1], pts[i + 1][j]
                mesh.append(((x0, y0, x1, y1), (*ul, *ll, *lr, *ur)))
        im.transform((W, H), Image.Transform.MESH, mesh, Image.BICUBIC).save(outdir / f"f{v}.png")

def cmd_aiplan(a):
    d = Path(a.dir); pl = load(d); t = json.loads((d / "timing.json").read_text()) if (d / "timing.json").exists() else {}
    ids = ai_scenes(pl["scenes"], a.hook, a.every)
    have = [i for i in ids if (d / "clips" / f"{i}.mp4").exists()]
    need = [i for i in ids if i not in have]
    print(f"AI clip scenes ({len(ids)}/{len(pl['scenes'])}): {','.join(ids)}")
    print(f"already have: {','.join(have) or '-'} | still needed: {len(need)} -> {','.join(need) or '-'}")
    for name, c4, c6 in (("Seedance 2.0 Mini 480p", 2, 2.5), ("Kling 3.0 std 3-4s", 3.75, 7.5)):
        cost = sum(c4 if t.get(i, 3) + GAP <= 4 else c6 for i in need)
        print(f"  {name}: ~{cost:g} Higgsfield credits")
    (d / "work").mkdir(exist_ok=True); (d / "work" / "ai_scenes.json").write_text(json.dumps(ids))

def cmd_render(a):
    d = Path(a.dir); pl = load(d); W, H = size(pl["aspect"]); work = d / "work"; work.mkdir(exist_ok=True); (d / "final").mkdir(exist_ok=True)
    sc = pl["scenes"]
    miss = [s["id"] for s in sc if not (d / "audio" / f"{s['id']}.wav").exists()
            or not ((d / "images" / f"{s['id']}.png").exists() or (d / "clips" / f"{s['id']}.mp4").exists())]
    if miss: die("missing audio/image for: " + ",".join(miss))
    subs, t0 = [], 0.0
    jobs = []
    allowed = set(ai_scenes(sc, a.ai_hook, a.ai_every)) if a.ai_hook is not None else None   # None = use every clip present
    for k, s in enumerate(sc):
        speech = dur(d / "audio" / f"{s['id']}.wav")
        D = speech + float(s.get("pause", GAP)) + (TAIL if k == len(sc) - 1 else 0)
        n = max(1, round(D * FPS)); D = n / FPS
        jobs.append((s, n, D))
        cap = 5 if pl["aspect"] == "9:16" else 8
        parts = chunks(s["narration"], cap); tot = sum(len(p) for p in parts) or 1; c = t0
        for p in parts:
            L = speech * len(p) / tot; subs.append((c, c + L, p)); c += L
        t0 += D
    def clip(job):
        s, n, D = job; out = work / f"{s['id']}.mp4"
        anim = d / "clips" / f"{s['id']}.mp4"   # optional AI-animated clip (Flow/Veo/Grok) replaces the still
        if anim.exists() and (allowed is None or s["id"] in allowed):
            run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(anim), "-frames:v", str(n), "-an",
                 "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1,format=yuv420p",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(FPS), str(out)])
        elif not a.no_boil:
            bd = work / f"boil_{s['id']}"; boil_frames(d / "images" / f"{s['id']}.png", bd, W, H, seed=hash(s["id"]) % 997)
            run(["ffmpeg", "-y", "-stream_loop", "-1", "-framerate", "8", "-i", str(bd / "f%d.png"), "-frames:v", str(n),
                 "-vf", "fps=%d," % FPS + motion_vf(s.get("motion", "zoom_in"), W, H, n, d=1),
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(FPS), str(out)])
        else:
            run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(d / "images" / f"{s['id']}.png"), "-frames:v", str(n),
                 "-vf", motion_vf(s.get("motion", "zoom_in"), W, H, n), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(FPS), str(out)])
        run(["ffmpeg", "-y", "-i", str(d / "audio" / f"{s['id']}.wav"), "-af", f"apad=whole_dur={D:.4f}", "-t", f"{D:.4f}",
             "-ar", "48000", "-ac", "1", str(work / f"{s['id']}_pad.wav")])
        return s["id"]
    with cf.ThreadPoolExecutor(4) as ex:
        for i in ex.map(clip, jobs): print("clip", i, flush=True)
    (work / "v.txt").write_text("".join(f"file '{s['id']}.mp4'\n" for s, _, _ in jobs))
    (work / "a.txt").write_text("".join(f"file '{s['id']}_pad.wav'\n" for s, _, _ in jobs))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "v.txt"), "-c", "copy", str(work / "video.mp4")])
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "a.txt"), "-c", "copy", str(work / "voice.wav")])
    slug = pl.get("slug") or d.name
    srt = d / "final" / f"{slug}.srt"
    srt.write_text("".join(f"{i+1}\n{srt_ts(b)} --> {srt_ts(e)}\n{t}\n\n" for i, (b, e, t) in enumerate(subs)))
    # audio mix: voice + optional music at about -18 dB under voice, then loudnorm -14 LUFS
    music = a.music or pl.get("music")
    if music:
        fa = (f"[1:a]aloop=loop=-1:size=2e9,volume={a.music_db}dB,afade=t=in:d=1.5,afade=t=out:st={max(t0-2.5,0):.2f}:d=2.5[m];"
              f"[0:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        run(["ffmpeg", "-y", "-i", str(work / "voice.wav"), "-i", os.path.expanduser(music), "-filter_complex", fa, "-map", "[a]",
             "-t", f"{t0:.3f}", "-ar", "48000", "-c:a", "pcm_s16le", str(work / "mix.wav")])
    else:
        run(["ffmpeg", "-y", "-i", str(work / "voice.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", str(work / "mix.wav")])
    vf = []
    if pl.get("captions", True) and not a.no_captions:
        fs = 64 if pl["aspect"] == "16:9" else 78; mv = 70 if pl["aspect"] == "16:9" else 520
        ass = work / "caps.ass"
        ass.write_text("[Script Info]\nScriptType: v4.00+\nPlayResX: %d\nPlayResY: %d\nWrapStyle: 0\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: C,%s,%d,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,2,2,80,80,%d,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" % (W, H, FONT, fs, mv)
            + "".join(f"Dialogue: 0,{ts(b)},{ts(e)},C,,0,0,0,,{t}\n" for b, e, t in subs))
        vf = ["-vf", f"ass={ass}:fontsdir={FONT_DIR}"]
    out = d / "final" / f"{slug}{a.suffix}.mp4"
    run(["ffmpeg", "-y", "-i", str(work / "video.mp4"), "-i", str(work / "mix.wav"), *vf, "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", str(out)])
    print(f"done {out}  ({dur(out):.1f}s)  srt: {srt}")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init"); p.add_argument("dir"); p.add_argument("--aspect", default="16:9", choices=["16:9", "9:16"]); p.add_argument("--lang", default="vi"); p.add_argument("--force", action="store_true")
    for name in ("check", "status", "export"): sp.add_parser(name).add_argument("dir")
    p = sp.add_parser("contact"); p.add_argument("dir"); p.add_argument("--refs", action="store_true"); p.add_argument("--only"); p.add_argument("--per", type=int, default=24)
    p = sp.add_parser("tts"); p.add_argument("dir"); p.add_argument("--only"); p.add_argument("--force", action="store_true")
    p = sp.add_parser("sheet"); p.add_argument("dir"); p.add_argument("--force", action="store_true"); p.add_argument("--model", default=IMG_MODEL)
    p = sp.add_parser("images"); p.add_argument("dir"); p.add_argument("--only"); p.add_argument("--force", action="store_true"); p.add_argument("--model", default=IMG_MODEL); p.add_argument("--workers", type=int, default=4)
    p = sp.add_parser("render"); p.add_argument("dir"); p.add_argument("--music"); p.add_argument("--music-db", type=float, default=-20); p.add_argument("--no-captions", action="store_true")
    p.add_argument("--ai-hook", type=int); p.add_argument("--ai-every", type=int, default=4); p.add_argument("--no-boil", action="store_true"); p.add_argument("--suffix", default="")
    p = sp.add_parser("aiplan"); p.add_argument("dir"); p.add_argument("--hook", type=int, default=5); p.add_argument("--every", type=int, default=4)
    a = ap.parse_args()
    {"init": cmd_init, "check": cmd_check, "status": cmd_status, "tts": cmd_tts, "sheet": cmd_sheet, "images": cmd_images, "render": cmd_render, "aiplan": cmd_aiplan, "contact": cmd_contact, "export": cmd_export}[a.cmd](a)

if __name__ == "__main__": main()
