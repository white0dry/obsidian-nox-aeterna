# -*- coding: utf-8 -*-
"""下载主题用的 OFL 字体(Google Fonts woff2 分片)，存到 fonts/，并记录 unicode-range。
用法: python tools/fetch_fonts.py
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fonts"
OUT.mkdir(exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# family 查询串 -> 要保留的子集
FAMILIES = {
    "EB+Garamond:ital,wght@0,400..800;1,400..800": {"latin", "latin-ext", "greek", "greek-ext"},
    "Cinzel:wght@400..900": {"latin", "latin-ext"},
    "Manufacturing+Consent": {"latin"},
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=60).read()


faces = []
for fam, subsets in FAMILIES.items():
    css = get(f"https://fonts.googleapis.com/css2?family={fam}&display=swap").decode("utf-8")
    for m in re.finditer(r"/\* ([a-z-]+) \*/\s*@font-face \{(.*?)\}", css, re.S):
        subset, body = m.group(1), m.group(2)
        if subset not in subsets:
            continue
        family = re.search(r"font-family: '([^']+)'", body).group(1)
        style = re.search(r"font-style: (\w+)", body).group(1)
        weight = re.search(r"font-weight: ([\d ]+);", body).group(1).strip()
        url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
        urange = re.search(r"unicode-range: ([^;]+);", body).group(1).strip()
        fname = f"{family.replace(' ', '')}-{style}-{weight.replace(' ', '_')}-{subset}.woff2"
        data = get(url)
        (OUT / fname).write_bytes(data)
        faces.append(dict(family=family, style=style, weight=weight, subset=subset,
                          file=fname, unicode_range=urange, bytes=len(data)))
        print(f"{fname:60s} {len(data)//1024:4d} KB")

(OUT / "faces.json").write_text(json.dumps(faces, ensure_ascii=False, indent=1), encoding="utf-8")
print("total", sum(f["bytes"] for f in faces) // 1024, "KB,", len(faces), "faces")
