# -*- coding: utf-8 -*-
"""程序化闪电纹(仿午夜领主盔甲上的真实分叉闪电)。
主干 = 递归中点位移(分形锯齿)，沿途随机长出分叉，分叉再分叉；
每条通道画成「粗细渐变 + 随机抖动」的填充多边形，外加两层更宽的半透明多边形当辉光
(不用模糊滤镜：最终会预渲染成位图，滤镜也不会进主题)。
"""
import math
import random

SVG = 'xmlns="http://www.w3.org/2000/svg"'


def _jag(rng, a, b, rough, depth):
    pts = [a, b]
    length = math.dist(a, b)
    disp = rough * length
    for _ in range(depth):
        new = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            dx, dy = q[0] - p[0], q[1] - p[1]
            n = math.hypot(dx, dy) or 1
            off = max(-2.2, min(2.2, rng.gauss(0, 1))) * disp
            new += [(mx - dy / n * off, my + dx / n * off), q]
        pts = new
        disp *= 0.52
    return pts


def _ribbon(rng, pts, w0, w1, jitter=0.22):
    """沿折线生成两侧偏移的多边形；宽度从 w0 渐变到 w1，末端收成尖"""
    n = len(pts)
    left, right = [], []
    for i, p in enumerate(pts):
        t = i / (n - 1)
        w = (w0 + (w1 - w0) * t ** 0.7) * (1 + rng.uniform(-jitter, jitter))
        if i == n - 1:
            w = w1 * 0.25
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        m = math.hypot(dx, dy) or 1
        nx, ny = -dy / m, dx / m
        left.append((p[0] + nx * w / 2, p[1] + ny * w / 2))
        right.append((p[0] - nx * w / 2, p[1] - ny * w / 2))
    poly = left + right[::-1]
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + "Z"


def _channel(rng, a, b, w0, w1, depth, gen, out, branch_p):
    pts = _jag(rng, a, b, 0.16 if gen == 0 else 0.2, depth)
    out.append((pts, w0, w1, gen))
    if gen >= 2:
        return
    total = math.dist(a, b)
    n = len(pts)
    for i in range(2, n - 3):
        if rng.random() > branch_p:
            continue
        t = i / (n - 1)
        p, q = pts[i], pts[i + 1]
        ang = math.atan2(q[1] - p[1], q[0] - p[0]) + rng.choice((-1, 1)) * math.radians(rng.uniform(18, 52))
        ln = total * (1 - t) * rng.uniform(0.25, 0.6) * (0.75 ** gen)
        if ln < 14:
            continue
        end = (p[0] + math.cos(ang) * ln, p[1] + math.sin(ang) * ln)
        wl = w0 + (w1 - w0) * t
        _channel(rng, p, end, wl * rng.uniform(0.38, 0.58), w1 * 0.4, max(3, depth - 2), gen + 1, out,
                 branch_p * 0.5)


SIDEBAR_W, SIDEBAR_H = 560, 560


def sidebar_storm():
    """文件列表底部用的闪电纹：CSS 里按固定像素尺寸贴面板右下角(不随面板缩放)。
    右缘贴面板边框，所以只有左侧和顶部需要在图内渐隐；画布比常见面板宽，面板拉宽也看不到切口。
    主干从图外上方伸进来、离右缘 60~150px(文件名多在左侧)，左半边一道细闪电只在宽面板露出。
    三道闪电起始粗细接近(1.8/1.6/1.5)，用户嫌右侧主干比左侧粗太多。"""
    return storm(width=SIDEBAR_W, height=SIDEBAR_H, seed=13,
                 bolts=[((0.90, -0.12), (0.73, 1.03), 1.8), ((1.06, 0.45), (0.93, 1.03), 1.6),
                        ((0.50, 0.30), (0.34, 1.03), 1.5)],
                 fade_top=0.5, fade_left=0.4, glow_cx=0.8, core="#d3def4", core_opacity=0.62)


def storm(width=320, height=440, seed=8, core="#e9f1ff", glow1="#9dbbe8", glow2="#4f74b8",
          bolts=None, fade_top=0.42, core_opacity=0.82, fade_left=0.0, glow_cx=0.45):
    """返回一整张闪电纹 SVG(透明底，顶部渐隐；fade_left>0 时左侧也渐隐)。
    bolts: [(起点, 终点, 主干起始宽)]，起点 y 可以为负(从图外上方伸进来)，这样渐隐区里看不到闪电的「起点」。"""
    rng = random.Random(seed)
    if bolts is None:
        bolts = [((0.72, 0.10), (0.22, 1.03), 3.6),
                 ((1.05, 0.50), (0.80, 1.03), 2.3)]
    chans = []
    for (ax, ay), (bx, by), w in bolts:
        _channel(rng, (ax * width, ay * height), (bx * width, by * height), w, w * 0.3, 7, 0, chans, 0.075)
    glow_a, glow_b, cores = [], [], []
    for pts, w0, w1, gen in chans:
        k = 1.0 if gen == 0 else 0.8
        glow_b.append(_ribbon(rng, pts, w0 * 7 * k, w1 * 5, 0.1))
        glow_a.append(_ribbon(rng, pts, w0 * 2.6, w1 * 2.2, 0.15))
        cores.append(_ribbon(rng, pts, w0, w1))
    left_def = left_open = left_close = ""
    if fade_left > 0:
        left_def = (f'<linearGradient id="fl" x1="0" y1="0" x2="1" y2="0">'
                    f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                    f'<stop offset="{fade_left}" stop-color="#fff" stop-opacity="1"/></linearGradient>'
                    f'<mask id="ml"><rect width="100%" height="100%" fill="url(#fl)"/></mask>')
        left_open, left_close = '<g mask="url(#ml)">', "</g>"
    return (f'<svg {SVG} width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            f'<defs><linearGradient id="f" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset="{fade_top}" stop-color="#fff" stop-opacity="1"/></linearGradient>'
            f'<mask id="m"><rect width="100%" height="100%" fill="url(#f)"/></mask>{left_def}'
            f'<radialGradient id="h" cx="{glow_cx}" cy="1" r=".75"><stop offset="0" stop-color="{glow2}" stop-opacity=".22"/>'
            f'<stop offset="1" stop-color="{glow2}" stop-opacity="0"/></radialGradient></defs>'
            f'<g mask="url(#m)">{left_open}<rect width="100%" height="100%" fill="url(#h)"/>'
            f'<path d="{" ".join(glow_b)}" fill="{glow2}" fill-opacity=".07"/>'
            f'<path d="{" ".join(glow_a)}" fill="{glow1}" fill-opacity=".16"/>'
            f'<path d="{" ".join(cores)}" fill="{core}" fill-opacity="{core_opacity}"/>{left_close}</g></svg>')
