# -*- coding: utf-8 -*-
"""生成模拟 Obsidian 1.14 DOM 的预览页(加载真 app.css + 本主题 theme.css)，供截图检查。
用法: python tools/make_harness.py [app.css 路径]
输出 preview/reading.html, preview/live.html, preview/empty.html
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
APP_CSS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "preview" / "app.css"
THEME_CSS = ROOT / "theme.css"
OUT = ROOT / "preview"

ICON = '<svg class="svg-icon lucide-pencil" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/></svg>'
CHEV = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" class="svg-icon right-triangle"><path d="M3 8L12 17L21 8"></path></svg>'

TITLE = "夜巡手记"

# ---------------------------------------------------------------- 内容(和 demo-vault/夜巡手记.md 同一套虚构示例，README 截图也用它)
P1 = ('这是 <strong>Night Lords · 午夜领主</strong> 主题的示例笔记：<strong>粗体</strong>、<em>斜体</em>、'
      '<del>删除线</del>、<mark>高亮</mark>、<code>行内代码</code>、'
      '<a class="internal-link" href="#">钟楼</a>（内部链接）、<a class="external-link" href="#">Obsidian 官网</a>（外部链接）、'
      '<a class="tag" href="#">#示例</a> 标签。中文与 English 混排时，主题会自动在两者之间留出间距。')
P2 = ('No one in the city has ever seen a sunrise. The sky is a single low sheet of lead, torn open only when the storms come. '
      'People keep time by the bells and divide the streets by lamplight; <em>where the lamps go out, the Watch no longer holds sway</em>. '
      '<strong>“We keep watch in the dark so that others may sleep.”</strong>')
P3 = ('钟楼立在旧城正中，塔顶的铜钟据说是用第一代守夜人的盔甲熔铸的。'
      '每到整点，钟声沿着石板街一路传到城墙脚下。')
QUOTE = '钟楼敲过十三下之后，<strong>城门不再为任何人打开。</strong>——《夜巡守则》第一条'
CALLOUT = ('闪电过后数到第七下才听见雷声，说明雷暴还在城外。<strong>雷暴最猛烈的那一夜，所有守夜人都要回到钟楼。</strong><br>'
           '<em>Count to seven between the flash and the thunder, and the storm is still beyond the walls.</em>')
TABLE = [
    ("物品", "用途", "数量"),
    ("<strong>黄铜提灯</strong>", "照明，也用来打信号", "1"),
    ("<strong>铁哨</strong>", "召集附近的同伴", "2"),
    ("<strong>羊皮地图</strong>", "标出熄灯的街区", "1"),
    ("<strong>银铃</strong>", "驱散蝙蝠群", "3"),
]
# 列表树：(文字, 子项, 子项是否有序)；深到 4 级，含会折行的父项和嵌在无序里的有序列表
UL = [("每条街至少留一盏长明灯", [
          ("灯油由街坊轮流供给", [
              ("轮值名单贴在钟楼西门", [("名单每逢新月更换一次", [], False)], False),
              ("灯罩必须用黄铜，玻璃会在雷暴里震碎", [], False)], False),
          ("Lamp hoods must be brass; glass shatters in the storms", [], False)], False),
      ("熄灯之后不得高声说话；如果必须呼唤同伴，就吹铁哨，一长两短表示平安，三声短哨表示有人闯入", [
          ("铁哨挂在提灯的铜环上", [], False),
          ("巡夜的顺序", [("从钟楼出发，沿北街走到城墙", [], False), ("在东门换岗", [], False)], True)], False),
      ("遇到不认识的守夜人，先问口令", [], False)]
LIVE_ACTIVE = "灯罩必须用黄铜，玻璃会在雷暴里震碎"   # 编辑视图里光标所在的列表行(没悬停时引导线跟随它)
OL = ["从钟楼出发，沿北街走到城墙", "绕城墙半圈，在东门换岗", "天亮之前（如果有天亮的话）回到钟楼"]
TASKS = [(True, "给钟楼的齿轮上油"), (False, "去档案馆归还《夜巡守则》抄本")]
CODE = ('<span class="token keyword">def</span> <span class="token function">ring_bell</span>(hour: <span class="token builtin">int</span>) -> <span class="token builtin">str</span>:\n'
        '    <span class="token comment"># After thirteen strokes the gates close</span>\n'
        '    <span class="token keyword">return</span> <span class="token string">"dong "</span> * <span class="token builtin">min</span>(hour, <span class="token number">13</span>)')


def reading_body():
    def el(cls, inner):
        return f'<div class="{cls}">{inner}</div>'
    rows = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in TABLE[1:])
    head = "<tr>" + "".join(f"<th>{c}</th>" for c in TABLE[0]) + "</tr>"

    def li(text, kids, ordered_kids, in_ol=False):
        """Obsidian 阅读视图：有子项的 li 前面有折叠图标；有序列表的 li 没有 .list-bullet(用 ::marker)"""
        sub = fold = ""
        if kids:
            fold = f'<div class="list-collapse-indicator collapse-indicator collapse-icon">{CHEV}</div>'
            tag = "ol" if ordered_kids else 'ul class="has-list-bullet"'
            sub = f"<{tag}>" + "".join(li(t, k, o, ordered_kids) for t, k, o in kids) + f"</{tag.split()[0]}>"
        bullet = "" if in_ol else '<span class="list-bullet"></span>'
        return f'<li data-line="0" dir="auto">{fold}{bullet}{text}{sub}</li>'
    ul = '<ul class="has-list-bullet">' + "".join(li(t, k, o) for t, k, o in UL) + "</ul>"
    ol = "<ol>" + "".join(f'<li data-line="0" dir="auto">{t}</li>' for t in OL) + "</ol>"
    tasks = '<ul class="contains-task-list has-list-bullet">' + "".join(
        f'<li data-line="0" data-task="{"x" if d else " "}" class="task-list-item{" is-checked" if d else ""}" dir="auto">'
        f'<span class="list-bullet"></span><input data-line="0" type="checkbox" class="task-list-item-checkbox"{" checked" if d else ""}>{t}</li>'
        for d, t in TASKS) + "</ul>"
    callout = ('<div data-callout-metadata="" data-callout-fold="" data-callout="note" class="callout">'
               f'<div class="callout-title" dir="auto"><div class="callout-icon">{ICON}</div><div class="callout-title-inner">笔记</div></div>'
               f'<div class="callout-content"><p dir="auto">{CALLOUT}</p></div></div>')
    callout2 = ('<div data-callout="warning" class="callout">'
                f'<div class="callout-title" dir="auto"><div class="callout-icon">{ICON}</div><div class="callout-title-inner">警告</div></div>'
                '<div class="callout-content"><p dir="auto">雷暴时不要站在城墙垛口之间。</p></div></div>')
    return "".join([
        el("el-h1", '<h1 data-heading="一、永夜之城">一、永夜之城</h1>'),
        el("el-p", f'<p dir="auto">{P1}</p>'),
        el("el-p", f'<p dir="auto">{P2}</p>'),
        el("el-h2", '<h2 data-heading="钟楼" dir="auto">钟楼</h2>'),
        el("el-p", f'<p dir="auto">{P3}</p>'),
        el("el-table", f'<div class="table-wrapper"><table><thead>{head}</thead><tbody>{rows}</tbody></table></div>'),
        el("el-h3", '<h3 data-heading="灯火的规矩" dir="auto">灯火的规矩</h3>'),
        el("el-ul", ul),
        el("el-blockquote", f'<blockquote><p dir="auto">{QUOTE}</p></blockquote>'),
        el("el-div", callout),
        el("el-h4", '<h4 dir="auto">巡夜的顺序</h4>'),
        el("el-ol", ol),
        el("el-hr", "<hr>"),
        el("el-h5", '<h5 dir="auto">今晚的事项</h5>'),
        el("el-ul", tasks),
        el("el-div", callout2),
        el("el-pre", f'<pre class="language-python" tabindex="0"><code class="language-python is-loaded">{CODE}</code></pre>'),
        el("el-h6", '<h6 dir="auto">六级标题</h6>'),
        el("el-p", '<p dir="auto">最小一级的标题，适合写极短的批注。</p>'),
    ])


def live_body():
    def line(cls, inner):
        return f'<div class="cm-line{(" " + cls) if cls else ""}" dir="ltr">{inner}</div>'

    def inl(html):
        return (html.replace("<strong>", '<span class="cm-strong">').replace("</strong>", "</span>")
                .replace("<em>", '<span class="cm-em">').replace("</em>", "</span>")
                .replace("<mark>", '<span class="cm-highlight">').replace("</mark>", "</span>")
                .replace("<del>", '<span class="cm-strikethrough">').replace("</del>", "</span>")
                .replace("<code>", '<span class="cm-inline-code">').replace("</code>", "</span>")
                .replace('<a class="internal-link" href="#">', '<span class="cm-hmd-internal-link"><span class="cm-underline">')
                .replace('<a class="external-link" href="#">', '<span class="cm-link"><span class="cm-underline">')
                .replace('<a class="tag" href="#">', '<span class="cm-hashtag cm-hashtag-begin cm-meta cm-tag-示例">')
                .replace("</a>", "</span></span>"))
    callout = ('<div contenteditable="false" class="cm-embed-block markdown-rendered cm-callout" tabindex="-1">'
               '<div data-callout-metadata="" data-callout-fold="" data-callout="note" class="callout">'
               f'<div class="callout-title" dir="auto"><div class="callout-icon">{ICON}</div><div class="callout-title-inner">笔记</div></div>'
               f'<div class="callout-content"><p dir="auto">{CALLOUT}</p></div></div></div>')

    def li(text, depth, ordered=False, num=1):
        """Obsidian 1.14 实时预览的列表行：每级缩进一个 .cm-indent(制表符，宽 = --list-indent)，
        悬挂缩进的 text-indent/padding 由页尾脚本按标记宽度量出来(Obsidian 也是运行时量的)"""
        indent = (f'<span class="cm-hmd-list-indent cm-hmd-list-indent-{depth - 1}">'
                  + '<span class="cm-indent">\t</span>' * (depth - 1) + '</span>') if depth > 1 else ""
        mark = (f'<span class="cm-formatting cm-formatting-list cm-formatting-list-ol cm-list-{depth}">{num}. </span>' if ordered else
                f'<span class="cm-formatting cm-formatting-list cm-formatting-list-ul cm-list-{depth}"><span class="list-bullet">-</span> </span>')
        active = " cm-active" if text == LIVE_ACTIVE else ""
        return (f'<div class="cm-line HyperMD-list-line HyperMD-list-line-{depth}{active}" dir="ltr">'
                f'{indent}{mark}<span class="cm-list-{depth}">{text}</span></div>')
    rows = []

    def walk(nodes, depth, ordered):
        for i, (t, kids, o) in enumerate(nodes):
            rows.append(li(t, depth, ordered, i + 1))
            walk(kids, depth + 1, o)
    walk(UL, 1, False)
    return "".join([
        line("HyperMD-header HyperMD-header-1", '<span class="cm-header cm-header-1">一、永夜之城</span>'),
        line("", inl(P1)),
        line("", ""),
        line("", inl(P2)),
        line("HyperMD-header HyperMD-header-2", '<span class="cm-formatting cm-formatting-header cm-formatting-header-2 cm-header cm-header-2">## </span><span class="cm-header cm-header-2">钟楼</span>'),
        line("", inl(P3)),
        line("HyperMD-header HyperMD-header-3", '<span class="cm-header cm-header-3">灯火的规矩</span>'),
        *rows,
        line("", ""),
        line("HyperMD-quote HyperMD-quote-1 cm-blockquote-border", f'<span class="cm-quote cm-quote-1">{inl(QUOTE)}</span>'),
        line("", ""),
        callout,
        line("", ""),
        line("hr", '<hr class="cm-hr">'),
        line("HyperMD-header HyperMD-header-4", '<span class="cm-header cm-header-4">巡夜的顺序</span>'),
        line("", "我们在黑暗中守望，好让别人安睡。"),
    ])


def properties():
    def prop(k, v):
        return (f'<div class="metadata-property" tabindex="0" data-property-key="{k}" data-property-type="text">'
                f'<div class="metadata-property-key"><span class="metadata-property-icon">{lucide("text")}</span>'
                f'<input class="metadata-property-key-input" autocapitalize="none" enterkeyhint="next" type="text" value="{k}"></div>'
                f'<div class="metadata-property-value"><div class="metadata-input-longtext mod-truncate" contenteditable="true">{v}</div></div></div>')
    tags = ('<div class="metadata-property" data-property-key="tags" data-property-type="tags"><div class="metadata-property-key">'
            f'<span class="metadata-property-icon">{lucide("tags")}</span><input class="metadata-property-key-input" type="text" value="tags"></div>'
            '<div class="metadata-property-value"><div class="multi-select-container">'
            '<div class="multi-select-pill"><div class="multi-select-pill-content"><span>示例</span></div></div>'
            '<div class="multi-select-pill"><div class="multi-select-pill-content"><span>哥特</span></div></div>'
            '<div class="multi-select-pill"><div class="multi-select-pill-content"><span>夜巡</span></div></div>'
            '</div></div></div>')
    return ('<div class="metadata-container" tabindex="-1" data-property-count="3">'
            '<div class="metadata-properties-heading" tabindex="0">'
            f'<div class="collapse-indicator collapse-icon">{CHEV}</div><div class="metadata-properties-title">笔记属性</div></div>'
            f'<div class="metadata-content"><div class="metadata-properties">{prop("类型", "手记")}{prop("作者", "守夜人")}{tags}</div></div></div>')


PUSHER = '<div style="width: 1px; height: 0.1px; margin-bottom: 0px;"></div>'


def sidebar_left():
    """Obsidian 1.14 文件列表：.nav-files-container > div(根，无 mod-root 文件夹) > .tree-item…；
    文件夹恒可折叠，折叠图标是 .tree-item-icon.collapse-icon(无 nav-folder-collapse-indicator)，is-collapsed 同时挂在 .tree-item 和图标上"""
    def folder(name, kids, open_=True):
        c = "" if open_ else " is-collapsed"
        return (f'<div class="tree-item nav-folder{c}"><div class="tree-item-self nav-folder-title is-clickable mod-collapsible">'
                f'<div class="tree-item-icon collapse-icon{c}">{CHEV}</div>'
                f'<div class="tree-item-inner nav-folder-title-content">{name}</div></div>'
                + (f'<div class="tree-item-children nav-folder-children">{PUSHER}{kids}</div>' if open_ else "") + '</div>')

    def file(name, active=False, tag=""):
        # data-path 带扩展名(真 Obsidian 是库内完整路径，主题按 $=".png" 之类认文件类型)
        return (f'<div class="tree-item nav-file"><div class="tree-item-self nav-file-title tappable is-clickable{" is-active" if active else ""}"'
                f' data-path="{name}.{tag or "md"}">'
                f'<div class="tree-item-inner nav-file-title-content">{name}</div>'
                + (f'<div class="nav-file-tag">{tag}</div>' if tag else "") + '</div></div>')
    tree = (folder("Archive", "", False) +
            folder("Assets", file("dresden-moonlight", tag="jpg") + file("night-storm", tag="jpg")) +
            folder("Codex", folder("Districts", "".join(file(n) for n in ("East Gate", "North Street", "东门", "北街")))
                   + file("The Bell Tower") + file("钟楼")) +
            folder("Journal", "", False) + folder("Templates", "", False) +
            file("The Night Watch") + file("夜巡手记", active=True))
    nav = nav_header(["edit", "folder-plus", "arrow-up-narrow-wide", "gallery-vertical", "chevrons-up-down", "search"], hidden=(5,), search_box=True)
    return ('<div class="workspace-leaf-content" data-type="file-explorer">' + nav +
            '<div class="nav-files-container node-insert-event" style="position: relative;">'
            f'<div>{PUSHER}{tree}</div></div></div>')


OUTLINE = [("一、永夜之城", [
               ("钟楼", [("灯火的规矩", [("守夜人的装备", [("附注：钟楼的蝙蝠", [("六级标题", [])])])])]),
               ("雷暴季", [])]),
           ("二、档案", [("抄本与代码", []), ("公式", []), ("巡夜路线", []), ("月下的城", []), ("嵌入另一篇笔记", [])])]


def sidebar_right():
    """Obsidian 1.14 大纲：.view-content(滚动容器，内联 position: relative) > div(根) > .tree-item >
    .tree-item-self(有子级时 .mod-collapsible + 折叠图标) + .tree-item-children；当前标题是 .tree-item-self.is-active"""
    def item(title, kids, active):
        col = " mod-collapsible" if kids else ""
        icon = f'<div class="tree-item-icon collapse-icon">{CHEV}</div>' if kids else ""
        sub = (f'<div class="tree-item-children">{PUSHER}' + "".join(item(t, k, active) for t, k in kids) + "</div>") if kids else ""
        return (f'<div class="tree-item"><div class="tree-item-self is-clickable{col}{" is-active" if title == active else ""}">'
                f'{icon}<div class="tree-item-inner">{title}</div></div>{sub}</div>')
    body = "".join(item(t, k, "钟楼") for t, k in OUTLINE)
    nav = nav_header(["search", "gallery-vertical", "chevrons-down-up"], search_box=True)
    return ('<div class="workspace-leaf-content" data-type="outline">' + nav + '<div class="view-header"><div class="view-header-title-container">'
            '<div class="view-header-title">大纲</div></div></div><div class="view-content node-insert-event" style="position: relative;">'
            f'<div>{PUSHER}{body}</div></div></div>')


# 侧栏标签只显示图标(app.css：.mod-primary-split/.mod-secondary-split 里标题 display: var(--sidebar-tab-text-display) = none)
LUCIDE = {
    "folder-closed": '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "bookmark": '<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>',
    "list": '<path d="M3 12h18M3 6h18M3 18h18"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "tags": '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r=".5"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "git-fork": '<circle cx="12" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><path d="M18 9v2c0 .6-.4 1-1 1H7c-.6 0-1-.4-1-1V9M12 12v3"/>',
    # 文件列表 / 大纲顶上按钮行(nav-header)的图标
    "edit": '<path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"/>',
    "folder-plus": '<path d="M12 10v6M9 13h6"/><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
    "arrow-up-narrow-wide": '<path d="m3 8 4-4 4 4M7 4v16M11 12h4M11 16h7M11 20h10"/>',
    "gallery-vertical": '<path d="M3 2h18M3 22h18"/><rect width="18" height="12" x="3" y="6" rx="2"/>',
    "chevrons-up-down": '<path d="m7 15 5 5 5-5M7 9l5-5 5 5"/>',
    "chevrons-down-up": '<path d="m7 20 5-5 5 5M7 4l5 5 5-5"/>',
    # 功能栏(ribbon)常见按钮：关系图谱 / 白板 / 日记 / 模板 / 随机笔记 / 命令面板
    "layout-dashboard": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "file-plus": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M9 15h6M12 18v-6"/>',
    "dices": '<rect width="12" height="12" x="2" y="10" rx="2" ry="2"/><path d="m17.92 14 3.5-3.5a2.24 2.24 0 0 0 0-3l-5-4.92a2.24 2.24 0 0 0-3 0L10 6M6 18h.01M10 14h.01M15 6h.01M18 9h.01"/>',
    "terminal": '<path d="m4 17 6-6-6-6M12 19h8"/>',
    # 左栏底部仓库栏
    "chevrons-up-down-s": '<path d="m7 15 5 5 5-5M7 9l5-5 5 5"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3M12 17h.01"/>',
    # 标签关闭 / 新标签 / 正文顶栏前进后退 / 阅读切换 / 更多 / 属性类型(照 1.14 app.js 的 LM(…) 图标名)
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "arrow-left": '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "book-open": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "more-vertical": '<circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/>',
    "text": '<path d="M17 6.1H3"/><path d="M21 12.1H3"/><path d="M15.1 18H3"/>',
    "settings": '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
}


def vault_profile(name="demo-vault"):
    """1.14 左栏底部仓库栏(app.js zO 类)：左栏 containerEl 里的 .workspace-sidedock-vault-profile(order: 1 排在所有标签组后面)
    > .workspace-drawer-vault-switcher(切换图标 + 仓库名) + .workspace-drawer-vault-actions(帮助 / 设置两个 span.clickable-icon)"""
    return ('<div class="workspace-sidedock-vault-profile"><div class="workspace-drawer-vault-switcher">'
            f'<div class="workspace-drawer-vault-switcher-icon">{lucide("chevrons-up-down-s")}</div>'
            f'<div class="workspace-drawer-vault-name">{name}</div></div><div class="workspace-drawer-vault-actions">'
            f'<span class="clickable-icon">{lucide("help")}</span><span class="clickable-icon">{lucide("settings")}</span></div></div>')


def nav_header(icons, hidden=(), search_box=False):
    """1.14 的 nav-header(app.js QL 类)：.nav-header > .nav-buttons-container > .clickable-icon.nav-action-button；
    addSearchButton 还会在 .nav-header 里追加一个默认 display: none 的 .search-input-container(点搜索按钮才显示)；
    文件列表的搜索按钮本身被 hide()"""
    hide = ' style="display: none;"'
    btns = "".join(f'<div class="clickable-icon nav-action-button"{hide if i in hidden else ""}>{lucide(n)}</div>'
                   for i, n in enumerate(icons))
    box = ('<div class="search-input-container" style="display: none;"><input enterkeyhint="search" type="search" spellcheck="false" '
           'placeholder="输入以开始搜索..."><div class="search-input-clear-button"></div></div>') if search_box else ""
    return f'<div class="nav-header"><div class="nav-buttons-container">{btns}</div>{box}</div>'


def lucide(name):
    return (f'<svg class="svg-icon lucide-{name}" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{LUCIDE[name]}</svg>')


def tab_header(titles, active=0, icons=None, types=None):
    """types = 每个标签的 data-type(视图类型)；app.css 按它藏掉主区笔记 / 空标签的图标"""
    tabs = "".join(
        f'<div class="workspace-tab-header tappable{" is-active mod-active" if i == active else ""}" draggable="true"'
        f'{f" data-type={chr(34)}{types[i]}{chr(34)}" if types else ""}>'
        f'<div class="workspace-tab-header-inner"><div class="workspace-tab-header-inner-icon">{lucide(icons[i]) if icons else lucide("file")}</div>'
        f'<div class="workspace-tab-header-inner-title">{t}</div><div class="workspace-tab-header-status-container"></div>'
        f'<div class="workspace-tab-header-inner-close-button">{lucide("x")}</div></div></div>' for i, t in enumerate(titles))
    return (f'<div class="workspace-tab-header-container"><div class="workspace-tab-header-container-inner">{tabs}</div>'
            f'<div class="workspace-tab-header-new-tab"><span class="clickable-icon">{lucide("plus")}</span></div><div class="workspace-tab-header-spacer"></div></div>')


def side_group(tabs, active, content, top="", grow=50):
    """侧栏里的一个标签组(.workspace-tabs)：tabs = [(标题, lucide 图标名)]；top = mod-top 类(顶上那组才有)。
    1.14 每个工作区元素(app.js UO 类)构造时就在自己的 containerEl 里建一根 hr.workspace-leaf-resize-handle(第一个子元素，
    子元素之后才加进来；所以分栏里最后一个标签组是 :last-child，它那根被 display: none)：
    标签组的那根贴着它自己的底边(.workspace-split.mod-horizontal > * > …)，最后一组的被 display: none"""
    return (f'<div class="workspace-tabs{top}" style="flex-grow: {grow};">{tab_header([t for t, _ in tabs], active, [i for _, i in tabs])}'
            f'<div class="workspace-tab-container"><div class="workspace-leaf">{content}</div></div>'
            '<hr class="workspace-leaf-resize-handle tappable"></div>')


def placeholder_leaf(kind, text):
    return (f'<div class="workspace-leaf-content" data-type="{kind}"><div class="view-content" '
            f'style="display:flex;align-items:center;justify-content:center;color:var(--text-faint);font-size:12px">{text}</div></div>')


# Windows「隐藏框架」(用户 obsidian.json frame: hidden)：窗口按钮浮在右上角，压在右侧栏顶上那组的标签栏上
TITLEBAR_SVG = {
    "minimize": '<rect fill="currentColor" width="10" height="1" x="1" y="6"></rect>',
    "maximize": '<rect width="9" height="9" x="1.5" y="1.5" fill="none" stroke="currentColor"></rect>',
    "close": ('<path fill="currentColor" fill-rule="evenodd" d="M10.052 10.968 1.03 1.93l.849-.848 9.023 9.037-.849.848Z"/>'
              '<path fill="currentColor" fill-rule="evenodd" d="M1.023 10.112 10.06 1.09l.848.85-9.037 9.023-.848-.85Z"/>'),
}
TITLEBAR = ('<div class="titlebar"><div class="titlebar-inner"><div class="titlebar-button-container mod-left"></div>'
            '<div class="titlebar-button-container mod-right">'
            + "".join(f'<div class="titlebar-button mod-{k}"><svg width="12" height="12" viewBox="0 0 12 12">{v}</svg></div>'
                      for k, v in TITLEBAR_SVG.items()) +
            '</div></div></div>')
# 功能栏左上角侧栏开关的图标(app.js 里的 sidebar-toggle-button-icon)
SIDEBAR_TOGGLE = ('<svg class="svg-icon sidebar-toggle-button-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
                  'stroke-width="2"><rect x="1" y="2" width="22" height="20" rx="4" pathLength="100" class="sidebar-toggle-icon-outer"/>'
                  '<rect x="4" y="5" width="2" height="14" rx="2" fill="currentColor" class="sidebar-toggle-icon-inner"/></svg>')


def view_header(title, parents=()):
    crumbs = "".join(f'<span class="view-header-breadcrumb">{p}</span><span class="view-header-breadcrumb-separator">/</span>'
                     for p in parents)
    return ('<div class="view-header"><div class="view-header-left"><div class="view-header-nav-buttons">'
            f'<button class="clickable-icon">{lucide("arrow-left")}</button><button class="clickable-icon">{lucide("arrow-right")}</button></div></div>'
            f'<div class="view-header-title-container mod-at-start"><div class="view-header-title-parent">{crumbs}</div>'
            f'<div class="view-header-title" tabindex="-1">{title}</div></div>'
            f'<div class="view-actions"><button class="clickable-icon view-action">{lucide("book-open")}</button>'
            f'<button class="clickable-icon view-action">{lucide("more-vertical")}</button></div></div>')


def page(main_leaf, theme=True, overlay="", left=None, right=None, body_cls=""):
    """theme: True=本主题, False=只用 app.css, Path=指定其他主题 css(性能对比用)；overlay = 叠在最上层的弹窗 HTML；
    left / right = 换掉左右栏里的标签组(side_group 拼好的 HTML，README 截图用)；body_cls = 额外的 body 类(模拟 Style Settings 选项)"""
    if left is None:
        left = (side_group([("文件列表", "folder-closed"), ("搜索", "search"), ("书签", "bookmark")], 0, sidebar_left(), " mod-top mod-top-left-space", 78)
                + side_group([("关系图谱", "git-fork")], 0, placeholder_leaf("localgraph", "局部关系图谱"), "", 22))
    if right is None:
        right = (side_group([("日历", "calendar"), ("书签", "bookmark")], 0, placeholder_leaf("calendar", "日历"), " mod-top mod-top-right-space", 26)
                 + side_group([("大纲", "list"), ("反向链接", "link"), ("标签", "tags")], 0, sidebar_right(), "", 74))
    css = f'<link rel="stylesheet" href="{APP_CSS.as_uri()}">'
    if theme is True:
        css += f'<link rel="stylesheet" href="{THEME_CSS.as_uri()}">'
    elif theme:
        css += f'<link rel="stylesheet" href="{Path(theme).as_uri()}">'
    # 1.14：左上角的侧栏开关按钮在功能栏里(绝对定位到功能栏上方的角块)；body 要有 show-ribbon，否则功能栏 display: none
    # 类名照 1.14 app.js：功能栏只有 mod-primary(left→primary)，开关按钮两个都有(mod-primary mod-left)
    ribbon = ('<div class="workspace-ribbon side-dock-ribbon mod-primary">'
              f'<div class="sidebar-toggle-button mod-primary mod-left"><div class="clickable-icon">{SIDEBAR_TOGGLE}</div></div><div class="side-dock-actions">'
              + "".join(f'<div class="clickable-icon side-dock-ribbon-action">{lucide(n)}</div>'
                        for n in ("git-fork", "layout-dashboard", "calendar", "file-plus", "dices", "terminal")) + "</div></div>")
    return f'''<!doctype html><html><head><meta charset="utf-8">{css}
<style>html,body{{height:100%;margin:0}} .app-container{{height:100vh}} /* CodeMirror 6 base theme (normally injected at runtime) */ .cm-editor{{position:relative;display:flex;flex-direction:column;height:100%}} .cm-scroller{{display:flex;align-items:flex-start;overflow:auto;height:100%;position:relative}} .cm-content{{margin:0;flex-grow:2;flex-shrink:0;display:block;white-space:pre;word-wrap:normal;box-sizing:border-box;min-height:100%;padding:4px 0;outline:none}} .cm-lineWrapping{{white-space:pre-wrap;white-space:break-spaces;word-break:break-word;overflow-wrap:anywhere;flex-shrink:1}} .cm-line{{display:block;padding:0 2px 0 6px}}</style></head>
<body class="mod-windows is-frameless is-hidden-frameless obsidian-app theme-dark show-inline-title show-view-header show-ribbon is-focused styled-scrollbars{(" " + body_cls) if body_cls else ""}">
<div class="app-container">{TITLEBAR}<div class="horizontal-main-container">
<div class="workspace is-left-sidedock-open is-right-sidedock-open">
{ribbon}
<div class="workspace-split mod-horizontal mod-sidedock mod-primary-split mod-left-split" style="width:270px">
 <hr class="workspace-leaf-resize-handle tappable">
 {vault_profile()}
 {left}</div>
<div class="workspace-split mod-vertical mod-root">
 <hr class="workspace-leaf-resize-handle tappable">
 <div class="workspace-tabs mod-top mod-active">{tab_header(["夜巡手记", "The Night Watch", "新标签页"], 0, types=["markdown", "markdown", "empty"])}
  <div class="workspace-tab-container"><div class="workspace-leaf mod-active">{main_leaf}</div></div></div></div>
<div class="workspace-split mod-horizontal mod-sidedock mod-secondary-split mod-right-split" style="width:260px">
 <hr class="workspace-leaf-resize-handle tappable">
 {right}</div>
</div></div>{overlay}</div>{TREE_INDENT_JS}</body></html>'''


def reading_leaf():
    return (f'<div class="workspace-leaf-content" data-type="markdown" data-mode="preview">{view_header("夜巡手记")}'
            '<div class="view-content"><div class="markdown-reading-view" style="width:100%;height:100%">'
            '<div class="markdown-preview-view markdown-rendered node-insert-event is-readable-line-width allow-fold-headings show-indentation-guide allow-fold-lists show-properties" tabindex="-1">'
            '<div class="markdown-preview-sizer markdown-preview-section">'
            '<div class="markdown-preview-pusher" style="width:1px;height:0.1px;margin-bottom:0px"></div>'
            f'<div class="mod-header mod-ui"><div class="inline-title" contenteditable="true" spellcheck="false" tabindex="-1">{TITLE}</div>'
            f'{properties()}</div>{reading_body()}<div class="mod-footer mod-ui"></div></div></div></div></div></div>')


def live_leaf():
    return (f'<div class="workspace-leaf-content" data-type="markdown" data-mode="source">{view_header("夜巡手记")}'
            '<div class="view-content"><div class="markdown-source-view cm-s-obsidian mod-cm6 node-insert-event is-readable-line-width is-live-preview is-folding show-properties">'
            '<div class="cm-editor"><div class="cm-scroller"><div class="cm-sizer">'
            f'<div class="inline-title" contenteditable="true" spellcheck="false" tabindex="-1">{TITLE}</div>'
            f'{properties()}<div class="cm-contentContainer"><div class="cm-content cm-lineWrapping" contenteditable="true" role="textbox">'
            f'{live_body()}</div></div></div></div></div></div></div></div>{HANGING_INDENT_JS}')


# Obsidian 的树(文件列表/大纲，虚拟列表 uO.update)运行时给每个 .tree-item-self 写内联 !important：
#   margin-inline-start: -c; padding-inline-start: c + 原 padding，c = 该项离滚动容器内容左缘的距离
# 也就是把每一行拉伸到面板最左边(悬停底色铺满)，文字靠加大的 padding 留在原位。
# 所以「按 .tree-item-self 左缘定位」的东西在深层会全挤到最左边——图标要跟着文字起点定位。
TREE_INDENT_JS = """<script>
window.nlTreeIndent = () => {
  for (const sc of document.querySelectorAll('.nav-files-container, [data-type="outline"] > .view-content')) {
    const r = parseFloat(getComputedStyle(sc).paddingInlineStart) || 0, sl = sc.getBoundingClientRect().left;
    const selves = [...sc.querySelectorAll('.tree-item-self')];
    for (const s of selves) { s.style.removeProperty('margin-inline-start'); s.style.removeProperty('padding-inline-start'); }
    const m = selves.map(s => [s, s.parentElement.getBoundingClientRect().left - sl - r, parseFloat(getComputedStyle(s).paddingInlineStart)]);
    for (const [s, c, pad] of m) {
      if (!c) continue;
      s.style.setProperty('margin-inline-start', -c + 'px', 'important');
      s.style.setProperty('padding-inline-start', (c + pad) + 'px', 'important');
    }
  }
};
document.fonts.ready.then(() => window.nlTreeIndent());
</script>"""

# Obsidian 运行时给列表行加悬挂缩进：量出行首标记(缩进+符号+空格)的宽度 K，写 text-indent:-K; padding-inline-start:K
HANGING_INDENT_JS = """<script>
document.fonts.ready.then(() => {
  for (const ln of document.querySelectorAll('.cm-line.HyperMD-list-line')) {
    const mk = ln.querySelector('.cm-formatting-list');
    if (!mk) continue;
    ln.style.textIndent = ''; ln.style.paddingInlineStart = '';
    const k = Math.floor(mk.getBoundingClientRect().right - ln.getBoundingClientRect().left);
    ln.style.textIndent = -k + 'px'; ln.style.paddingInlineStart = k + 'px';
  }
});
</script>"""


# 弹窗类：命令面板(.prompt)、悬浮预览(.popover.hover-popover)、设置(.modal.mod-settings)——结构照 1.14 app.js
def prompt_overlay():
    items = ["切换左侧边栏", "切换右侧边栏", "切换阅读视图与编辑视图", "切换折叠状态", "切换粗体", "切换斜体"]
    res = "".join(f'<div class="suggestion-item mod-complex{" is-selected" if i == 0 else ""}"><div class="suggestion-content">'
                  f'<div class="suggestion-title">{t}</div></div><div class="suggestion-aux"></div></div>' for i, t in enumerate(items))
    return ('<div class="modal-container mod-dim"><div class="modal-bg" style="opacity: 0.85;"></div><div class="prompt">'
            '<div class="prompt-input-container mod-raised"><input class="prompt-input" type="text" placeholder="输入命令…" value="切换">'
            '<div class="prompt-input-cta"></div><div class="search-input-clear-button"></div></div>'
            f'<div class="prompt-results">{res}</div><div class="prompt-instructions">'
            + "".join(f'<div class="prompt-instruction"><span class="prompt-instruction-command">{k}</span><span>{v}</span></div>'
                      for k, v in (("↑↓", "选择"), ("↵", "执行"), ("esc", "关闭"))) + '</div></div></div>')


def popover():
    return ('<div class="popover hover-popover" style="top: 300px; left: 560px; width: 420px; height: 230px;">'
            '<div class="markdown-embed is-loaded"><div class="markdown-embed-content"><div class="markdown-preview-view markdown-rendered">'
            '<div class="markdown-preview-sizer markdown-preview-section"><div class="el-h2"><h2>钟声 · The Toll</h2></div>'
            '<div class="el-p"><p>钟楼每到整点敲钟，敲过十三下，城门关闭。雷暴之夜，钟声会被雷声盖过，守夜人便改用铁哨联络。</p></div>'
            '</div></div></div></div></div>')


def settings_overlay():
    nav = "".join(f'<div class="vertical-tab-nav-item tappable{" is-active" if n == "外观" else ""}">{n}</div>'
                  for n in ("关于", "编辑器", "文件与链接", "外观", "快捷键", "核心插件", "第三方插件"))
    rows = "".join(f'<div class="setting-item"><div class="setting-item-info"><div class="setting-item-name">{a}</div>'
                   f'<div class="setting-item-description">{b}</div></div><div class="setting-item-control">'
                   '<div class="checkbox-container is-enabled"><input type="checkbox" tabindex="0"></div></div></div>'
                   for a, b in (("Dark Deco 卡片框", "侧栏、弹窗的铜色线框与阶梯角花"), ("闪电纹", "文件列表底部的分叉闪电"),
                                ("暗角", "烛光照不到的四角")))
    return ('<div class="modal-container mod-dim"><div class="modal-bg" style="opacity: 0.85;"></div>'
            '<div class="modal mod-settings mod-sidebar-layout"><div class="modal-close-button mod-raised clickable-icon">'
            f'{lucide("x")}</div><div class="modal-header"><div class="modal-title"></div></div>'
            '<div class="modal-content vertical-tabs-container"><div class="vertical-tab-header">'
            '<div class="vertical-tab-header-group-container"><div class="vertical-tab-header-group">'
            f'<div class="vertical-tab-header-group-title">选项</div><div class="vertical-tab-header-group-items">{nav}</div></div></div></div>'
            f'<div class="vertical-tab-content-container"><div class="vertical-tab-content">{rows}</div></div></div></div></div>')


def empty_leaf():
    return ('<div class="workspace-leaf-content" data-type="empty"><div class="view-header"><div class="view-header-title-container">'
            '<div class="view-header-title">新标签页</div></div></div><div class="view-content"><div class="empty-state"><div class="empty-state-container">'
            '<div class="empty-state-title">没有打开的文件</div><div class="empty-state-action-list">'
            '<div class="empty-state-action tappable mod-close">新建笔记 (Ctrl + N)</div>'
            '<div class="empty-state-action tappable">打开文件 (Ctrl + O)</div>'
            '<div class="empty-state-action tappable">查看近期文件 (Ctrl + O)</div>'
            '<div class="empty-state-action tappable mod-close">关闭标签页</div></div></div></div></div></div>')


def ensure_public():
    """app.css 引用的 public/images、public/fonts(外链图标、复选框勾等)从本机 Obsidian 安装包 asar 里抽到 preview/public/"""
    import json
    import os
    import re
    import struct
    want = sorted(set(re.findall(r"url\((public/[^)]+)\)", APP_CSS.read_text(encoding="utf-8"))))
    if all((OUT / w).exists() for w in want):
        return
    asars = sorted((Path(os.environ.get("APPDATA", "")) / "obsidian").glob("obsidian-*.asar"))
    if not asars:
        print("没找到 Obsidian asar，跳过 public/ 资源")
        return
    with open(asars[-1], "rb") as f:
        _, hsize, _, jlen = struct.unpack("<4I", f.read(16))
        header = json.loads(f.read(jlen))
        for w in want:
            node = header
            for part in w.split("/"):
                node = node["files"][part]
            f.seek(8 + hsize + int(node["offset"]))
            (OUT / w).parent.mkdir(parents=True, exist_ok=True)
            (OUT / w).write_bytes(f.read(node["size"]))


if __name__ == "__main__":
    ensure_public()
    (OUT / "reading.html").write_text(page(reading_leaf()), encoding="utf-8")
    (OUT / "live.html").write_text(page(live_leaf()), encoding="utf-8")
    (OUT / "empty.html").write_text(page(empty_leaf()), encoding="utf-8")
    (OUT / "modal.html").write_text(page(reading_leaf(), overlay=prompt_overlay()), encoding="utf-8")
    (OUT / "popover.html").write_text(page(reading_leaf(), overlay=popover()), encoding="utf-8")
    (OUT / "settings.html").write_text(page(reading_leaf(), overlay=settings_overlay()), encoding="utf-8")
    (OUT / "reading_default.html").write_text(page(reading_leaf(), theme=False), encoding="utf-8")
    # 性能对比用长文档：正文重复 12 遍
    long_read = reading_leaf().replace(reading_body(), reading_body() * 12)
    long_live = live_leaf().replace(live_body(), live_body() * 12)
    paperk = Path(r"C:\Users\DELL\Documents\Obsidian Vault\.obsidian\themes\PaperK\theme.css")
    for tag, th in (("nl", True), ("default", False), ("paperk", paperk)):
        (OUT / f"long_read_{tag}.html").write_text(page(long_read, theme=th), encoding="utf-8")
        (OUT / f"long_live_{tag}.html").write_text(page(long_live, theme=th), encoding="utf-8")
    print("harness ok")
