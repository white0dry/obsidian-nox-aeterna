# -*- coding: utf-8 -*-
"""组装 Nox Aeterna 主题(原名 Night Lords)：src/theme.src.css + 内嵌字体 + SVG 装饰 → 仓库根目录 theme.css + manifest.json
(社区主题目录从仓库根目录读 manifest.json，发版时这两个文件作为 release 附件上传)
用法:
  python build.py              # 只构建到仓库根目录
  python build.py --install    # 构建并复制到 Obsidian 库的 .obsidian/themes/Nox Aeterna/
"""
import base64
import json
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import ornaments as O  # noqa: E402

THEME_NAME = "Nox Aeterna"
VERSION = "1.0.8"
VAULT = Path(r"C:\Users\DELL\Documents\Obsidian Vault")
DIST = ROOT

# 内嵌字体: (Google family, 主题内别名, size-adjust, 只收这些子集, 只收这些字重)
FONT_MAP = {
    "EB Garamond": ("NL Garamond", "112%", None, None),
    "Cinzel": ("NL Cinzel", "100%", None, None),
    # 新标签页题铭 Ave Dominus Nox(第九轮，用户指定 Manufacturing Consent：矢量 Textura 哥特体)
    "Manufacturing Consent": ("NL Manufacturing Consent", "100%", {"latin"}, {"400"}),
}
# 分割线、新标签页徽记用的骨白(与横幅骷髅同色)；新标签页徽的翅膀用血红(= --nl-crimson)
BONE = "#d8ccb2"
CRIMSON = "#b3262e"
CJK_PUNCT_RANGE = "U+00B7, U+2014-2015, U+201C-201D, U+2026, U+2E3A"
CJK_PUNCT_RANGE_LITE = "U+00B7, U+2014-2015, U+2026, U+2E3A"


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def svg_uri(svg: str) -> str:
    return f'url("data:image/svg+xml;base64,{b64(svg.encode("utf-8"))}")'


def font_faces() -> str:
    faces = json.loads((ROOT / "fonts" / "faces.json").read_text(encoding="utf-8"))
    out = []
    for f in faces:
        if f["family"] not in FONT_MAP:
            continue
        alias, adjust, subsets, weights = FONT_MAP[f["family"]]
        if subsets and f["subset"] not in subsets:
            continue
        if weights and f["weight"] not in weights:
            continue
        data = (ROOT / "fonts" / f["file"]).read_bytes()
        out.append(
            "@font-face {\n"
            f'  font-family: "{alias}";\n'
            f'  font-style: {f["style"]};\n'
            f'  font-weight: {f["weight"]};\n'
            "  font-display: block;\n"
            f"  size-adjust: {adjust};\n"
            f'  src: url("data:font/woff2;base64,{b64(data)}") format("woff2");\n'
            f'  unicode-range: {f["unicode_range"]};\n'
            "}")
    punct = (ROOT / "fonts" / "NLCJKPunct-VF.woff2").read_bytes()
    out.append(
        "@font-face {\n"
        '  font-family: "NL CJK Punct";\n'
        "  font-style: normal;\n"
        "  font-weight: 200 900;\n"
        "  font-display: block;\n"
        f'  src: url("data:font/woff2;base64,{b64(punct)}") format("woff2");\n'
        f"  unicode-range: {CJK_PUNCT_RANGE};\n"
        "}")
    # 同一字体去掉弯引号的版本：Style Settings「弯引号用西文字形」切换用
    out.append(out[-1].replace('"NL CJK Punct"', '"NL CJK Punct Lite"')
               .replace(CJK_PUNCT_RANGE, CJK_PUNCT_RANGE_LITE))
    # 中文正文：思源宋体 GB2312 子集(tools/make_cjk_serif.py)。本机装了完整版思源宋体时字体栈先用本机的
    song = (ROOT / "fonts" / "NLNotoSerifSC-GB2312-VF.woff2").read_bytes()
    out.append(
        "@font-face {\n"
        '  font-family: "NL Noto Serif SC";\n'
        "  font-style: normal;\n"
        "  font-weight: 200 900;\n"
        "  font-display: block;\n"
        f'  src: url("data:font/woff2;base64,{b64(song)}") format("woff2");\n'
        "}")
    return "/* ---- embedded fonts (OFL 1.1) ---- */\n" + "\n".join(out)


def webp_uri(data: bytes) -> str:
    return f'url("data:image/webp;base64,{b64(data)}")'


def ornaments() -> dict:
    import lightning as L
    import raster as R
    return {
        # 矢量装饰(小、无滤镜，重绘便宜)
        "ORN:banner": svg_uri(O.heraldic_banner(rot=-45, bones=False, claw=False, edge=False)),
        "ORN:wing": svg_uri(O.raised_wing(rot=-12)),
        "ORN:skull": svg_uri(O.skull(fill="#b08a52")),
        "ORN:rule": svg_uri(O.rule_center(fill=BONE)),
        "ORN:emblem": svg_uri(O.emblem(fill=BONE, wing_fill=CRIMSON)),
        "ORN:folder": svg_uri(O.folder()),
        "ORN:folder-open": svg_uri(O.folder_open()),
        "ORN:bat-roost": svg_uri(O.bat_roost()),
        "ORN:bat-open": svg_uri(O.bat_open()),
        # Dark Deco：侧栏卡片/弹窗线框(淡蓝)、属性框线框(铜色，上边中段留给标题行)、侧栏战旗、主区标签
        "ORN:deco-frame": svg_uri(O.deco_frame(32)),
        "ORN:deco-frame-prop": svg_uri(O.deco_frame(26, top=False, col=O.C_DECO_PROP)),
        "ORN:deco-frame-img": svg_uri(O.deco_frame(26, col=O.C_DECO_PROP)),
        "ORN:deco-banner": svg_uri(O.deco_banner(rod=False)),
        "ORN:deco-banner-rod": svg_uri(O.deco_banner()),
        "ORN:deco-tab-frame": svg_uri(O.deco_tab_frame()),
        "ORN:deco-tab-mark": svg_uri(O.deco_tab_mark()),
        "ORN:deco-tab-sep": svg_uri(O.deco_tab_sep()),
        "ORN:pin": svg_uri(O.pin_glyph()),
        # 任务清单复选框：铜双线框 + 打勾的爪痕遮罩
        "ORN:task-frame": svg_uri(O.task_frame()),
        "ORN:task-claw": svg_uri(O.callout_glyph("claw-slashes")),
        "ORN:nav-wings": svg_uri(O.nav_wings()),
        "ORN:rb-link-oval": svg_uri(O.ribbon_link_oval()),
        "ORN:rb-head": svg_uri(O.ribbon_head()),
        "ORN:rb-tail": svg_uri(O.ribbon_tail()),
        # 位图(构建时栅格化：SVG 滤镜不进主题)
        "RASTER:atmos": webp_uri(R.render_webp(O.tex_atmos(1024), 1024, 1024, quality=72)),
        "RASTER:grain": webp_uri(R.render_webp(O.tex_grain(256), 256, 256, quality=60)),
        "RASTER:storm": webp_uri(R.render_webp(L.sidebar_storm(), L.SIDEBAR_W, L.SIDEBAR_H, scale=1.5, quality=82)),
    }


def callout_icon_css() -> str:
    """callout 图标：已知类型(含别名)藏掉内置 Lucide 图标，用 ::before + 遮罩画剪影，颜色 = --callout-color。
    自定义 callout 类型不受影响；Style Settings 开 nl-native-callout-icons 恢复原版"""
    out = ["/* ---- callout icons (generated from ornaments.CALLOUT_ICONS) ---- */"]
    every = []
    for types, name in O.CALLOUT_ICONS:
        sels = [f'.callout[data-callout="{t}"]' for t in types]
        every += sels
        out.append(f'{", ".join(sels)} {{ --nl-glyph: {svg_uri(O.callout_glyph(name))}; --nl-latin: "{O.CALLOUT_LATIN[types[0]]}"; }}')
    g = f"body:not(.nl-native-callout-icons) :is({', '.join(every)}) > .callout-title > .callout-icon"
    # 剪影普遍比 18px 的 Lucide 图标宽(眼、徽、书)：图标位撑到剪影宽度，再和标题拉开一点
    out.append(f"{g} {{ position: relative; min-width: var(--nl-glyph-size); justify-content: center; "
               "margin-inline-end: 0.2em; }")
    out.append(f"{g} > .svg-icon {{ opacity: 0; }}")
    out.append(
        f'{g}::before {{ content: ""; position: absolute; left: 50%; top: 50%; '
        "width: var(--nl-glyph-size); height: var(--nl-glyph-size); transform: translate(-50%, -50%); "
        "background-color: var(--callout-color); "
        "-webkit-mask: var(--nl-glyph) center / contain no-repeat; mask: var(--nl-glyph) center / contain no-repeat; }")
    return "\n".join(out)


TASK_COLORS = {"red": "var(--nl-crimson)", "brass": "var(--nl-brass)", "ash": "color-mix(in srgb, var(--nl-dust) 78%, transparent)"}


def task_css() -> str:
    """任务清单扩展状态：每个字符一条规则——只留外框(取消用灰框)，::after 遮罩画符号、按颜色类别着色。
    选择器同时认阅读视图(li[data-task] > input，松散列表多一层 p)和实时预览(.HyperMD-task-line[data-task])"""
    def sel(ch, suffix=""):
        q = f"[data-task='{ch}']"
        box = "input.task-list-item-checkbox"
        return (f"body:not(.nl-native-tasks) :is(.markdown-rendered li{q} > {box}, .markdown-rendered li{q} > p > {box}, "
                f".markdown-source-view.mod-cm6 .HyperMD-task-line{q} {box}){suffix}")
    dark = "linear-gradient(rgba(4, 8, 16, 0.6), rgba(4, 8, 16, 0.6))"
    alt = svg_uri(O.task_frame(inner=False))
    ash = svg_uri(O.task_frame(col=O.C_TASK_ASH, inner=False))
    out = ["/* ---- task states (generated from ornaments.TASK_GLYPHS) ---- */",
           # 进行中：内框左半垫血红(跟主强调色走)，不画爪痕
           f"{sel('/')} {{ background-image: {svg_uri(O.task_frame())}, linear-gradient(var(--nl-crimson), var(--nl-crimson)), {dark}; "
           "background-position: center, 3.4px 3.4px, 1px 1px; background-size: 100% 100%, 4.6px 9.2px, 14px 14px; }",
           f"{sel('/', '::after')} {{ display: none; }}"]
    for ch, (_, kind) in O.TASK_GLYPHS.items():
        out.append(f"{sel(ch)} {{ background-image: {ash if kind == 'ash' else alt}, {dark}; }}")
        out.append(f"{sel(ch, '::after')} {{ top: 0; left: 0; width: 16px; height: 16px; background-color: {TASK_COLORS[kind]}; "
                   f"-webkit-mask-image: {svg_uri(O.task_glyph(ch))}; mask-image: {svg_uri(O.task_glyph(ch))}; }}")
    # 只有完成(x 及 Obsidian 认作勾选的其他字符)和取消划线变灰，这些扩展状态保持正文样式。
    # Obsidian 自己只给 x 划线，取消 [-] 要补上
    done = "text-decoration: var(--checklist-done-decoration); color: var(--checklist-done-color);"
    out.append(f"body:not(.nl-native-tasks) .markdown-rendered li.task-list-item[data-task='-'], "
               f"body:not(.nl-native-tasks) .markdown-source-view.mod-cm6 .HyperMD-task-line[data-task='-'] {{ {done} }}")
    keep = ", ".join(f"[data-task='{ch}']" for ch in ["/"] + [c for c in O.TASK_GLYPHS if c != "-"])
    out.append(f"body:not(.nl-native-tasks) .markdown-rendered li.task-list-item:is({keep}) {{ text-decoration: none; color: var(--text-normal); }}")
    out.append(f"body:not(.nl-native-tasks) .markdown-source-view.mod-cm6 .HyperMD-task-line:is({keep}), "
               f"body:not(.nl-native-tasks) .markdown-source-view.mod-cm6 .HyperMD-task-line:is({keep}) * "
               "{ text-decoration: none; color: var(--text-normal); }")
    return "\n".join(out)


# ---- 每级纹章图标(大纲面板用；笔记列表附加样式也用) ----
LIST_DEPTH = 8
BULLETS = [  # (ornaments 函数, 显示宽 em, 高 em)，按级循环
    (O.bullet_skull, .62, .72),
    (O.bullet_bat, 1.06, .35),
    (O.bullet_bolt, .42, .8),
    (O.bullet_lozenge, .38, .38),
]
# 笔记列表附加样式(src/extras/list-thread.css + list_css 生成的按级规则)：第十八轮把“大纲视图”误解成笔记列表时做的，
# 用户要的是大纲面板，所以默认不打包；改 True 即接回(Style Settings 项见该文件开头注释)
LIST_EXTRAS = False


def bullet_defs() -> str:
    """各级图标只定义一次放在变量里(正常 + 折叠时的余烬红)"""
    defs = [f"--nl-bul-{i}: {svg_uri(fn())}; --nl-bul-{i}-x: {svg_uri(fn(O.C_EMBER))};"
            for i, (fn, _, _) in enumerate(BULLETS, 1)]
    return ".theme-dark, .theme-light { " + " ".join(defs) + " }"


def outline_css() -> str:
    """大纲面板：每一级同一个平面骷髅(正常 + 折叠后的余烬红)；按嵌套深度给 --nl-d(血线逐级流出的延迟用)，
    越深的选择器越具体，覆盖浅层"""
    out = ["/* ---- outline pane: skull icon & depth (generated by build.py outline_css) ---- */",
           '.workspace-leaf-content[data-type="outline"] { '
           f"--nl-ol-skull: {svg_uri(O.outline_skull())}; "
           f"--nl-ol-skull-x: {svg_uri(O.outline_skull(fill=O.C_EMBER, eye='#2c080c'))}; "
           f"--nl-ol-skull-o: {svg_uri(O.hollow_skull())}; }}"]
    for d in range(1, LIST_DEPTH + 1):
        sel = '.workspace-leaf-content[data-type="outline"] ' + " ".join([".tree-item"] * d)
        out.append(f"{sel} {{ --nl-d: {d - 1}; }}")
    # 每一级一根线(子级容器 ::before)，从父骷髅中心往下，下端锚到这一级路径项那一行的中线。
    # 1.0.7(用户：收起 / 展开某级标题时整根血线跳一下、重新展开)：原来线按父项 .tree-item 定位，bottom 量的是到父项底边的距离，
    # 收起 / 展开它下面的子项时父项变矮 / 变高，bottom 的数值跟着变(线的终点其实没动)，transition: bottom 把它播成「先缩短再长回去」。
    # 现在线按大纲的滚动区 .view-content 定位(面板高度，不随子项收起变化)，起点、终点都锚到悬停路径上的元素：
    # 路径上第 k 级那项的行 --nl-or{k}(中线)、文字 --nl-ot{k}(左缘 = 文字起点，骷髅中心在它左边 13px)；
    # 选择器从列表根一级级写 :hover，只落在悬停路径上(同名锚点各级唯一)
    p = 'body:not(.nl-outline-marker, .nl-outline-native) .workspace-leaf-content[data-type="outline"]'
    root = f"{p} .view-content > div > .tree-item:hover"
    out.append("@supports (anchor-name: --nl-x) {")
    for k in range(LIST_DEPTH + 1):
        s = root + " > .tree-item-children > .tree-item:hover" * k
        out.append(f"  {s} > .tree-item-self {{ anchor-name: --nl-or{k}; }}")
        out.append(f"  {s} > .tree-item-self > .tree-item-inner {{ anchor-name: --nl-ot{k}; }}")
    for d in range(LIST_DEPTH):
        s = root + " > .tree-item-children > .tree-item:hover" * d
        out.append(f"  {s} > .tree-item-children::before {{ top: anchor(--nl-or{d} center); "
                   f"left: calc(anchor(--nl-ot{d} left) - 13px - var(--nl-thread-w) / 2); "
                   f"bottom: calc(anchor(--nl-or{d + 1} center) - var(--nl-thread-w) / 2); }}")
    out.append("}")
    return "\n".join(out)


def _lv(lo: int) -> str:
    """级数 ≥ lo 的列表行"""
    return ":is(" + ", ".join(f".HyperMD-list-line-{k}" for k in range(lo, LIST_DEPTH + 1)) + ")"


def list_css() -> str:
    """列表符号与血线。
    阅读视图(嵌套 li)：悬停路径上每一级的符号(::after 图标框 / 任务框 / 有序项的占位框)挂上按深度编号的锚点名，
      父项的 ::after 用 anchor() 从自己的符号拉一条竖线、圆角拐进悬停子项的符号——父项折行多少行都接得上。
    编辑视图(平铺 .cm-line，每行自成定位容器，锚点跨不了行)：按 Maple / Logseq bullet threading 的思路，
      用兄弟选择器认出目标行(悬停的列表行；鼠标不在列表上时 = 光标行)的各级祖先，逐行画：
      祖先行 ::after 从符号往下，祖先之间的行 ::after 整行竖线，下一级祖先/目标行 ::before 画拐角。
      横坐标 x(a) = (a-1)·缩进 + 符号中心偏移，和缩进线对齐。"""
    out = ["/* ---- list bullets & blood thread (generated by build.py list_css) ---- */", bullet_defs()]
    # 1) 符号：图标变量见 bullet_defs，这里给各级引用
    for d in range(1, LIST_DEPTH + 1):
        i = (d - 1) % len(BULLETS)
        _, w, h = BULLETS[i]
        out.append(f".markdown-rendered {' '.join(['li'] * d)}, .markdown-source-view.mod-cm6 .HyperMD-list-line-{d} "
                   f"{{ --nl-bul: var(--nl-bul-{i + 1}); --nl-bul-x: var(--nl-bul-{i + 1}-x); --nl-bul-w: {w}em; --nl-bul-h: {h}em; }}")

    # 2) 阅读视图血线
    p = "body:not(.nl-list-marker, .nl-list-plain) .markdown-rendered"
    sub = ":is(ul.has-list-bullet, ul.contains-task-list, ol)"
    out.append(f"{p} ol > li:hover::before {{ content: \"\"; position: absolute; visibility: hidden; pointer-events: none; "
               "inset-inline-end: calc(100% + 0.3em); width: 1.1em; top: var(--list-spacing); height: calc(var(--line-height-normal) * 1em); }")
    out.append(f"{p} li:hover:has(> {sub} > li:hover)::after {{ content: \"\"; position: absolute; pointer-events: none; "
               "box-sizing: border-box; border-inline-start: var(--nl-thread-w) solid var(--nl-thread); "
               "border-bottom: var(--nl-thread-w) solid var(--nl-thread); border-end-start-radius: 5px; "
               "animation: nl-bleed 0.22s ease-out both; }")
    for d in range(1, LIST_DEPTH + 1):
        lis = " ".join(["li"] * d)
        up = " ".join(["li"] * (d - 1))
        ol_li = f"{up} ol > li" if up else "ol > li"
        out.append(f"{p} {lis}:hover > .list-bullet::after, {p} {lis}.task-list-item:hover > .task-list-item-checkbox, "
                   f"{p} {ol_li}:hover::before {{ anchor-name: --nl-m{d}; }}")
        if d < LIST_DEPTH:
            out.append(f"{p} {lis}:hover:has(> {sub} > li:hover)::after {{ "
                       f"top: calc(anchor(--nl-m{d} bottom) + 3px); left: calc(anchor(--nl-m{d} center) - var(--nl-thread-w) / 2); "
                       f"bottom: calc(anchor(--nl-m{d + 1} center) - var(--nl-thread-w) / 2); right: calc(anchor(--nl-m{d + 1} left) + 3px); "
                       f"animation-delay: {(d - 1) * 110}ms; }}")

    # 3) 编辑视图血线。两条性能教训(长文档实测)：
    #    · 别用 Maple 那种 :has(~ …) 兄弟选择器认祖先：每次悬停换行重算 30ms+，关掉开关也一样(选择器还在)；
    #    · 别给每个符号放 fixed 锚点框：几百个脱离文档流的盒子，每次悬停布局 90ms。
    #    现在：锚点名直接挂在符号上(正常流) --nl-L{级}，目标行之后的行用 `目标 ~ 行` 摘掉锚点名，
    #    同名锚点取树序最后一个 → 就是目标行前面最近的那一级符号 = 它的祖先。
    #    .cm-content 是 fixed 定位的包含块(contain: layout)，目标行自己的第 a 个 .cm-indent::after 画第 a 段：
    #    从 a 级祖先的符号往下，拐进 a+1 级祖先(最后一段拐进目标行自己的符号 --nl-T)。
    #    目标行默认 = 鼠标悬停的列表行；Style Settings 可改成光标所在行(两者不混用：混用要 :has 判断，代价同上)
    on = "body:not(.nl-list-marker, .nl-list-plain) .markdown-source-view.mod-cm6"
    mark = ":is(.list-bullet, .cm-formatting-list-ol)"
    ok = ":not(.HyperMD-quote, .HyperMD-list-line-nobullet)"
    targets = (f"body:not(.nl-list-marker, .nl-list-plain):not(.nl-thread-cursor-only) .markdown-source-view.mod-cm6 .cm-content > .HyperMD-list-line{ok}:hover",
               f"body.nl-thread-cursor-only:not(.nl-list-marker, .nl-list-plain) .markdown-source-view.mod-cm6 .cm-content > .HyperMD-list-line{ok}.cm-active")
    each = lambda tail: ", ".join(f"{s}{tail}" for s in targets)
    for a in range(1, LIST_DEPTH + 1):
        out.append(f"{on} .HyperMD-list-line-{a}:not(.HyperMD-quote) {mark} {{ anchor-name: --nl-L{a}; }}")
    out.append(f"{each(f' ~ .HyperMD-list-line {mark}')} {{ anchor-name: none; }}")
    out.append(f"{each(f' {mark}')} {{ anchor-name: --nl-T; }}")
    for a in range(1, LIST_DEPTH):
        _, wn, _ = BULLETS[a % len(BULLETS)]          # a+1 级图标宽
        _, _, ha = BULLETS[(a - 1) % len(BULLETS)]    # a 级图标高
        out.append(f"{each(f' .cm-indent:nth-child({a} of .cm-indent)::after')} {{ content: \"\"; "
                   f"left: calc(anchor(--nl-L{a} center) - var(--nl-thread-w) / 2); top: calc(anchor(--nl-L{a} center) + {ha / 2:g}em + 2px); "
                   f"bottom: calc(anchor(--nl-L{a + 1} center) - var(--nl-thread-w) / 2); "
                   f"right: calc(anchor(--nl-L{a + 1} left) + 3px + {wn / 2 - .16:g}em); animation-delay: {(a - 1) * 110}ms; }}")
    # 最后一段拐进目标行自己的符号(符号盒宽 0.32em，图标居中；有序行的标记 span 前有 --list-indent-editing 内边距)
    out.append(f"{each(' .cm-indent:nth-last-child(1 of .cm-indent)::after')} {{ bottom: calc(anchor(--nl-T center) - var(--nl-thread-w) / 2); "
               "right: calc(anchor(--nl-T left) + 3px + var(--nl-bul-w) / 2 - 0.16em - var(--nl-t-pad, 0px)); }")
    return "\n".join(out)


def settings_lang_css(src: str) -> str:
    """Style Settings「设置语言」强制中文 / English：按 data-id 把设置项名称、说明换成另一种语言。
    插件本身只按 Obsidian 界面语言自动在 title / title.zh(description 同理)里挑一个；强制时把原文字号压成 0、
    用 ::after / ::before 写出另一种语言(分组标题的折叠箭头是 9px 定尺寸的 svg，不受字号影响)。
    下拉选项的文字插件不支持多语言(只认 label)：支持可自定义下拉框的内核上按语言换文字(见下)，
    旧内核原样显示 label(英文)"""
    import yaml
    m = re.search(r"/\* @settings\s*\n(.*?)\n\*/", src, re.S)
    items = yaml.safe_load(m.group(1))["settings"]
    q = lambda s: '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    scope = ".style-settings-container"
    sel = lambda sid, part: f'{scope} .setting-item[data-id="{sid}"] > .setting-item-info > .setting-item-{part}'
    ids = [s["id"] for s in items if "title.zh" in s]
    desc_ids = [s["id"] for s in items if "description.zh" in s]
    forced = "body:is(.nl-lang-zh, .nl-lang-en)"
    out = [f"{forced} :is({', '.join(sel(i, 'name') for i in ids)}) {{ font-size: 0; }}",
           f"{forced} :is({', '.join(sel(i, 'name') for i in ids)})::after {{ font-size: var(--setting-item-name-size); }}",
           f"{forced} {scope} .setting-item-heading > .setting-item-info > .setting-item-name::after {{ font-size: var(--setting-group-heading-size); }}"]
    if desc_ids:
        out += [f"{forced} :is({', '.join(sel(i, 'description') for i in desc_ids)}) {{ font-size: 0; }}",
                f"{forced} :is({', '.join(sel(i, 'description') for i in desc_ids)})::before {{ font-size: var(--font-ui-smaller); }}"]
    for s in items:
        if "title.zh" not in s:
            continue
        for cls, key in (("nl-lang-en", "title"), ("nl-lang-zh", "title.zh")):
            out.append(f"body.{cls} {sel(s['id'], 'name')}::after {{ content: {q(s[key])}; }}")
        if "description.zh" in s:
            for cls, key in (("nl-lang-en", "description"), ("nl-lang-zh", "description.zh")):
                out.append(f"body.{cls} {sel(s['id'], 'description')}::before {{ content: {q(s[key])}; }}")

    # ---- 下拉框：选项文字插件只认 label，原生下拉列表的文字 CSS 也改不了。用可自定义下拉框
    # (appearance: base-select，Chromium 135+；Obsidian 1.14 = Chromium 142)把选项变成普通元素，按 value 换文字；
    # 收起时显示的文字用 select::before，按 body 上的选中值类名挑(class-select 的选中项本来就挂成 body 类)。
    # 下拉框跟随语言：强制中文 / English 看 body 类；跟随 Obsidian 时看 <html lang>(Obsidian 把界面语言写在这里)。
    # 清单里 label = 英文、label.zh = 中文(插件忽略 label.zh)；插件给下拉框说明自动加的「默认值：xxx」行显示原始 label，藏掉
    zh = ":is(html:lang(zh) body:not(.nl-lang-en), body.nl-lang-zh)"
    en = ":is(html:not(:lang(zh)) body:not(.nl-lang-zh), body.nl-lang-en)"
    selects = [s for s in items if s.get("type") == "class-select" and all("label.zh" in o for o in s["options"])]
    if selects:
        # 整段包在 @supports 里：旧内核(Chromium < 135，旧版安装包)不认 base-select，原文字号压 0 后下拉框会变空白
        out.append("@supports (appearance: base-select) {")
        dd = lambda sid: f'{scope} .setting-item[data-id="{sid}"] > .setting-item-control > select.dropdown'
        allsel = ", ".join(dd(s["id"]) for s in selects)
        out += [
            f":is({allsel}), :is({allsel})::picker(select) {{ appearance: base-select; }}",
            # 原文字号压 0 藏起来；原版下拉框的内边距 / 右侧箭头尺寸和位置都按 em 算(会跟着归零)，改按界面小字号
            # (= 原版下拉框字号 13px)换算回原值；宽度按显示的文字自适应，不用 Obsidian 按原文量出的 --dropdown-fitted-width
            f":is({allsel}) {{ font-size: 0; width: max-content; "
            f"padding: 0 calc(var(--font-ui-small) * 2.4) 0 calc(var(--font-ui-small) * 0.8); "
            f"background-size: var(--font-ui-small) auto, calc(var(--font-ui-small) * 2) calc(var(--font-ui-small) * 2); "
            f"background-position: right calc(var(--font-ui-small) * 0.65) top 50%, right calc(var(--font-ui-small) * 0.15) top 50%; }}",
            f":is({allsel})::picker-icon {{ display: none; }}",
            f":is({allsel}) {{ display: inline-flex; align-items: center; }}",
            f":is({allsel})::before {{ font-size: var(--font-ui-small); line-height: normal; white-space: nowrap; }}",
            f":is({allsel})::picker(select) {{ margin-block: 4px; padding: 4px; border: 1px solid color-mix(in srgb, var(--nl-lightning) 30%, transparent); "
            f"border-radius: 2px; background-color: var(--nl-night-900); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6); }}",
            f":is({allsel}) option {{ gap: 6px; padding: 5px 12px 5px 6px; border-radius: 2px; color: var(--text-normal); font-size: 0; }}",
            f":is({allsel}) option:is(:hover, :focus-visible) {{ outline: none; background-color: var(--background-modifier-hover); }}",
            f":is({allsel}) option:checked {{ color: var(--nl-bone); }}",
            f":is({allsel}) option::after {{ font-size: var(--font-ui-small); }}",
            f":is({allsel}) option::checkmark {{ font-size: var(--font-ui-small); color: var(--nl-crimson); }}",
        ]
        for s in selects:
            sid = s["id"]
            info = f'{scope} .setting-item[data-id="{sid}"] > .setting-item-info > .setting-item-description'
            out.append(f"{info} > div {{ display: none; }}" if "description" in s else f"{info} {{ display: none; }}")
            vals = [o["value"] for o in s["options"]]
            for lang, key in ((zh, "label.zh"), (en, "label")):
                for o in s["options"]:
                    out.append(f"{lang}.{o['value']} {dd(sid)}::before {{ content: {q(o[key])}; }}")
                    out.append(f"{lang} {dd(sid)} option[value=\"{o['value']}\"]::after {{ content: {q(o[key])}; }}")
                default = next((o for o in s["options"] if o["value"] == s.get("default")), s["options"][0])
                not_any = ", ".join("." + v for v in vals)
                out.append(f"{lang}:not({not_any}) {dd(sid)}::before {{ content: {q(default[key])}; }}")
        out.append("}")
    return "\n".join(out)


# ---- Mermaid：按图表类型(svg 的 aria-roledescription)改色 ----
MM = {"F": "flowchart-v2", "S": "stateDiagram", "Q": "sequence", "C": "class", "E": "er",
      "G": "gantt", "P": "pie", "M": "mindmap", "T": "timeline"}
MM_SECTIONS = 6     # theme.src.css 里的分组色 --nl-mm-c0..5 / --nl-mm-d0..5


def mermaid_css() -> str:
    """Mermaid 每张图自带一段 `#图id .node rect { … }` 样式。选择器里的 :is(svg, #nl-mermaid) 带一个用不到的 id，
    特异性压过它们又不用 !important：用户在图里写的 classDef / style(Mermaid 输出成内联或 !important)照样优先。
    不在 MM 里的图表类型保留反色滤镜(theme.src.css)"""
    def pre(types: str) -> str:
        roles = ", ".join(f'[aria-roledescription="{MM[t]}"]' for t in types)
        return f".mermaid > :is(svg, #nl-mermaid):is({roles})"

    ALL, NODE = "".join(MM), "FSCE"
    # 用户自定义了填充色的节点(classDef / style)：文字颜色也交给用户，不改成浅色。
    # 1.0.5 性能(issue #1，Mac 上写日记打字卡)：原来写成 :not(:where(.node:has(…) *))——:has() 套在 :not / :where 里、又不在主体位置，
    # Chromium 定不出受影响的范围，页面上任何元素的 style 属性一变(CodeMirror 每打一个字都改光标的 style)就把 body 整棵树标成要重算。
    # 改成圣血天使第三十七版的写法：:has() 只给这种节点挂个标记(主体就是节点自己，失效只到它本身)，带 own 的文字规则包进样式查询，在标记底下不生效。
    # 1.0.7 性能(用户：大纲里拖标题严重卡顿)：标记写成 .node:has(> [style*='fill'])，:has() 参数里有 style 属性——
    # 页面上任何元素的内联 style 一变(拖动时跟着鼠标的提示框、虚拟列表的占位高度、CodeMirror 的光标)，浏览器都要沿祖先查一遍 :has()，
    # 碰上高层锚点就整片重算。现在不用 :has()：经典形状(直接挂在节点下，文字 .label 是它后面的兄弟，流程图、状态图)用兄弟选择器把标记挂到 .label 上；
    # classDef 会给节点加类名(流程图、类图的节点本来是 "node default")，类名多出来就算。
    # 认不出的只有 Mermaid 11 新形状 / 类图只用 style 指令改填充(样式在内层 g 的 path 上)，文字照主题色
    own = "@@OWN@@"
    shape = ":is(rect, circle, ellipse, polygon, path)"
    rules = [
        (ALL, [""], "filter: none;"),
        (ALL, [f":is(text, tspan){own}"], "fill: var(--nl-mm-text);"),
        (ALL, [f":is(span, p){own}"], "color: var(--nl-mm-text);"),
        # 节点：Mermaid 11 的不少形状是一对 path(一条只填色 stroke=none、一条只描边 fill=none)，按属性分开上色
        (NODE, [f".node {shape}:not(:where(.label *, [fill='none']))"], "fill: var(--nl-mm-fill);"),
        (NODE, [f".node {shape}:not(:where(.label *, [stroke='none']))"], "stroke: var(--nl-mm-line);"),
        # 连线与箭头
        (NODE, [":is(.flowchart-link, .transition, .relation, .relationshipLine, .edgePath .path)"], "stroke: var(--nl-mm-edge);"),
        ("FS", ["marker :is(path, circle)"], "fill: var(--nl-mm-edge); stroke: var(--nl-mm-edge);"),
        # 类图箭头的颜色 Mermaid 写在 marker 上(带 !important)，改在里面的 path 上(继承来的值不论 !important)；
        # 空心的继承+聚合不填色
        ("C", ["marker.marker :is(path, circle)"], "stroke: var(--nl-mm-edge);"),
        ("C", ["marker:is(.composition, .dependency) path"], "fill: var(--nl-mm-edge);"),
        ("E", ["marker path"], "fill: none; stroke: var(--nl-mm-edge);"),
        ("E", ["marker circle"], "fill: var(--nl-mm-bg); stroke: var(--nl-mm-edge);"),
        # 连线上的文字：底色换成页面底色
        (NODE, [":is(.edgeLabel, .edgeLabel p, .labelBkg)"], "background-color: var(--nl-mm-bg);"),
        (NODE, [".edgeLabel rect"], "fill: var(--nl-mm-bg); opacity: 1;"),
        (NODE, [f":is(.edgeLabel, .edgeTerminals) :is(span, p){own}"], "color: var(--nl-mm-label);"),
        # 子图 / 复合状态：深一层的底、血红细框、黄铜标题
        ("F", [".cluster > rect"], "fill: var(--nl-mm-group); stroke: var(--nl-mm-group-line);"),
        ("S", [".statediagram-cluster rect.outer"], "fill: var(--nl-mm-fill); stroke: var(--nl-mm-line);"),
        ("S", [".statediagram-cluster rect.inner"], "fill: var(--nl-mm-group); stroke: var(--nl-mm-line);"),
        ("FS", [".cluster-label :is(span, p, text, tspan)"], "fill: var(--nl-mm-title); color: var(--nl-mm-title);"),
        # 类名、实体名用黄铜色；ER 的 PK / FK 用余烬红
        ("C", [".label-group :is(span, p)"], "color: var(--nl-mm-title);"),
        ("C", [".annotation-group :is(span, p)"], "color: var(--nl-mm-label);"),
        ("E", [".label.name :is(span, p)"], "color: var(--nl-mm-title);"),
        ("E", [".label.attribute-keys :is(span, p)"], "color: var(--nl-ember-light);"),
        ("E", [":is(.row-rect-odd, .row-rect-even) path:not([fill='none'])"], "fill: var(--nl-night-850);"),
        ("E", [".row-rect-even path:not([fill='none'])"], "fill: var(--nl-night-800);"),
        ("E", [":is(.row-rect-odd, .row-rect-even, .divider) path:not([stroke='none'])"], "stroke: var(--nl-mm-line-soft);"),
        # 状态图：起点实心血红点、终点血红靶心、分叉 / 汇合横条用连线色
        ("S", ["circle.state-start"], "fill: var(--nl-mm-accent); stroke: var(--nl-mm-accent);"),
        ("S", [".node[id*='_end-'] > g > path:not([stroke='none'])"], "stroke: var(--nl-mm-accent);"),
        ("S", [".node[id*='_end-'] > g > g > path"], "fill: var(--nl-mm-accent); stroke: var(--nl-mm-accent);"),
        ("S", [".statediagram-state > g > path[fill='#333333']"], "fill: var(--nl-mm-edge);"),
        ("S", [".statediagram-state > g > path[stroke='#333333']"], "stroke: var(--nl-mm-edge);"),
        # 注释：血色便笺
        ("S", [".statediagram-note .label-container > path:not([fill='none'])"], "fill: var(--nl-mm-note);"),
        ("S", [".statediagram-note .label-container > path:not([stroke='none'])"], "stroke: var(--nl-mm-note-line);"),
        ("Q", ["rect.note"], "fill: var(--nl-mm-note); stroke: var(--nl-mm-note-line);"),
        ("SC", [".node:is(.statediagram-note, [id^='note']) :is(span, p)"], "color: var(--nl-mm-note-text);"),
        ("Q", [":is(.noteText, .noteText > tspan)"], "fill: var(--nl-mm-note-text);"),
        # 类图注释框的颜色被 Mermaid 写成内联 !important，CSS 盖不掉：用滤镜把淡黄底 / 橄榄框映射成血色(拟合值)
        ("C", [".node[id^='note'] > .label-container"],
         "filter: invert(0.851) sepia(0.651) saturate(8.282) hue-rotate(55.2deg) brightness(0.657) contrast(1.609);"),
        # 时序图
        ("Q", ["rect.actor"], "fill: var(--nl-mm-fill); stroke: var(--nl-mm-line);"),
        ("Q", [".actor-man :is(line, circle)"], "fill: var(--nl-mm-fill); stroke: var(--nl-mm-line);"),
        ("Q", [".actor-line"], "stroke: var(--nl-shade);"),
        ("Q", [":is(.messageLine0, .messageLine1)"], "stroke: var(--nl-mm-edge);"),
        ("Q", ["marker path"], "fill: var(--nl-mm-edge); stroke: var(--nl-mm-edge);"),
        ("Q", ["marker[id$='crosshead'] path"], "fill: none;"),
        ("Q", ["marker circle"], "fill: var(--nl-mm-accent); stroke: var(--nl-mm-accent);"),
        ("Q", [".sequenceNumber"], "fill: var(--nl-bone);"),
        ("Q", [":is(.activation0, .activation1, .activation2)"], "fill: var(--nl-blood-800); stroke: var(--nl-mm-accent);"),
        ("Q", [".loopLine"], "stroke: var(--nl-mm-loop);"),
        ("Q", [".labelBox"], "fill: var(--nl-night-700); stroke: var(--nl-mm-loop);"),
        ("Q", [":is(.labelText, .labelText > tspan, .loopText, .loopText > tspan)"], "fill: var(--nl-lightning);"),
        # 甘特图：分区隔行淡蓝底；任务 = 夜蓝 / 进行中 = 黄铜 / 完成 = 暗 / 关键 = 血红
        ("G", [":is(.section0, .section2)"], "fill: color-mix(in srgb, var(--nl-night-600) 45%, transparent); opacity: 1;"),
        ("G", [":is(.section1, .section3)"], "fill: transparent;"),
        ("G", [".grid .tick line"], "stroke: var(--nl-line); opacity: 1;"),
        ("G", [".grid .tick text"], "fill: var(--nl-mm-label);"),
        ("G", [".grid .domain"], "fill: none; stroke: none;"),
        ("G", [".exclude-range"], "fill: var(--nl-night-900);"),
        ("G", [":is(.task0, .task1, .task2, .task3)"], "fill: var(--nl-night-600); stroke: var(--nl-mm-loop);"),
        ("G", [":is(.active0, .active1, .active2, .active3)"], "fill: var(--nl-bronze-800); stroke: var(--nl-mm-line);"),
        ("G", [":is(.done0, .done1, .done2, .done3)"], "fill: var(--nl-night-800); stroke: var(--nl-shade);"),
        ("G", [":is(.crit0, .crit1, .crit2, .crit3)"], "fill: var(--nl-blood-700); stroke: var(--nl-mm-accent);"),
        ("G", [":is(.activeCrit0, .activeCrit1, .activeCrit2, .activeCrit3)"], "fill: var(--nl-blood-800); stroke: var(--nl-ember);"),
        ("G", [":is(.doneCrit0, .doneCrit1, .doneCrit2, .doneCrit3)"], "fill: var(--nl-night-800); stroke: var(--nl-blood-600);"),
        # 任务文字的颜色 Mermaid 大多写成 !important(甘特图没有 classDef，用户改不了这些，跟着 !important 不碍事)
        ("G", [":is(.taskText, .taskTextOutsideRight, .taskTextOutsideLeft)"], "fill: var(--nl-mm-text) !important;"),
        ("G", [":is(.doneText0, .doneText1, .doneText2, .doneText3, .doneCritText0, .doneCritText1, .doneCritText2, .doneCritText3)"],
         "fill: var(--nl-mm-label) !important;"),
        ("G", [":is(.taskText, .taskTextOutsideRight, .taskTextOutsideLeft).clickable"], "fill: var(--nl-lightning) !important;"),
        ("G", [".vertText"], "fill: var(--nl-ember-light) !important;"),
        ("G", [":is(.sectionTitle, .sectionTitle > tspan)"], "fill: var(--nl-mm-title);"),
        ("G", [":is(.today, .vert)"], "stroke: var(--nl-mm-accent);"),
        # 饼图：扇区间用页面底色勾缝
        ("P", [".pieCircle"], "stroke: var(--nl-mm-bg); stroke-width: 2px; opacity: 1;"),
        ("P", [".pieOuterCircle"], "stroke: var(--nl-mm-line); stroke-width: 1px;"),
        ("P", ["text.slice"], "fill: var(--nl-bone);"),
        # 时间线连线
        ("T", [".lineWrapper line"], "stroke: var(--nl-mm-edge);"),
        ("T", ["marker path"], "fill: var(--nl-mm-edge);"),
    ]
    # 分组色循环：思维导图分支、时间线时段(-1 起)、饼图扇区和图例(图例色是内联样式，只能 !important)
    for n in range(-1, 12):
        k = (n + 1) % MM_SECTIONS
        c, d = f"var(--nl-mm-c{k})", f"var(--nl-mm-d{k})"
        rules += [
            ("MT", [f".section-{n} {shape}:not(:where(.label *))"], f"fill: {d};"),
            ("MT", [f".section-{n} line"], f"stroke: {c};"),
            ("M", [f".section-edge-{n}"], f"stroke: color-mix(in srgb, {c} 75%, transparent);"),
        ]
    for k in range(MM_SECTIONS):
        fill = f"color-mix(in srgb, var(--nl-mm-c{k}) 72%, var(--nl-night-900))"
        rules += [
            ("P", [f"path.pieCircle:nth-of-type({MM_SECTIONS}n + {k + 1})"], f"fill: {fill};"),
            ("P", [f"g.legend:nth-of-type({MM_SECTIONS}n + {k + 1}) rect"], f"fill: {fill} !important; stroke: {fill} !important;"),
        ]
    # 思维导图根节点(同时带 section--1，要排在分组色后面)
    rules.append(("M", [f".section-root {shape}:not(:where(.label *))"], "fill: var(--nl-blood-800); stroke: var(--nl-mm-accent);"))
    out = ["/* ---- Mermaid colours (generated by build.py mermaid_css) ---- */",
           f"{pre(ALL)} .node > [style*='fill'] ~ .label,\n{pre('FC')} .node.default:not([class='node default']) {{ --nl-mm-own: 1; }}"]
    for types, inner, decl in rules:
        sels = ",\n".join(f"{pre(types)} {s}".rstrip() for s in inner)
        rule = f"{sels} {{ {decl} }}"
        if own in sels:
            rule = "@container not style(--nl-mm-own: 1) {\n" + rule.replace(own, "") + "\n}"
        out.append(rule)
    return "\n".join(out)


def build() -> Path:
    src = (ROOT / "src" / "theme.src.css").read_text(encoding="utf-8")
    table = ornaments()

    def sub(m):
        key = m.group(1)
        if key not in table:
            raise KeyError(f"unknown placeholder @@{key}@@")
        return table[key]
    css = re.sub(r"@@([A-Z]+:[a-z0-9-]+)@@", sub, src)
    css = css.replace("/*@@FONTS@@*/", font_faces())
    css = css.replace("/*@@CALLOUT-ICONS@@*/", callout_icon_css())
    css = css.replace("/*@@TASK-STATES@@*/", task_css())
    css = css.replace("/*@@OUTLINE-THREAD@@*/", outline_css())
    css = css.replace("/*@@SETTINGS-LANG@@*/", settings_lang_css(src))
    css = css.replace("/*@@MERMAID@@*/", mermaid_css())
    if LIST_EXTRAS:
        extra = (ROOT / "src" / "extras" / "list-thread.css").read_text(encoding="utf-8")
        css += "\n" + extra.replace("/*@@LIST-THREAD@@*/", list_css())
    left = re.findall(r"@@[^@\s]+@@", css)
    if left:
        raise SystemExit(f"unreplaced placeholders: {left}")
    DIST.mkdir(parents=True, exist_ok=True)
    (DIST / "theme.css").write_text(css, encoding="utf-8")
    manifest = {
        "name": THEME_NAME,
        "version": VERSION,
        "minAppVersion": "1.6.0",
        "author": "whitedry",
        "authorUrl": "https://github.com/white0dry",
    }
    (DIST / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    kb = (DIST / "theme.css").stat().st_size // 1024
    print(f"built {DIST / 'theme.css'}  ({kb} KB)")
    return DIST


if __name__ == "__main__":
    out = build()
    if "--install" in sys.argv:
        dst = VAULT / ".obsidian" / "themes" / THEME_NAME
        dst.mkdir(parents=True, exist_ok=True)
        for f in ("theme.css", "manifest.json"):
            shutil.copy2(out / f, dst / f)
        print("installed ->", dst)
        # README 截图用的示例库(tools/make_demo_vault.py 建的)也同步一份
        demo = Path(__file__).resolve().parent / "demo-vault" / ".obsidian" / "themes" / THEME_NAME
        if demo.parent.parent.exists():
            demo.mkdir(parents=True, exist_ok=True)
            for f in ("theme.css", "manifest.json"):
                shutil.copy2(out / f, demo / f)
            print("installed ->", demo)
