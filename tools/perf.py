# -*- coding: utf-8 -*-
"""滚动性能对比：在长文档预览页里逐帧滚动，统计帧耗时。
用法: python tools/perf.py preview/long_read_nl.html [preview/long_read_paperk.html ...] [--gpu] [--dpr=1.25]
输出每页: 平均帧间隔 / P95 / 超过 33ms 的长帧占比；以及 Chrome 的 Paint/Raster 耗时(trace)
"""
import json
import statistics
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

SCROLLER = ".markdown-preview-view, .cm-scroller"
JS = """async (sel) => {
  const el = document.querySelector('.workspace-split.mod-root ' + sel.split(',')[0]) ||
             document.querySelector('.workspace-split.mod-root ' + sel.split(',')[1].trim());
  el.scrollTop = 0;
  await new Promise(r => setTimeout(r, 300));
  const t = [];
  return await new Promise(resolve => {
    let n = 0;
    function step(ts) {
      t.push(ts);
      el.scrollTop += 45;
      if (++n < 240) requestAnimationFrame(step);
      else resolve(t.slice(1).map((v, i) => v - t[i]));
    }
    requestAnimationFrame(step);
  });
}"""

with sync_playwright() as p:
    gpu = ["--enable-gpu", "--use-angle=d3d11", "--ignore-gpu-blocklist", "--enable-gpu-rasterization"]
    dpr = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--dpr=")), "1")
    b = p.chromium.launch(args=[f"--force-device-scale-factor={dpr}", "--disable-gpu-vsync",
                                "--disable-frame-rate-limit"] + (gpu if "--gpu" in sys.argv else []))
    for html in [a for a in sys.argv[1:] if not a.startswith("--")]:
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(Path(html).resolve().as_uri())
        pg.wait_for_timeout(1500)
        cdp = pg.context.new_cdp_session(pg)
        cdp.send("Performance.enable")
        m0 = {m["name"]: m["value"] for m in cdp.send("Performance.getMetrics")["metrics"]}
        runs = []
        for _ in range(2):
            runs += pg.evaluate(JS, SCROLLER)
        m1 = {m["name"]: m["value"] for m in cdp.send("Performance.getMetrics")["metrics"]}
        runs.sort()
        avg = statistics.mean(runs)
        p95 = runs[int(len(runs) * 0.95)]
        slow = sum(1 for v in runs if v > 33.4) / len(runs) * 100
        d = lambda k: (m1.get(k, 0) - m0.get(k, 0)) * 1000
        print(f"{Path(html).name:28s} frame avg {avg:6.1f}ms  p95 {p95:6.1f}ms  >33ms {slow:5.1f}%  "
              f"layout {d('LayoutDuration'):7.0f}ms  recalc {d('RecalcStyleDuration'):6.0f}ms  script {d('ScriptDuration'):6.0f}ms")
        pg.close()
    b.close()
