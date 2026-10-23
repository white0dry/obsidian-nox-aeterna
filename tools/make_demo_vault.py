# -*- coding: utf-8 -*-
"""示例库 demo-vault/：给 README 截图用(真 Obsidian 打开这个文件夹当库)，内容全是虚构的示例笔记。
笔记本身(.md)和配图直接放在 demo-vault/ 里。配图是维基共享资源上的公有领域油画：
  Assets/dresden-moonlight.jpg  J. C. Dahl《月光下的德累斯顿》1839
    https://commons.wikimedia.org/wiki/File:Johan_Christian_Clausen_Dahl,_Blick_auf_Dresden_bei_Vollmondschein.jpg
  Assets/night-storm.jpg        A.-L.-R. Ducros《切法卢的夜间风暴》约 1800–1805
    https://commons.wikimedia.org/wiki/File:Louis_Ducros,_Night_Storm_at_Cefal%C3%B9,_ca.1800-1805.jpg
这个脚本负责：
  1. 写 .obsidian 配置(暗色、启用本主题和 Style Settings、核心插件、书签、日记文件夹)
  2. 复制主题(仓库根目录的 theme.css)和 Style Settings、Calendar 两个插件(从主库复制，不带 data.json = 全部默认值)
用法: python build.py 之后  python tools/make_demo_vault.py
"""
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "demo-vault"
MAIN_VAULT = Path(r"C:\Users\DELL\Documents\Obsidian Vault")
THEME = "Nox Aeterna"


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ob = DEMO / ".obsidian"
    write_json(ob / "appearance.json", {"cssTheme": THEME, "theme": "obsidian", "showRibbon": True, "nativeMenus": False})
    write_json(ob / "app.json", {"showInlineTitle": True, "propertiesInDocument": "visible", "defaultViewMode": "preview",
                                 "attachmentFolderPath": "Assets", "foldHeading": True, "readableLineLength": True})
    write_json(ob / "core-plugins.json", {
        "file-explorer": True, "global-search": True, "switcher": True, "graph": True, "backlink": True, "canvas": True,
        "outgoing-link": True, "tag-pane": True, "footnotes": True, "properties": True, "page-preview": True,
        "daily-notes": True, "templates": True, "note-composer": True, "command-palette": True, "editor-status": True,
        "bookmarks": True, "outline": True, "word-count": True, "file-recovery": True, "bases": True, "sync": False})
    write_json(ob / "daily-notes.json", {"folder": "Journal", "format": "YYYY-MM-DD", "template": "Templates/日记模板"})
    write_json(ob / "templates.json", {"folder": "Templates"})
    write_json(ob / "bookmarks.json", {"items": [
        {"type": "file", "ctime": 1761100000000, "path": "夜巡手记.md"},
        {"type": "file", "ctime": 1761100000001, "path": "The Night Watch.md"},
        {"type": "file", "ctime": 1761100000002, "path": "Codex/钟楼.md"},
        {"type": "file", "ctime": 1761100000003, "path": "Codex/The Bell Tower.md"}]})
    write_json(ob / "community-plugins.json", ["obsidian-style-settings", "calendar"])

    theme_dst = ob / "themes" / THEME
    theme_dst.mkdir(parents=True, exist_ok=True)
    for f in ("theme.css", "manifest.json"):
        shutil.copy2(ROOT / f, theme_dst / f)
    for plugin in ("obsidian-style-settings", "calendar"):     # 右上角放日历(Calendar 插件)
        src = MAIN_VAULT / ".obsidian" / "plugins" / plugin
        dst = ob / "plugins" / plugin
        dst.mkdir(parents=True, exist_ok=True)
        for f in ("main.js", "manifest.json", "styles.css"):   # 不带 data.json：示例库里的选项都是默认值
            if (src / f).exists():
                shutil.copy2(src / f, dst / f)
    print("demo vault ->", DEMO)


if __name__ == "__main__":
    main()
