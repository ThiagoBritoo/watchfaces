"""Watchface "Espectro": um arco-íris suave que desliza ao longo do dia (a cor do fundo muda com a hora), hora grande por cima.
Abstrata e vibrante. Original."""
from __future__ import annotations

import colorsys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, finalizar, grupo, hora, img, redondo, tpl

NOME = "espectro"
FAIXA = 2400


def faixa() -> Image.Image:
    xs = np.arange(FAIXA) / FAIXA
    cor = np.array([colorsys.hsv_to_rgb((x * 1.0) % 1, 0.72, 0.95) for x in xs], np.float32) * 255
    yy = np.linspace(0, 1, W)[:, None, None]
    img_ = cor[None, :, :] * (1 - 0.35 * yy ** 1.5) + 255 * 0.0
    img_ += np.random.default_rng(1).normal(0, 1.2, img_.shape)
    out = np.dstack([np.clip(img_, 0, 255), np.full((W, FAIXA), 255)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def xml() -> str:
    L = cabecalho(NOME, "DIGITAL") + ['  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + img(0, 0, FAIXA, W, "faixa", "", f'<Transform target="x" value="0 - [SECONDS_IN_DAY] / 86400 * {FAIXA - W}" />'))
    a("      " + hora(30, 150, 420, 140, "hh:mm", 120, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(110, 290, 260, 30, 22, "#ffffffff", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "SEMI_BOLD"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(30, 160, 420, 140, "hh:mm", 100, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 230), f"{h:02d}:{mi:02d}", font=fonte("Light", 100), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    off = int((h * 3600 + mi * 60) / 86400 * (FAIXA - W))
    base.alpha_composite(A["faixa"].crop((off, 0, off + W, W)))
    d = ImageDraw.Draw(base)
    d.text((C, 218), f"{h:02d}:{mi:02d}", font=fonte("Bold", 120), fill=(255, 255, 255), anchor="mm")
    d.text((C, 305), "SEX 31 OUT", font=fonte("SemiBold", 22), fill=(255, 255, 255), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Spectrum"}
    pt = {"watch_face_name": "Espectro"}
    A = {"faixa": faixa()}
    pv = [previa(A, h, 8) for h in (1, 7, 13, 19)] + [previa(A, 13, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["01:08", "07:08", "13:08", "19:08", "Ambiente (AOD)"], cols=5, nomes_previa=["h01", "h07", "h13", "h19", "ambiente"])
