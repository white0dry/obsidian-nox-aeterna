# -*- coding: utf-8 -*-
"""滚动时的绘制诊断：录 Chrome trace，统计 Paint / RasterTask / 合成层情况。
用法: python tools/trace.py preview/long_read_nl.html [...] [--gpu] [--dpr=1.25]
滚动期间 Paint 次数≈滚动帧数 = 没走合成器滚动(每帧重绘)；只有个位数 = 合成器滚动。
--dpr 很重要：Chromium 在 DPR<1.5 时保 LCD 次像素文字，透明滚动容器不会走合成器滚动；
本机 Windows 缩放 125% = DPR 1.25。
"""
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright

files = [a for a in sys.argv[1:] if not a.startswith("--")]
gpu = "--gpu" in sys.argv
dpr = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--dpr=")), "1")
args = [f"--force-device-scale-factor={dpr}"] + (["--enable-lcd-text"] if "--lcd" in sys.argv else [])
if gpu:
    args += ["--enable-gpu", "--use-angle=d3d11", "--ignore-gpu-blocklist", "--enable-gpu-rasterization"]
JS = """async () => {
  const el = document.querySelector('.workspace-split.mod-root .markdown-preview-view') ||
             document.querySelector('.workspace-split.mod-root .cm-scroller');
  el.scrollTop = 0; await new Promise(r => setTimeout(r, 300));
  await new Promise(res => { let n = 0; (function f(){ el.scrollTop += 45; if (++n < 120) requestAnimationFrame(f); else res(); })(); });
}"""
with sync_playwright() as p:
    b = p.chromium.launch(args=args)
    for html in files:
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(Path(html).resolve().as_uri())
        pg.wait_for_timeout(1500)
        out = Path(tempfile.gettempdir()) / "nl_trace.json"
        b.start_tracing(page=pg, path=str(out), categories=["devtools.timeline", "disabled-by-default-devtools.timeline", "cc", "blink"])
        pg.evaluate(JS)
        b.stop_tracing()
        ev = json.loads(out.read_text(encoding="utf-8"))
        ev = ev["traceEvents"] if isinstance(ev, dict) else ev
        dur, cnt = Counter(), Counter()
        area, full = 0.0, 0
        for e in ev:
            if e.get("ph") == "X" and e.get("name") in ("Paint", "RasterTask", "UpdateLayerTree", "Layout",
                                                           "PrePaint", "Layerize", "ImageDecodeTask", "Commit",
                                                           "ScrollLayer", "CompositeLayers", "ScheduleStyleRecalculation"):
                dur[e["name"]] += e.get("dur", 0) / 1000
                cnt[e["name"]] += 1
            if e.get("name") == "Paint" and e.get("ph") == "X":
                c = e.get("args", {}).get("data", {}).get("clip")
                if c:
                    w, h = max(c[0::2]) - min(c[0::2]), max(c[1::2]) - min(c[1::2])
                    area += w * h
                    full += w >= 1000 and h <= 1300  # 视口大小的重绘 = 逐帧整屏重绘(主线程滚动)
        print(Path(html).name, "gpu" if gpu else "sw", f"dpr={dpr}",
              f"| repaint area {area / 1e6:.0f} Mpx, viewport-sized paints {full}")
        for k in sorted(dur, key=lambda k: -dur[k]):
            print(f"   {k:18s} n={cnt[k]:5d}  total={dur[k]:8.1f}ms")
        pg.close()
    b.close()
