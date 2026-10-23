# -*- coding: utf-8 -*-
"""内嵌中文正文字体：从思源宋体可变字体(Noto Serif SC VF，Adobe，OFL 1.1，无保留字体名)
抽 GB2312 全部 6763 个汉字 + GB2312 符号区 + 常用标点/全角符号 + 战锤译文常用的几个 GB2312 外汉字，
保留全部字重(wght 200–900)，输出 woff2。
主题里注册为 "NL Noto Serif SC"(不用原名：同名 @font-face 会遮住用户本机装的完整版思源宋体)，
字体栈：本机思源宋体 → 内嵌子集 → 系统宋体。子集外的生僻字/繁体字由后两者兜底。
Obsidian 社区主题规定不能联网加载字体，所以只能内嵌。
用法: python tools/make_cjk_serif.py [源字体路径]
"""
import sys
import time
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Windows\Fonts\NotoSerifSC-VF.ttf")
DST = ROOT / "fonts" / "NLNotoSerifSC-GB2312-VF.woff2"
# GB2312 之外、简体战锤/奇幻译文里常见的字(祂=混沌诸神的代词)
EXTRA = "祂牠祇菈瞭祕"


def gb2312(lo, hi):
    out = set()
    for b1 in range(lo, hi + 1):
        for b2 in range(0xA1, 0xFF):
            try:
                out.add(ord(bytes([b1, b2]).decode("gb2312")))
            except UnicodeDecodeError:
                pass
    return out


chars = (gb2312(0xA1, 0xA9) | gb2312(0xB0, 0xF7) | set(map(ord, EXTRA))
         | set(range(0x2000, 0x2070)) | set(range(0x3000, 0x3040)) | set(range(0xFF00, 0xFFF0)))
t = time.time()
font = TTFont(SRC)
opts = subset.Options()
opts.flavor = "woff2"
opts.layout_features = ["kern", "locl", "vert", "vrt2"]
opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]
sub = subset.Subsetter(opts)
sub.populate(unicodes=chars)
sub.subset(font)
font.flavor = "woff2"
font.save(DST)
print(f"{DST}  {len(chars)} 码位  {DST.stat().st_size / 1048576:.2f} MB  ({time.time() - t:.0f}s)")
