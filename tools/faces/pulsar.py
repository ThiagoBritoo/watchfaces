"""Watchface "Pulsar": linhas onduladas empilhadas (como o sinal de um pulsar), com a hora grande em cima; a linha do minuto atual é destacada na cor
de destaque e um anel mostra os segundos. Abstrata. Original."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, textos_acento, tint, tpl, colar

NOME = "pulsar"
NL = 30
Y0, DY = 128, 9.8
X0, X1 = 64, 416


def perfil(i: int, x: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(100 + i)
    env = np.exp(-(((x - C) / 62.0) ** 2))
    ru = rng.normal(0, 1, x.shape)
    ru = np.convolve(ru, np.ones(5) / 5, mode="same")
    return env * (14 + 22 * np.abs(ru) * 1.6) * (0.55 + 0.45 * math.sin(i * 1.7) ** 2)


def linhas(destaque: int | None = None) -> Image.Image:
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    xs = np.arange(X0, X1 + 1, 1.0)
    for i in range(NL):
        y0 = Y0 + i * DY
        ys = y0 - perfil(i, xs)
        pts = [(float(x * s), float(y * s)) for x, y in zip(xs, ys)]
        # preenchimento preto sob a linha para esconder as de trás
        d.polygon(pts + [(X1 * s, (y0 + 6) * s), (X0 * s, (y0 + 6) * s)], fill=(0, 0, 0, 255))
        d.line(pts, fill=(255, 255, 255, 255), width=int(2.6 * s), joint="curve")
    return im.resize((W, W), Image.LANCZOS)


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + img(0, 0, W, W, "linhas", ' alpha="235"'))
    a(f'      <PartDraw {full}><Arc centerX="{C}" centerY="{C}" width="470" height="470" startAngle="0" endAngle="0"><Stroke thickness="5" color="{ac}" cap="ROUND" /><Transform target="endAngle" value="[SECOND] * 6" /></Arc></PartDraw>')
    a("      " + hora(60, 20, 360, 90, "hh:mm", 72, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(110, 414, 260, 26, 18, ac, "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + img(0, 0, W, W, "linhas", ' alpha="110"'))
    a("      " + hora(60, 20, 360, 90, "hh:mm", 64, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    ln = A["linhas"].copy()
    r, g, b, al = ln.split()
    ln = Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * (110 if ambiente_ else 235) / 255))))
    base.alpha_composite(ln)
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 65), f"{h:02d}:{mi:02d}", font=fonte("Light", 64), fill=(192, 192, 200), anchor="mm")
    else:
        d.arc([5, 5, W - 5, W - 5], -90, -90 + s * 6, fill=ac, width=5)
        d.text((C, 65), f"{h:02d}:{mi:02d}", font=fonte("Bold", 72), fill=(255, 255, 255), anchor="mm")
        d.text((C, 427), "SEX 31 OUT", font=fonte("Medium", 18), fill=ac, anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Pulsar", "Pulsar")
    A = {"linhas": linhas()}
    pv = [previa(A, "#ff7a2f", 10, 8, 20), previa(A, "#33d6ff", 21, 45, 50), previa(A, "#ff5c93", 3, 12, 5), previa(A, "#ff7a2f", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Laranja", "Ciano", "Rosa", "Ambiente (AOD)"], cols=4, nomes_previa=["laranja", "ciano", "rosa", "ambiente"])
