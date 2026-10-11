#!/usr/bin/env python3
"""Hand-coded doodle images for cho-pug (no AI). Run: python3 draw_scenes.py [s01,s02...]"""
import sys, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".claude/skills/stickman-video/scripts"))
from svgdraw import *

OUT = Path(__file__).parent / "images"
W, H = 1920, 1080
GY = H * .8
MAN = dict(outfit=PAL["mustard"], hair="messy")

# ---- local props
def mountains(y, c="#B9A27F"):
    return g([poly([(0, y), (300, y - 260), (600, y)], fill=c, w=SW * .7), poly([(420, y), (800, y - 340), (1180, y)], fill="#A99271", w=SW * .7),
              poly([(1000, y), (1450, y - 280), (1920, y)], fill=c, w=SW * .7)])
def hill(cx, top, w=900, c=PAL["grass"]): return path(f"M{cx-w},{H} Q{cx},{top-120} {cx+w},{H} Z", fill=c, w=SW * .8)
def winding_road():
    return path(f"M-50,{H} C400,{GY} 200,{GY-120} 700,{GY-140} S1300,{GY-260} 1700,{GY-300}", w=70, c="#D9C29A", extra='opacity="1"')
def bow_weapon(x, y): return g([path(f"M{x},{y-120} Q{x+70},{y} {x},{y+120}", w=SW, c=PAL["brown"]), line([(x, y - 120), (x, y + 120)], w=3)])
def dog_head(x, y, s=1.0):
    return g([ellipse(x, y, 85 * s, 75 * s, fill="#C9C2B5", w=SW), path(f"M{x+60*s},{y-10*s} L{x+230*s},{y+5*s} Q{x+260*s},{y+40*s} {x+225*s},{y+60*s} L{x+50*s},{y+60*s} Z", fill="#C9C2B5", w=SW),
              ellipse(x + 240 * s, y + 20 * s, 22 * s, 18 * s, fill=INK, w=0), circle(x + 20 * s, y - 20 * s, 14 * s, fill=INK, w=0),
              path(f"M{x-50*s},{y-55*s} Q{x-120*s},{y+20*s} {x-70*s},{y+90*s} Q{x-40*s},{y+20*s} {x-30*s},{y-60*s} Z", fill="#8E8576", w=SW * .7)])
def table_tea(x, y):
    o = [rect(x - 130, y - 160, 260, 30, fill="#fff", r=6, w=SW * .8), line([(x - 100, y - 130), (x - 100, y)], w=SW), line([(x + 100, y - 130), (x + 100, y)], w=SW)]
    for dx in (-60, 50): o += [path(f"M{x+dx-28},{y-200} L{x+dx+28},{y-200} L{x+dx+20},{y-162} L{x+dx-20},{y-162} Z", fill=PAL["blue"], w=SW * .6)]
    return g(o)
def drop(x, y, s=1.0, c="#7FB8E0"): return path(f"M{x},{y-30*s} Q{x+22*s},{y} {x},{y+14*s} Q{x-22*s},{y} {x},{y-30*s} Z", fill=c, w=SW * .5)
def cloth(x, y, r): return rect(x - 20, y - 18, 60, 40, fill=PAL["blue"], r=8, w=SW * .5)
def roller(x, y, r): return g([line([(x, y), (x + 50, y - 60)], w=SW), rect(x + 30, y - 110, 90, 55, fill="#fff", r=14, w=SW * .7)])
def book(x, y, r): return rect(x - 45, y - 35, 90, 60, fill=PAL["red"], r=6, w=SW * .6)
def dag(x, y, r): return dagger(x, y, 1.0)
def heat(x, y): return g([path(f"M{x+i*40},{y} q15,-25 0,-50 q-15,-25 0,-50", w=5, c=PAL["orange"]) for i in range(4)])
def cape_pug(x, y, s=1.0): return path(f"M{x-40*s},{y-150*s} Q{x+150*s},{y-210*s} {x+260*s},{y-110*s} L{x+40*s},{y-60*s} Z", fill=PAL["red"], w=SW * .8)
def thorn(x, y): return g([path(f"M{x},{y} Q{x+120},{y-60} {x+260},{y-20}", w=SW, c=PAL["brown"])] + [line([(x + k, y - 20 - k * .1), (x + k + 10, y - 50 - k * .1)], w=5, c=PAL["brown"]) for k in (60, 130, 200)])
def wrinkle_glow(x, y, s):
    r = 60 * s; hy = y - 2.05 * r; hr = .95 * r
    o = [path(f"M{x-hr*(.42-k*.08)},{hy+hr*wy} Q{x},{hy+hr*(wy-.1)} {x+hr*(.42-k*.08)},{hy+hr*wy}", w=SW * 1.2, c=PAL["orange"]) for k, wy in enumerate((-.72, -.58))]
    o.append(line([(x, hy - hr * .8), (x, hy - hr * .5)], w=SW * 1.2, c=PAL["orange"]))
    return g(o)
def smalldog_lines(x, y): return fx_lines(x, y, 3, 50, 180, spread=25)

S = {}
def scene(fn): S[fn.__name__] = fn; return fn

@scene
def s01():
    sc = Scene("palace"); sc.add(lantern(500, 180, 1.4), lantern(1420, 180, 1.4), lantern(960, 120, 1.0))
    sc.add(cushion(960, 800, 420)); sc.add(pug(960, 790, 1.5, "sit", "happy")); sc.add(sparkle(1180, 430), sparkle(740, 480, .7), sparkle(1220, 600, .6)); return sc
@scene
def s02():
    sc = Scene("plain"); sc.add(pug(960, 1050, 4.0, "sit", "sparkle")); return sc
@scene
def s03():
    sc = Scene("dusk"); sc.add(mountains(GY - 60), winding_road(), pagoda(1650, GY - 300, .55), pagoda(1800, GY - 280, .45))
    sc.add(pug(330, 1000, .9, "stand", "happy", flip=True)); return sc
@scene
def s04():
    sc = Scene("dusk"); sc.add(mountains(GY - 120), sun(1500, 330, 90, rays=False))
    sc.add(rect(150, GY - 170, 1620, 170, fill="#C9A77F", r=4, w=SW * .8))
    for x, s_ in ((450, .9), (960, 1.3), (1450, .9)): sc.add(pagoda(x, GY - 170, s_))
    for x in range(200, 1760, 120): sc.add(rect(x, GY - 200, 60, 30, fill="#C9A77F", r=3, w=SW * .6))
    return sc
@scene
def s05():
    sc = Scene("palace"); sc.add(throne(960, GY + 10)); sc.add(bow_weapon(1650, GY - 140))
    sc.add(stickman(960, GY - 60, 1.15, "sit_hold", "smile", outfit=PAL["gold"], hair=None, hat="emperor"))
    sc.add(pug(985, GY - 175, .75, "sit", "happy")); sc.add(lantern(420, 200), lantern(1500, 200)); return sc
@scene
def s06():
    sc = Scene("plain"); sc.add(pug(960, 1290, 6.0, "sit", "happy")); sc.add(wrinkle_glow(960, 1290, 6.0)); return sc
@scene
def s07():
    sc = Scene("sea"); sc.add(sun(250, 200, 70), cloud(700, 220, 1.1), cloud(1500, 160, .8))
    sc.add(ship(960, 760, 1.25)); sc.add(pug(1250, 690, .75, "stand", "happy", flip=True)); sc.add(waves(800, W + 240)); sc.add(fx_lines(1420, 560, 3, 60, 0)); return sc
@scene
def s08():
    sc = Scene("outdoor"); sc.add(castle(1500, GY + 20, 1.0), cloud(500, 200), hill(700, 560, 900))
    sc.add(cape_pug(700, 640, 1.2)); sc.add(pug(700, 640, 1.2, "stand", "happy", flip=True)); sc.add(sun(1750, 170, 60)); return sc
@scene
def s09():
    sc = Scene("night"); sc.add(tent(960, GY, 1500, 760, "#8C7B5E"))
    sc.add(bed(1350, GY, 560, PAL["navy"])); sc.add(stickman(1430, GY - 175, .75, "stand", "sleep", outfit=PAL["orange"], hair="messy", rot=-90))
    sc.add(stickman(400, GY, 1.0, "point", "scared", outfit=PAL["navy"], hair=None, hat="mask", item=dag))
    sc.add(pug(820, GY, 1.0, "stand", "bark")); sc.add(fx_lines(640, GY - 150, 3, 70, 200)); return sc
@scene
def s10():
    sc = Scene("outdoor"); sc.add(flag(300, GY), flag(1550, GY), castle(960, GY - 10, .6), confetti(W, H, 50))
    sc.add(stickman(960, GY + 120, 1.2, "hold_up", "laugh", outfit=PAL["orange"], hair="messy", hat="crown")); sc.add(pug(960, 520, .8, "sit", "sparkle")); return sc
@scene
def s11():
    sc = Scene("room"); sc.add(window(1500, 380, 320, 300), rect(380, 120, 260, 340, fill=PAL["gold"], r=8, w=SW * .8), rect(410, 150, 200, 280, fill="#F7E7C8", r=6, w=SW * .6))
    sc.add(stickman(820, GY, 1.2, "hold_front", "smile", outfit="#fff", dress=True, hair="long", hat="tiara"))
    sc.add(rect(1060, GY - 170, 220, 30, fill=PAL["red"], r=8, w=SW * .8), line([(1080, GY - 140), (1080, GY)], w=SW), line([(1260, GY - 140), (1260, GY)], w=SW))
    sc.add(pug(1170, GY - 170, .8, "sit", "happy", collar=PAL["gold"])); sc.add(heart(1010, 380, 1.0)); return sc
@scene
def s12():
    sc = Scene("room"); sc.add(bed(1350, GY, 620, PAL["purple"]))
    sc.add(stickman(800, GY - 40, 1.1, "jump_pain", "shock", outfit=PAL["navy"], hair=None, hat="bicorne"))
    sc.add(pug(1030, GY, .85, "stand", "angry")); sc.add(fx_lines(700, 350, 3, 60, 220))
    sc.add(stickman(1700, GY, .8, "stand", "laugh", outfit="#fff", dress=True, hair="long", hat="tiara")); return sc
@scene
def s13():
    sc = Scene("outdoor"); sc.add(tree(250, GY), tree(1700, GY, .9), table_tea(1180, GY))
    sc.add(stickman(800, GY, 1.1, "hands_hips", "smile", outfit=INK, dress=True, hair="bun", hair_color="#999", hat="crown"))
    for x, s_, f in ((420, .7, True), (560, .6, False), (1000, .65, True), (1430, .7, False), (1560, .6, True)): sc.add(pug(x, GY + 60, s_, "sit", "happy", flip=f))
    return sc
@scene
def s14():
    sc = Scene("plain"); sc.add(pug(960, 1000, 2.0, "sit", "surprised", rot=-10)); sc.add(question(1340, 230, 1.6)); return sc
@scene
def s15():
    sc = Scene("plain"); sc.add(pug(850, 1010, 3.6, "sit", "surprised")); sc.add(magnifier(870, 640, 1.5))
    sc.add(line([(1060, 830), (1300, 1000)], w=SW * 2.5)); return sc
@scene
def s16():
    sc = Scene("plain"); sc.add(dog_head(420, 520, 1.5)); sc.add(pug(1400, 1250, 2.8, "sit", "happy"))
    sc.add(line([(960, 200), (960, 880)], w=SW * .6, extra='stroke-dasharray="20 18"')); return sc
@scene
def s17():
    sc = Scene("room"); sc.add(window(400, 330, 280, 260, sky=PAL["night"], inner=moon(400, 300, 45)), sofa(1050, GY, 640))
    sc.add(pug(1060, GY - 230, 1.0, "back", "sleep")); sc.add(zzz(1170, 400, 1.3))
    sc.add(stickman(1650, GY, 1.05, "cover_ears", "tired", **MAN)); return sc
@scene
def s18():
    sc = Scene("room"); sc.add(window(700, 340, 360, 320, sky="#FFE7A8", inner=sun(700, 340, 80, rays=True)), thermometer(1350, 560))
    sc.add(pug(960, GY + 80, 1.3, "lie", "pant")); sc.add(drop(820, 640, 1.2), drop(1120, 600)); return sc
@scene
def s19():
    sc = Scene("outdoor"); sc.add(sun(1650, 180, 110)); sc.add(rect(-20, GY - 10, W + 40, 120, fill="#BDB5A6", r=0, w=SW * .7))
    sc.add(stickman(1350, GY + 20, 1.1, "jog", "smile", **MAN, flip=False)); sc.add(pug(380, GY + 70, 1.0, "lie", "pant"))
    sc.add(heat(260, 620), heat(1100, 600), drop(520, 760)); return sc
@scene
def s20():
    sc = Scene("outdoor"); sc.add(f'<rect width="{W}" height="{GY}" fill="#FCE3B8"/>', sun(1500, GY - 20, 120, rays=True), line([(0, GY), (W, GY)], w=SW * .8))
    sc.add(f'<rect y="{GY}" width="{W}" height="{H-GY}" fill="{PAL["grass"]}"/>', tree(250, GY), tree(1800, GY, .8))
    sc.add(stickman(720, GY + 60, 1.05, "walk", "smile", **MAN)); sc.add(pug(1150, GY + 70, .8, "stand", "happy", flip=True))
    sc.add(leash((770, GY - 140), (1210, GY - 30))); return sc
@scene
def s21():
    sc = Scene("plain"); sc.add(pug(960, 1160, 5.0, "sit", "happy")); sc.add(drop(1130, 660, 1.6)); sc.add(thorn(1350, 330)); return sc
@scene
def s22():
    sc = Scene("room"); sc.add(window(1550, 330))
    sc.add(pug(760, GY, 1.4, "sit", "sleep")); sc.add(stickman(1100, GY, 1.1, "kneel", "smile", **MAN, flip=True, item=cloth)); sc.add(heart(600, 320, .8)); return sc
@scene
def s23():
    sc = Scene("room"); sc.add(bowl(1150, GY + 20, 2.2)); sc.add(pug(620, GY, 1.4, "sit", "sparkle")); sc.add(drop(640, 640, 1.0, "#9FD3F0"), sparkle(870, 300)); return sc
@scene
def s24():
    sc = Scene("room"); sc.add(fridge(1250, GY))
    sc.add(stickman(900, GY, 1.1, "point", "surprised", **MAN)); sc.add(pug(620, GY + 40, 1.0, "sit", "sparkle")); sc.add(fx_lines(420, GY - 120, 4, 120, 180, spread=12)); return sc
@scene
def s25():
    sc = Scene("plain"); sc.add(pug(560, 900, 1.6, "sit", "happy", fat=.85)); sc.add(pug(1400, 900, 1.6, "sit", "tired", fat=1.55))
    sc.add(drop(1660, 380), drop(1150, 420, .8)); sc.add(line([(960, 200), (960, 880)], w=SW * .6, extra='stroke-dasharray="20 18"')); return sc
@scene
def s26():
    sc = Scene("room"); sc.add(scale_(900, GY + 40)); sc.add(pug(900, GY + 0, 1.0, "stand", "worried" if False else "surprised"))
    sc.add(stickman(1350, GY + 40, 1.05, "kneel", "smile", **MAN, flip=True)); return sc
@scene
def s27():
    sc = Scene("room"); sc.add(sofa(760, GY, 700, PAL["navy"]), hairs(450, 560, 620, 230, 140))
    sc.add(pug(760, GY - 230, .95, "sit", "happy")); sc.add(stickman(1450, GY, 1.1, "point", "shock", **MAN, item=roller)); return sc
@scene
def s28():
    sc = Scene("room"); sc.add(rect(200, 200, 420, 260, fill="#fff", r=6, w=SW * .8))
    sc.add(stickman(960, GY, 1.2, "look_down", "shock", outfit="#33363d", hair="messy")); sc.add(hairs(880, 480, 170, 240, 70, 5))
    sc.add(stickman(420, GY, .95, "point", "laugh", outfit=PAL["grey"], hair="bun", hair_color="#5a3a22"), stickman(1500, GY, .95, "shrug", "laugh", outfit=PAL["green"], hair="messy", flip=True)); return sc
@scene
def s29():
    sc = Scene("room"); sc.add(window(350, 330), door(1700, GY))
    sc.add(stickman(1250, GY, 1.1, "walk", "smile", **MAN)); sc.add(pug(820, GY + 20, .9, "stand", "happy", flip=True)); sc.add(footprints(200, GY + 60, 700, 6)); return sc
@scene
def s30():
    sc = Scene("room"); sc.add(door(1300, GY, 260, 480)); sc.add(pug(880, GY + 20, 1.3, "stand", "sparkle", flip=True)); sc.add(heart(1000, 380, .9)); return sc
@scene
def s31():
    sc = Scene("night"); sc.add(f'<rect width="{W}" height="{GY}" fill="#3A4466"/>', window(1600, 330, 300, 280, sky=PAL["night"], inner=moon(1600, 300, 50)))
    sc.add(bed(800, GY, 900, PAL["blue"])); sc.add(stickman(860, GY - 120, .95, "sit_hold", "smile", **MAN, item=None))
    sc.add(book(860, GY - 280, 1)); sc.add(pug(1080, GY - 165, .75, "lie", "sleep")); sc.add(zzz(1150, 480, .8)); return sc
@scene
def s32():
    sc = Scene("night"); sc.add(f'<rect width="{W}" height="{GY}" fill="#3A4466"/>', window(1450, 420, 380, 360, sky="#1b2236", inner=moon(1520, 350, 40)))
    sc.add(stickman(1440, GY - 120, 1.0, "climb", "surprised", outfit=PAL["navy"], hair=None, hat="mask")); sc.add(sack(1150, GY + 30))
    sc.add(pug(700, GY + 30, 1.1, "stand", "happy", flip=True)); sc.add(fx_lines(560, GY - 150, 3, 50, 200), toy_ball(900, GY + 10), heart(760, 470, .7)); return sc
@scene
def s33():
    sc = Scene("dusk"); sc.add(sun(1450, GY - 200, 110, rays=False), bench(900, GY + 40, 700), tree(250, GY))
    sc.add(stickman(780, GY - 60, 1.0, "sit", "smile", **MAN)); sc.add(pug(1080, GY - 100, .85, "lie", "sleep", old=True))
    for x, y, rr in ((300, 950, 20), (1300, 980, 70), (1600, 940, -30), (500, 1000, 110)): sc.add(leaf(x, y, PAL["orange"], rr))
    return sc
@scene
def s34():
    sc = Scene("outdoor"); sc.add(rect(1150, 330, 600, GY - 330, fill="#F4EEDD", r=8, w=SW * .8), poly([(1110, 340), (1450, 150), (1790, 340)], fill=PAL["red"], w=SW * .8))
    sc.add(stickman(1450, GY, 1.1, "point", "smile", outfit=PAL["green"], hair=None, hat="beanie", flip=True))
    sc.add(stickman(700, GY, 1.05, "kneel", "smile", **MAN)); sc.add(pug(980, GY + 20, .65, "sit", "sparkle")); sc.add(heart(900, 520, .6)); return sc
@scene
def s35():
    sc = Scene("plain"); sc.add(pug(960, 1130, 4.6, "sit", "beg", rot=-6)); sc.add(sparkle(420, 300), sparkle(1500, 260, .8), sparkle(1600, 520, .6), sparkle(330, 600, .6)); return sc

if __name__ == "__main__":
    ids = sys.argv[1].split(",") if len(sys.argv) > 1 else sorted(S)
    def one(i):
        S[i]().save(OUT / f"{i}.png"); (OUT / f"{i}.svg").unlink(missing_ok=True); return i
    with cf.ThreadPoolExecutor(4) as ex:
        for i in ex.map(one, ids): print(i, end=" ", flush=True)
    print()
