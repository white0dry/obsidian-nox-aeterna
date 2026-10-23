# -*- coding: utf-8 -*-
"""量 src/icons/callout/*.svg 里图案的实际外框(浏览器 getBBox)，写 bbox.json，
ornaments.callout_glyph 用它取正方形 viewBox，让每个剪影在图标位里居中(game-icons 原图常偏一边)。
加新图标后重跑: python tools/icon_bbox.py
"""
import json
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
DIR = Path(__file__).resolve().parent.parent / "src" / "icons" / "callout"
out = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    for f in sorted(DIR.glob("*.svg")):
        src = f.read_text(encoding="utf-8")
        vb = re.search(r'viewBox="([^"]+)"', src).group(1)
        ds = re.findall(r'<path[^>]*\sd="([^"]+)"', src)
        pg.set_content(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><g id="g">'
                       + "".join(f'<path d="{d}"/>' for d in ds) + "</g></svg>")
        bb = pg.evaluate("() => { const r = document.getElementById('g').getBBox(); return [r.x, r.y, r.width, r.height]; }")
        # 视觉重心(按面积加权)：爪痕这类一头粗一头细的图案，外框居中了看着仍偏，要按重心居中
        cxy = pg.evaluate("""([vb, ds]) => new Promise(res => {
            const [x0, y0, w, h] = vb.split(/[ ,]+/).map(Number), N = 256;
            const c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d');
            g.setTransform(N / w, 0, 0, N / h, -x0 * N / w, -y0 * N / h);
            for (const d of ds) g.fill(new Path2D(d));
            const a = g.getImageData(0, 0, N, N).data; let s = 0, sx = 0, sy = 0;
            for (let i = 0; i < N * N; i++) { const v = a[i * 4 + 3]; s += v; sx += v * (i % N); sy += v * Math.floor(i / N); }
            res([x0 + (sx / s + .5) * w / N, y0 + (sy / s + .5) * h / N]); })""", [vb, ds])
        out[f.stem] = [round(v, 2) for v in bb] + [round(v, 2) for v in cxy]
        print(f"{f.stem:22s} bbox {out[f.stem][:4]}  centroid {out[f.stem][4:]}")
    b.close()
(DIR / "bbox.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
