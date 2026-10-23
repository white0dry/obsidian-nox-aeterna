# -*- coding: utf-8 -*-
"""把 SVG(纹理/闪电纹)在构建时预渲染成 WebP 位图。
原因：feTurbulence 等 SVG 滤镜作为 CSS 背景时，Chromium 每次重绘都会重新计算整片噪声，
滚动时就是逐帧重算(实测帧耗时 10.9ms/P95 40ms，关掉纹理后 2.9ms)。位图只解码一次。
结果按内容哈希缓存在 assets/cache/，SVG 不变就不重渲。
"""
import hashlib
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "assets" / "cache"


def render_webp(svg: str, width: int, height: int, scale: float = 1.0, quality: int = 78,
                lossless: bool = False) -> bytes:
    key = hashlib.sha1(f"{svg}|{width}|{height}|{scale}|{quality}|{lossless}".encode()).hexdigest()[:16]
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{key}.webp"
    if out.exists():
        return out.read_bytes()
    from PIL import Image
    from playwright.sync_api import sync_playwright
    html = (f'<html><body style="margin:0;background:transparent">'
            f'<div style="width:{width}px;height:{height}px;background:url(\'data:image/svg+xml;base64,'
            f'{__import__("base64").b64encode(svg.encode()).decode()}\') 0 0/{width}px {height}px no-repeat"></div>'
            f'</body></html>')
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": height}, device_scale_factor=scale)
        pg.set_content(html)
        pg.wait_for_timeout(300)
        png = pg.screenshot(omit_background=True, clip=dict(x=0, y=0, width=width, height=height))
        b.close()
    im = Image.open(io.BytesIO(png)).convert("RGBA")
    buf = io.BytesIO()
    if lossless:
        im.save(buf, "WEBP", lossless=True, method=6)
    else:
        im.save(buf, "WEBP", quality=quality, alpha_quality=quality, method=6)
    out.write_bytes(buf.getvalue())
    return out.read_bytes()
