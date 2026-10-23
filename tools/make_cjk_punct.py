# -*- coding: utf-8 -*-
"""从本机 Noto Serif SC 可变字体抽出中西文共用码位的标点(“”…—·)，做成内嵌小字体。
目的：这些码位在 EB Garamond 里也有字形，浏览器会优先用西文字形 →
中文引号变窄、…… 贴底、—— 断开、人名间的 · 贴字。放在字体栈最前面强制走中文字形。
(‘’ 故意不收：英文撇号 don’t 要保持西文字形)
用法: python tools/make_cjk_punct.py
"""
import sys
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
SRC = r"C:\Windows\Fonts\NotoSerifSC-VF.ttf"
CHARS = [0x201C, 0x201D, 0x2026, 0x2014, 0x2015, 0x2E3A, 0x00B7]

opts = subset.Options()
opts.flavor = "woff2"
opts.layout_features = ["*"]
opts.name_IDs = ["*"]
opts.notdef_outline = False
font = TTFont(SRC)
cmap = font.getBestCmap()
hmtx = font["hmtx"]
for c in CHARS:
    g = cmap.get(c)
    print(f"U+{c:04X} {chr(c)} glyph={g} advance={hmtx[g][0] if g else None}")
sub = subset.Subsetter(opts)
sub.populate(unicodes=CHARS)
sub.subset(font)
dst = ROOT / "fonts" / "NLCJKPunct-VF.woff2"
font.flavor = "woff2"
font.save(dst)
print(dst, dst.stat().st_size, "bytes")
