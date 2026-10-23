# -*- coding: utf-8 -*-
"""用 Playwright(Chromium) 截图本地 html。
用法: python tools/shoot.py <html> <png> [宽 高] [--scale=1] [--full]
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

args = [a for a in sys.argv[1:] if not a.startswith("--")]
opts = dict(a[2:].split("=", 1) if "=" in a else (a[2:], "1") for a in sys.argv[1:] if a.startswith("--"))
html, png = Path(args[0]).resolve(), Path(args[1]).resolve()
w, h = (int(args[2]), int(args[3])) if len(args) >= 4 else (1400, 900)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=float(opts.get("scale", 1)))
    pg.goto(html.as_uri())
    pg.wait_for_timeout(int(opts.get("wait", 600)))
    pg.evaluate("document.fonts.ready")
    clip = None
    if "clip" in opts:
        x, y, cw, ch = (float(v) for v in opts["clip"].split(","))
        clip = dict(x=x, y=y, width=cw, height=ch)
    pg.screenshot(path=str(png), full_page="full" in opts, clip=clip)
    b.close()
print(png)
