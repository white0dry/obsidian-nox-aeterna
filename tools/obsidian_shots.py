# -*- coding: utf-8 -*-
"""在真 Obsidian 里截 README 用图(示例库 demo-vault/)。
准备：完全退出 Obsidian → 带调试端口启动：
    "C:\\Program Files\\Obsidian\\Obsidian.exe" --remote-debugging-port=9222
在 Obsidian 里打开 demo-vault，把窗口和侧栏摆成想要的样子(最大化；左栏上文件列表、下关系图谱，右栏上日历、下大纲)，再运行：
    python tools/obsidian_shots.py [只截的图名 ...]
脚本不动布局，只切界面语言(英文图用英文界面，结束后还原)、切到要截的笔记、悬停、开关弹窗；
截图用窗口的实际尺寸，只有截整篇笔记时临时把视口加高。只操作标题含 demo-vault 的窗口。
英文图存 docs/images/<名>.webp，中文图存 <名>-zh.webp；动图和三选一对比图只出一份(中文笔记)。"""
import base64
import io
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.argv, ONLY = sys.argv[:1], set(sys.argv[1:])
import readme_shots as R                                  # noqa: E402  拼图 / 存图 / 画鼠标的工具函数
from PIL import Image                                     # noqa: E402
from playwright.sync_api import sync_playwright           # noqa: E402

ROOT = R.ROOT
IMG = R.IMG
NOTE = {"zh": "夜巡手记.md", "en": "The Night Watch.md"}
LINK = {"zh": "钟楼", "en": "The Bell Tower"}                     # 悬浮预览用的内部链接
DEEP = {"zh": "守夜人的装备", "en": "Watchkeeper's Kit"}           # 大纲里悬停的深层标题
QUERY = {"zh": "切换", "en": "toggle"}                            # 命令面板里输入的字
THREAD = ["钟楼", "灯火的规矩", "守夜人的装备", "附注：钟楼的蝙蝠", "雷暴季", "抄本与代码", "巡夜路线"]

# 只切到那篇笔记(已有标签就激活它，没有就在第一个标签里打开)，阅读视图、滚到顶
OPEN_JS = """async (note) => {
  const w = app.workspace;
  // 重载后 Obsidian 会把「出链」「全部属性」补回右栏，布局里本来没有，去掉
  for (const t of ['outgoing-link', 'all-properties']) w.getLeavesOfType(t).forEach(l => l.detach());
  const leaves = [];
  const walk = n => n.children ? n.children.forEach(walk) : leaves.push(n);
  walk(w.rootSplit);
  let leaf = leaves.find(l => l.getViewState().state?.file === note);
  if (!leaf) { leaf = leaves[0]; await leaf.openFile(app.vault.getAbstractFileByPath(note)); }
  w.setActiveLeaf(leaf, {focus: true});
  await leaf.loadIfDeferred?.();
  const st = leaf.getViewState();
  if (st.state.mode !== 'preview') { st.state.mode = 'preview'; await leaf.setViewState(st); }
  await new Promise(r => setTimeout(r, 300));
  leaf.view.previewMode?.applyScroll?.(0);
  return 'ok';
}"""

ACTIVE_SIZER = ".workspace-leaf.mod-active .markdown-reading-view .markdown-preview-sizer"


class Obs:
    def __init__(self, p):
        ws = json.load(urllib.request.urlopen("http://127.0.0.1:9222/json/version"))["webSocketDebuggerUrl"]
        self.b = p.chromium.connect_over_cdp(ws)
        self.pg = next(pg for c in self.b.contexts for pg in c.pages
                       if "demo-vault" in pg.title() and pg.url.startswith("app://"))
        self.cdp = self.pg.context.new_cdp_session(self.pg)
        self.cdp.send("Animation.enable")
        self.lang0 = self.js("localStorage.getItem('language')")
        self.native = self.js("[innerWidth, innerHeight, devicePixelRatio]")
        self.lang = None
        self.mouse_pt = None

    # -- 视口：平时用窗口实际尺寸；截整篇笔记时临时加高(宽度、缩放不变，正文排版和窗口里一模一样)
    def tall(self, h):
        w, _, dpr = self.native
        self.cdp.send("Emulation.setDeviceMetricsOverride", {"width": w, "height": h, "deviceScaleFactor": dpr, "mobile": False})
        self.pg.wait_for_timeout(1500)

    def normal(self):
        self.cdp.send("Emulation.clearDeviceMetricsOverride")
        self.pg.wait_for_timeout(800)

    def js(self, code, arg=None):
        return self.pg.evaluate(code, arg)

    def grab(self, clip=None, fast=False):
        """整窗截图后在本地裁切。不用 CDP 的 clip：带 clip 截图时 Chromium 会临时改视口、重新布局，
        随后按真实鼠标位置重算悬停，模拟的悬停(大纲血线、按钮展开)就被清掉了。fast = JPEG(录动图用，一帧约 0.1s)"""
        if fast and self.mouse_pt:     # 每帧补发一次模拟鼠标事件，顶住真实鼠标对悬停状态的干扰
            self.cdp.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": self.mouse_pt[0], "y": self.mouse_pt[1], "button": "none"})
        params = {"format": "jpeg", "quality": 95} if fast else {"format": "png"}
        r = self.cdp.send("Page.captureScreenshot", params)
        im = Image.open(io.BytesIO(base64.b64decode(r["data"]))).convert("RGB")
        return im if clip is None else self.crop(im, clip)

    def crop(self, im, clip):
        d = im.width / self.js("innerWidth")
        x, y, w, h = clip
        return im.crop((round(x * d), round(y * d), round((x + w) * d), round((y + h) * d)))

    def move(self, x, y):
        self.mouse_pt = (x, y)
        self.pg.mouse.move(x, y)

    def hold(self, ms):
        """停在当前位置等 ms 毫秒，期间每 50ms 补发一次鼠标事件(悬停截图前用)"""
        for _ in range(max(1, ms // 50)):
            self.cdp.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": self.mouse_pt[0], "y": self.mouse_pt[1], "button": "none"})
            self.pg.wait_for_timeout(50)

    def box(self, sel, nth=0):
        b = self.js("([s, n]) => { const e = document.querySelectorAll(s)[n]; if (!e) return null; "
                    "const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }", [sel, nth])
        if b is None:
            raise RuntimeError(f"找不到 {sel} #{nth}")
        return b

    def set_lang(self, lang):
        """Obsidian 界面语言(localStorage language，所有窗口共用；结束时还原)，改完重载示例库窗口(布局先存盘，重载后原样恢复)"""
        cur = self.js("localStorage.getItem('language') || 'en'")
        if cur != lang:
            # 先把布局读进内存并存盘、等写完再重载：重载时若正好在写 workspace.json，文件被截断，
            # Obsidian 读不出来就换成默认布局(踩过：用户手调的布局整个丢了)。重载后再用内存里这份写回去
            layout = self.js("""async (l) => { const w = app.workspace; const lay = w.getLayout(); await w.saveLayout();
                                 await new Promise(r => setTimeout(r, 1500)); localStorage.setItem('language', l); return lay; }""", lang)
            self.pg.reload()
            # 按时间轮询：默认按动画帧轮询，示例库窗口被别的窗口挡住时不出帧，会一直等到超时(踩过)
            self.pg.wait_for_function("window.app && app.workspace && app.workspace.layoutReady", polling=500, timeout=30000)
            self.pg.wait_for_timeout(1500)
            self.js("async (lay) => { await app.workspace.changeLayout(lay); }", layout)
            self.pg.wait_for_timeout(2000)
        self.lang = lang

    def open(self, lang):
        self.set_lang(lang)
        self.js(OPEN_JS, NOTE[lang])
        self.rest()
        self.pg.wait_for_timeout(1500)

    def rest(self):
        """鼠标停到不触发任何悬停效果的地方(功能栏最底下的空白)"""
        h = self.js("innerHeight")
        self.move(20, h - 30)

    def rate(self, r):
        self.cdp.send("Animation.setPlaybackRate", {"playbackRate": r})

    def body_cls(self, add=(), remove=()):
        self.js("([a, r]) => { document.body.classList.remove(...r); document.body.classList.add(...a); }", [list(add), list(remove)])
        self.pg.wait_for_timeout(600)


def suffix(lang):
    return "" if lang == "en" else "-zh"


def hover_outline(o, text):
    b = o.js("""(t) => { const e = [...document.querySelectorAll('.workspace-leaf-content[data-type="outline"] .tree-item-self')]
                  .find(x => x.querySelector('.tree-item-inner')?.textContent.trim() === t);
                  if (!e) return null; const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }""", text)
    if b is None:
        raise RuntimeError("大纲里没有 " + text)
    pt = (b[0] + min(b[2] / 2, 60), b[1] + b[3] / 2)
    o.move(*pt)
    return pt


CURRENT = ["en"]          # 主程序按语言分两轮跑(先英文后中文)，免得来回切界面语言重载


def langs():
    return tuple(CURRENT)


# ---------------------------------------------------------------- 静态图
def shot_cover(o):
    """整个窗口：阅读视图，鼠标停在大纲深层标题上(血线亮出)"""
    for lang in langs():
        o.open(lang)
        hover_outline(o, DEEP[lang])
        o.hold(1500)
        im = o.grab()
        R.save_webp(im, "cover" + suffix(lang))
        if lang == "en":   # 商店缩略图 512×288
            im.resize((512, 288), Image.LANCZOS).save(ROOT / "screenshot.png", optimize=True)
            print("screenshot.png  512x288")
        o.rest()


NOTE_BLOCKS_JS = """(sel) => {
  const v = document.querySelector(sel);
  const r0 = v.getBoundingClientRect();
  const blocks = [...v.children].map(e => { const r = e.getBoundingClientRect();
    return {cls: e.className, top: r.top, bottom: r.bottom, img: !!e.querySelector('img'), text: e.innerText.slice(0, 20)}; });
  const callouts = [...v.querySelectorAll(':scope > .el-div > .callout')].map(e => { const r = e.getBoundingClientRect();
    return [r.x, r.y, r.width, r.height, e.dataset.calloutFold || '']; });
  const vh = document.querySelector('.workspace-leaf.mod-active .view-header').getBoundingClientRect();
  return {left: r0.left, width: r0.width, blocks, callouts, viewHeaderBottom: vh.bottom, scrollH: v.parentElement.scrollHeight};
}"""


def shot_note(o):
    """整篇笔记按段裁：标题与属性 / 列表 / 任务清单(全部状态) / 表格与小标题 / 代码公式 Mermaid / 图片嵌入脚注；Callout 拼成两列"""
    for lang in langs():
        o.open(lang)
        o.tall(7600)
        o.js(OPEN_JS, NOTE[lang])
        o.rest()
        o.pg.wait_for_timeout(3000)                       # 等 Mermaid、公式、图片渲染完
        d = o.js(NOTE_BLOCKS_JS, ACTIVE_SIZER)
        bl = d["blocks"]
        x, w = d["left"] - 40, d["width"] + 80
        cls = [b["cls"].split()[0] if b["cls"] else "" for b in bl]

        def idx(c, start=0):
            return next(i for i in range(start, len(bl)) if cls[i] == c)
        h1 = idx("el-h1")
        h2 = idx("el-h2")
        h4 = idx("el-h4")
        h6 = idx("el-h6")
        hr = idx("el-hr")
        img = next(i for i, b in enumerate(bl) if b["img"])
        img_h = max(i for i in range(img) if cls[i] == "el-h2")
        foot = max(i for i, c in enumerate(cls) if c == "el-section")
        header = next(i for i, b in enumerate(bl) if "mod-header" in b["cls"])
        tasks = max(i for i in range(h2, h4) if cls[i] == "el-p")   # 「今晚的事项：」那段，后面是全部状态的任务清单
        cuts = [("note-title", max(bl[header]["top"] - 24, d["viewHeaderBottom"] + 1), bl[h1 + 1]["bottom"] + 24),
                ("note-lists", bl[h2]["top"] - 24, bl[tasks - 1]["bottom"] + 24),
                ("note-tasks", bl[tasks]["top"] - 16, bl[h4 - 1]["bottom"] + 24),
                ("note-table", bl[h4]["top"] - 24, bl[h6 + 1]["bottom"] + 24),
                ("note-code", bl[hr]["top"] - 10, bl[img_h - 1]["bottom"] + 24),
                ("note-media", bl[img_h]["top"] - 24, bl[foot]["bottom"] + 24)]
        full = o.grab()
        for name, y0, y1 in cuts:   # 任务清单只占左半边，裁窄一点
            R.save_webp(o.crop(full, (x, y0, min(w, 720) if name == "note-tasks" else w, y1 - y0)), name + suffix(lang))
        # Callout：前 14 个(不含最后那个可折叠的)，各自带一圈底色裁下来，两列拼图
        cs = [c for c in d["callouts"] if not c[4]][:14]
        pad = 10
        tiles = [o.crop(full, (c[0] - pad, c[1] - pad, c[2] + pad * 2, c[3] + pad * 2)) for c in cs]
        tw = max(t.width for t in tiles)
        tiles = [t.resize((tw, round(t.height * tw / t.width)), Image.LANCZOS) if t.width != tw else t for t in tiles]
        rows = [tiles[i:i + 2] for i in range(0, len(tiles), 2)]
        gap = round(14 * o.native[2])
        th = max(t.height for t in tiles)
        out = Image.new("RGB", (tw * 2 + gap * 3, (th + gap) * len(rows) + gap), (11, 20, 36))
        for r, row in enumerate(rows):
            for c, t in enumerate(row):
                out.paste(t, (gap + c * (tw + gap), gap + r * (th + gap)))
        R.save_webp(out, "callouts" + suffix(lang))
        o.normal()


def shot_live(o):
    """实时预览(编辑视图)：光标放在第一个一级标题那一行，显示出 # 标记"""
    for lang in langs():
        o.open(lang)
        o.js("""async () => { const leaf = app.workspace.activeLeaf; const st = leaf.getViewState();
                st.state.mode = 'source'; st.state.source = false; await leaf.setViewState(st);
                await new Promise(r => setTimeout(r, 500));
                const ed = leaf.view.editor; const n = ed.lineCount();
                let line = 0; for (let i = 0; i < n; i++) if (ed.getLine(i).startsWith('# ')) { line = i; break; }
                ed.setCursor({line, ch: ed.getLine(line).length}); ed.focus();
                await new Promise(r => setTimeout(r, 400)); ed.scrollTo(0, 0); }""")
        o.rest()
        o.pg.wait_for_timeout(1200)
        sx = o.box(".workspace-leaf.mod-active .cm-sizer")
        vh = o.box(".workspace-leaf.mod-active .view-header")
        h = o.js("innerHeight")
        R.save_webp(o.grab((sx[0] - 40, vh[1] + vh[3], sx[2] + 80, h - (vh[1] + vh[3]))), "live" + suffix(lang))
        o.js(OPEN_JS, NOTE[lang])


def shot_frames(o):
    """左栏卡片顶 + 主区标签栏 + 笔记标题：Dark Deco 线框、军团战旗、切角标签"""
    for lang in langs():
        o.open(lang)
        ls = o.box(".workspace-split.mod-left-split")
        title = o.box(".workspace-leaf.mod-active .inline-title")
        banner_bottom = title[1] + title[3] + 80
        R.save_webp(o.grab((ls[0], 0, title[0] + title[2] + 40 - ls[0], banner_bottom)), "frames" + suffix(lang))


def shot_ribbon(o):
    """功能栏颅骨锁链 + 提示框：鼠标停在第一枚铁环上，等 Obsidian 自己弹出提示框"""
    for lang in langs():
        o.open(lang)
        x, y, w, h = o.box(".workspace-ribbon.mod-primary .side-dock-ribbon-action")
        o.move(x + w / 2, y + h / 2)
        o.hold(1500)
        rb = o.box(".workspace-ribbon.mod-primary .side-dock-actions")
        tip = o.js("(() => { const t = document.querySelector('.tooltip'); if (!t) return null; const r = t.getBoundingClientRect(); return [r.right, r.bottom]; })()")
        ls = o.box(".workspace-split.mod-left-split")
        right = max(ls[0] + ls[2], (tip[0] + 16) if tip else 0)
        R.save_webp(o.grab((0, 0, right, rb[1] + rb[3] + 16)), "ribbon" + suffix(lang))
        o.rest()


def shot_variants(o):
    """三选一对比(中文笔记)：文件夹图标 / 大纲样式"""
    o.open("zh")
    # 文件夹
    ims = []
    for c in ("nl-folder-bat", "nl-folder-classic", "nl-folder-native"):
        o.body_cls([c], ["nl-folder-bat", "nl-folder-classic", "nl-folder-native"])
        fx, fy, fw, fh = o.box(".nav-files-container")
        ims.append(o.grab((fx, fy, fw, min(fh, 470))))
    o.body_cls(["nl-folder-bat"], ["nl-folder-classic", "nl-folder-native"])
    R.save_webp(R.labelled_row(ims, ["Hanging bat", "Bronze folder", "Native arrow"], size=30, label_h=60), "folders")
    # 大纲
    ims = []
    for c in ("nl-outline-thread", "nl-outline-marker", "nl-outline-native"):
        o.body_cls([c], ["nl-outline-thread", "nl-outline-marker", "nl-outline-native"])
        hover_outline(o, DEEP["zh"])
        o.hold(1500)
        vx, vy, vw, vh = o.box('.workspace-leaf-content[data-type="outline"] > .view-content')
        ims.append(o.grab((vx, vy, vw, min(vh, 380))))
        o.rest()
    o.body_cls(["nl-outline-thread"], ["nl-outline-marker", "nl-outline-native"])
    R.save_webp(R.labelled_row(ims, ["Blood thread", "Marker", "Native"], size=30, label_h=60), "outline")
    o.js(OPEN_JS, NOTE["zh"])


def shot_dialogs(o):
    """命令面板 + 悬浮预览"""
    for lang in langs():
        o.open(lang)
        o.js("() => app.commands.executeCommandById('command-palette:open')")
        o.pg.wait_for_timeout(500)
        o.js("(q) => { const i = document.querySelector('.prompt-input'); i.value = q; i.dispatchEvent(new Event('input')); }", QUERY[lang])
        o.pg.wait_for_timeout(800)
        x, y, w, h = o.box(".prompt")
        a = o.grab((x - 1, y - 1, w + 2, h + 2))
        o.pg.keyboard.press("Escape")
        o.pg.wait_for_timeout(500)
        lx, ly, lw, lh = o.js("""(t) => { const e = [...document.querySelectorAll('.workspace-leaf.mod-active .markdown-reading-view a.internal-link')]
                                 .find(a => a.textContent.trim() === t); const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }""", LINK[lang])
        o.move(lx + lw / 2, ly + lh / 2)
        o.hold(1800)
        x, y, w, h = o.box(".popover.hover-popover")
        b = o.grab((x - 1, y - 1, w + 2, h + 2))
        o.rest()
        o.pg.wait_for_timeout(1200)
        gap, pad = 36, 28
        out = Image.new("RGB", (a.width + b.width + gap + pad * 2, max(a.height, b.height) + pad * 2), R.BG)
        out.paste(a, (pad, (out.height - a.height) // 2))
        out.paste(b, (pad + a.width + gap, (out.height - b.height) // 2))
        R.save_webp(out, "dialogs" + suffix(lang))


def shot_empty(o):
    for lang in langs():
        o.open(lang)
        o.js("""() => { const w = app.workspace; const leaves = []; const walk = n => n.children ? n.children.forEach(walk) : leaves.push(n);
                walk(w.rootSplit); const e = leaves.find(l => l.view.getViewType() === 'empty'); w.setActiveLeaf(e, {focus: true}); }""")
        o.pg.wait_for_timeout(800)
        x, y, w, h = o.box(".workspace-leaf.mod-active .empty-state-container")
        R.save_webp(o.grab((x - 160, y - 60, w + 320, h + 120)), "empty" + suffix(lang))
        o.js(OPEN_JS, NOTE[lang])


def shot_settings(o):
    """Style Settings 设置页(本主题那一节展开)。1.14 的设置是单独弹出的窗口，要连到那个窗口去截"""
    for lang in langs():
        o.open(lang)
        o.js("() => { app.setting.open(); app.setting.openTabById('obsidian-style-settings'); }")
        o.pg.wait_for_timeout(1500)
        pop = next(x for c in o.b.contexts for x in c.pages if x.url == "about:blank" and "demo-vault" in x.title())
        cdp = pop.context.new_cdp_session(pop)
        dpr = pop.evaluate("devicePixelRatio")
        cdp.send("Emulation.setDeviceMetricsOverride", {"width": 960, "height": 1040, "deviceScaleFactor": dpr, "mobile": False})
        pop.wait_for_timeout(800)
        pop.evaluate("""() => { const h = document.querySelector('.style-settings-heading[data-id="night-lords"]');
                         if (h && h.classList.contains('is-collapsed')) h.click(); }""")
        pop.wait_for_timeout(1000)
        r = cdp.send("Page.captureScreenshot", {"format": "png"})
        R.save_webp(Image.open(io.BytesIO(base64.b64decode(r["data"]))).convert("RGB"), "settings" + suffix(lang))
        cdp.send("Emulation.clearDeviceMetricsOverride")
        o.js("() => app.setting.close()")
        o.pg.wait_for_timeout(600)


# ---------------------------------------------------------------- 动图(真 Obsidian 里放慢录)
def record(o, clip, frames, seconds, rate, cur):
    t_end = time.perf_counter() + seconds
    last = time.perf_counter()
    while time.perf_counter() < t_end:
        im = o.grab(clip, fast=True)
        now = time.perf_counter()
        frames.append((im, (now - last) * rate * 1000, cur))
        last = now


def to_clip(pt, clip, scale):
    return None if pt is None else ((pt[0] - clip[0]) * scale, (pt[1] - clip[1]) * scale)


def anim_nav(o):
    """侧栏面板按钮行：平时一对蝙蝠翼，悬停展开成按钮"""
    o.open("zh")
    rate, sc = 0.2, o.native[2]
    fx, fy, fw, _ = o.box('.workspace-leaf-content[data-type="file-explorer"] .nav-files-container')
    clip = (fx - 8, 0, fw + 16, fy + 170)
    rest = (fx + fw * 0.62, fy + 150)
    frames = []
    o.move(*rest)
    o.pg.wait_for_timeout(400)
    o.rate(rate)
    try:
        frames.append((o.grab(clip, fast=True), 900, to_clip(rest, clip, sc)))
        nx, ny, nw, nh = o.box('.workspace-leaf-content[data-type="file-explorer"] > .nav-header')
        path = [(rest[0] + (nx + nw / 2 + 6 - rest[0]) * k / 6, rest[1] + (ny + nh / 2 - rest[1]) * k / 6) for k in range(1, 7)]
        for pt in path:
            o.move(*pt)
            frames.append((o.grab(clip, fast=True), 40, to_clip(pt, clip, sc)))
        record(o, clip, frames, 3.2, rate, to_clip(path[-1], clip, sc))
        frames.append((o.grab(clip, fast=True), 1300, to_clip(path[-1], clip, sc)))
        for pt in reversed(path[:-1]):
            o.move(*pt)
            frames.append((o.grab(clip, fast=True), 40, to_clip(pt, clip, sc)))
        o.move(*rest)
        record(o, clip, frames, 6.0, rate, to_clip(rest, clip, sc))
        frames.append((o.grab(clip, fast=True), 900, to_clip(rest, clip, sc)))
    finally:
        o.rate(1)
        o.rest()
    R.save_anim(frames, "nav-wings", sc)


def anim_thread(o):
    """大纲血线：鼠标在标题间移动，血线从父骷髅流向悬停的标题"""
    o.open("zh")
    rate, sc = 0.35, o.native[2]
    vx, vy, vw, vh = o.box('.workspace-leaf-content[data-type="outline"] > .view-content')
    clip = (vx, vy, vw, min(vh, 380))
    pts = []
    for t in THREAD:
        b = o.js("""(t) => { const e = [...document.querySelectorAll('.workspace-leaf-content[data-type="outline"] .tree-item-self')]
                      .find(x => x.querySelector('.tree-item-inner')?.textContent.trim() === t);
                      const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }""", t)
        pts.append((min(b[0] + b[2] - 50, vx + vw - 40), b[1] + b[3] / 2))
    start = (pts[0][0] + 30, vy + min(vh, 380) - 14)
    o.move(*start)
    o.pg.wait_for_timeout(500)
    frames = []
    o.rate(rate)
    try:
        frames.append((o.grab(clip, fast=True), 700, to_clip(start, clip, sc)))
        prev = start
        for pt in pts:
            for k in range(1, 4):
                q = (prev[0] + (pt[0] - prev[0]) * k / 3, prev[1] + (pt[1] - prev[1]) * k / 3)
                o.move(*q)
                frames.append((o.grab(clip, fast=True), 30, to_clip(q, clip, sc)))
            record(o, clip, frames, 1.6, rate, to_clip(pt, clip, sc))
            frames.append((o.grab(clip, fast=True), 450, to_clip(pt, clip, sc)))
            prev = pt
        o.move(*start)
        record(o, clip, frames, 1.0, rate, to_clip(start, clip, sc))
        frames.append((o.grab(clip, fast=True), 700, to_clip(start, clip, sc)))
    finally:
        o.rate(1)
        o.rest()
    R.save_anim(frames, "outline-thread", sc)


SHOTS = {"cover": shot_cover, "note": shot_note, "live": shot_live, "frames": shot_frames, "ribbon": shot_ribbon,
         "variants": shot_variants, "dialogs": shot_dialogs, "empty": shot_empty, "settings": shot_settings,
         "nav-wings": anim_nav, "outline-thread": anim_thread}
BILINGUAL = {"cover", "note", "live", "frames", "ribbon", "dialogs", "empty", "settings"}

if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        o = Obs(p)
        try:
            for lang in ("en", "zh"):
                CURRENT[:] = [lang]
                for name, fn in SHOTS.items():
                    if (not ONLY or name in ONLY) and (name in BILINGUAL or lang == "zh"):
                        fn(o)
        finally:
            o.rate(1)
            o.normal()
            if o.lang0 is not None:      # 还原 Obsidian 界面语言
                o.set_lang(o.lang0)
            o.js(OPEN_JS, NOTE["zh"])
