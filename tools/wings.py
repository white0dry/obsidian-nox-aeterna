# -*- coding: utf-8 -*-
"""蝙蝠翼几何：以 game-icons.net「batwing-emblem」(Lorc, CC BY 3.0) 的左翼为底稿，
做仿射变换(旋转/镜像/缩放)并自动算外框，生成横幅双翼与 H2 用的竖立单翼。
"""
import math
import re

# Lorc batwing-emblem 拆出的左翼(512 坐标系)。翼尖(15,26)，腕关节(205,198)，
# 外缘两道扇贝弧的指尖(29,201)(93,338)，翼根(192,366)~(226,335)
LORC_WING = ("M15.406 25.938c41.737 42.61 52.607 128.648 13.438 174.78"
             "c63.818 10.74 75.725 61.317 64.47 137.5"
             "c32.67-20.39 72.694-12.612 98.25 27.688"
             "L225.9 334.8C173 311.95 153.79 238.832 205.28 197.72"
             "C171.063 113 99.715 43.782 15.407 25.937Z")
WRIST = (205.28, 197.72)
FINGERTIPS = ((28.844, 200.718), (93.314, 338.218))
ROOT = (208.0, 352.0)
TIP = (15.406, 25.938)
# 腕关节上的拇指爪(真蝙蝠翼前缘的小钩)，同一 512 坐标系
CLAW = "M204 200C196 178 199 160 214 146C209 163 212 180 221 196Z"


def parse(d):
    """→ [(cmd, [pts...])]，cmd ∈ M L C Z，全部绝对坐标"""
    toks = re.findall(r"[MmLlCcSsHhVvZz]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?", d)
    out, i, cur, start, last_c2, cmd = [], 0, (0.0, 0.0), (0.0, 0.0), None, None

    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v
    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]):
            cmd = toks[i]; i += 1
            if cmd in "Zz":
                out.append(("Z", [])); cur = start; last_c2 = None
                continue
        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = cur if rel else (0.0, 0.0)
        if c == "M":
            cur = (ox + num(), oy + num()); start = cur
            out.append(("M", [cur])); cmd = "l" if rel else "L"; last_c2 = None
        elif c == "L":
            cur = (ox + num(), oy + num()); out.append(("L", [cur])); last_c2 = None
        elif c == "H":
            cur = ((ox if rel else 0) + num(), cur[1]); out.append(("L", [cur])); last_c2 = None
        elif c == "V":
            cur = (cur[0], (oy if rel else 0) + num()); out.append(("L", [cur])); last_c2 = None
        elif c == "C":
            p1 = (ox + num(), oy + num()); p2 = (ox + num(), oy + num()); p3 = (ox + num(), oy + num())
            out.append(("C", [p1, p2, p3])); cur = p3; last_c2 = p2
        elif c == "S":
            p1 = (2 * cur[0] - last_c2[0], 2 * cur[1] - last_c2[1]) if last_c2 else cur
            p2 = (ox + num(), oy + num()); p3 = (ox + num(), oy + num())
            out.append(("C", [p1, p2, p3])); cur = p3; last_c2 = p2
    return out


def affine(rot_deg=0.0, scale=1.0, mirror=False, origin=(0, 0), to=(0, 0)):
    """先平移 origin→原点，再镜像/缩放/旋转，最后平移到 to。返回 f(pt)"""
    a = math.radians(rot_deg)
    ca, sa = math.cos(a), math.sin(a)

    def f(p):
        x, y = p[0] - origin[0], p[1] - origin[1]
        if mirror:
            x = -x
        x, y = x * scale, y * scale
        return (to[0] + x * ca - y * sa, to[1] + x * sa + y * ca)
    return f


def transform(segs, f):
    return [(c, [f(p) for p in pts]) for c, pts in segs]


def to_d(segs, prec=2):
    s = []
    for c, pts in segs:
        s.append(c + " ".join(f"{x:.{prec}f},{y:.{prec}f}" for x, y in pts))
    return "".join(s)


def bbox(segs):
    """曲线实际外框(对三次贝塞尔采样，不算控制点)"""
    xs, ys, cur = [], [], (0.0, 0.0)
    for c, pts in segs:
        if c == "C":
            p0, (p1, p2, p3) = cur, pts
            for i in range(1, 25):
                t = i / 24
                u = 1 - t
                xs.append(u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0])
                ys.append(u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])
        for p in pts[-1:]:
            xs.append(p[0]); ys.append(p[1]); cur = p
    return min(xs), min(ys), max(xs), max(ys)


def wing(rot=0.0, scale=1.0, mirror=False, to=(0, 0), claw=True):
    """返回 (翼面[+拇指爪] path d, 指骨 path d, bbox)。指骨=腕关节→两道扇贝弧的指尖"""
    f = affine(rot, scale, mirror, ROOT, to)
    segs = transform(parse(LORC_WING), f)
    w = f(WRIST)
    bones = " ".join(f"M{w[0]:.2f},{w[1]:.2f} L{t[0]:.2f},{t[1]:.2f}" for t in map(f, FINGERTIPS))
    d = to_d(segs) + (to_d(transform(parse(CLAW), f)) if claw else "")
    return d, bones, bbox(segs)
