"""Watchface "Espiral": uma espiral de Arquimedes com 6 voltas representa as 12 horas; um ponto brilhante percorre a espiral (do centro para fora) e
mostra o horário. Sem ponteiros. Cinco cores. Original."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, colar, cor_config, finalizar, grupo, hora, img, redondo, rgb, textos_acento, tint, tpl

NOME = "espiral"
R0, R1 = 34, 214
VOLTAS = 6
BOLA = 44


def ponto(t: float) -> tuple[float, float]:
    r = R0 + (R1 - R0) * t
    a = t * VOLTAS * 2 * math.pi
    return C + r * math.sin(a), C - r * math.cos(a)


def trilho() -> Image.Image:
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(ponto(t)[0] * s, ponto(t)[1] * s) for t in np.linspace(0, 1, 1400)]
    d.line(pts, fill=(255, 255, 255, 120), width=int(2.4 * s), joint="curve")
    for h in range(13):                                   # marcas das horas sobre a espiral
        x, y = ponto(h / 12)
        d.ellipse([(x - 4) * s, (y - 4) * s, (x + 4) * s, (y + 4) * s], fill=(255, 255, 255, 255))
    return im.resize((W, W), Image.LANCZOS)


def bola() -> Image.Image:
    return grad_radial(BOLA, BOLA / 2, BOLA / 2, [(0, (255, 255, 255, 255)), (7, (255, 255, 255, 255)), (11, (255, 255, 255, 150)), (BOLA / 2, (255, 255, 255, 0))])


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    t = "([HOUR_0_11_MINUTE] / 12)"
    r = f"({R0} + {R1 - R0} * {t})"
    ang = f"({t} * {VOLTAS * 2 * math.pi:.5f})"
    a("    " + grupo("vivo", "", 0))
    a("      " + img(0, 0, W, W, "trilho", f' tintColor="{ac}"'))
    a("      " + img(C - BOLA // 2, C - BOLA // 2, BOLA, BOLA, "bola", f' tintColor="{ac}"', f'<Transform target="x" value="{C - BOLA // 2} + {r} * sin({ang})" /><Transform target="y" value="{C - BOLA // 2} - {r} * cos({ang})" />'))
    a("      " + hora(110, 196, 260, 80, "hh:mm", 64, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(130, 262, 220, 24, 17, "#ffa0a0a8", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + img(0, 0, W, W, "trilho", ' alpha="80"'))
    a("      " + hora(110, 200, 260, 80, "hh:mm", 60, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    tr = A["trilho"]
    if ambiente_:
        r, g, b, al = tr.split()
        base.alpha_composite(Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * 80 / 255)))))
        ImageDraw.Draw(base).text((C, 240), f"{h:02d}:{mi:02d}", font=fonte("Light", 60), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    base.alpha_composite(tint(tr, ac))
    t = (h % 12 + mi / 60) / 12
    x, y = ponto(t)
    colar(base, tint(A["bola"], ac), int(x - BOLA / 2), int(y - BOLA / 2))
    d = ImageDraw.Draw(base)
    d.text((C, 236), f"{h:02d}:{mi:02d}", font=fonte("Bold", 64), fill=(255, 255, 255), anchor="mm")
    d.text((C, 274), "SEX 31", font=fonte("Medium", 17), fill=(160, 160, 168), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Spiral", "Espiral")
    A = {"trilho": trilho(), "bola": bola()}
    pv = [previa(A, "#f2c14e", 10, 8), previa(A, "#33d6ff", 3, 45), previa(A, "#ff5c93", 7, 22), previa(A, "#f2c14e", 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["10:08", "03:45", "07:22", "Ambiente (AOD)"], cols=4, nomes_previa=["h10", "h03", "h07", "ambiente"])
