"""Dígitos de tubo de neon (7 segmentos com ponta arredondada e brilho), em PNG branco."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SEGS = {"0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def digito(ch: str, w: int, h: int, esp: int, pad: int, brilho: float = 1.0) -> Image.Image:
    s = 4
    W_, H_ = (w + 2 * pad) * s, (h + 2 * pad) * s
    nucleo = Image.new("L", (W_, H_), 0)
    d = ImageDraw.Draw(nucleo)
    x0, y0 = pad * s, pad * s
    ww, hh = w * s, h * s
    e = esp * s
    pts = {"a": ((x0 + e, y0), (x0 + ww - e, y0)), "g": ((x0 + e, y0 + hh / 2), (x0 + ww - e, y0 + hh / 2)), "d": ((x0 + e, y0 + hh), (x0 + ww - e, y0 + hh)),
           "f": ((x0, y0 + e), (x0, y0 + hh / 2 - e)), "b": ((x0 + ww, y0 + e), (x0 + ww, y0 + hh / 2 - e)),
           "e": ((x0, y0 + hh / 2 + e), (x0, y0 + hh - e)), "c": ((x0 + ww, y0 + hh / 2 + e), (x0 + ww, y0 + hh - e))}
    if ch == ":":
        for yy in (hh * 0.32, hh * 0.68):
            d.ellipse([x0 + ww / 2 - e * 0.7, y0 + yy - e * 0.7, x0 + ww / 2 + e * 0.7, y0 + yy + e * 0.7], fill=255)
    for n in SEGS.get(ch, ""):
        d.line(pts[n], fill=255, width=int(e * 0.62))
        for p in pts[n]:
            r = e * 0.31
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)
    n_ = nucleo.resize((W_ // s, H_ // s), Image.LANCZOS)
    glow = n_.filter(ImageFilter.GaussianBlur(esp * 1.1)).point(lambda v: int(min(255, v * 0.95 * brilho)))
    glow2 = n_.filter(ImageFilter.GaussianBlur(esp * 0.45)).point(lambda v: int(min(255, v * 0.8 * brilho)))
    a = np.maximum(np.maximum(np.asarray(n_, np.float32), np.asarray(glow, np.float32) * 0.65), np.asarray(glow2, np.float32))
    out = np.zeros(a.shape + (4,), np.uint8)
    out[..., :3] = 255
    out[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")
