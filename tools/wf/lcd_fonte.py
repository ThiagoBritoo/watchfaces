"""Dígitos de 7 segmentos (LCD) em PNG branco com segmentos apagados em baixa opacidade (efeito fantasma de LCD)."""
from __future__ import annotations

from PIL import Image, ImageDraw

SEGS = {"0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def _seg(d, nome, x0, y0, w, h, e, cor):
    m = h / 2
    t = e / 2
    if nome in "adg":
        y = {"a": y0, "g": y0 + m - t, "d": y0 + h - e}[nome]
        pts = [(x0 + t, y + t), (x0 + e, y), (x0 + w - e, y), (x0 + w - t, y + t), (x0 + w - e, y + e), (x0 + e, y + e)]
    else:
        x = x0 if nome in "fe" else x0 + w - e
        ya = y0 if nome in "fb" else y0 + m
        pts = [(x + t, ya + t), (x + e, ya + e), (x + e, ya + m - e + t * 0.5), (x + t, ya + m - t + t * 0.2), (x, ya + m - e + t * 0.5), (x, ya + e)]
    d.polygon(pts, fill=cor)


def digito(ch: str, w: int, h: int, e: int, pad: int, fantasma: float = 0.09) -> Image.Image:
    s = 4
    W_, H_ = (w + 2 * pad) * s, (h + 2 * pad) * s
    luz = Image.new("L", (W_, H_), 0)
    apg = Image.new("L", (W_, H_), 0)
    dl, da = ImageDraw.Draw(luz), ImageDraw.Draw(apg)
    ativos = SEGS.get(ch, "")
    for n in "abcdefg":
        _seg(dl if n in ativos else da, n, pad * s, pad * s, w * s, h * s, e * s, 255)
    if ch == ":":
        for yy in (h * 0.3, h * 0.7):
            dl.rectangle([(pad + w / 2 - e / 2) * s, (pad + yy - e / 2) * s, (pad + w / 2 + e / 2) * s, (pad + yy + e / 2) * s], fill=255)
    luz = luz.resize((W_ // s, H_ // s), Image.LANCZOS)
    apg = apg.resize((W_ // s, H_ // s), Image.LANCZOS)
    from PIL import ImageChops
    a = ImageChops.lighter(luz, apg.point(lambda v: int(v * fantasma)))
    out = Image.new("RGBA", a.size, (255, 255, 255, 0))
    out.putalpha(a)
    return out
