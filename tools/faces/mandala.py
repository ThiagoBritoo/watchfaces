"""Watchface "Mandala": 12 pétalas (as horas), a pétala da hora acesa, um ponto brilhante que orbita pelos minutos e outro pelos segundos. Hora
pequena no centro. Cinco paletas. Original."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, grad_radial, polar, reduzir_por, tela
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, strings_opcoes, tint, tpl, colar

NOME = "mandala"
PALETAS = [("aurora", "#ff6bb5 #5ee6ff #fff2a8"), ("brasa", "#ff8a3d #ffd166 #ffffff"), ("oceano", "#4dd2ff #7b8cff #c8fff0"), ("floresta", "#6bff9c #d4ff6b #ffffff"), ("uva", "#b18cff #ff7ac8 #ffe9a8")]
R0, R1 = 128, 226
BEAD = 40


def petala(angulo: float, n: int, r0: float, r1: float, larg: float) -> list[tuple[float, float]]:
    pts = []
    for i in range(61):
        t = i / 60
        r = r0 + (r1 - r0) * t
        w = larg * math.sin(math.pi * t ** 0.8) ** 1.0
        pts.append((r, w))
    out = []
    for r, w in pts:
        a = math.degrees(math.atan2(w, r))
        out.append(polar(C * n, C * n, r * n, angulo + a))
    for r, w in reversed(pts):
        a = math.degrees(math.atan2(w, r))
        out.append(polar(C * n, C * n, r * n, angulo - a))
    return out


def petalas_base() -> Image.Image:
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(12):
        pts = petala(k * 30, s, R0, R1, 38)
        d.polygon(pts, outline=(255, 255, 255, 255), fill=(255, 255, 255, 46))
    return im.resize((W, W), Image.LANCZOS)


def petala_hora() -> Image.Image:
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon(petala(0, s, R0, R1, 38), fill=(255, 255, 255, 235), outline=(255, 255, 255, 255))
    return im.resize((W, W), Image.LANCZOS)


def conta() -> Image.Image:
    return grad_radial(BEAD, BEAD / 2, BEAD / 2, [(0, (255, 255, 255, 255)), (5, (255, 255, 255, 255)), (9, (255, 255, 255, 140)), (BEAD / 2, (255, 255, 255, 0))])


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    p = lambda i: f"[CONFIGURATION.paleta.{i}]"  # noqa: E731
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + img(0, 0, W, W, "petalas", f' tintColor="{p(0)}" alpha="150"'))
    a(f'      <Group name="hora" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="floor([HOUR_0_11_MINUTE]) * 30" />' + img(0, 0, W, W, "petala_hora", f' tintColor="{p(0)}"') + "</Group>")
    for nome, r, ci, expr in (("min", 104, 1, "([MINUTE] + [SECOND] / 60) * 6"), ("seg", 84, 2, "[SECOND] * 6")):
        a(f'      <Group name="{nome}" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="{expr}" />' + img(C - BEAD // 2, C - r - BEAD // 2, BEAD, BEAD, "conta", f' tintColor="{p(ci)}"') + "</Group>")
    a("      " + hora(110, 196, 260, 70, "hh:mm", 56, "#ffffffff", "LIGHT", "CENTER"))
    a("      " + tpl(130, 256, 220, 24, 17, "#ccffffff", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + img(0, 0, W, W, "petalas", ' alpha="80"'))
    a("      " + hora(110, 200, 260, 70, "hh:mm", 56, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, paleta: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c0, c1, c2 = (rgb(c) for c in paleta.split())
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        pb = A["petalas"].copy()
        r, g, b, al = pb.split()
        base.alpha_composite(Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * 80 / 255)))))
        ImageDraw.Draw(base).text((C, 235), f"{h:02d}:{mi:02d}", font=fonte("Light", 56), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    pb = tint(A["petalas"], c0)
    r, g, b, al = pb.split()
    base.alpha_composite(Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * 150 / 255)))))
    base.alpha_composite(tint(A["petala_hora"], c0).rotate(-(h % 12) * 30, center=(C, C), resample=Image.BICUBIC))
    for r_, ang, cor in ((104, (mi + s / 60) * 6, c1), (84, s * 6, c2)):
        x, y = polar(C, C, r_, ang)
        base.alpha_composite(tint(A["conta"], cor), (int(x - BEAD / 2), int(y - BEAD / 2)))
    d = ImageDraw.Draw(base)
    d.text((C, 231), f"{h:02d}:{mi:02d}", font=fonte("Light", 56), fill=(255, 255, 255), anchor="mm")
    d.text((C, 268), "SEX 31", font=fonte("Medium", 17), fill=(204, 204, 204), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Mandala", "paleta_label": "Palette"}
    pt = {"watch_face_name": "Mandala", "paleta_label": "Paleta"}
    strings_opcoes(en, pt, "paleta", {"aurora": ("Aurora", "Aurora"), "brasa": ("Ember", "Brasa"), "oceano": ("Ocean", "Oceano"), "floresta": ("Forest", "Floresta"), "uva": ("Grape", "Uva")})
    A = {"petalas": petalas_base(), "petala_hora": petala_hora(), "conta": conta()}
    pv = [previa(A, PALETAS[0][1], 10, 8, 20), previa(A, PALETAS[1][1], 3, 45, 40), previa(A, PALETAS[2][1], 7, 22, 5), previa(A, PALETAS[4][1], 12, 55, 50), previa(A, PALETAS[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Aurora", "Brasa", "Oceano", "Uva", "Ambiente (AOD)"], cols=5, nomes_previa=["aurora", "brasa", "oceano", "uva", "ambiente"])
