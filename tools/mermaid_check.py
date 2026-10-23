# -*- coding: utf-8 -*-
"""Mermaid 配色检查：在 demo-vault 新标签里打开临时笔记 _mt/mermaid.md(内容 = tools/mermaid_test.md，13 种图)，
加高视口截下每张图，拼成总览 preview/mermaid_check.png。准备同 obsidian_shots.py(带调试端口启动 Obsidian、打开示例库)。
用法: python tools/mermaid_check.py [--css 测试样式.css] [--only 0,1,2] [--out 文件名] [--dump]
      python tools/mermaid_check.py --cleanup      # 看完关掉标签、删掉临时笔记、清出最近文件列表
--css 把样式注入页面(不用重建主题就能试)；--dump 把每张图里各类元素的计算颜色写到 preview/mermaid_dump.json"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "preview"
args = sys.argv[1:]
sys.path.insert(0, str(HERE))
sys.argv = sys.argv[:1]
import obsidian_shots as S  # noqa: E402
from PIL import Image  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default


MD = (HERE / "mermaid_test.md").read_text(encoding="utf-8")
PATH = "_mt/mermaid.md"

OPEN = """async ([path, md]) => {
  const w = app.workspace;
  if (!app.vault.getAbstractFileByPath('_mt')) await app.vault.createFolder('_mt');
  let f = app.vault.getAbstractFileByPath(path);
  if (!f) f = await app.vault.create(path, md); else await app.vault.modify(f, md);
  let leaf = w.getLeavesOfType('markdown').find(l => l.view.file?.path === path);
  if (!leaf) { window.__mtPrev = w.getMostRecentLeaf(); leaf = w.getLeaf('tab'); await leaf.openFile(f, {state: {mode: 'preview'}}); }
  w.setActiveLeaf(leaf, {focus: true});
  const st = leaf.getViewState();
  if (st.state.mode !== 'preview') { st.state.mode = 'preview'; await leaf.setViewState(st); }
  leaf.view.previewMode.rerender(true);
  await new Promise(r => setTimeout(r, 2500));
  leaf.view.previewMode.applyScroll(0);
  return 'ok';
}"""

CLEANUP = """async (path) => {
  const w = app.workspace;
  w.getLeavesOfType('markdown').filter(l => l.view.file?.path === path).forEach(l => l.detach());
  const f = app.vault.getAbstractFileByPath('_mt');
  if (f) await app.vault.delete(f, true);
  const t = w.recentFileTracker; if (t?.lastOpenFiles) t.lastOpenFiles = t.lastOpenFiles.filter(p => !p.startsWith('_mt'));
  if (window.__mtPrev) w.setActiveLeaf(window.__mtPrev, {focus: true});
  document.getElementById('nl-mt')?.remove();
  await w.saveLayout();
  return w.getLastOpenFiles();
}"""

BOXES = """() => [...document.querySelectorAll('.workspace-leaf.mod-active .markdown-reading-view .mermaid')].map(m => {
  const r = m.getBoundingClientRect(); const s = m.querySelector('svg');
  return [r.x, r.y, r.width, r.height, s?.getAttribute('aria-roledescription') || '?'];
})"""

DUMP = r"""() => [...document.querySelectorAll('.workspace-leaf.mod-active .markdown-reading-view .mermaid > svg')].map(s => {
  const seen = {};
  for (const e of s.querySelectorAll('*')) {
    const c = e.getAttribute('class'); const k = e.tagName + (c ? '.' + c.trim().split(/\s+/).join('.') : '');
    if (seen[k]) continue;
    const cs = getComputedStyle(e);
    seen[k] = [cs.fill, cs.stroke, ['text', 'tspan', 'SPAN', 'P'].includes(e.tagName) ? cs.color : '',
               e.getAttribute('fill') || '', e.getAttribute('style') || ''].join(' | ');
  }
  return [s.getAttribute('aria-roledescription'), seen];
})"""

with sync_playwright() as p:
    o = S.Obs(p)
    if "--cleanup" in args:
        o.normal()
        print(o.js(CLEANUP, PATH))
        sys.exit()
    css = opt("--css")
    o.js("(c) => { let e = document.getElementById('nl-mt'); if (!c) { e?.remove(); return; }"
         " if (!e) { e = document.createElement('style'); e.id = 'nl-mt'; document.head.append(e); } e.textContent = c; }",
         Path(css).read_text(encoding="utf-8") if css else None)
    o.tall(9000)                        # 阅读视图是虚拟列表，视口加高才会把所有图都渲染出来
    o.js(OPEN, [PATH, MD])
    o.rest()
    o.pg.wait_for_timeout(2500)
    OUT.mkdir(exist_ok=True)
    if "--dump" in args:
        (OUT / "mermaid_dump.json").write_text(json.dumps(o.js(DUMP), ensure_ascii=False, indent=1), encoding="utf-8")
    only = [int(i) for i in opt("--only", "").split(",") if i != ""]
    for _ in range(10):                 # 版面还在变(图陆续渲染、虚拟列表重算高度)就等它稳定
        boxes = o.js(BOXES)
        full = o.grab()
        if o.js(BOXES) == boxes:
            break
        o.pg.wait_for_timeout(1000)
    tiles = []
    for i, b in enumerate(boxes):
        if only and i not in only:
            continue
        print(i, b[4], [round(v) for v in b[:4]])
        tiles.append(o.crop(full, (b[0] - 12, b[1] - 12, b[2] + 24, b[3] + 24)))
    o.normal()
    cols = 2 if len(tiles) > 2 else len(tiles)
    cw = max(t.width for t in tiles)
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    H = sum(max(t.height for t in r) + 8 for r in rows)
    sheet = Image.new("RGB", (cw * cols + 8 * (cols - 1), H), (40, 0, 0))
    y = 0
    for r in rows:
        for c, t in enumerate(r):
            sheet.paste(t, (c * (cw + 8), y))
        y += max(t.height for t in r) + 8
    out = OUT / (opt("--out", "mermaid_check") + ".png")
    sheet.save(out)
    print(out, sheet.size)
