#!/usr/bin/env python3
"""Free, offline doodle renderer: stickmen, a pug, props, backgrounds -> SVG -> PNG (headless Chrome).

Use when no image API is available, or for a fully consistent hand-coded look.
    from svgdraw import *
    sc = Scene(bg="room"); sc.add(stickman(700, 900, pose="wave", expr="smile")); sc.add(pug(1150, 900)); sc.save("images/s01.png")
Coordinates: 1920x1080 (16:9) or 1080x1920 (9:16). y of a character = ground line under its feet.
"""
import math, os, subprocess, tempfile
from pathlib import Path

INK = "#1c1c1c"
SW = 9  # main stroke width
CHROME = os.environ.get("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")   # Linux: google-chrome
PAL = dict(paper="#F3E9D2", paper2="#EBDDBF", sky="#CFE3E8", sky_dusk="#F2C9A0", night="#2B3550", grass="#A9BD8B",
           sand="#E3CB98", wall="#EAD9B8", floor="#D2B48C", mustard="#E0A93B", fawn="#D9B07C", fawn_d="#B98D5A",
           red="#C8473A", orange="#E8833A", blue="#6F9BC4", navy="#34466B", green="#7FA36B", grey="#9A9A94",
           pink="#E89AA0", gold="#E9C04A", brown="#8B5A2B", white="#FFFFFF", purple="#8A6BA8", cream="#FBF6EA")

def P(*pts): return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

def line(pts, w=SW, c=INK, extra=""):
    return f'<polyline points="{P(*pts)}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'

def path(d, fill="none", w=SW, c=INK, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'

def circle(x, y, r, fill="none", w=SW, c=INK, extra=""):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{c}" stroke-width="{w}" {extra}/>'

def ellipse(x, y, rx, ry, fill="none", w=SW, c=INK, extra=""):
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{c}" stroke-width="{w}" {extra}/>'

def rect(x, y, w_, h, fill="none", r=10, w=SW, c=INK, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w_:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" stroke="{c}" stroke-width="{w}" {extra}/>'

def poly(pts, fill="none", w=SW, c=INK, extra=""):
    return f'<polygon points="{P(*pts)}" fill="{fill}" stroke="{c}" stroke-width="{w}" stroke-linejoin="round" {extra}/>'

def g(items, tf=""):
    return f'<g transform="{tf}">' + "".join(items) + "</g>" if tf else "<g>" + "".join(items) + "</g>"

def shadow(x, y, rx, ry=None): return ellipse(x, y, rx, ry or rx * 0.16, fill="#000", w=0, extra='opacity="0.12"')

# ------------------------------------------------------------------ faces
def face(x, y, r, expr="smile", look=(0, 0), brows=True):
    ex, ey = look[0] * r * 0.12, look[1] * r * 0.12
    o = []
    exy = [(x - r * 0.33 + ex, y - r * 0.08 + ey), (x + r * 0.33 + ex, y - r * 0.08 + ey)]
    if expr in ("sleep", "happy_closed"):
        for X, Y in exy: o.append(path(f"M{X-r*.13},{Y} Q{X},{Y+(r*.12 if expr=='sleep' else -r*.14)} {X+r*.13},{Y}", w=SW * .8))
    else:
        big = expr in ("surprised", "shock", "scared", "sparkle")
        for X, Y in exy:
            o.append(ellipse(X, Y, r * (0.13 if big else 0.1), r * (0.17 if big else 0.14), fill=INK, w=0))
            o.append(circle(X + r * .04, Y - r * .06, r * .04, fill="#fff", w=0))
    if brows:
        by = y - r * 0.38
        if expr == "angry":
            o += [line([(x - r * .5, by - r * .08), (x - r * .15, by + r * .1)], w=SW * .8), line([(x + r * .5, by - r * .08), (x + r * .15, by + r * .1)], w=SW * .8)]
        elif expr in ("worried", "sad", "scared", "tired"):
            o += [line([(x - r * .5, by + r * .08), (x - r * .18, by - r * .06)], w=SW * .8), line([(x + r * .5, by + r * .08), (x + r * .18, by - r * .06)], w=SW * .8)]
        elif expr in ("surprised", "shock"):
            o += [path(f"M{x-r*.5},{by-r*.02} Q{x-r*.33},{by-r*.2} {x-r*.16},{by-r*.04}", w=SW * .8), path(f"M{x+r*.16},{by-r*.04} Q{x+r*.33},{by-r*.2} {x+r*.5},{by-r*.02}", w=SW * .8)]
    my = y + r * 0.38
    if expr in ("smile", "sparkle", "happy_closed"): o.append(path(f"M{x-r*.28},{my-r*.06} Q{x},{my+r*.2} {x+r*.28},{my-r*.06}", w=SW * .85))
    elif expr == "laugh": o.append(path(f"M{x-r*.32},{my-r*.1} Q{x},{my+r*.35} {x+r*.32},{my-r*.1} Z", fill="#7a2e2e", w=SW * .8))
    elif expr in ("surprised", "shock", "scared"): o.append(ellipse(x, my + r * .02, r * .13, r * .17, fill="#7a2e2e", w=SW * .7))
    elif expr in ("sad", "worried", "tired"): o.append(path(f"M{x-r*.22},{my+r*.08} Q{x},{my-r*.1} {x+r*.22},{my+r*.08}", w=SW * .85))
    elif expr == "angry": o.append(line([(x - r * .22, my + r * .05), (x + r * .22, my + r * .05)], w=SW * .85))
    elif expr == "sleep": o.append(ellipse(x, my, r * .08, r * .06, w=SW * .6))
    else: o.append(line([(x - r * .18, my), (x + r * .18, my)], w=SW * .85))
    return o

# ------------------------------------------------------------------ stickman
POSES = {  # (l_elbow, l_hand, r_elbow, r_hand, l_knee, l_foot, r_knee, r_foot) relative to shoulder/hip, in head-radius units
    "stand": [(-.55, 1.0), (-.7, 2.0), (.55, 1.0), (.7, 2.0), (-.25, 1.25), (-.35, 2.45), (.25, 1.25), (.35, 2.45)],
    "wave": [(-.55, 1.0), (-.7, 2.0), (.9, -.4), (1.2, -1.4), (-.25, 1.25), (-.35, 2.45), (.25, 1.25), (.35, 2.45)],
    "point": [(-.55, 1.0), (-.7, 2.0), (1.0, .1), (2.0, -.2), (-.25, 1.25), (-.35, 2.45), (.25, 1.25), (.35, 2.45)],
    "think": [(-.55, 1.0), (-.7, 2.0), (.8, .8), (.35, -.25), (-.25, 1.25), (-.35, 2.45), (.25, 1.25), (.35, 2.45)],
    "shrug": [(-.9, .4), (-1.3, -.3), (.9, .4), (1.3, -.3), (-.25, 1.25), (-.35, 2.45), (.25, 1.25), (.35, 2.45)],
    "cheer": [(-.8, -.5), (-1.0, -1.5), (.8, -.5), (1.0, -1.5), (-.3, 1.25), (-.5, 2.45), (.3, 1.25), (.5, 2.45)],
    "hold_up": [(-.6, -.6), (-.35, -1.6), (.6, -.6), (.35, -1.6), (-.3, 1.25), (-.45, 2.45), (.3, 1.25), (.45, 2.45)],
    "walk": [(-.5, .9), (-.2, 1.9), (.5, .9), (.9, 1.7), (-.35, 1.2), (-.7, 2.4), (.4, 1.15), (.45, 2.45)],
    "run": [(-.7, .5), (-1.1, 1.2), (.7, .7), (1.2, .2), (-.7, 1.0), (-1.2, 2.0), (.6, 1.1), (.4, 2.45)],
    "jog": [(-.6, .6), (-.9, 1.3), (.6, .8), (1.0, .4), (-.5, 1.15), (-.8, 2.3), (.4, 1.2), (.35, 2.45)],
    "sit": [(-.6, .9), (-.9, 1.7), (.6, .9), (.9, 1.7), (-.9, .55), (-1.0, 1.8), (-.6, .55), (-.75, 1.8)],
    "sit_hold": [(-.7, .8), (-.25, 1.25), (.7, .8), (.25, 1.25), (-.9, .55), (-1.0, 1.8), (-.6, .55), (-.75, 1.8)],
    "kneel": [(-.55, 1.0), (-.6, 1.9), (.7, .9), (1.4, 1.2), (-.6, 1.3), (-1.3, 1.5), (.35, 1.0), (.4, 1.75)],
    "cover_ears": [(-.9, .1), (-.55, -.85), (.9, .1), (.55, -.85), (-.25, 1.25), (-.35, 2.45), (.25, 1.25), (.35, 2.45)],
    "jump_pain": [(-.9, -.3), (-1.3, -1.0), (.9, -.3), (1.3, -1.0), (-.2, 1.0), (-.5, 1.9), (.6, .9), (1.0, .4)],
    "hands_hips": [(-.9, .6), (-.4, 1.15), (.9, .6), (.4, 1.15), (-.3, 1.25), (-.45, 2.45), (.3, 1.25), (.45, 2.45)],
    "climb": [(-.6, -.4), (-.5, -1.4), (.7, .2), (1.3, -.3), (-.2, 1.0), (-.6, 1.6), (.4, 1.2), (.5, 2.4)],
    "look_down": [(-.5, .9), (-.3, 1.7), (.5, .9), (.3, 1.7), (-.25, 1.25), (-.35, 2.45), (.25, 1.25), (.35, 2.45)],
    "hold_front": [(-.6, .8), (.1, 1.2), (.6, .8), (1.1, 1.0), (-.25, 1.25), (-.35, 2.45), (.25, 1.25), (.35, 2.45)],
}

def _head_extra(kind, hx, hy, r, color):
    o = []
    if kind == "messy":
        o.append(path(f"M{hx-r*.95},{hy-r*.15} Q{hx-r*.9},{hy-r*1.15} {hx},{hy-r*1.08} Q{hx+r*.95},{hy-r*1.15} {hx+r*.98},{hy-r*.2} "
                      f"L{hx+r*.7},{hy-r*.55} L{hx+r*.45},{hy-r*.4} L{hx+r*.2},{hy-r*.62} L{hx-r*.1},{hy-r*.42} L{hx-r*.35},{hy-r*.65} L{hx-r*.6},{hy-r*.45} Z", fill=color or INK, w=SW * .8))
    elif kind == "long":
        o.append(path(f"M{hx-r*1.0},{hy+r*.9} Q{hx-r*1.25},{hy-r*1.2} {hx},{hy-r*1.1} Q{hx+r*1.25},{hy-r*1.2} {hx+r*1.0},{hy+r*.9} "
                      f"L{hx+r*.75},{hy+r*.2} Q{hx+r*.7},{hy-r*.55} {hx},{hy-r*.55} Q{hx-r*.7},{hy-r*.55} {hx-r*.75},{hy+r*.2} Z", fill=color or "#5a3a22", w=SW * .8))
    elif kind == "bun":
        o.append(circle(hx, hy - r * 1.15, r * .35, fill=color or "#888", w=SW * .8))
        o.append(path(f"M{hx-r*.95},{hy-r*.2} Q{hx},{hy-r*1.35} {hx+r*.95},{hy-r*.2} Q{hx},{hy-r*.75} {hx-r*.95},{hy-r*.2} Z", fill=color or "#888", w=SW * .8))
    elif kind == "caveman":
        o.append(path(f"M{hx-r*1.0},{hy} Q{hx-r*1.2},{hy-r*1.25} {hx},{hy-r*1.15} Q{hx+r*1.2},{hy-r*1.25} {hx+r*1.0},{hy} "
                      f"L{hx+r*.8},{hy-r*.5} L{hx+r*.5},{hy-r*.35} L{hx+r*.3},{hy-r*.6} L{hx},{hy-r*.4} L{hx-r*.3},{hy-r*.62} L{hx-r*.55},{hy-r*.38} L{hx-r*.8},{hy-r*.5} Z", fill=color or "#4a2f1c", w=SW * .8))
    return o

def _hat(kind, hx, hy, r):
    o = []
    if kind == "crown":
        y0 = hy - r * .85
        o.append(poly([(hx - r * .6, y0), (hx - r * .65, y0 - r * .55), (hx - r * .3, y0 - r * .25), (hx, y0 - r * .7), (hx + r * .3, y0 - r * .25), (hx + r * .65, y0 - r * .55), (hx + r * .6, y0)], fill=PAL["gold"], w=SW * .8))
    elif kind == "tiara":
        o.append(path(f"M{hx-r*.55},{hy-r*.78} Q{hx},{hy-r*1.35} {hx+r*.55},{hy-r*.78}", fill=PAL["gold"], w=SW * .7)); o.append(circle(hx, hy - r * 1.02, r * .1, fill=PAL["pink"], w=SW * .5))
    elif kind == "bicorne":
        o.append(path(f"M{hx-r*1.3},{hy-r*.6} Q{hx},{hy-r*1.8} {hx+r*1.3},{hy-r*.6} Q{hx},{hy-r*.95} {hx-r*1.3},{hy-r*.6} Z", fill=INK, w=SW * .8))
        o.append(circle(hx + r * .2, hy - r * 1.05, r * .12, fill=PAL["red"], w=0))
    elif kind == "emperor":
        o.append(rect(hx - r * .75, hy - r * 1.2, r * 1.5, r * .45, fill=INK, r=4, w=SW * .8)); o.append(line([(hx - r * 1.0, hy - r * 1.2), (hx + r * 1.0, hy - r * 1.2)], w=SW))
    elif kind == "mask":
        o.append(rect(hx - r * .95, hy - r * .35, r * 1.9, r * .4, fill=INK, r=8, w=0))
        for X in (hx - r * .33, hx + r * .33): o.append(ellipse(X, hy - r * .15, r * .14, r * .1, fill="#fff", w=0))
    elif kind == "beanie":
        o.append(path(f"M{hx-r*.95},{hy-r*.25} Q{hx},{hy-r*1.6} {hx+r*.95},{hy-r*.25} Z", fill=PAL["red"], w=SW * .8))
    return o

def stickman(x, y, s=1.0, pose="stand", expr="smile", outfit=None, hair="messy", hair_color=None, hat=None,
             dress=False, flip=False, look=(0, 0), rot=0, body_color=None, cape=None, item=None):
    """Big-round-head doodle stickman. outfit = shirt colour (None = plain stick body). y = feet ground line."""
    r = 62 * s
    hip = (x, y - 2.45 * r); sh = (x, y - 4.15 * r); hx, hy = x, y - 5.2 * r
    q = POSES[pose]
    def J(base, d): return (base[0] + (-d[0] if flip else d[0]) * r, base[1] + d[1] * r)
    lsh, rsh = (sh[0] - .25 * r, sh[1] + .1 * r), (sh[0] + .25 * r, sh[1] + .1 * r)
    lhip, rhip = (hip[0] - .2 * r, hip[1]), (hip[0] + .2 * r, hip[1])
    if pose.startswith("sit") or pose == "kneel":
        dy = (0.65 if pose.startswith("sit") else 0.7) * r
        hip = (hip[0], hip[1] + dy); sh = (sh[0], sh[1] + dy); hy += dy; lsh = (lsh[0], lsh[1] + dy); rsh = (rsh[0], rsh[1] + dy)
        lhip, rhip = (lhip[0], lhip[1] + dy), (rhip[0], rhip[1] + dy)
    o = []
    if not rot: o.append(shadow(x, y + 4, r * 1.1))
    if cape: o.append(path(f"M{lsh[0]},{lsh[1]} Q{x-2.2*r*(-1 if flip else 1)},{hip[1]} {x-2.6*r*(-1 if flip else 1)},{hip[1]+.5*r} L{rsh[0]},{rsh[1]} Z", fill=cape, w=SW * .8))
    # legs
    for hp, k, f in ((lhip, q[4], q[5]), (rhip, q[6], q[7])):
        o.append(line([hp, J(hip, k), J(hip, f)]))
        fx, fy = J(hip, f); o.append(ellipse(fx + (-1 if flip else 1) * r * .12 * (1 if f[0] >= 0 else -1), fy + 2, r * .22, r * .11, fill=PAL["white"] if outfit else INK, w=SW * .7))
    # body
    bc = body_color or outfit
    if dress:
        o.append(poly([(sh[0] - .35 * r, sh[1] + .05 * r), (sh[0] + .35 * r, sh[1] + .05 * r), (hip[0] + 1.0 * r, hip[1] + .55 * r), (hip[0] - 1.0 * r, hip[1] + .55 * r)], fill=bc or PAL["white"], w=SW * .85))
    elif bc:
        o.append(path(f"M{sh[0]-.48*r},{sh[1]+.05*r} Q{sh[0]},{sh[1]-.12*r} {sh[0]+.48*r},{sh[1]+.05*r} L{hip[0]+.5*r},{hip[1]+.15*r} Q{hip[0]},{hip[1]+.3*r} {hip[0]-.5*r},{hip[1]+.15*r} Z", fill=bc, w=SW * .85))
    else:
        o.append(line([sh, hip]))
    # arms
    for sp, e, hnd in ((lsh, q[0], q[1]), (rsh, q[2], q[3])):
        o.append(line([sp, J(sh, e), J(sh, hnd)], c=INK))
        hxp, hyp = J(sh, hnd); o.append(circle(hxp, hyp, r * .14, fill=INK, w=0))
    if item: o.append(item(*J(sh, q[3]), r))
    # neck + head
    o.append(line([(hx, hy + r * .9), sh], w=SW))
    o.append(circle(hx, hy, r, fill=PAL["white"], w=SW))
    o += face(hx, hy, r, expr, look)
    if hair: o += _head_extra(hair, hx, hy, r, hair_color)
    if hat: o += _hat(hat, hx, hy, r)
    tf = f"rotate({rot} {x} {y - 2.5 * r})" if rot else ""
    return g(o, tf)

# ------------------------------------------------------------------ pug
def pug(x, y, s=1.0, pose="sit", expr="happy", flip=False, rot=0, tongue=True, collar=None, old=False, fat=1.0):
    """Chubby fawn pug with black mask, big eyes, curled tail. y = ground line. pose: sit|stand|lie|back|run."""
    r = 60 * s; o = []
    F, D = PAL["fawn"], PAL["fawn_d"]
    o.append(shadow(x, y + 3, r * 1.5 * fat))
    if pose in ("stand", "run"):
        bx, by = x, y - r * 1.05
        o.append(path(f"M{bx-.15*r},{by-.55*r} Q{bx+1.6*r},{by-1.0*r} {bx+1.45*r},{by-.1*r}", w=SW * .8, fill="none"))  # tail base
        o.append(path(f"M{bx+1.25*r},{by-.55*r} q{.35*r},{-.45*r} {.05*r},{-.55*r} q{-.3*r},{-.05*r} {-.15*r},{.25*r}", w=SW * .8, fill=F))
        legs = [(-.85, .55), (-.45, .6), (.55, .6), (.95, .55)]
        if pose == "run": legs = [(-1.2, .45), (-.6, .55), (.6, .5), (1.25, .35)]
        for lx, ly in legs: o.append(rect(bx + lx * r - .17 * r, by + .2 * r, .34 * r, .85 * r - (ly - .55) * r, fill=F, r=8, w=SW * .8))
        o.append(ellipse(bx + .1 * r, by, 1.35 * r * fat, .78 * r * fat, fill=F, w=SW))
        hx, hy = bx - 1.15 * r, by - .55 * r
    elif pose == "lie":
        bx, by = x, y - r * .5
        o.append(ellipse(bx + .3 * r, by, 1.55 * r * fat, .55 * r, fill=F, w=SW))
        for lx in (-1.0, -.6): o.append(ellipse(bx + lx * r, by + .45 * r, .32 * r, .14 * r, fill=F, w=SW * .8))
        o.append(path(f"M{bx+1.75*r},{by-.2*r} q{.4*r},{-.4*r} {.1*r},{-.55*r} q{-.3*r},0 {-.2*r},{.25*r}", w=SW * .8, fill=F))
        hx, hy = bx - 1.15 * r, by - .35 * r
    elif pose == "back":   # sleeping on its back, belly up
        bx, by = x, y - r * .75
        o.append(ellipse(bx, by, 1.45 * r * fat, .75 * r, fill=F, w=SW))
        o.append(ellipse(bx + .1 * r, by - .15 * r, .9 * r, .4 * r, fill="#EED3AE", w=0))
        for lx, ang in ((-.7, -25), (-.25, -10), (.35, 10), (.8, 25)):
            o.append(g([rect(bx + lx * r - .16 * r, by - 1.25 * r, .32 * r, .65 * r, fill=F, r=8, w=SW * .8)], f"rotate({ang} {bx+lx*r} {by-.6*r})"))
        hx, hy = bx - 1.45 * r, by + .05 * r
    else:   # sit
        bx, by = x, y - r * 1.0
        o.append(path(f"M{bx+.75*r},{by+.35*r} q{.65*r},{-.25*r} {.4*r},{-.75*r} q{-.35*r},{-.2*r} {-.3*r},{.2*r}", w=SW * .8, fill=F))
        o.append(path(f"M{bx-.85*r*fat},{by+1.0*r} Q{bx-1.05*r*fat},{by-.55*r} {bx},{by-.75*r} Q{bx+1.05*r*fat},{by-.55*r} {bx+.85*r*fat},{by+1.0*r} Z", fill=F, w=SW))
        for lx in (-.42, .42): o.append(rect(bx + lx * r - .16 * r, by + .05 * r, .32 * r, .95 * r, fill=F, r=10, w=SW * .8))
        for lx in (-.78, .78): o.append(ellipse(bx + lx * r * fat, by + .92 * r, .32 * r, .16 * r, fill=F, w=SW * .8))
        hx, hy = bx, by - 1.05 * r
    if collar: o.append(path(f"M{hx-.6*r},{hy+.75*r} Q{hx},{hy+1.05*r} {hx+.6*r},{hy+.75*r}", w=SW * 1.6, c=collar))
    # head
    hr = .95 * r
    for sgn in (-1, 1):  # ears
        o.append(path(f"M{hx+sgn*.55*hr},{hy-.75*hr} Q{hx+sgn*1.25*hr},{hy-.85*hr} {hx+sgn*1.05*hr},{hy-.15*hr} Q{hx+sgn*.85*hr},{hy-.45*hr} {hx+sgn*.55*hr},{hy-.75*hr} Z", fill=INK, w=SW * .6))
    o.append(path(f"M{hx-hr},{hy} Q{hx-hr},{hy-hr*1.0} {hx},{hy-hr} Q{hx+hr},{hy-hr*1.0} {hx+hr},{hy} Q{hx+hr*1.02},{hy+hr*.95} {hx},{hy+hr*.92} Q{hx-hr*1.02},{hy+hr*.95} {hx-hr},{hy} Z", fill=F, w=SW))
    o.append(path(f"M{hx-hr*.72},{hy+hr*.05} Q{hx-hr*.75},{hy+hr*.88} {hx},{hy+hr*.85} Q{hx+hr*.75},{hy+hr*.88} {hx+hr*.72},{hy+hr*.05} Q{hx},{hy-hr*.25} {hx-hr*.72},{hy+hr*.05} Z", fill="#2a2a2a" if not old else "#6d6a66", w=0))
    for k, wy in enumerate((-.72, -.58)):  # forehead wrinkles
        o.append(path(f"M{hx-hr*(.42-k*.08)},{hy+hr*wy} Q{hx},{hy+hr*(wy-.1)} {hx+hr*(.42-k*.08)},{hy+hr*wy}", w=SW * .55, c=D))
    o.append(line([(hx, hy - hr * .8), (hx, hy - hr * .5)], w=SW * .55, c=D))
    big = expr in ("sparkle", "surprised", "beg")
    for sgn in (-1, 1):
        ex_, ey_ = hx + sgn * .4 * hr, hy - .08 * hr
        if expr == "sleep":
            o.append(path(f"M{ex_-.18*hr},{ey_} Q{ex_},{ey_+.14*hr} {ex_+.18*hr},{ey_}", w=SW * .7, c="#f0e0c8"))
        else:
            o.append(circle(ex_, ey_, hr * (.3 if big else .25), fill="#111", w=SW * .5, c="#f0e0c8"))
            o.append(circle(ex_ + .08 * hr, ey_ - .1 * hr, hr * (.11 if big else .08), fill="#fff", w=0))
            if big: o.append(circle(ex_ - .1 * hr, ey_ + .08 * hr, hr * .05, fill="#fff", w=0))
            if expr == "tired": o.append(line([(ex_ - .25 * hr, ey_ - .12 * hr), (ex_ + .25 * hr, ey_ - .12 * hr)], w=SW * .7, c=F))
            if expr == "angry": o.append(line([(ex_ - sgn * .3 * hr, ey_ - .4 * hr), (ex_ + sgn * .2 * hr, ey_ - .22 * hr)], w=SW * .8, c="#f0e0c8"))
    o.append(ellipse(hx, hy + .35 * hr, .2 * hr, .13 * hr, fill="#000", w=0))
    if expr in ("bark", "pant", "surprised"):
        o.append(ellipse(hx, hy + .62 * hr, .2 * hr, .17 * hr, fill="#7a2e2e", w=SW * .5, c="#f0e0c8"))
        if expr == "pant": o.append(path(f"M{hx-.12*hr},{hy+.65*hr} q{.12*hr},{.55*hr} {.24*hr},0", fill=PAL["pink"], w=SW * .5))
    else:
        o.append(path(f"M{hx-.25*hr},{hy+.55*hr} Q{hx-.12*hr},{hy+.68*hr} {hx},{hy+.52*hr} Q{hx+.12*hr},{hy+.68*hr} {hx+.25*hr},{hy+.55*hr}", w=SW * .55, c="#f0e0c8"))
        if tongue and expr != "sleep": o.append(path(f"M{hx-.08*hr},{hy+.62*hr} q{.08*hr},{.28*hr} {.16*hr},0", fill=PAL["pink"], w=SW * .4))
    tf = []
    if flip: tf.append(f"translate({2*x},0) scale(-1,1)")
    if rot: tf.append(f"rotate({rot} {x} {y - r})")
    return g(o, " ".join(tf))

# ------------------------------------------------------------------ props
def fx_lines(x, y, n=3, length=60, ang=0, c=INK, spread=28):
    o = []
    for i in range(n):
        a = math.radians(ang + (i - (n - 1) / 2) * spread)
        o.append(line([(x + math.cos(a) * 20, y + math.sin(a) * 20), (x + math.cos(a) * (20 + length), y + math.sin(a) * (20 + length))], w=SW * .7, c=c))
    return g(o)

def zzz(x, y, s=1.0):
    o = []
    for i, k in enumerate((1.0, .75, .55)):
        X, Y, w = x + i * 45 * s, y - i * 55 * s, 34 * s * k
        o.append(line([(X, Y), (X + w, Y), (X, Y + w), (X + w, Y + w)], w=SW * .7))
    return g(o)

def question(x, y, s=1.0, c=PAL["orange"]):
    return g([path(f"M{x-40*s},{y-40*s} Q{x-40*s},{y-100*s} {x},{y-100*s} Q{x+45*s},{y-100*s} {x+45*s},{y-55*s} Q{x+45*s},{y-20*s} {x},{y} L{x},{y+30*s}", w=SW * 2.2, c=c),
              circle(x, y + 75 * s, 12 * s, fill=c, w=0)])

def heart(x, y, s=1.0, c=PAL["red"]):
    return path(f"M{x},{y+30*s} C{x-60*s},{y-10*s} {x-30*s},{y-55*s} {x},{y-25*s} C{x+30*s},{y-55*s} {x+60*s},{y-10*s} {x},{y+30*s} Z", fill=c, w=SW * .7)

def sparkle(x, y, s=1.0, c=PAL["gold"]):
    return poly([(x, y - 30 * s), (x + 8 * s, y - 8 * s), (x + 30 * s, y), (x + 8 * s, y + 8 * s), (x, y + 30 * s), (x - 8 * s, y + 8 * s), (x - 30 * s, y), (x - 8 * s, y - 8 * s)], fill=c, w=SW * .5)

def sun(x, y, r=70, c=PAL["gold"], rays=True):
    o = [circle(x, y, r, fill=c, w=SW * .8)]
    if rays:
        for i in range(10):
            a = i * math.pi / 5; o.append(line([(x + math.cos(a) * (r + 18), y + math.sin(a) * (r + 18)), (x + math.cos(a) * (r + 48), y + math.sin(a) * (r + 48))], w=SW * .8))
    return g(o)

def moon(x, y, r=55): return path(f"M{x},{y-r} A{r},{r} 0 1,0 {x},{y+r} A{r*.75},{r*.75} 0 1,1 {x},{y-r} Z", fill="#F4E7B5", w=SW * .7)

def cloud(x, y, s=1.0): return path(f"M{x-90*s},{y} Q{x-110*s},{y-50*s} {x-55*s},{y-55*s} Q{x-40*s},{y-100*s} {x+10*s},{y-75*s} Q{x+60*s},{y-105*s} {x+80*s},{y-50*s} Q{x+125*s},{y-40*s} {x+95*s},{y} Z", fill="#fff", w=SW * .7)

def tree(x, y, s=1.0, c=PAL["green"]):
    return g([rect(x - 16 * s, y - 150 * s, 32 * s, 150 * s, fill=PAL["brown"], r=6, w=SW * .8), circle(x, y - 200 * s, 85 * s, fill=c, w=SW * .8), circle(x - 60 * s, y - 160 * s, 55 * s, fill=c, w=SW * .8), circle(x + 60 * s, y - 165 * s, 55 * s, fill=c, w=SW * .8)])

def lantern(x, y, s=1.0):
    return g([line([(x, y - 60 * s), (x, y - 30 * s)], w=SW * .6), ellipse(x, y, 34 * s, 42 * s, fill=PAL["red"], w=SW * .7),
              line([(x - 34 * s, y), (x + 34 * s, y)], w=SW * .4), line([(x, y + 42 * s), (x, y + 70 * s)], w=SW * .5, c=PAL["gold"])])

def pagoda_roof(x, y, w, c=PAL["red"]):
    return path(f"M{x-w/2-40},{y} Q{x-w/4},{y-25} {x-w/2+30},{y-70} L{x+w/2-30},{y-70} Q{x+w/4},{y-25} {x+w/2+40},{y} Z", fill=c, w=SW * .8)

def pagoda(x, y, s=1.0, c=PAL["red"]):
    o = []
    for i in range(3):
        w = (220 - i * 50) * s; yy = y - i * 130 * s
        o.append(rect(x - w / 2 + 20 * s, yy - 110 * s, w - 40 * s, 110 * s, fill=PAL["wall"], r=4, w=SW * .7))
        o.append(pagoda_roof(x, yy - 110 * s, w, c))
    return g(o)

def castle(x, y, s=1.0):
    o = [rect(x - 180 * s, y - 260 * s, 360 * s, 260 * s, fill="#D8D2C4", r=4, w=SW * .8)]
    for dx in (-200, 140):
        o.append(rect(x + dx * s, y - 380 * s, 60 * s, 380 * s, fill="#CFC8B8", r=4, w=SW * .8))
        o.append(poly([(x + dx * s - 10 * s, y - 380 * s), (x + dx * s + 30 * s, y - 470 * s), (x + dx * s + 70 * s, y - 380 * s)], fill=PAL["orange"], w=SW * .8))
    o.append(path(f"M{x-45*s},{y} L{x-45*s},{y-90*s} Q{x},{y-150*s} {x+45*s},{y-90*s} L{x+45*s},{y} Z", fill="#6b4a2f", w=SW * .8))
    return g(o)

def ship(x, y, s=1.0):
    return g([path(f"M{x-260*s},{y-60*s} L{x+260*s},{y-60*s} L{x+200*s},{y+40*s} L{x-200*s},{y+40*s} Z", fill=PAL["brown"], w=SW * .9),
              line([(x - 40 * s, y - 60 * s), (x - 40 * s, y - 420 * s)], w=SW), line([(x + 120 * s, y - 60 * s), (x + 120 * s, y - 330 * s)], w=SW),
              path(f"M{x-40*s},{y-400*s} Q{x+70*s},{y-300*s} {x-40*s},{y-140*s} Z", fill="#fff", w=SW * .8),
              path(f"M{x+120*s},{y-310*s} Q{x+210*s},{y-230*s} {x+120*s},{y-110*s} Z", fill="#fff", w=SW * .8),
              poly([(x - 40 * s, y - 420 * s), (x + 50 * s, y - 400 * s), (x - 40 * s, y - 380 * s)], fill=PAL["orange"], w=SW * .6)])

def waves(y, W, c=PAL["blue"]):
    d = f"M0,{y} " + " ".join(f"Q{x+60},{y-30} {x+120},{y} T{x+240},{y}" for x in range(0, W, 240)) + f" L{W},{y+400} L0,{y+400} Z"
    return path(d, fill=c, w=SW * .7)

def sofa(x, y, w=520, c=PAL["blue"]):
    return g([rect(x - w / 2, y - 260, w, 150, fill=c, r=30, w=SW * .9), rect(x - w / 2 + 20, y - 150, w - 40, 110, fill=c, r=20, w=SW * .9),
              rect(x - w / 2 - 40, y - 200, 80, 170, fill=c, r=30, w=SW * .9), rect(x + w / 2 - 40, y - 200, 80, 170, fill=c, r=30, w=SW * .9),
              line([(x - w / 2 + 10, y - 40), (x - w / 2 + 10, y)], w=SW), line([(x + w / 2 - 10, y - 40), (x + w / 2 - 10, y)], w=SW)])

def bed(x, y, w=620, c=PAL["blue"]):
    return g([rect(x - w / 2 - 20, y - 330, 50, 330, fill=PAL["brown"], r=8, w=SW * .8), rect(x - w / 2, y - 170, w, 110, fill="#fff", r=14, w=SW * .8),
              rect(x - w / 2 + 40, y - 215, 140, 60, fill="#fff", r=25, w=SW * .7), rect(x - w / 2 + 200, y - 190, w - 210, 70, fill=c, r=14, w=SW * .8),
              line([(x - w / 2 + 10, y - 60), (x - w / 2 + 10, y)], w=SW), line([(x + w / 2 - 10, y - 60), (x + w / 2 - 10, y)], w=SW)])

def window(x, y, w=260, h=240, sky="#CFE3E8", inner=None):
    o = [rect(x - w / 2, y - h / 2, w, h, fill=sky, r=6, w=SW * .9)]
    if inner: o.append(inner)
    o += [line([(x, y - h / 2), (x, y + h / 2)], w=SW * .7), line([(x - w / 2, y), (x + w / 2, y)], w=SW * .7)]
    return g(o)

def door(x, y, w=200, h=380, c=PAL["brown"]):
    return g([rect(x - w / 2, y - h, w, h, fill=c, r=6, w=SW * .9), circle(x + w / 2 - 30, y - h / 2, 10, fill=PAL["gold"], w=SW * .5)])

def fridge(x, y, open_=True):
    o = [rect(x - 120, y - 520, 240, 520, fill="#F4F4F0", r=16, w=SW * .9), line([(x - 120, y - 330), (x + 120, y - 330)], w=SW * .7)]
    if open_:
        o += [rect(x - 100, y - 500, 200, 150, fill="#FFF6C9", r=8, w=SW * .6), rect(x - 85, y - 310, 170, 280, fill="#FFF6C9", r=8, w=SW * .6),
              circle(x - 40, y - 250, 26, fill=PAL["red"], w=SW * .5), rect(x + 5, y - 280, 55, 70, fill=PAL["green"], r=6, w=SW * .5),
              ellipse(x - 20, y - 120, 55, 28, fill=PAL["orange"], w=SW * .5),
              poly([(x + 120, y - 520), (x + 260, y - 480), (x + 260, y - 30), (x + 120, y)], fill="#E9E9E2", w=SW * .9)]
    return g(o)

def bowl(x, y, s=1.0, food=True):
    o = []
    if food: o.append(path(f"M{x-110*s},{y-60*s} Q{x},{y-260*s} {x+110*s},{y-60*s} Z", fill=PAL["brown"], w=SW * .8))
    o.append(path(f"M{x-140*s},{y-70*s} L{x+140*s},{y-70*s} L{x+100*s},{y} L{x-100*s},{y} Z", fill=PAL["red"], w=SW * .9))
    return g(o)

def scale_(x, y): return g([rect(x - 120, y - 40, 240, 40, fill="#E6E6E6", r=10, w=SW * .8), rect(x - 45, y - 34, 90, 26, fill="#fff", r=4, w=SW * .5)])

def thermometer(x, y):
    return g([rect(x - 22, y - 260, 44, 230, fill="#fff", r=22, w=SW * .8), rect(x - 10, y - 220, 20, 190, fill=PAL["red"], r=8, w=0), circle(x, y - 20, 40, fill=PAL["red"], w=SW * .8)])

def clock(x, y, r=55, hm=(2, 0)):
    a1 = math.radians(hm[0] * 30 - 90); a2 = math.radians(hm[1] * 6 - 90)
    return g([circle(x, y, r, fill="#fff", w=SW * .8), line([(x, y), (x + math.cos(a1) * r * .5, y + math.sin(a1) * r * .5)], w=SW * .8), line([(x, y), (x + math.cos(a2) * r * .78, y + math.sin(a2) * r * .78)], w=SW * .6)])

def throne(x, y, c=PAL["red"]):
    return g([rect(x - 130, y - 420, 260, 300, fill=PAL["gold"], r=30, w=SW * .9), rect(x - 105, y - 390, 210, 260, fill=c, r=24, w=SW * .7),
              rect(x - 150, y - 160, 300, 70, fill=PAL["gold"], r=12, w=SW * .9), rect(x - 140, y - 90, 30, 90, fill=PAL["gold"], r=6, w=SW * .8), rect(x + 110, y - 90, 30, 90, fill=PAL["gold"], r=6, w=SW * .8)])

def cushion(x, y, w=330, c=PAL["red"]):
    return g([path(f"M{x-w/2},{y-30} Q{x},{y-110} {x+w/2},{y-30} Q{x+w/2+20},{y+10} {x+w/2-10},{y+20} L{x-w/2+10},{y+20} Q{x-w/2-20},{y+10} {x-w/2},{y-30} Z", fill=c, w=SW * .9),
              circle(x - w / 2 + 5, y + 10, 14, fill=PAL["gold"], w=SW * .5), circle(x + w / 2 - 5, y + 10, 14, fill=PAL["gold"], w=SW * .5)])

def tent(x, y, w=900, h=600, c="#C9B48A"):
    return g([poly([(x - w / 2, y), (x, y - h), (x + w / 2, y)], fill=c, w=SW * .9), poly([(x - 120, y), (x, y - 330), (x + 120, y)], fill="#3b3247", w=SW * .8)])

def campfire(x, y):
    return g([line([(x - 70, y), (x + 70, y - 25)], w=SW * 2.2, c=PAL["brown"]), line([(x - 70, y - 25), (x + 70, y)], w=SW * 2.2, c=PAL["brown"]),
              path(f"M{x-50},{y-20} Q{x-60},{y-90} {x},{y-160} Q{x+60},{y-90} {x+50},{y-20} Z", fill=PAL["orange"], w=SW * .7),
              path(f"M{x-22},{y-25} Q{x-25},{y-70} {x},{y-100} Q{x+25},{y-70} {x+22},{y-25} Z", fill=PAL["gold"], w=0)])

def magnifier(x, y, s=1.0, rot=-35):
    return g([circle(x, y, 70 * s, fill="#ffffff", w=SW, extra='fill-opacity="0.35"'), line([(x + 50 * s, y + 50 * s), (x + 130 * s, y + 130 * s)], w=SW * 2.2)])

def bench(x, y, w=520):
    return g([rect(x - w / 2, y - 140, w, 30, fill=PAL["brown"], r=6, w=SW * .8), rect(x - w / 2, y - 250, w, 26, fill=PAL["brown"], r=6, w=SW * .8),
              line([(x - w / 2 + 30, y - 110), (x - w / 2 + 30, y)], w=SW), line([(x + w / 2 - 30, y - 110), (x + w / 2 - 30, y)], w=SW)])

def leaf(x, y, c=PAL["orange"], rot=0): return g([path(f"M{x},{y} Q{x+25},{y-25} {x+50},{y} Q{x+25},{y+25} {x},{y} Z", fill=c, w=SW * .5)], f"rotate({rot} {x} {y})")

def flag(x, y, c=PAL["orange"], h=300): return g([line([(x, y), (x, y - h)], w=SW), path(f"M{x},{y-h} Q{x+80},{y-h-25} {x+150},{y-h+10} L{x+150},{y-h+100} Q{x+80},{y-h+70} {x},{y-h+90} Z", fill=c, w=SW * .8)])

def confetti(W, H, n=40, seed=3):
    import random
    rnd = random.Random(seed); cs = [PAL["orange"], PAL["gold"], PAL["red"], PAL["blue"], PAL["green"]]
    return g([rect(rnd.uniform(0, W), rnd.uniform(0, H * .6), 18, 30, fill=rnd.choice(cs), r=3, w=0, extra=f'transform="rotate({rnd.uniform(0,90)} {0} {0})"') for _ in range(n)])

def hairs(x, y, w, h, n=60, seed=1):
    import random
    rnd = random.Random(seed)
    return g([line([(X, Y), (X + rnd.uniform(-14, 14), Y + rnd.uniform(-10, 10))], w=3, c=PAL["fawn_d"]) for X, Y in ((rnd.uniform(x, x + w), rnd.uniform(y, y + h)) for _ in range(n))])

def leash(a, b): return path(f"M{a[0]},{a[1]} Q{(a[0]+b[0])/2},{max(a[1],b[1])+80} {b[0]},{b[1]}", w=SW * .6, c=PAL["red"])

def footprints(x0, y0, x1, n=6):
    return g([g([ellipse(x0 + i * (x1 - x0) / n, y0 + (12 if i % 2 else -12), 14, 9, fill=INK, w=0, extra='opacity="0.35"')]) for i in range(n)])

def dagger(x, y, s=1.0): return g([poly([(x, y), (x + 70 * s, y - 12 * s), (x + 75 * s, y), (x + 70 * s, y + 12 * s)], fill="#ddd", w=SW * .5), rect(x - 30 * s, y - 8 * s, 30 * s, 16 * s, fill=PAL["brown"], r=4, w=SW * .5)])

def sack(x, y): return path(f"M{x-60},{y} Q{x-80},{y-110} {x-20},{y-140} L{x+20},{y-140} Q{x+80},{y-110} {x+60},{y} Z", fill="#B79B6E", w=SW * .8)

def toy_ball(x, y, r=26): return circle(x, y, r, fill=PAL["red"], w=SW * .6)

def spear(x, y, s=1.0): return g([line([(x, y), (x + 40 * s, y - 330 * s)], w=SW * .8, c=PAL["brown"]), poly([(x + 40 * s, y - 330 * s), (x + 30 * s, y - 370 * s), (x + 60 * s, y - 335 * s)], fill="#999", w=SW * .5)])

# ------------------------------------------------------------------ backgrounds
def bg(kind, W, H):
    gy = H * .8
    o = [f'<rect width="{W}" height="{H}" fill="{PAL["paper"]}"/>']
    if kind == "plain": pass
    elif kind == "room":
        o += [f'<rect width="{W}" height="{gy}" fill="{PAL["wall"]}"/>', f'<rect y="{gy}" width="{W}" height="{H-gy}" fill="{PAL["floor"]}"/>', line([(0, gy), (W, gy)], w=SW * .8)]
    elif kind == "outdoor":
        o += [f'<rect width="{W}" height="{gy}" fill="{PAL["sky"]}"/>', f'<rect y="{gy}" width="{W}" height="{H-gy}" fill="{PAL["grass"]}"/>', line([(0, gy), (W, gy)], w=SW * .8)]
    elif kind == "dusk":
        o += [f'<rect width="{W}" height="{gy}" fill="{PAL["sky_dusk"]}"/>', f'<rect y="{gy}" width="{W}" height="{H-gy}" fill="#C9A776"/>', line([(0, gy), (W, gy)], w=SW * .8)]
    elif kind == "night":
        o += [f'<rect width="{W}" height="{gy}" fill="{PAL["night"]}"/>', f'<rect y="{gy}" width="{W}" height="{H-gy}" fill="#4B4A5C"/>', line([(0, gy), (W, gy)], w=SW * .8)]
    elif kind == "palace":
        o += [f'<rect width="{W}" height="{gy}" fill="#E9C9A3"/>', f'<rect y="{gy}" width="{W}" height="{H-gy}" fill="#B5523F"/>', line([(0, gy), (W, gy)], w=SW * .8)]
        for X in (W * .12, W * .88):
            o.append(rect(X - 45, H * .05, 90, gy - H * .05, fill=PAL["red"], r=4, w=SW * .8))
    elif kind == "sea":
        o += [f'<rect width="{W}" height="{H}" fill="{PAL["sky"]}"/>']
    return g(o), gy

class Scene:
    def __init__(self, bg_kind="plain", W=1920, H=1080):
        self.W, self.H = W, H; b, self.gy = bg(bg_kind, W, H); self.items = [b]
    def add(self, *its): self.items += list(its); return self
    def svg(self):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" viewBox="0 0 {self.W} {self.H}">' + "".join(self.items) + "</svg>"
    def save(self, png):
        png = Path(png); png.parent.mkdir(parents=True, exist_ok=True)
        sv = png.with_suffix(".svg"); sv.write_text(self.svg())
        render([(sv, png)], self.W, self.H)

def render(pairs, W=1920, H=1080):
    """pairs: [(svg_path, png_path)]. One headless Chrome call per file."""
    for sv, png in pairs:
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
                        f"--screenshot={Path(png).resolve()}", f"file://{Path(sv).resolve()}"], capture_output=True, timeout=60)
