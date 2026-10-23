# -*- coding: utf-8 -*-
"""从 Heritage Library「Deadly Skulls 02 · Element 1」(正面骷髅版画线稿)做扁平纹章骷髅：
实心剪影(线稿外轮廓闭合后漫水) + 眼窝、鼻腔、缺牙的嘴(模糊后墨量最浓、开运算后仍成块的区域，按位置筛)，
平滑后描成矢量路径存 src/icons/skull-flat.svg：
  - #skull：骨白剪影，眼窝/鼻腔/嘴是 evenodd 窟窿
  - #eyes：两个眼窝(略放大)，画在剪影下面填血红 = 红目镜
授权(License_HeritageLibrary.pdf)：允许修改后用于作品，不允许单独再分发原文件——仓库只放这份改过的矢量。
用法: python tools/heritage_skull.py [原 PNG 路径]
"""
import sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else Path(
    r"E:\AI工作\素材库\Heritage Library\Deadly Skulls 02\PNG\HTC_Heritage Library_Deadly Skulls 02Element 1.png")
DST = ROOT / "src" / "icons" / "skull-flat.svg"
SCALE = 0.04          # 原图 px → SVG 单位
CROP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9      # 剪影只留上面这么多(截掉大半下颌，图标更扁)
SQUASH = float(sys.argv[3]) if len(sys.argv) > 3 else 0.82   # 竖向再压扁的倍数(原比例 0.61 嫌长、0.95 嫌扁，0.9/0.82 ≈ 0.81)
CLOSE = 18            # 闭合线稿缺口的半径(px)
SMOOTH = 9            # 掩膜平滑(高斯 σ，px)，去掉版画锯齿
EPS = 5.0             # 折线简化容差(px)


def ell(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def smooth(mask, s=SMOOTH):
    return (cv2.GaussianBlur(mask.astype(np.float32), (0, 0), s) > 0.5).astype(np.uint8)


a = np.asarray(Image.open(SRC).convert("RGBA"))[:, :, 3]
ys, xs = np.nonzero(a > 100)
a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
a = cv2.copyMakeBorder(a, 60, 60, 60, 60, cv2.BORDER_CONSTANT, value=0)
ink = (a > 100).astype(np.uint8)
H, W = ink.shape

# 剪影：线稿加粗闭合 → 从角落漫水得外部 → 取反 → 收回加粗量
closed = cv2.dilate(ink, ell(CLOSE))
ff = (1 - closed).astype(np.uint8)
cv2.floodFill(ff, np.zeros((H + 2, W + 2), np.uint8), (0, 0), 2)
sil = smooth(cv2.erode((ff != 2).astype(np.uint8), ell(CLOSE)))

# 窟窿：墨量密度
dens = cv2.GaussianBlur(ink.astype(np.float32), (0, 0), 14)
inner = cv2.erode(sil, ell(20))


def solid(m):
    """填掉块内部的小空洞(版画里眼窝中间残留的几点留白)"""
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, ell(15))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = np.zeros_like(m)
    cv2.drawContours(out, cs, -1, 1, cv2.FILLED)
    return out


def blobs(thresh, open_r, y0, y1, x0=0.18, x1=0.82, max_frac=1.0):
    d = cv2.morphologyEx((dens > thresh).astype(np.uint8), cv2.MORPH_OPEN, ell(open_r)) & inner
    n, lab, st, ce = cv2.connectedComponentsWithStats(d)
    out, total = [], int(sil.sum(dtype=np.int64))
    for i in range(1, n):
        cx, cy = ce[i]
        if y0 * H < cy < y1 * H and x0 * W < cx < x1 * W and 0.002 * total < st[i, 4] < max_frac * total:
            out.append(solid((lab == i).astype(np.uint8)))
    return out


upper = blobs(0.88, 22, 0.30, 0.72)                 # 眼窝 ×2 + 鼻腔
mouth = blobs(0.80, 12, 0.72, 0.92, 0.32, 0.68, max_frac=0.02)   # 缺牙的嘴(只要正中的齿缝，下颌侧面的阴影不要)
upper = sorted(upper, key=lambda m: -int(m.sum(dtype=np.int64)))[:3]   # 两个眼窝 + 鼻腔(更小的碎块不要)
eyes = upper[:2]
holes = np.zeros_like(sil)
for m in upper + mouth:
    holes |= m
holes = smooth(holes, 6) & cv2.erode(sil, ell(12))
eye_mask = smooth(cv2.dilate(sum(eyes).clip(0, 1).astype(np.uint8), ell(10)), 6)
print(f"眼窝 {len(eyes)}，上部窟窿 {len(upper)}，嘴 {len(mouth)}")

# 截掉下颌：只留上 CROP，底边圆一下(和剪影同样的平滑)，免得一刀切成直线
cut = np.zeros_like(sil)
cut[:int(H * CROP)] = 1
sil = smooth(sil & cut, 14) & sil
holes &= sil
H = int(H * CROP) + 20


def path_of(mask, holes_too=True):
    mode = cv2.RETR_CCOMP if holes_too else cv2.RETR_EXTERNAL
    cs, _ = cv2.findContours(mask, mode, cv2.CHAIN_APPROX_NONE)
    parts = []
    for c in cs:
        c = cv2.approxPolyDP(c, EPS, True)[:, 0, :]
        if len(c) < 3:
            continue
        parts.append("M" + " L".join(f"{x * SCALE:.1f},{y * SCALE * SQUASH:.1f}" for x, y in c) + "Z")
    return " ".join(parts)


skull_d = path_of((sil & (1 - holes)).astype(np.uint8))
eyes_d = path_of(eye_mask, holes_too=False)
ys_, xs_ = np.nonzero(sil)
x0, x1, y0, y1 = xs_.min(), xs_.max() + 1, ys_.min(), ys_.max() + 1
# 空心版(大纲里没有子级的项)：只留外轮廓一圈，粗细 ≈ 高度的 RING 倍(12px 图标上约 1.4px)
RING = 0.115
dist = cv2.distanceTransform(sil, cv2.DIST_L2, 5)
ring = smooth(((dist > 0) & (dist < RING * (y1 - y0))).astype(np.uint8), 6) & sil
ring_d = path_of(ring)
vb = f"{x0 * SCALE:.1f} {y0 * SCALE * SQUASH:.1f} {(x1 - x0) * SCALE:.1f} {(y1 - y0) * SCALE * SQUASH:.1f}"
print(f"宽高比 {(x1 - x0) / ((y1 - y0) * SQUASH):.3f}")
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">\n'
       f'<path id="eyes" d="{eyes_d}"/>\n'
       f'<path id="skull" fill-rule="evenodd" d="{skull_d}"/>\n'
       f'<path id="ring" fill-rule="evenodd" d="{ring_d}"/>\n</svg>\n')
DST.write_text(svg, encoding="utf-8")
print(DST, vb, len(svg), "bytes")
