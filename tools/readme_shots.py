# -*- coding: utf-8 -*-
"""预览环境(模拟 DOM)版的 README 用图。README 现在用的是真 Obsidian 截图(tools/obsidian_shots.py)，
这里不带参数只生成配色条 palette.webp；其余各图是备用(真 Obsidian 不在手边时)，要显式点名才会生成，会覆盖真机图：
    python tools/readme_shots.py                 # 只出 palette
    python tools/readme_shots.py cover callouts  # 备用：用预览环境重出这几张
基于 make_harness 的模拟 DOM(真 app.css + 仓库根目录的主题)。布局换成 README 用的：左栏只放文件列表、右栏只放大纲，
没有占位面板；body 挂上 Style Settings 的默认类(装了插件的用户看到的就是这样)。"""
import io
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.argv, ONLY = sys.argv[:1], set(sys.argv[1:])        # make_harness import 时会读 argv[1]
import make_harness as H                                  # noqa: E402
from fontTools.ttLib import TTFont                        # noqa: E402
from PIL import Image, ImageDraw, ImageFont               # noqa: E402
from playwright.sync_api import sync_playwright           # noqa: E402

ROOT = H.ROOT
IMG = ROOT / "docs" / "images"
TMP = ROOT / "preview" / "_readme"
BG = (6, 11, 21)                      # --nl-night-950，拼图的底色
LABEL = (210, 176, 122)               # --nl-brass
DEFAULTS = "nl-lang-auto nl-folder-bat nl-outline-thread nl-align-left nl-cjk-noto nl-autohide-nav"

LEFT = H.side_group([("文件列表", "folder-closed"), ("搜索", "search"), ("书签", "bookmark")], 0, H.sidebar_left(),
                    " mod-top mod-top-left-space", 100)
RIGHT = H.side_group([("大纲", "list"), ("反向链接", "link"), ("标签", "tags")], 0, H.sidebar_right(),
                     " mod-top mod-top-right-space", 100)

CALLOUTS = [
    ("note", "Note", "羽毛笔 · Quill"),
    ("abstract", "Abstract", "展开的卷轴 · Unfurled scroll"),
    ("info", "Info", "半睁的眼 · Half-closed eye"),
    ("todo", "Todo", "系绳卷轴 · Tied scroll"),
    ("important", "Important", "军团徽记 · Legion emblem"),
    ("tip", "Tip", "烛光 · Candle light"),
    ("success", "Success", "桂冠 · Laurels"),
    ("question", "Question", "塔罗月牌 · Tarot moon"),
    ("warning", "Warning", "爪痕 · Claw slashes"),
    ("failure", "Failure", "交叉的骨 · Crossed bones"),
    ("danger", "Danger", "骷髅与骨 · Skull and crossbones"),
    ("bug", "Bug", "蛛网 · Spider web"),
    ("example", "Example", "翻开的书 · Open book"),
    ("quote", "Quote", "We have come for you."),
]


def callout(kind, title, text):
    return (f'<div class="el-div"><div data-callout-metadata="" data-callout-fold="" data-callout="{kind}" class="callout">'
            f'<div class="callout-title" dir="auto"><div class="callout-icon">{H.ICON}</div>'
            f'<div class="callout-title-inner">{title}</div></div>'
            f'<div class="callout-content"><p dir="auto">{text}</p></div></div></div>')


def reading_leaf_with(body):
    """阅读视图，正文换成 body(不带笔记标题和属性)"""
    leaf = H.reading_leaf()
    head = leaf[:leaf.index('<div class="mod-header mod-ui">')]
    tail = leaf[leaf.index('<div class="mod-footer mod-ui">'):]
    return head + body + tail


def tooltip(text, x, y):
    """Obsidian 的提示框：body 下的 div.tooltip(文字 + .tooltip-arrow)，右侧弹出时挂 mod-right、top 取按钮中线"""
    return (f'<div class="tooltip mod-right" style="top: {y}px; left: {x}px;">{text}'
            '<div class="tooltip-arrow"></div></div>')


# ---------------------------------------------------------------- 工具
_fonts = {}


def font(size, name="Cinzel-normal-400_900-latin.woff2"):
    """拼图标签用主题自带的 Cinzel(woff2 → 内存里转 ttf 给 PIL)"""
    if name not in _fonts:
        f = TTFont(ROOT / "fonts" / name)
        f.flavor = None
        buf = io.BytesIO()
        f.save(buf)
        _fonts[name] = buf.getvalue()
    return ImageFont.truetype(io.BytesIO(_fonts[name]), size)


def labelled_row(images, labels, gap=24, pad=28, label_h=54, size=26):
    """几张图横排，每张上面写一行标签"""
    w = sum(i.width for i in images) + gap * (len(images) - 1) + pad * 2
    h = max(i.height for i in images) + label_h + pad * 2
    out = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(out)
    x = pad
    for im, lb in zip(images, labels):
        tw = d.textlength(lb, font=font(size))
        d.text((x + (im.width - tw) / 2, pad + 6), lb, fill=LABEL, font=font(size))
        out.paste(im, (x, pad + label_h))
        x += im.width + gap
    return out


CURSOR = [(0, 0), (0, 17), (4.2, 13.2), (7, 19.6), (9.6, 18.5), (6.9, 12.2), (12.4, 12.2)]


def draw_cursor(im, x, y, s):
    d = ImageDraw.Draw(im)
    d.polygon([(x + px * s, y + py * s) for px, py in CURSOR], fill=(250, 250, 250), outline=(0, 0, 0), width=max(1, round(s)))


def save_webp(im, name, **kw):
    path = IMG / f"{name}.webp"
    im.save(path, "WEBP", quality=kw.get("quality", 90), method=6)
    print(f"{path.relative_to(ROOT)}  {im.width}x{im.height}  {path.stat().st_size // 1024} KB")


def save_anim(frames, name, scale):
    """frames = [(PIL 图, 显示毫秒, 鼠标位置或 None)]；连续相同的帧合并，画上鼠标，存成动图 WebP"""
    merged = []
    for im, ms, cur in frames:
        if merged and merged[-1][2] == cur and merged[-1][0].tobytes() == im.tobytes():
            merged[-1][1] += ms
        else:
            merged.append([im, ms, cur])
    out = []
    for im, ms, cur in merged:
        im = im.convert("RGB")
        if cur:
            draw_cursor(im, cur[0], cur[1], scale)
        out.append((im, max(20, round(ms))))
    path = IMG / f"{name}.webp"
    out[0][0].save(path, "WEBP", save_all=True, append_images=[i for i, _ in out[1:]],
                   duration=[ms for _, ms in out], loop=0, quality=82, method=4)
    print(f"{path.relative_to(ROOT)}  {len(out)} frames  {path.stat().st_size // 1024} KB")


class Shooter:
    def __init__(self, p):
        self.b = p.chromium.launch()

    def open(self, html, w=1600, h=1000, scale=1.0, name="page"):
        f = TMP / f"{name}.html"
        f.write_text(html, encoding="utf-8")
        pg = self.b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        pg.goto(f.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(900)
        pg.scale = scale
        return pg

    @staticmethod
    def grab(pg, clip):
        x, y, w, h = clip
        return Image.open(io.BytesIO(pg.screenshot(clip={"x": x, "y": y, "width": w, "height": h}))).convert("RGB")

    @staticmethod
    def box(pg, sel, nth=0):
        b = pg.locator(sel).nth(nth).bounding_box()
        return b["x"], b["y"], b["width"], b["height"]


def outline_item(text):
    return f'[data-type="outline"] .tree-item-self:has(.tree-item-inner:text-is("{text}"))'


def hover_center(pg, sel):
    x, y, w, h = Shooter.box(pg, sel)
    pg.mouse.move(x + min(w / 2, 60), y + h / 2)
    return x + min(w / 2, 60), y + h / 2


# ---------------------------------------------------------------- 各张图
def shot_cover(s):
    """封面：整个工作区，阅读视图；鼠标停在大纲深层标题上，血线亮出"""
    pg = s.open(H.page(H.reading_leaf(), left=LEFT, right=RIGHT, body_cls=DEFAULTS), 1600, 1000, 1, "cover")
    hover_center(pg, outline_item("守夜人的装备"))
    pg.wait_for_timeout(1500)
    save_webp(s.grab(pg, (0, 0, 1600, 1000)), "cover")
    pg.close()
    # 商店缩略图 512×288：小一号的窗口，标题、翼骷髅、侧栏都要看得清
    pg = s.open(H.page(H.reading_leaf(), left=LEFT, right=RIGHT, body_cls=DEFAULTS), 1280, 720, 1, "thumb")
    hover_center(pg, outline_item("守夜人的装备"))
    pg.wait_for_timeout(1500)
    im = s.grab(pg, (0, 0, 1280, 720)).resize((512, 288), Image.LANCZOS)
    im.save(ROOT / "screenshot.png", optimize=True)
    print("screenshot.png  512x288")
    pg.close()


def shot_typography(s):
    """正文排版：按元素分三段裁(标题区 / 表格列表引用 / 小标题分割线代码)"""
    pg = s.open(H.page(H.reading_leaf(), left=LEFT, right=RIGHT, body_cls=DEFAULTS), 1600, 3200, 1.25, "typo")
    sizer = s.box(pg, ".markdown-preview-sizer")
    x, w = sizer[0] - 36, sizer[2] + 72

    def top_of(sel, nth=0):
        return s.box(pg, sel, nth)[1]

    def bottom_of(sel, nth=0):
        b = s.box(pg, sel, nth)
        return b[1] + b[3]
    cuts = [("typography-title", max(top_of(".inline-title") - 40, bottom_of(".view-header") + 1), bottom_of(".el-p", 1) + 24),
            ("typography-blocks", bottom_of(".el-p", 2) + 6, bottom_of(".el-div") + 30),
            ("typography-more", top_of(".el-h4") - 30, bottom_of(".el-pre") + 30)]
    for name, y0, y1 in cuts:
        save_webp(s.grab(pg, (x, y0, w, y1 - y0)), name)
    pg.close()


def shot_callouts(s):
    """14 种 callout 图标：两列网格"""
    body = ('<style>.markdown-preview-sizer.markdown-preview-section { max-width: 1080px !important; display: grid; '
            'grid-template-columns: 1fr 1fr; gap: 20px 30px; align-items: start; } '
            '.markdown-preview-sizer > .el-div, .markdown-preview-sizer > .el-div > .callout { margin: 0; } '
            '.markdown-preview-pusher { grid-column: 1 / -1; }</style>'
            + "".join(callout(*c) for c in CALLOUTS))
    pg = s.open(H.page(reading_leaf_with(body), left=LEFT, right=RIGHT, body_cls=DEFAULTS),
                1900, 1400, 1, "callouts")
    first, last = s.box(pg, ".callout", 0), s.box(pg, ".callout", len(CALLOUTS) - 1)
    sizer = s.box(pg, ".markdown-preview-sizer")
    save_webp(s.grab(pg, (sizer[0] - 26, first[1] - 26, sizer[2] + 52, last[1] + last[3] - first[1] + 52)), "callouts")
    pg.close()


def shot_folders(s):
    """文件夹图标三选一：文件列表一截"""
    ims = []
    for cls in ("nl-folder-bat", "nl-folder-classic", "nl-folder-native"):
        pg = s.open(H.page(H.reading_leaf(), left=LEFT, right=RIGHT, body_cls=DEFAULTS.replace("nl-folder-bat", cls)),
                    1600, 1000, 1.5, "folder")
        x, y, w, h = s.box(pg, ".nav-files-container")
        ims.append(s.grab(pg, (x, y + 4, w, 470)))
        pg.close()
    save_webp(labelled_row(ims, ["Hanging bat", "Bronze folder", "Native arrow"], size=30, label_h=60), "folders")


def shot_outline(s):
    """大纲面板三选一：鼠标停在同一个深层标题上"""
    ims = []
    for cls in ("nl-outline-thread", "nl-outline-marker", "nl-outline-native"):
        pg = s.open(H.page(H.reading_leaf(), left=LEFT, right=RIGHT, body_cls=DEFAULTS.replace("nl-outline-thread", cls)),
                    1600, 1000, 1.5, "outline")
        hover_center(pg, outline_item("守夜人的装备"))
        pg.wait_for_timeout(1500)
        x, y, w, h = s.box(pg, '[data-type="outline"] > .view-content')
        ims.append(s.grab(pg, (x, y, w, 360)))
        pg.close()
    save_webp(labelled_row(ims, ["Blood thread", "Marker", "Native"], size=30, label_h=60), "outline")


def shot_ribbon(s):
    """左侧功能栏颅骨锁链 + 血印提示框(鼠标停在第一枚铁环上)"""
    pg = s.open(H.page(H.reading_leaf(), left=LEFT, right=RIGHT, body_cls=DEFAULTS), 1600, 1000, 2, "ribbon")
    x, y, w, h = s.box(pg, ".side-dock-ribbon-action", 0)
    pg.mouse.move(x + w / 2, y + h / 2)
    pg.evaluate("h => document.body.insertAdjacentHTML('beforeend', h)", tooltip("打开关系图谱 Open graph view", x + w + 8, y + h / 2))
    pg.wait_for_timeout(600)
    rb = s.box(pg, ".workspace-ribbon")
    save_webp(s.grab(pg, (0, 0, 314, rb[1] + 380)), "ribbon")
    pg.close()


def shot_frames(s):
    """Dark Deco：侧栏卡片的双线框 + 战旗，主区标签切角"""
    pg = s.open(H.page(H.reading_leaf(), left=LEFT, right=RIGHT, body_cls=DEFAULTS), 1600, 1000, 1.5, "frames")
    save_webp(s.grab(pg, (44, 0, 1056, 224)), "frames")
    pg.close()


def shot_dialogs(s):
    """命令面板 + 悬浮预览"""
    pg = s.open(H.page(H.reading_leaf(), overlay=H.prompt_overlay(), left=LEFT, right=RIGHT, body_cls=DEFAULTS), 1600, 1000, 1.25, "modal")
    x, y, w, h = s.box(pg, ".prompt")
    a = s.grab(pg, (x - 1, y - 1, w + 2, h + 2))
    pg.close()
    # 悬浮预览的框外有一圈透明内边距(给角花留位置)，底下放空白正文，免得透出正文文字
    pg = s.open(H.page(reading_leaf_with(""), overlay=H.popover(), left=LEFT, right=RIGHT, body_cls=DEFAULTS), 1600, 1000, 1.25, "popover")
    x, y, w, h = s.box(pg, ".popover")
    b = s.grab(pg, (x - 1, y - 1, w + 2, h + 2))
    pg.close()
    gap, pad = 36, 28
    out = Image.new("RGB", (a.width + b.width + gap + pad * 2, max(a.height, b.height) + pad * 2), BG)
    out.paste(a, (pad, pad))
    out.paste(b, (pad + a.width + gap, (out.height - b.height) // 2))
    save_webp(out, "dialogs")


def shot_empty(s):
    pg = s.open(H.page(H.empty_leaf(), left=LEFT, right=RIGHT, body_cls=DEFAULTS), 1600, 1000, 1.25, "empty")
    x, y, w, h = s.box(pg, ".empty-state-container")
    save_webp(s.grab(pg, (x - 160, y - 60, w + 320, h + 120)), "empty")
    pg.close()


def shot_palette(s):
    sw = [("Midnight", "#0b1424", "Note background"), ("Abyss", "#060b15", "Frame & ribbon"),
          ("Crimson", "#b3262e", "Accent"), ("Ember", "#e8705f", "Links"),
          ("Brass", "#d2b07a", "Ornaments"), ("Bone", "#e8dcc4", "Headings & text"), ("Lightning", "#9dbbe8", "Interface frames")]
    cells = "".join(f'<div class="c"><div class="s" style="background:{c}"></div><div class="n">{n}</div><div class="h">{c}</div>'
                    f'<div class="r">{r}</div></div>' for n, c, r in sw)
    html = (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{H.APP_CSS.as_uri()}">'
            f'<link rel="stylesheet" href="{H.THEME_CSS.as_uri()}"><style>'
            'body { margin: 0; background: #060b15; } .p { display: flex; gap: 18px; padding: 26px 30px; width: max-content; }'
            '.c { width: 120px; font-family: var(--font-text); color: var(--text-muted); font-size: 13px; text-align: center; }'
            '.s { height: 72px; border: 1px solid rgba(157,187,232,.35); outline: 1px solid rgba(157,187,232,.18); outline-offset: 3px; margin-bottom: 12px; }'
            '.n { font-family: var(--nl-font-display); color: var(--nl-bone); font-size: 16px; letter-spacing: .04em; }'
            '.h { font-family: var(--font-monospace); font-size: 12px; margin: 2px 0; }</style></head>'
            f'<body class="theme-dark"><div class="p">{cells}</div></body></html>')
    pg = s.open(html, 1200, 300, 1.5, "palette")
    save_webp(s.grab(pg, s.box(pg, ".p")), "palette")
    pg.close()


# ---------------------------------------------------------------- 动图
def slowed(pg, rate):
    cdp = pg.context.new_cdp_session(pg)
    cdp.send("Animation.enable")
    cdp.send("Animation.setPlaybackRate", {"playbackRate": rate})


def record(s, pg, clip, frames, seconds, rate, cur):
    """以放慢的速度连续截图 seconds 秒，按真实时间 × rate 还原每帧显示时长"""
    t_end = time.perf_counter() + seconds
    last = time.perf_counter()
    while time.perf_counter() < t_end:
        im = s.grab(pg, clip)
        now = time.perf_counter()
        frames.append((im, (now - last) * rate * 1000, cur))
        last = now


def to_clip(pt, clip, scale):
    return None if pt is None else ((pt[0] - clip[0]) * scale, (pt[1] - clip[1]) * scale)


def anim_nav(s):
    """侧栏面板按钮行：平时是一对蝙蝠翼，悬停展开成按钮"""
    rate, sc = 0.2, 2
    pg = s.open(H.page(H.reading_leaf(), left=LEFT, right=RIGHT, body_cls=DEFAULTS), 1600, 1000, sc, "anim_nav")
    slowed(pg, rate)
    fx, fy, fw, _ = s.box(pg, '[data-type="file-explorer"] .nav-files-container')
    clip = (fx - 8, 0, fw + 16, 230)
    rest = (fx + fw * 0.62, 196)
    frames = []
    pg.mouse.move(*rest)
    pg.wait_for_timeout(300)
    frames.append((s.grab(pg, clip), 900, to_clip(rest, clip, sc)))
    nx, ny, nw, nh = s.box(pg, '[data-type="file-explorer"] > .nav-header')
    path = [(rest[0] + (nx + nw / 2 + 6 - rest[0]) * k / 6, rest[1] + (ny + nh / 2 - rest[1]) * k / 6) for k in range(1, 7)]
    for pt in path:
        pg.mouse.move(*pt)
        frames.append((s.grab(pg, clip), 40, to_clip(pt, clip, sc)))
    record(s, pg, clip, frames, 3.2, rate, to_clip(path[-1], clip, sc))
    frames.append((s.grab(pg, clip), 1300, to_clip(path[-1], clip, sc)))
    for pt in reversed(path[:-1]):
        pg.mouse.move(*pt)
        frames.append((s.grab(pg, clip), 40, to_clip(pt, clip, sc)))
    pg.mouse.move(*rest)
    record(s, pg, clip, frames, 6.0, rate, to_clip(rest, clip, sc))
    frames.append((s.grab(pg, clip), 900, to_clip(rest, clip, sc)))
    pg.close()
    save_anim(frames, "nav-wings", sc)


def anim_thread(s):
    """大纲血线：鼠标在标题间移动，血线从父骷髅流向悬停的标题"""
    rate, sc = 0.35, 2
    pg = s.open(H.page(H.reading_leaf(), left=LEFT, right=RIGHT, body_cls=DEFAULTS), 1600, 1000, sc, "anim_thread")
    slowed(pg, rate)
    vx, vy, vw, _ = s.box(pg, '[data-type="outline"] > .view-content')
    clip = (vx, vy, vw, 350)
    frames = []
    targets = ["钟楼", "灯火的规矩", "守夜人的装备", "附注：钟楼的蝙蝠", "雷暴季", "抄本与代码", "巡夜路线"]
    pts = []
    for t in targets:
        x, y, w, h = s.box(pg, outline_item(t))
        pts.append((x + w - 70, y + h / 2))
    start = (pts[0][0] + 40, vy + 330)
    pg.mouse.move(*start)
    frames.append((s.grab(pg, clip), 700, to_clip(start, clip, sc)))
    prev = start
    for pt in pts:
        for k in range(1, 4):
            q = (prev[0] + (pt[0] - prev[0]) * k / 3, prev[1] + (pt[1] - prev[1]) * k / 3)
            pg.mouse.move(*q)
            frames.append((s.grab(pg, clip), 30, to_clip(q, clip, sc)))
        record(s, pg, clip, frames, 1.6, rate, to_clip(pt, clip, sc))
        frames.append((s.grab(pg, clip), 450, to_clip(pt, clip, sc)))
        prev = pt
    pg.mouse.move(*start)
    record(s, pg, clip, frames, 1.0, rate, to_clip(start, clip, sc))
    frames.append((s.grab(pg, clip), 700, to_clip(start, clip, sc)))
    pg.close()
    save_anim(frames, "outline-thread", sc)


SHOTS = {"cover": shot_cover, "typography": shot_typography, "callouts": shot_callouts,
         "folders": shot_folders, "outline": shot_outline, "ribbon": shot_ribbon, "frames": shot_frames,
         "dialogs": shot_dialogs, "empty": shot_empty, "palette": shot_palette,
         "nav-wings": anim_nav, "outline-thread": anim_thread}

if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        s = Shooter(p)
        for name, fn in SHOTS.items():
            if name in (ONLY or {"palette"}):
                fn(s)
        s.b.close()
    for f in TMP.glob("*.html"):
        f.unlink()
    TMP.rmdir()
