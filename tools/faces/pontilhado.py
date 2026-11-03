"""Watchface "Pontilhado": 60 pontos em círculo; os segundos são um cometa de pontos acesos que gira, o minuto é um ponto grande de outra cor
e a hora vai grande no centro. Cinco paletas. Original."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte, polar
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rgb, strings_opcoes, tpl

NOME = "pontilhado"
PALETAS = [("coral", "#ff5a4d #ffd166"), ("ciano", "#33d6ff #ff5c93"), ("lima", "#b6f23a #3ad6ff"), ("violeta", "#a58bff #ffd166"), ("branco", "#ffffff #ff7a2f")]
R = 212
DOT = 12


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    p = lambda i: f"[CONFIGURATION.paleta.{i}]"  # noqa: E731
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    for j in range(60):
        x, y = polar(C, C, R, j * 6)
        tam = DOT if j % 5 == 0 else 7
        atras = f"(([SECOND] - {j} + 60) % 60)"
        a(f'      <PartDraw x="{round(x - tam / 2)}" y="{round(y - tam / 2)}" width="{tam}" height="{tam}"><Transform target="alpha" value="40 + 215 * clamp(1 - {atras} / 14, 0, 1)" />'
          f'<Ellipse x="0" y="0" width="{tam}" height="{tam}"><Fill color="{p(0)}" /></Ellipse></PartDraw>')
    a(f'      <Group name="min" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="([MINUTE] + [SECOND] / 60) * 6" />'
      f'<PartDraw x="{C - 11}" y="{C - R + 22 - 11}" width="22" height="22"><Ellipse x="0" y="0" width="22" height="22"><Fill color="{p(1)}" /></Ellipse></PartDraw></Group>')
    a("      " + hora(100, 130, 280, 200, "hh", 190, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(130, 318, 220, 26, 20, "#ff9aa0aa", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for j in range(0, 60, 5):
        x, y = polar(C, C, R, j * 6)
        a(f'      <PartDraw x="{round(x - 4)}" y="{round(y - 4)}" width="8" height="8"><Ellipse x="0" y="0" width="8" height="8"><Fill color="#99ffffff" /></Ellipse></PartDraw>')
    a("      " + hora(40, 160, 400, 120, "hh:mm", 100, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(paleta: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c0, c1 = (rgb(c) for c in paleta.split())
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        for j in range(0, 60, 5):
            x, y = polar(C, C, R, j * 6)
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(153, 153, 153))
        d.text((C, 220), f"{h:02d}:{mi:02d}", font=fonte("Light", 100), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    for j in range(60):
        x, y = polar(C, C, R, j * 6)
        tam = DOT if j % 5 == 0 else 7
        atras = (s - j + 60) % 60
        al = 40 + 215 * max(0, min(1, 1 - atras / 14))
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(cam).ellipse([x - tam / 2, y - tam / 2, x + tam / 2, y + tam / 2], fill=c0 + (int(al),))
        base.alpha_composite(cam)
    x, y = polar(C, C, R - 22, (mi + s / 60) * 6)
    d = ImageDraw.Draw(base)
    d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=c1)
    d.text((C, 232), f"{h:02d}", font=fonte("Bold", 190), fill=(255, 255, 255), anchor="mm")
    d.text((C, 331), "SEX 31", font=fonte("Medium", 20), fill=(154, 160, 170), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Dotted", "paleta_label": "Palette"}
    pt = {"watch_face_name": "Pontilhado", "paleta_label": "Paleta"}
    strings_opcoes(en, pt, "paleta", {"coral": ("Coral", "Coral"), "ciano": ("Cyan", "Ciano"), "lima": ("Lime", "Lima"), "violeta": ("Violet", "Violeta"), "branco": ("White", "Branco")})
    pv = [previa(PALETAS[0][1], 10, 8, 32), previa(PALETAS[1][1], 3, 45, 5), previa(PALETAS[2][1], 18, 22, 50), previa(PALETAS[3][1], 7, 15, 20), previa(PALETAS[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Coral", "Ciano", "Lima", "Violeta", "Ambiente (AOD)"], cols=5, nomes_previa=["coral", "ciano", "lima", "violeta", "ambiente"])
