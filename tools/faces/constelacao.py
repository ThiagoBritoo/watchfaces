"""Watchface "Constelação": um céu estrelado com dois anéis de estrelas (12 horas e 60 minutos). A estrela da hora e a do minuto
brilham e giram, ligadas ao centro por linhas finas, como numa constelação. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial, polar
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, strings_opcoes, tint, tpl

NOME = "constelacao"
PALETAS = [("polar", "#ffffff #8fc8ff #cfe6ff"), ("nebulosa", "#ff8fd0 #6ee7ff #ffd0ec"), ("ouro", "#ffd36e #ffffff #ffe9b0"), ("jade", "#8dffc4 #e8fff4 #b6ffe0")]
RH, RM = 118, 188
ESTR = 72


def fundo() -> Image.Image:
    rng = np.random.default_rng(21)
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(150):
        x, y = rng.integers(12, W - 12), rng.integers(12, W - 12)
        if (x - C) ** 2 + (y - C) ** 2 > 228 ** 2:
            continue
        r = float(rng.choice([0.7, 1.0, 1.0, 1.6]))
        d.ellipse([(x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s], fill=(255, 255, 255, int(rng.integers(60, 190))))
    for k in range(12):                                  # anel das horas
        x, y = polar(C * s, C * s, RH * s, k * 30)
        r = (4.2 if k % 3 == 0 else 2.6) * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 235 if k % 3 == 0 else 160))
    for k in range(60):                                  # anel dos minutos
        x, y = polar(C * s, C * s, RM * s, k * 6)
        r = (3.0 if k % 5 == 0 else 1.5) * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 220 if k % 5 == 0 else 120))
    return im.resize((W, W), Image.LANCZOS)


def estrela() -> Image.Image:
    return grad_radial(ESTR, ESTR / 2, ESTR / 2, [(0, (255, 255, 255, 255)), (5, (255, 255, 255, 255)), (9, (255, 255, 255, 140)), (ESTR / 2, (255, 255, 255, 0))])


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME) + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("ceu", "", 0) + f'<PartImage {full}><Image resource="fundo" /></PartImage></Group>')
    a("    " + grupo("fundo_amb", ' alpha="0"', 255) + f'<PartImage {full}><Image resource="fundo" /></PartImage></Group>')

    def astro(nome, r, ci, expr, amb=False):
        cor = f"[CONFIGURATION.paleta.{ci}]"
        linha = f'<PartDraw x="{C - 1}" y="{C - r}" width="2" height="{r}"><Rectangle x="0" y="0" width="2" height="{r}"><Fill color="{cor}" /></Rectangle></PartDraw>'
        estr = f'<PartImage x="{C - ESTR // 2}" y="{C - r - ESTR // 2}" width="{ESTR}" height="{ESTR}" tintColor="{cor}"><Image resource="estrela" /></PartImage>'
        return (f'<Group name="{nome}" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="{expr}" />'
                f'{"" if amb else linha.replace("<Fill", "<Fill").replace(chr(34) + "[", chr(34) + "[")}{estr}</Group>')

    hexpr, mexpr = "[HOUR_0_11_MINUTE] * 30", "([MINUTE] + [SECOND] / 60) * 6"
    a("    " + grupo("astros", "", 0))
    a("      " + astro("hora", RH, 0, hexpr))
    a("      " + astro("min", RM, 1, mexpr))
    a(f'      <Group name="seg" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="[SECOND] * 6" />'
      f'<PartImage x="{C - 14}" y="{C - 222 - 14}" width="28" height="28" tintColor="[CONFIGURATION.paleta.2]"><Image resource="estrela" /></PartImage></Group>')
    a("      " + tpl(140, 340, 200, 28, 20, "#ff9aa0aa", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("astros_amb", ' alpha="0"', 255))
    a("      " + astro("hora_a", RH, 0, hexpr, True))
    a("      " + astro("min_a", RM, 1, mexpr, True))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, paleta: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    cs = [rgb(c) for c in paleta.split()]
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    base.alpha_composite(A["fundo"])
    d = ImageDraw.Draw(base)
    for r, ang, cor in ((RH, (h % 12 + mi / 60) * 30, cs[0]), (RM, (mi + s / 60) * 6, cs[1])):
        x, y = polar(C, C, r, ang)
        if not ambiente_:
            d.line([(C, C), (x, y)], fill=cor + (255,), width=2)
        base.alpha_composite(tint(A["estrela"], cor), (int(x - ESTR / 2), int(y - ESTR / 2)))
    if not ambiente_:
        x, y = polar(C, C, 222, s * 6)
        e = tint(A["estrela"].resize((28, 28), Image.LANCZOS), cs[2])
        base.alpha_composite(e, (int(x - 14), int(y - 14)))
        ImageDraw.Draw(base).text((C, 354), "SEX 31", font=fonte("Medium", 20), fill=(154, 160, 170), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Constellation", "paleta_label": "Stars"}
    pt = {"watch_face_name": "Constelação", "paleta_label": "Estrelas"}
    strings_opcoes(en, pt, "paleta", {"polar": ("Polar", "Polar"), "nebulosa": ("Nebula", "Nebulosa"), "ouro": ("Gold", "Ouro"), "jade": ("Jade", "Jade")})
    A = {"fundo": fundo(), "estrela": estrela()}
    pv = [previa(A, PALETAS[0][1], 10, 8, 32), previa(A, PALETAS[1][1], 4, 47, 10), previa(A, PALETAS[2][1], 8, 22, 50), previa(A, PALETAS[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Polar", "Nebulosa", "Ouro", "Ambiente (AOD)"], cols=4, nomes_previa=["polar", "nebulosa", "ouro", "ambiente"])
