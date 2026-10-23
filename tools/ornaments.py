# -*- coding: utf-8 -*-
"""主题里所有装饰 SVG 的生成器(午夜领主徽 + 自绘蝙蝠翼/闪电/菱形)。
build.py 会 import 本模块，把返回的 SVG 字符串转成 data URI 塞进 theme.css。
直接运行 = 输出预览页 preview/ornaments.html
"""
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "src" / "icons"

_emblem = (ICONS / "nl-emblem.svg").read_text(encoding="utf-8")
NL_TF = re.search(r'<g transform="([^"]+)"', _emblem).group(1)
NL_BODY = re.search(r'<g [^>]*>(.*)</g>', _emblem, re.S).group(1)
_skull = (ICONS / "nl-skull.svg").read_text(encoding="utf-8")
SKULL_BODY = re.search(r'<g [^>]*>(.*)</g>', _skull, re.S).group(1)
_wings = (ICONS / "nl-wings.svg").read_text(encoding="utf-8")
WINGS_BODY = re.search(r'<g [^>]*>(.*)</g>', _wings, re.S).group(1)   # 和 nl-emblem/nl-skull 同一坐标系
# 骷髅在原图(变换前)坐标里的外框，Playwright getBBox 量得
SKULL_BOX = (304.86, 194.45, 389.71, 450.45)
# 眼窝位置(原图坐标)：图标里眼睛是镂空，背后垫红色就成了午夜领主头盔的红目镜
EYES = ((425, 462), (577, 462))

SVG = 'xmlns="http://www.w3.org/2000/svg"'


def _eyes_defs(gid, hot="#ff6a4a", mid="#d0201e", dark="#5a0a0a"):
    return (f'<radialGradient id="{gid}"><stop offset="0" stop-color="{hot}"/>'
            f'<stop offset=".55" stop-color="{mid}"/><stop offset="1" stop-color="{dark}"/></radialGradient>')


def _eyes(gid, rx=52, ry=36):
    return "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="url(#{gid})"/>' for x, y in EYES)


def emblem(fill="#b08a52", eyes=True, opacity=1, wing_fill=None):
    """完整午夜领主翼骷髅徽，红目镜。viewBox 941x800。wing_fill：翅膀单独上色(骷髅仍用 fill)"""
    defs = f"<defs>{_eyes_defs('e')}</defs>" if eyes else ""
    eye = f'<g transform="{NL_TF}">{_eyes("e")}</g>' if eyes else ""
    if wing_fill:
        body = (f'<g transform="{NL_TF}" fill="{wing_fill}" fill-opacity="{opacity}">{WINGS_BODY}</g>'
                f'<g transform="{NL_TF}" fill="{fill}" fill-opacity="{opacity}">{SKULL_BODY}</g>')
    else:
        body = f'<g transform="{NL_TF}" fill="{fill}" fill-opacity="{opacity}">{NL_BODY}</g>'
    return f'<svg {SVG} viewBox="0 0 941.19 800">{defs}{eye}{body}</svg>'


# 右翼(局部坐标：肩部为原点，向右展开)。前缘=上弧到腕关节再甩到翼尖，
# 后缘=指尖之间向内凹的膜(Q 曲线控制点往上提)
WING_PATH = ("M0,-4 C22,-30 58,-46 100,-42 C156,-37 218,-31 272,-14 "
             "Q240,-3 218,23 Q192,7 162,37 Q134,19 106,43 Q78,22 48,33 Q24,16 0,21 Z")
# 指骨：腕关节 → 各指尖
WING_BONES = "M100,-42 L218,23 M100,-42 L162,37 M100,-42 L106,43 M100,-42 L272,-14 M0,-4 L100,-42"


def _skull_g(cx, top, h, fill, eye_gid):
    x, y, w, hh = SKULL_BOX
    s = h / hh
    tx, ty = cx - (x + w / 2) * s, top - y * s
    eyes = _eyes(eye_gid) if eye_gid else ""
    return f'<g transform="translate({tx:.2f},{ty:.2f}) scale({s:.5f})">{eyes}<g fill="{fill}">{SKULL_BODY}</g></g>'


def batwing_banner(skull="#d8ccb2", membrane="#5e1219", membrane2="#8e1b22", bone="#b08a52",
                   eyes=True):
    """横向展开的蝙蝠双翼 + 中央午夜领主骷髅。viewBox 600x100"""
    defs = (f'<defs><linearGradient id="m" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{membrane2}"/><stop offset="1" stop-color="{membrane}"/></linearGradient>'
            + (_eyes_defs("e") if eyes else "") + "</defs>")

    def wing(mirror):
        tf = "translate(268,50) scale(-1,1)" if mirror else "translate(332,50)"
        return (f'<g transform="{tf}"><path d="{WING_PATH}" fill="url(#m)" stroke="{bone}" '
                f'stroke-width="2" stroke-linejoin="round"/>'
                f'<path d="{WING_BONES}" fill="none" stroke="{bone}" stroke-width="2.4" stroke-linecap="round"/></g>')
    return (f'<svg {SVG} viewBox="0 0 600 100">{defs}{wing(True)}{wing(False)}'
            f'{_skull_g(300, 9, 82, skull, "e" if eyes else None)}</svg>')


def _membrane_defs(mid, top, bottom):
    return (f'<linearGradient id="{mid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>')


def heraldic_banner(rot=-38, skull="#d8ccb2", membrane="#4a0e14", membrane2="#9a1f27", bone="#c39a5b",
                    eyes=True, gap=34, wing_len=250, bones=True, claw=True, edge=True):
    """纹章式双翼横幅：Lorc 左翼底稿外旋 rot 度，镜像成右翼，中央午夜领主骷髅。
    bones=指骨线，claw=腕关节拇指爪，edge=翼面黄铜描边。viewBox 自动贴合。"""
    import wings as W
    s = wing_len / math.dist(W.ROOT, W.TIP)
    cx, root_y = 300, 58
    lw, lb, lbox = W.wing(rot=rot, scale=s, to=(cx - gap, root_y), claw=claw)
    rw, rb, rbox = W.wing(rot=-rot, scale=s, mirror=True, to=(cx + gap, root_y), claw=claw)
    x0, y0 = min(lbox[0], rbox[0]) - 4, min(lbox[1], rbox[1], 6) - 4
    x1, y1 = max(lbox[2], rbox[2]) + 4, max(lbox[3], rbox[3], 100) + 4
    defs = f"<defs>{_membrane_defs('m', membrane2, membrane)}" + (_eyes_defs("e") if eyes else "") + "</defs>"
    wings_svg = "".join(
        (f'<path d="{d}" fill="url(#m)" stroke="{bone}" stroke-width="2.2" stroke-linejoin="round"/>' if edge
         else f'<path d="{d}" fill="url(#m)"/>')
        + (f'<path d="{b}" fill="none" stroke="{bone}" stroke-width="2.6" stroke-linecap="round" stroke-opacity=".9"/>'
           if bones else "")
        for d, b in ((lw, lb), (rw, rb)))
    return (f'<svg {SVG} viewBox="{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}">{defs}{wings_svg}'
            f'{_skull_g(cx, 8, 92, skull, "e" if eyes else None)}</svg>')


def classic_banner(skull="#d8ccb2", membrane="#4a0e14", membrane2="#9a1f27", bone="#c39a5b", eyes=True):
    """经典蝙蝠剪影双翼(game-icons skoll/bat 底稿，CC BY 3.0)，中央身体换成骷髅。"""
    bat = ("M362.005 149.115s-7 55.77-79 83.36v-24.69c-2.76-1-4.63 7.88-7.26 9.15h-39.49c-2.63-1.27-4.5-10.11-7.26-9.15"
           "v24.69c-72-27.59-79-83.36-79-83.36-60.71 67.68-121.41 80-121.41 80 102.53-16.11 101.36 44.89 101.36 44.89 "
           "69.71-11.91 65.64 36.31 65.64 36.31 60.63-6.9 60.41 52.57 60.41 52.57s-.22-59.47 60.41-52.57c0 0-4.07-48.22 "
           "65.64-36.31 0 0-1.16-61 101.37-44.88.02.01-60.69-12.33-121.41-80.01z")
    defs = f"<defs>{_membrane_defs('m', membrane2, membrane)}" + (_eyes_defs("e") if eyes else "") + "</defs>"
    # 指骨：腕关节(翼前缘顶点)→ 下缘扇贝的尖
    bones = ("M150 149 L131 274 M150 149 L197 310 M150 149 L29 229 "
             "M362 149 L381 274 M362 149 L315 310 M362 149 L483 229")
    return (f'<svg {SVG} viewBox="20 120 472 230">{defs}'
            f'<path d="{bat}" fill="url(#m)" stroke="{bone}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="{bones}" fill="none" stroke="{bone}" stroke-width="3.2" stroke-linecap="round" stroke-opacity=".85"/>'
            f'<g transform="translate(-6,0)">{_skull_g(262, 150, 150, skull, "e" if eyes else None)}</g></svg>')


def raised_wing(rot=-12, top="#d63a40", bottom="#7c1820"):
    """单侧扬起的蝙蝠翼(赛维塔头盔两侧那种)：纯色剪影，无描边、无指骨、无拇指爪。
    H2 里翼高 = 1em，rot≥0(近乎竖直)时只剩一条细缝认不出，rot=-12 翼尖斜向上约 45°、扇贝翼膜可辨。
    viewBox 紧贴翼面外框，CSS 里 background-size 的高度就是翼的实际高度。"""
    import wings as W
    d, _, (x0, y0, x1, y1) = W.wing(rot=rot, scale=1.0, to=(0, 0), claw=False)
    return (f'<svg {SVG} viewBox="{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}">'
            f'<defs>{_membrane_defs("m", top, bottom)}</defs><path d="{d}" fill="url(#m)"/></svg>')


def bolt(fill="#c4313a", stroke="none"):
    """闪电(午夜领主盔甲上的闪电纹)。viewBox 12x24"""
    return (f'<svg {SVG} viewBox="0 0 12 24"><path d="M8,0 L1.2,13.4 L5.6,13.4 L3.2,24 L11,9.4 L6.6,9.4 L9.6,0 Z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width=".6" stroke-linejoin="round"/></svg>')


def diamond(fill="#b08a52"):
    return f'<svg {SVG} viewBox="0 0 10 10"><path d="M5,0 L10,5 L5,10 L0,5 Z" fill="{fill}"/></svg>'


# 盔甲彩绘式纹章闪电(沿 +x 指向尖端，y=6 是中线)：上缘 6 点 + 下缘 5 点，折角锐利
_HERALD_BOLT = [(2, 2), (18, 2.2), (15, 5.6), (31, 4.6), (27, 7.6), (46, 6), (25, 10.4), (28.6, 7.6), (13, 9), (16, 6), (2, 7)]
# 闪电中线(上下缘对应点取中)：画一道细暗槽，做出刻出来的斜面感
_HERALD_MID = [(2, 4.5), (17, 4.1), (14, 7.3), (29.8, 6.1), (26, 9.0), (44, 6.0)]


RULE_W = 184          # 徽+闪电部分的设计坐标宽(高 40)；整张图按 32px 高显示 → 1 单位 = 0.8px
RULE_LINE_START = 88  # 细叉从闪电尖的实色渐变到双线透明度，终点离中心 88 单位(70.4px)
# 两条线：y(单位)、透明度、两端渐隐(占 hr 全宽的比例：从 f0 处透明渐显到 f1 处满)
RULE_LINES = ((17.5, .55, .03, .22), (22.5, .3, .08, .26))


def rule_center(fill="#d8ccb2", bolt="#b08a52", groove="#5e4526", eyes=True, length=55, W=RULE_W):
    """分隔线整条画在一张不定宽 SVG 里(根 svg 不写宽高，CSS 里 background-size: 100% 32px 撑满 hr)：
    中央午夜领主翼骷髅徽(骨白、红目镜)，两侧各一道铜色盔甲纹章闪电从翼后射出，闪电尖分成两股 1px 细叉，
    一笔画成上下两条线直通到两端，两端按百分比渐隐(遮罩)。
    以前双线是 CSS 渐变、和 SVG 各自对齐像素网格，125% 缩放下接口会错开 1 个物理像素，所以全部画进同一张图。
    设计坐标仍是 W x 40、徽在 x=W/2：整组放进 x=50% 的嵌套 svg、平移 -W/2，中心就落在 hr 正中"""
    cx = W / 2
    k, kv = length / 44, 1.35
    tip = 15 + length
    far = 8000   # 线画到中心外 8000 单位(6400px)，由根视口裁掉

    def pts(seq, side):
        return " L".join(f"{cx + side * (15 + (x - 2) * k):.2f},{20 + (y - 6) * kv:.2f}" for x, y in seq)
    bolts = " ".join(f"M{pts(_HERALD_BOLT, s)}Z" for s in (1, -1))
    mids = " ".join(f"M{pts(_HERALD_MID, s)}" for s in (1, -1))
    centered = f'<svg x="50%" overflow="visible"><g transform="scale(.8) translate({-cx:g},0)">{{}}</g></svg>'
    grads, lines = [], []
    for i, (y, op, f0, f1) in enumerate(RULE_LINES):
        # 两端渐隐：userSpaceOnUse 的百分比按根视口(= hr 宽)算
        grads.append(f'<linearGradient id="f{i}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="100%" y2="0">'
                     f'<stop offset="{f0}" stop-color="#fff" stop-opacity="0"/><stop offset="{f1}" stop-color="#fff"/>'
                     f'<stop offset="{1 - f1:g}" stop-color="#fff"/><stop offset="{1 - f0:g}" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                     f'<mask id="m{i}" maskUnits="userSpaceOnUse" x="0" y="0" width="100%" height="100%">'
                     f'<rect width="100%" height="100%" fill="url(#f{i})"/></mask>')
        paths = []
        for side in (1, -1):
            gid = f"p{'r' if side > 0 else 'l'}{i}"
            x0, x1 = cx + side * (tip - 2), cx + side * RULE_LINE_START
            grads.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x0:.2f}" y1="0" x2="{x1:.2f}" y2="0">'
                         f'<stop offset="0" stop-color="{bolt}"/><stop offset="1" stop-color="{bolt}" stop-opacity="{op}"/></linearGradient>')
            # 从闪电尖斜出到线的高度，再平直一路画到头；1.25 单位 = 1px
            paths.append(f'<path d="M{cx + side * (tip - 2):.2f},20 L{cx + side * (tip + 4):.2f},{y} L{cx + side * far:g},{y}" '
                         f'fill="none" stroke="url(#{gid})" stroke-width="1.25" stroke-linejoin="round"/>')
        lines.append(f'<g mask="url(#m{i})">{centered.format("".join(paths))}</g>')
    defs = f"<defs>{_eyes_defs('e') if eyes else ''}{''.join(grads)}</defs>"
    s = 34 / 800
    tx = cx - 941.19 * s / 2
    eye = _eyes("e") if eyes else ""
    centre = (f'<path d="{bolts}" fill="{bolt}"/>'
              f'<path d="{mids}" fill="none" stroke="{groove}" stroke-width=".7" stroke-linejoin="round" stroke-opacity=".9"/>'
              f'<g transform="translate({tx:.2f},3) scale({s:.5f})"><g transform="{NL_TF}">{eye}</g>'
              f'<g transform="{NL_TF}" fill="{fill}">{NL_BODY}</g></g>')
    return f'<svg {SVG}>{defs}{"".join(lines)}{centered.format(centre)}</svg>'


FOLDER_VB = "0 1 16 12.5"   # 文件夹图标外框(CSS 里画成 13px 宽，和蝙蝠的视觉大小一致)


def folder(fill="#a0804c"):
    """文件列表的合上文件夹：扁平纹章剪影，斜切的页签 + 一道切开的翻盖缝 + 正面镂空菱形(和 H3 菱形、缝线菱形同一语言)"""
    return (f'<svg {SVG} viewBox="{FOLDER_VB}"><path fill-rule="evenodd" fill="{fill}" d="'
            'M.5,1.5 H5.8 L7.4,3.2 H15.5 V4.3 H.5 Z '
            'M.5,5.1 H15.5 V13 H.5 Z M8,6.2 L10.1,9 L8,11.8 L5.9,9 Z"/></svg>')


def folder_open(front="#b08a52", back="#5e4526"):
    """打开的文件夹：暗铜后片(带页签) + 亮铜前片向右上掀开，前片上同样镂空菱形(透出后片的暗色)"""
    return (f'<svg {SVG} viewBox="{FOLDER_VB}">'
            f'<path fill="{back}" d="M.5,1.5 H5.8 L7.4,3.2 H14.5 V13 H.5 Z"/>'
            f'<path fill-rule="evenodd" fill="{front}" d="M3.6,6.1 H15.9 L13.3,13 H.5 Z M8.3,7.3 L10.2,9.6 L8.3,11.9 L6.4,9.6 Z"/></svg>')


def _mirror_path(start, segs, cx):
    """左半边轮廓(从顶部中线出发，L/Q 段走到底部中线)→ 左右对称的闭合路径：右半边 = 左半边镜像后倒着走回去"""
    m = lambda p: (2 * cx - p[0], p[1])
    f = lambda p: f"{p[0]:g},{p[1]:g}"
    d, pts = [f"M{f(start)}"], [start]
    for s in segs:
        d.append(f"L{f(s[1])}" if s[0] == "L" else f"Q{f(s[1])} {f(s[2])}")
        pts.append(s[-1])
    for i in range(len(segs) - 1, -1, -1):
        s, p0 = segs[i], pts[i]
        d.append(f"L{f(m(p0))}" if s[0] == "L" else f"Q{f(m(s[1]))} {f(m(p0))}")
    return " ".join(d) + "Z"


# 文件夹蝙蝠：合上 / 打开是同一只倒挂在横杆上的蝙蝠(同一根横杆、同一对脚爪、同一个朝下的头和尖耳朵，铜色身子)，
# 合上 = 翅膀裹起来；打开 = 张开双翼(经典张翅蝙蝠倒过来的姿势：耳朵冲下、扇贝翼缘朝上、翼膜贴到脚边)、翼膜血红。
# viewBox 都是 0 0 20 16，中线 x=10；耳尖都落在 y=14.1
# (第一版打开状态让翅膀从脚边往外张，翅膀长在了不对的位置，看着像两块红布——用户：看不出是翅膀)


C_OLD_BONE = "#bfb39a"   # 蝙蝠身子：旧骨白(比徽的骨白暗一档、偏黄，亮度和文件名相当，不抢字；原为铜色)


def _bat_perch(fill, perch, foot_y):
    return (f'<path d="M3,.8 H17" stroke="{perch}" stroke-width="1.1" stroke-linecap="round"/>'
            f'<path d="M9.1,{foot_y} V.8 M10.9,{foot_y} V.8" stroke="{fill}" stroke-width=".9"/>')


def bat_roost(fill=C_OLD_BONE, perch="#857b68", seam="#6b6252"):
    """合上的文件夹 = 倒挂在横杆上睡觉的蝙蝠：脚爪勾着横杆，裹着的翅膀上宽下窄，头朝下、两只尖耳朵冲下
    (认蝙蝠就靠这对耳朵；横杆和脚爪交代倒挂的姿势)"""
    d = _mirror_path((10, 2.8), [
        ("L", (8.9, 2.4)), ("L", (7.4, 2.9)),
        ("L", (5.8, 1.8)),                                         # 翅腕尖
        ("Q", (4.7, 4.5), (5.5, 6.8)),                             # 裹着的翅膀外缘(最宽)
        ("Q", (6.3, 9.3), (7.9, 11.3)),                            # 往下收到头
        ("L", (8.6, 14.1)), ("L", (9.1, 11.9)), ("L", (10, 11.6)),  # 耳尖冲下、两耳之间的 V(和张开那只的头一样)
    ], 10)
    return (f'<svg {SVG} viewBox="0 0 20 16">{_bat_perch(fill, perch, 2.5)}<path d="{d}" fill="{fill}"/>'
            f'<path d="M10,3.5 C10.2,5.7 10.2,7.9 10,10.1" fill="none" stroke="{seam}" stroke-width=".55"/></svg>')


BAT_OPEN_VB = "-2.6 0 25.2 16"   # 张开的翅膀比合上那只(0 0 20 16)宽；CSS 图标框 22×14，两者同一缩放


def bat_open(fill=C_OLD_BONE, membrane="#a3232b", perch="#857b68", rot=-26, wing_len=13.6, root_y=10.0):
    """打开的文件夹 = 同一只倒挂的蝙蝠张开双翼。翅膀直接用笔记标题下横幅的翼形(Lorc batwing-emblem 左翼 +
    镜像，wings.wing)，按正立蝙蝠外旋 rot 度摆好后**整对上下翻转**(蝙蝠是倒挂的)：扇贝翼缘朝上对着脚、
    翼尖垂到外下方，翼膜血红；旧骨白身子顶端是平的胯部，脚爪从胯部伸上去勾住横杆，头朝下、耳朵冲下。
    (试过：自己画的翼——位置不对像两块红布 / 翼骨细节多余；分割线徽章的翼——又高又圆，像红斗篷；
    横幅翼不翻转——翼尖朝上，和倒挂的身子方向对不上)"""
    import wings as W
    s = wing_len / math.dist(W.ROOT, W.TIP)
    lw, _, _ = W.wing(rot=rot, scale=s, to=(9, root_y), claw=False)
    rw, _, _ = W.wing(rot=-rot, scale=s, mirror=True, to=(11, root_y), claw=False)
    f = W.affine(rot, s, False, W.ROOT, (9, root_y))
    flip = lambda p: (f(p)[0], 16 - f(p)[1])
    fp, wr = flip(W.FINGERTIPS[1]), flip(W.WRIST)       # 翻过来后离身子最近的指尖、腕关节
    body = _mirror_path((10, 2.8), [
        ("L", (8.8, 2.8)),                                         # 平的胯部(脚爪从这里伸上去)
        ("Q", (7.9, 6.2), (8.4, 9.6)),
        ("Q", (8.4, 10.8), (7.9, 11.5)),
        ("L", (8.6, 14.1)), ("L", (9.1, 11.9)), ("L", (10, 11.6)),  # 头：耳尖冲下(和合上那只一样)
    ], 10)
    # 补翼膜：横幅翼的翼根是个细尖，靠身体那侧还有一大块半圆凹口(原本是骷髅旁的前缘弧)，翻过来后翅膀
    # 只有一小段贴着身子，看着像断开(用户：连接处像断开了)。两侧各补一片：下沿接到肩部(头上方)，
    # 上沿沿身子往上延到胯部附近、带一道浅凹弧，和原有的扇贝翼缘连成一气
    #   (按指尖 fp、腕关节 wr 算，翅膀放大后照样贴合)
    pts = [(8.7, 4.3), ("Q", ((8.7 + fp[0]) / 2 + .2, fp[1] + .3), fp), (wr[0] - .5, (fp[1] + wr[1]) / 2 + .4),
           (wr[0] - .5, wr[1] - .35), ("Q", (wr[0] - .4, wr[1] + .05), (wr[0], wr[1] + .15)), (8.5, 10.9)]

    def web_path(mx):
        g = lambda p: f"{(20 - p[0]) if mx else p[0]:.2f},{p[1]:.2f}"
        d = []
        for i, p in enumerate(pts):
            d.append(f"Q{g(p[1])} {g(p[2])}" if p[0] == "Q" else ("M" if i == 0 else "L") + g(p))
        return " ".join(d) + "Z"
    web = web_path(False) + " " + web_path(True)
    return (f'<svg {SVG} viewBox="{BAT_OPEN_VB}">{_bat_perch(fill, perch, 3.4)}'
            f'<g transform="translate(0 16) scale(1 -1)"><path d="{lw}{rw}" fill="{membrane}"/></g>'
            f'<path d="{web}" fill="{membrane}"/><path d="{body}" fill="{fill}"/></svg>')


def bat(fill="#0b1322"):
    """一只飞行中的小蝙蝠剪影(空状态页用)。viewBox 64x32"""
    return (f'<svg {SVG} viewBox="0 0 64 32"><path d="M32,9 L30,5 L29.5,9.5 C26,9 24,11 23,14 '
            f'C19,8 11,6 2,9 C7,11 9,15 9,19 C12,16 15,16 17,19 C19,16 22,17 24,20 C27,19 30,21 32,24 '
            f'C34,21 37,19 40,20 C42,17 45,16 47,19 C49,16 52,16 55,19 C55,15 57,11 62,9 C53,6 45,8 41,14 '
            f'C40,11 38,9 34.5,9.5 L34,5 Z" fill="{fill}"/></svg>')


# ---- 列表符号：每一级一个扁平纹章剪影(色板内一两色平涂，按级循环) ----
C_BONE, C_CRIMSON, C_BRONZE, C_EMBER = "#d8ccb2", "#b3262e", "#b08a52", "#e8705f"


def bullet_skull(fill=C_BONE, eye=C_CRIMSON):
    """一级：午夜领主骷髅，眼窝镂空处垫平涂血红(红目镜)"""
    x, y, w, h = SKULL_BOX
    eyes = "".join(f'<ellipse cx="{ex}" cy="{ey}" rx="60" ry="44" fill="{eye}"/>' for ex, ey in EYES)
    return f'<svg {SVG} viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}">{eyes}<g fill="{fill}">{SKULL_BODY}</g></svg>'


def outline_skull(fill=C_BONE, eye=C_CRIMSON, hollow=False):
    """大纲面板的图标：Heritage「Deadly Skulls 02 · Element 1」平面化(tools/heritage_skull.py 生成 skull-flat.svg)，
    骨白剪影 + 平涂血红眼窝，鼻腔、嘴镂空。hollow=True 是空心版(只留外轮廓一圈 + 血红眼窝)，
    给没有子级的标题——对应 Maple 的空心圆点 / 实心圆点"""
    src = (ICONS / "skull-flat.svg").read_text(encoding="utf-8")
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    eyes = re.search(r'id="eyes" d="([^"]+)"', src).group(1)
    body = re.search(rf'id="{"ring" if hollow else "skull"}"[^>]* d="([^"]+)"', src).group(1)
    return (f'<svg {SVG} viewBox="{vb}"><path d="{eyes}" fill="{eye}"/>'
            f'<path d="{body}" fill="{fill}" fill-rule="evenodd"/></svg>')


def hollow_skull(fill=C_BONE, eye=C_CRIMSON, thicken=10):
    """空心骷髅(大纲里没有子级的标题)：用户指定的 ICOOON MONO「頭蓋骨の無料アイコン7」(侧面骷髅线稿，
    src/icons/skull-hollow.svg 原样保存)，轮廓改骨白、眼窝平涂血红。原轮廓线约 16/512 宽，12px 下只剩 0.4px 发虚，
    给轮廓再描一圈同色 thicken 单位的边(两侧各外扩一半)略加粗(试过 0/6/10/14/30：30 把下颌牙齿糊成一团，用户嫌粗；10 不发虚、细节还在)。
    (之前试过 Lucide skull 改色、同剪影描边的空心版，用户改用这个)"""
    path = ICONS / "skull-hollow.svg"
    if not path.exists():   # ICOOON MONO 不许再分发素材文件，仓库里没有这个文件 → 退回 Heritage 剪影的空心版
        print("[ornaments] 缺 src/icons/skull-hollow.svg(ICOOON MONO「頭蓋骨の無料アイコン7」，https://icooon-mono.com/ 免费下载 SVG)，"
              "空心骷髅改用 skull-flat 的外轮廓", file=sys.stderr)
        return outline_skull(fill, eye, hollow=True)
    src = path.read_text(encoding="utf-8")
    outline, socket = re.findall(r'<path[^>]* d="([^"]+)"', src)[:2]
    return (f'<svg {SVG} viewBox="0 0 512 512">'
            f'<path d="{outline}" fill="{fill}" stroke="{fill}" stroke-width="{thicken}" stroke-linejoin="round"/>'
            f'<path d="{socket}" fill="{eye}"/></svg>')


def bullet_bat(fill=C_CRIMSON):
    """二级：展翼蝙蝠剪影(bat() 的形，视框收紧)"""
    return bat(fill).replace('viewBox="0 0 64 32"', 'viewBox="1.5 4.5 61 20"')


C_CHAIN = "#535b6a"   # 功能栏铁链 / 铁钩：暗冷铁灰，比图标和铁环(CSS 里用 --icon-color)暗一档(用户要求)。
#                        不能叫 C_STEEL——后面 callout 图标那组同名常量(#aeb8c8)会覆盖它
C_STEEL_SKULL, C_STEEL_EYE = "#5e6676", "#5c1519"   # 链尾骷髅坠：和铁链同一档暗铁灰(略亮一点好认) + 暗红眼窝(骨白 + 亮红太抢眼)


RB_LINK_H = 13   # 铁钩下 / 链尾那种带侧面环的链节高度(px)


def ribbon_link(h=RB_LINK_H):
    """左侧功能栏的一节铁链(10×h)：正面椭圆环 + 上下两截侧面环(竖短杠)接到两端，外加一道细高光。
    铁钩到第一枚环、链尾用这种；两枚铁环之间用 ribbon_link_oval(只有椭圆)。
    (第一版是一条连续平铺的链子垫在铁环后面，环距 38 不是链节 16 的整数倍，每个空隙露出的截面都不同，看着杂乱——用户指出)"""
    c = h / 2
    return (f'<svg {SVG} width="10" height="{h}" viewBox="0 0 10 {h}">'
            f'<ellipse cx="5" cy="{c}" rx="2.7" ry="4.7" fill="none" stroke="{C_CHAIN}" stroke-width="1.3"/>'
            f'<ellipse cx="4.6" cy="{c - .6}" rx="1.6" ry="3.4" fill="none" stroke="#a3abba" stroke-opacity=".2" stroke-width=".6"/>'
            f'<path d="M5,0 V{c - 4.6:.2f} M5,{c + 4.6:.2f} V{h}" stroke="{C_CHAIN}" stroke-width="1.7"/></svg>')


def ribbon_link_oval():
    """两枚铁环之间的那节链环(10×10)：只有正面椭圆环(和 ribbon_link 同一个椭圆)，没有上下侧面环——
    按钮间距 10px，椭圆 9.4 高，两端各有约 1px 藏在铁环后面(CSS 里画在所有铁环下层)，看着是链环穿过铁环"""
    return (f'<svg {SVG} width="10" height="10" viewBox="0 0 10 10">'
            f'<ellipse cx="5" cy="5" rx="2.7" ry="4.7" fill="none" stroke="{C_CHAIN}" stroke-width="1.3"/>'
            f'<ellipse cx="4.6" cy="4.4" rx="1.6" ry="3.4" fill="none" stroke="#a3abba" stroke-opacity=".2" stroke-width=".6"/></svg>')


def ribbon_tail(n=4, h=RB_LINK_H, sw=16):
    """链尾：最后一枚铁环下面再垂 n 节链环，末端挂一颗冷铁骷髅坠(bullet_skull 改铁灰 + 暗红眼窝)。宽 sw(16，原 13 嫌小)，高 n·h − 1 + 骷髅高"""
    x, y, w, hh = SKULL_BOX
    sh = sw * hh / w
    links = "".join(f'<g transform="translate({(sw - 10) / 2} {k * h})">{ribbon_link(h)[ribbon_link(h).index(">") + 1:-6]}</g>' for k in range(n))
    skull = (f'<svg x="0" y="{n * h - 1}" width="{sw}" height="{sh:.2f}" viewBox="{x:.1f} {y:.1f} {w:.1f} {hh:.1f}">'
             + "".join(f'<ellipse cx="{ex}" cy="{ey}" rx="60" ry="44" fill="{C_STEEL_EYE}"/>' for ex, ey in EYES)
             + f'<g fill="{C_STEEL_SKULL}">{SKULL_BODY}</g></svg>')
    H = n * h - 1 + sh
    return f'<svg {SVG} width="{sw}" height="{H:.2f}" viewBox="0 0 {sw} {H:.2f}">{links}{skull}</svg>'


def ribbon_head():
    """锁链顶端：一道横梁 + J 形铁钩，钩底挂下第一节链环，一张图 14×27(钩子和链环分开画时，钩底在竖杆左边 2px、
    和挂在正中的链环错开，两者也只是刚好相碰、取整后露缝——用户指出)。
    竖杆在中线右边 2.5px，钩弯是以中线为圆心的半圆，最低点正落在中线上；链环顶上的侧面环插进钩弯 1.6px，
    下端伸到图底(= 第一枚铁环的圆底顶边，CSS 里比环线再往下 1.5px，藏在圆底后面)，两头都不留缝"""
    hl = "#a3abba"
    return (f'<svg {SVG} width="14" height="27" viewBox="0 0 14 27">'
            f'<path d="M2,1.5 H12" stroke="{C_CHAIN}" stroke-width="1.6" stroke-linecap="round"/>'
            f'<path d="M9.5,1.5 V10.5 A2.5,2.5 0 0 1 4.5,10.5 V9" fill="none" stroke="{C_CHAIN}" stroke-width="1.6" stroke-linecap="round"/>'
            f'<path d="M7,11.4 V14.8 M7,24.2 V27" stroke="{C_CHAIN}" stroke-width="1.7"/>'
            f'<ellipse cx="7" cy="19.5" rx="2.7" ry="4.7" fill="none" stroke="{C_CHAIN}" stroke-width="1.3"/>'
            f'<ellipse cx="6.6" cy="18.9" rx="1.6" ry="3.4" fill="none" stroke="{hl}" stroke-opacity=".2" stroke-width=".6"/></svg>')


def nav_wings(rot=-45, gap=0, wing_len=100):
    """侧栏各面板顶上的按钮行收起时留下的一对蝙蝠翼(遮罩用：黑色剪影，颜色由 CSS 铺 --icon-color)。
    只要左右两片翅膀、不画身子(先用的整只小蝙蝠 bullet_bat 缩到 24×8 看不出是蝙蝠，用户要只留两翼)，两翼在正中连起来。
    翼形 = 笔记标题下翼骷髅横幅同源的 Lorc 左翼(wings.wing)外旋 45°、镜像成右翼，翼根贴在中线上(gap=0)；
    翼根是一条直边(左翼 (191.56,365.91)→(225.9,334.8))，左右两条交叉后上下各留一个 V 形缺口，
    取四个端点的凸包补一块接合块，连成一个整体剪影。
    三块合成一条 path、统一绕向(镜像出来的右翼方向是反的，要倒过来；接合块按面积符号对齐)：
    分开画会在贴边处留抗锯齿浅缝、描边盖缝又会在接合块顶点冒出小圆点；方向不一致写进同一条 path，
    重叠处按 nonzero 规则互相抵消、正中裂一道细缝。
    试过外旋 20/32/45/58°、翼根间距 -4~12：45° 在 10px 高时扇贝翼缘还清楚；分开(12)读得出两片但用户要连起来；
    视框贴合外框，宽高比约 3.6:1，CSS 里画成 36×10"""
    import wings as W
    s = wing_len / math.dist(W.ROOT, W.TIP)
    fl = W.affine(rot, s, False, W.ROOT, (-gap, 0))
    fr = W.affine(-rot, s, True, W.ROOT, (gap, 0))
    left = W.transform(W.parse(W.LORC_WING), fl)
    right = W.transform(W.parse(W.LORC_WING), fr)

    def reverse(segs):
        """倒转一条闭合路径(只有 M / L / C / Z)"""
        nodes, cur = [], None
        for c, pts in segs:
            if c == "M":
                cur = pts[0]
            elif c in "LC":
                nodes.append((c, cur, pts))
                cur = pts[-1]
        out = [("M", [cur])]
        for c, a, pts in reversed(nodes):
            out.append(("C", [pts[1], pts[0], a]) if c == "C" else ("L", [a]))
        return out + [("Z", [])]

    def area(poly):
        return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1])) / 2
    ends = lambda segs: [pts[-1] for c, pts in segs if pts]
    right = reverse(right)
    edge = ((191.564, 365.906), (225.9, 334.8))
    pts = sorted({fl(p) for p in edge} | {fr(p) for p in edge})
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for seq, out in ((pts, lo), (pts[::-1], up)):
        for q in seq:
            while len(out) >= 2 and cross(out[-2], out[-1], q) <= 0:
                out.pop()
            out.append(q)
    joint = lo[:-1] + up[:-1]
    if (area(joint) > 0) != (area(ends(left)) > 0):
        joint.reverse()
    jd = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in joint) + "Z"
    x0, y0, x1, y1 = W.bbox(left)[:2] + W.bbox(right)[2:]
    return (f'<svg {SVG} viewBox="{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}">'
            f'<path d="{W.to_d(left)}{W.to_d(right)}{jd}" fill="#000"/></svg>')


def bullet_bolt(fill=C_BRONZE):
    """三级：纹章闪电"""
    return bolt(fill)


def bullet_lozenge(fill=C_BONE):
    """四级：骨白菱形"""
    return diamond(fill)


def skull(fill="#b08a52", eyes=True):
    """单独的午夜领主骷髅(H1 饰线中心)。"""
    x, y, w, h = SKULL_BOX
    defs = f"<defs>{_eyes_defs('e')}</defs>" if eyes else ""
    eye = _eyes("e") if eyes else ""
    return (f'<svg {SVG} viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}">{defs}{eye}'
            f'<g fill="{fill}">{SKULL_BODY}</g></svg>')


# ---- 色板常量：原为 callout 角花(第七轮，2026-10-23 已删)定义，后面的图案仍按这里的值取色(会覆盖前面的同名常量)，别删 ----
C_BONE, C_BRONZE, C_STEEL, C_BOLT, C_GLOW, C_BLOOD = "#d8ccb2", "#b08a52", "#aeb8c8", "#c9d7f0", "#7fa2dc", "#9a1f27"


C_RULE_BRONZE = "#b08a52"   # = 分割线闪电/双线的铜色


# ---- Callout 图标(第十六轮)：替换 Obsidian 内置 Lucide 线条图标为单色纹章剪影(CSS 遮罩着色，跟随类型颜色) ----
# 剪影来自 game-icons.net(Lorc，CC BY 3.0)，存在 src/icons/callout/；构建时只抽 path 数据重新输出干净的 SVG。
# "@" 开头的是本主题自绘：午夜领主徽、哥特引号。tarot-moon.svg：用户提供的 ICOOON MONO 风塔罗牌，外框圆角 42→22、角饰圆角 24→12
CALLOUT_ICONS = (
    (("note",), "quill"),
    (("abstract", "summary", "tldr"), "scroll-unfurled"),
    (("info",), "semi-closed-eye"),
    (("todo",), "tied-scroll"),
    (("important",), "@emblem"),
    (("tip", "hint"), "candle-light"),
    (("success", "check", "done"), "laurels"),
    (("question", "help", "faq"), "tarot-moon"),         # 塔罗牌(月与星)：迷雾、未知、疑问
    (("warning", "caution", "attention"), "claw-slashes"),  # 闪电爪的三道爪痕
    (("failure", "fail", "missing"), "crossed-bones"),
    (("danger", "error"), "skull-crossed-bones"),
    (("bug",), "spider-web"),
    (("example",), "open-book"),
    (("quote", "cite"), "@quote"),
)
# Callout 拉丁铭牌(标题前的铜色小字)，按 CALLOUT_ICONS 每组第一个类型取词，别名同词
CALLOUT_LATIN = {
    "note": "NOTA", "abstract": "SUMMA", "info": "NOTITIA", "todo": "AGENDA", "important": "MEMENTO",
    "tip": "CONSILIUM", "success": "FACTUM", "question": "QUAESTIO", "warning": "CAVE", "failure": "DEFECTUS",
    "danger": "PERICULUM", "bug": "VITIUM", "example": "EXEMPLUM", "quote": "DICTUM",
}


def callout_glyph(name):
    """→ 遮罩用 SVG(黑色剪影)。game-icons 的图案在 512 画布里常常不居中(爪痕明显偏右)，
    按 src/icons/callout/bbox.json(tools/icon_bbox.py 量的实际外框)取正方形 viewBox 重新居中"""
    if name == "@emblem":
        return f'<svg {SVG} viewBox="0 0 941.19 800"><g transform="{NL_TF}">{NL_BODY}</g></svg>'
    if name == "@quote":
        # 两枚上提的粗引号(❝)：圆头 + 向右上甩起的尾巴
        mark = "M{x},38 C{a},38 {b},34 {b},29.5 C{b},22 {c},14 {d},9 L{e},11.5 C{f},15 {g},19.5 {g},22 C{h},21.5 {i},25 {i},29.5 C{i},34.5 {j},38 {x},38Z"
        def one(o):
            v = dict(x=12 + o, a=7.5 + o, b=4 + o, c=8 + o, d=17 + o, e=18.5 + o, f=13.5 + o, g=11 + o, h=16.5 + o, i=20 + o, j=16.5 + o)
            return mark.format(**{k: f"{w:.1f}" for k, w in v.items()})
        return f'<svg {SVG} viewBox="0 0 48 48"><path d="{one(0)} {one(22)}"/></svg>'
    import json
    icons = ROOT / "src" / "icons" / "callout"
    if name == "tarot-moon" and not (icons / "tarot-moon.svg").exists():
        # ICOOON MONO 改出来的塔罗牌不随仓库分发(素材条款不许再分发) → 用半闭眼代替
        print("[ornaments] 缺 src/icons/callout/tarot-moon.svg(ICOOON MONO 素材，不随仓库分发)，question 图标改用 semi-closed-eye", file=sys.stderr)
        name = "semi-closed-eye"
    src = (icons / f"{name}.svg").read_text(encoding="utf-8")
    ds = re.findall(r'<path[^>]*\sd="([^"]+)"', src)
    x, y, w, h, gx, _ = json.loads((icons / "bbox.json").read_text(encoding="utf-8"))[name]
    # 水平中心往视觉重心挪一半(爪痕一头粗一头细，外框居中仍显得偏右)；正方形框放大到仍能装下整个外框
    cx, cy = x + w / 2 + (gx - (x + w / 2)) * .5, y + h / 2
    side = max(2 * max(cx - x, x + w - cx), h) * 1.04
    vb = f"{cx - side / 2:.1f} {cy - side / 2:.1f} {side:.1f} {side:.1f}"
    return f'<svg {SVG} viewBox="{vb}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</svg>"


def emblem_faint():
    """空白页水印：极淡的徽 + 微弱红目。"""
    defs = _eyes_defs("e", hot="#ff5a3c", mid="#a3161c", dark="#2a0508")
    return (f'<svg {SVG} viewBox="0 0 941.19 800"><defs>{defs}</defs>'
            f'<g transform="{NL_TF}" opacity=".55">{_eyes("e")}</g>'
            f'<g transform="{NL_TF}" fill="#9dbbe8" fill-opacity=".055">{NL_BODY}</g></svg>')


def tex_grain(size=240):
    """细颗粒：亮点+暗点两层噪声。"""
    return (f'<svg {SVG} width="{size}" height="{size}">'
            '<filter id="a" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".82" numOctaves="3" seed="3" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 .86  0 0 0 0 .82  0 0 0 0 .72  2.2 0 0 0 -1.32"/></filter>'
            '<filter id="b" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="2" seed="11" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 .02  -2.4 0 0 0 1.02"/></filter>'
            '<rect width="100%" height="100%" filter="url(#a)" opacity=".16"/>'
            '<rect width="100%" height="100%" filter="url(#b)" opacity=".32"/></svg>')


def tex_mottle(size=760):
    """斑驳：低频噪声 → 暗色淤斑 + 冷蓝浮光。"""
    return (f'<svg {SVG} width="{size}" height="{size}">'
            '<filter id="d" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".0062" numOctaves="5" seed="7" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 .005  0 0 0 0 .012  0 0 0 0 .03  -1.9 0 0 0 .95"/></filter>'
            '<filter id="l" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".0085" numOctaves="4" seed="23" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 .2  0 0 0 0 .3  0 0 0 0 .5  1.6 0 0 0 -.86"/></filter>'
            '<rect width="100%" height="100%" filter="url(#d)" opacity=".44"/>'
            '<rect width="100%" height="100%" filter="url(#l)" opacity=".17"/></svg>')


def tex_stains(size=1180):
    """更大尺度的水渍/锈斑，带一点干涸血色。"""
    return (f'<svg {SVG} width="{size}" height="{size}">'
            '<filter id="s" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".0028" numOctaves="3" seed="41" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 .01  0 0 0 0 .015  0 0 0 0 .035  -3 0 0 0 1.38"/></filter>'
            '<filter id="r" x="0" y="0" width="100%" height="100%"><feTurbulence type="turbulence" baseFrequency=".004" numOctaves="4" seed="5" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 .35  0 0 0 0 .04  0 0 0 0 .05  3.2 0 0 0 -1.5"/></filter>'
            '<rect width="100%" height="100%" filter="url(#s)" opacity=".5"/>'
            '<rect width="100%" height="100%" filter="url(#r)" opacity=".065"/></svg>')


def tex_atmos(size=1024):
    """斑驳 + 冷蓝浮光 + 大尺度水渍/干涸血色，合成一张无缝贴图(构建时栅格化)。
    第三轮：频率约减半(斑块放大一倍)、八度加到 5，块大但边缘仍斑驳；第四轮：用户嫌太斑驳，亮斑/暗斑对比度调低。"""
    return (f'<svg {SVG} width="{size}" height="{size}">'
            '<filter id="d" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".0028" numOctaves="5" seed="7" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 .005  0 0 0 0 .012  0 0 0 0 .03  -1.9 0 0 0 .95"/></filter>'
            '<filter id="l" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".0036" numOctaves="5" seed="23" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 .2  0 0 0 0 .3  0 0 0 0 .5  1.7 0 0 0 -.9"/></filter>'
            '<filter id="s" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".0016" numOctaves="3" seed="41" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 .01  0 0 0 0 .015  0 0 0 0 .035  -3 0 0 0 1.38"/></filter>'
            '<filter id="r" x="0" y="0" width="100%" height="100%"><feTurbulence type="turbulence" baseFrequency=".0022" numOctaves="4" seed="5" stitchTiles="stitch"/>'
            '<feColorMatrix values="0 0 0 0 .35  0 0 0 0 .04  0 0 0 0 .05  3.2 0 0 0 -1.5"/></filter>'
            '<rect width="100%" height="100%" filter="url(#s)" opacity=".5"/>'
            '<rect width="100%" height="100%" filter="url(#r)" opacity=".065"/>'
            '<rect width="100%" height="100%" filter="url(#d)" opacity=".41"/>'
            '<rect width="100%" height="100%" filter="url(#l)" opacity=".18"/></svg>')


# ---- Dark Deco：侧栏卡片 / 弹窗的线框与蝙蝠翼扇角花、侧栏战旗、主区标签、属性框 ----
# 线框都是 border-image 九宫格：整张 SVG 3S×3S(带 width/height，切片按 CSS px 算)，四角各 S×S 不拉伸，
# 中间那段只有两条直线、随边长拉伸。角花在 26×26 的设计格里画(外线在 1.5、内线在 5.5)，按 S/26 缩放，
# 线宽用 non-scaling-stroke 保持 1px。
# 配色：界面外框(卡片/弹窗/战旗/主区标签)用闪电淡蓝；属性框在正文里，跟正文的分割线、标题饰一样用铜色
C_DECO = "#9dbbe8"            # = --nl-lightning
C_DECO_PROP = C_RULE_BRONZE
_DECO_O, _DECO_I = 1.5, 5.5   # 外线、内线到边缘的距离(设计格单位)
_NS = 'vector-effect="non-scaling-stroke"'


def _fan_points(r=16, n=4, c=_DECO_O):
    return [(c + r * math.cos(math.radians(90 * i / n)), c + r * math.sin(math.radians(90 * i / n))) for i in range(n + 1)]


def _fan_scallops(pts, c=_DECO_O, pull=.62):
    """相邻两根扇骨尖之间的扇贝弧(控制点往角上拉 = 蝙蝠翼膜的内凹缘)"""
    d = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        d.append(((x0, y0), (c + (mx - c) * pull, c + (my - c) * pull), (x1, y1)))
    return d


def _bone_spike(o, tip, out=4.5, w0=1.3, w1=.7):
    """从角 (o,o) 出发、穿过翼膜缘 tip 再往外伸 out 的翼骨：根部宽 w0，到翼膜缘处 w1，伸出部分收成尖刺"""
    ux, uy = tip[0] - o, tip[1] - o
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    nx, ny = -uy, ux
    end = (tip[0] + ux * out, tip[1] + uy * out)
    pts = [(o + nx * w0 / 2, o + ny * w0 / 2), (tip[0] + nx * w1 / 2, tip[1] + ny * w1 / 2), end,
           (tip[0] - nx * w1 / 2, tip[1] - ny * w1 / 2), (o - nx * w0 / 2, o - ny * w0 / 2)]
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"


def _deco_corner(col):
    """左上角角花(设计格坐标)：蝙蝠翼扇，三片扇贝翼膜从角上展开，两根翼骨穿出翼膜缘、骨刺突出在外，
    内线接到第一片扇贝弧上。(原来四片扇贝 + 细扇骨，用户说像蜘蛛网，去掉一片、让骨刺突出)"""
    o, i = _DECO_O, _DECO_I
    line = lambda d, a: f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{a}" stroke-width="1" {_NS}/>'
    pts = _fan_points(n=3)
    sc = _fan_scallops(pts)
    fan = f"M{o},{o} L{pts[0][0]:.2f},{pts[0][1]:.2f} " + " ".join(f"Q{c[0]:.2f},{c[1]:.2f} {b[0]:.2f},{b[1]:.2f}" for _, c, b in sc) + " Z"
    ribs = " ".join(_bone_spike(o, p) for p in pts[1:-1])
    # 在第一片扇贝弧上找 y = 5.5 的点
    (a, c, b) = sc[0]
    t = min((abs((1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1] - i), t) for t in [k / 400 for k in range(401)])[1]
    xi = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0]
    return (line(f"M{o},26 V{o} H26", .62)
            + f'<path d="{fan}" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".62" stroke-width="1" {_NS}/>'
            + f'<path d="{ribs}" fill="{col}" fill-opacity=".8"/>'
            + line(f"M26,{i} H{xi:.2f} M{i},26 V{xi:.2f}", .32))


def deco_frame(S=32, top=True, col=C_DECO):
    """卡片 / 弹窗线框(border-image 用，切片 = S)。top=False：上边中段不画(属性框的上边由标题行自己画、好在字的位置断开)"""
    k, W = S / 26, 3 * S
    g = f'<g transform="scale({k:.4f})">{_deco_corner(col)}</g>'
    tf = ["", f"translate({W} 0) scale(-1 1)", f"translate(0 {W}) scale(1 -1)", f"translate({W} {W}) scale(-1 -1)"]
    corners = "".join(f'<g transform="{t}">{g}</g>' for t in tf)
    o, i = _DECO_O * k, _DECO_I * k
    edges = []
    for off, a in ((o, .62), (i, .32)):
        d = f"M{off:.2f},{S} V{2 * S} M{W - off:.2f},{S} V{2 * S} M{S},{W - off:.2f} H{2 * S}"
        if top:
            d += f" M{S},{off:.2f} H{2 * S}"
        edges.append(f'<path d="{d}" stroke="{col}" stroke-opacity="{a}" stroke-width="1"/>')
    return f'<svg {SVG} width="{W}" height="{W}" viewBox="0 0 {W} {W}">{corners}{"".join(edges)}</svg>'


def deco_banner(cloth="#5a1018", col=C_DECO_PROP, rod=True):
    """侧栏当前标签 = 悬挂的军团战旗：暗血红旗面 + 铜色细边(原为闪电淡蓝，用户要试铜色)，三齿下摆照战锤军团战旗的轮廓
    (两侧齿深 ≈ 0.14 旗宽、中齿 ≈ 0.22 旗宽，齿边都接近 45°)。单位 = CSS px，宽 32、居中挂在 28 宽的标签头上。
    (旗里原有一圈内框，卡片开着时它的上边正好接着卡片内框线，看着像框线穿过了旗，用户要去掉)
    rod=False(卡片框开着，仿 Fancy-a-Story)：图 32×40，旗顶比卡片外框线高约 2.4px、盖住两道框线；
      图标在图里占 (8,13)-(24,29)，齿根离图标笔画 4–6px(版面见主题 12 节卡片那段；图标下移 4px 后旗面同步加长 4px)。
    rod=True(卡片框关掉)：图 32×32，顶边比标签头高 1px(= 标签栏 overflow 的裁切线)，旗挂在两端带圆钮的横杆下，
      图标在图里占 (8,6)-(24,22)；图左缘落在裁切线外 2px，标签栏左边要补 2px 内边距，否则左圆钮被裁掉一半"""
    x0, x1 = 3.3, 28.7                # 旗面左右
    if rod:
        H, top, ye = 32, 2.4, 25.7    # 图高、旗面上缘、齿根
    else:
        H, top, ye = 40, .5, 32
    w = x1 - x0
    side, mid = .14 * w, .22 * w
    cl = (f"M{x0},{top:.2f} H{x1} V{ye} L{x1 - .13 * w:.2f},{ye + side:.2f} L{x1 - .28 * w:.2f},{ye} "
          f"L{(x0 + x1) / 2:.2f},{ye + mid:.2f} L{x0 + .28 * w:.2f},{ye} L{x0 + .13 * w:.2f},{ye + side:.2f} L{x0},{ye} Z")
    svg = (f'<svg {SVG} width="32" height="{H}" viewBox="0 0 32 {H}">'
           f'<path d="{cl}" fill="{cloth}" stroke="{col}" stroke-opacity=".75" stroke-width="1"/>')
    if rod:
        svg += (f'<path d="M1.6,1.4 H30.4" stroke="{col}" stroke-width="1.5" stroke-linecap="round"/>'
                f'<circle cx="1.6" cy="1.4" r="1.25" fill="{col}"/><circle cx="30.4" cy="1.4" r="1.25" fill="{col}"/>')
    return svg + "</svg>"


def deco_tab_frame(col=C_DECO):
    """主区当前标签的框(border-image，切片 8，底边不画)：双线，两侧 + 上边，两个上角 45° 切角，内线在外线里 3px。
    标签栏也是两道底线(外 45%、内 22%，主题里画)，外框落在下面那道、内框落在上面那道，
    看着是两条线升起来围住当前标签(和侧栏卡片的双线框同一个语言)"""
    return (f'<svg {SVG} width="24" height="24" viewBox="0 0 24 24">'
            f'<path d="M.5,24 V7.5 L7.5,.5 H16.5 L23.5,7.5 V24" fill="none" stroke="{col}" stroke-opacity=".45" stroke-width="1"/>'
            f'<path d="M3.5,24 V8.74 L8.74,3.5 H15.26 L20.5,8.74 V24" fill="none" stroke="{col}" stroke-opacity=".22" stroke-width="1"/></svg>')


def pin_glyph():
    """锁定标签的钉子(遮罩用黑色剪影)：game-icons.net · Lorc「stiletto」细刃匕首(CC BY 3.0)，水平翻转成刀尖朝左下。
    (自画的穿刺骷髅 / 剥皮刀 / 翼骷髅钉 / 闪电钉被用户否掉：不是主题的平面剪影风格)"""
    src = (ICONS / "stiletto.svg").read_text(encoding="utf-8")
    ds = re.findall(r'<path[^>]*\sd="([^"]+)"', src)
    return (f'<svg {SVG} viewBox="0 0 512 512"><g transform="translate(512 0) scale(-1 1)">'
            + "".join(f'<path d="{d}"/>' for d in ds) + "</g></svg>")


def deco_tab_mark():
    """主区当前标签上边正中挂的血红阶梯尖"""
    return (f'<svg {SVG} width="16" height="7" viewBox="0 0 16 7"><path d="M0,0 H16 L12,2.6 H10.3 L8,6.6 L5.7,2.6 H4 Z" '
            f'fill="#b3262e"/></svg>')


def deco_tab_sep(col=C_DECO):
    """主区标签之间的分隔：细竖线中间串一粒小菱形"""
    return (f'<svg {SVG} width="5" height="16" viewBox="0 0 5 16"><path d="M2.5,0 V5.4 M2.5,10.6 V16" stroke="{col}" '
            f'stroke-opacity=".35" stroke-width="1"/><path d="M2.5,5.8 L4.7,8 L2.5,10.2 L.3,8 Z" fill="{col}" fill-opacity=".6"/></svg>')


if __name__ == "__main__":
    import base64
    import lightning as L

    def uri(s):
        return "data:image/svg+xml;base64," + base64.b64encode(s.encode()).decode()
    variants = {
        "现用 外旋45": heraldic_banner(rot=-45, bones=False, claw=False),
        "带指骨+爪": heraldic_banner(rot=-45),
    }
    rows = []
    for name, sv in variants.items():
        rows.append(f'<div class="row"><span>{name}</span><img src="{uri(sv)}" style="height:96px">'
                    f'<img src="{uri(sv)}" style="height:48px"></div>')
    h2 = "".join(
        f'<div class="h2"><img src="{uri(raised_wing(rot=r))}" style="height:1em;vertical-align:-0.12em;margin-right:.28em">'
        f'① 结论摘要 Summary <small>rot={r}</small></div>' for r in (0, -12, -24))
    rows.append(f'<div class="row" style="flex-direction:column;align-items:flex-start">{h2}</div>')
    rows.append(f'<div class="row"><div style="width:320px;height:520px;background:#08101d url({uri(L.sidebar_storm())}) '
                f'bottom/100% auto no-repeat"></div></div>')
    (ROOT / "preview" / "ornaments.html").write_text(
        '<html><body style="margin:0;padding:20px;background:#0c1424;color:#cdc2a9;font:14px serif">'
        '<style>.row{display:flex;gap:28px;align-items:center;margin:14px 0}.row span{width:150px}'
        '.h2{font:600 24px "Noto Serif SC",serif;color:#d2b07a;margin:4px 0}.h2 small{font-size:12px;color:#777}</style>'
        + "".join(rows) + "</body></html>", encoding="utf-8")
    print("ok")
