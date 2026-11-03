"""Watchface "Prisma": um anel de cores em degradê cônico que gira (um passo por segundo, uma volta por minuto) em volta da hora grande. Três
conjuntos de cores. Original."""
from __future__ import annotations

import colorsys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grade
from wf.kit import C, W, cabecalho, finalizar, grupo, hora, img, redondo, strings_opcoes, tpl

NOME = "prisma"
R0, R1 = 148, 226
PALETAS = {"arcoiris": [(255, 60, 80), (255, 190, 40), (90, 230, 120), (50, 190, 255), (180, 90, 255), (255, 60, 80)],
           "quente": [(255, 30, 90), (255, 120, 20), (255, 215, 60), (255, 120, 20), (255, 30, 90)],
           "frio": [(0, 229, 255), (122, 92, 255), (255, 92, 225), (122, 92, 255), (0, 229, 255)]}


def anel(cores) -> Image.Image:
    xx, yy = grade(W)
    dx, dy = xx + 0.5 - C, yy + 0.5 - C
    r = np.hypot(dx, dy)
    th = (np.degrees(np.arctan2(dx, -dy)) % 360) / 360
    pos = np.linspace(0, 1, len(cores))
    cor = np.stack([np.interp(th, pos, [c[k] for c in cores]) for k in range(3)], -1)
    a = np.clip((R1 - r) / 1.3, 0, 1) * np.clip((r - R0) / 1.3, 0, 1)
    brilho = 0.82 + 0.18 * np.clip(1 - np.abs(r - (R0 + R1) / 2) / ((R1 - R0) / 2), 0, 1)
    out = np.dstack([np.clip(cor * brilho[..., None], 0, 255), a * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", '    <ListConfiguration id="cores" displayName="cores_label" defaultValue="arcoiris">'
                                       + "".join(f'<ListOption id="{k}" displayName="cores_{k}" />' for k in PALETAS) + "</ListConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0) + '<ListConfiguration id="cores">')
    for k in PALETAS:
        a(f'      <ListOption id="{k}"><Group name="c_{k}" {full}>' + img(0, 0, W, W, f"anel_{k}", ' pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="[SECOND] * 6" />') + "</Group></ListOption>")
    a("    </ListConfiguration>")
    a("      " + hora(60, 150, 360, 140, "hh:mm", 100, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(130, 270, 220, 28, 20, "#ffa0a0a8", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw {full}><Ellipse x="{C - R1}" y="{C - R1}" width="{2 * R1}" height="{2 * R1}"><Stroke thickness="2" color="#55ffffff" /></Ellipse></PartDraw>')
    a("      " + hora(60, 160, 360, 140, "hh:mm", 92, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, k: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.ellipse([C - R1, C - R1, C + R1, C + R1], outline=(85, 85, 85), width=2)
        d.text((C, 230), f"{h:02d}:{mi:02d}", font=fonte("Light", 92), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    base.alpha_composite(A[f"anel_{k}"].rotate(-s * 6, center=(C, C), resample=Image.BICUBIC))
    d = ImageDraw.Draw(base)
    d.text((C, 225), f"{h:02d}:{mi:02d}", font=fonte("Bold", 100), fill=(255, 255, 255), anchor="mm")
    d.text((C, 284), "SEX 31 OUT", font=fonte("Medium", 20), fill=(160, 160, 168), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Prism", "cores_label": "Colors", "cores_arcoiris": "Rainbow", "cores_quente": "Warm", "cores_frio": "Cool"}
    pt = {"watch_face_name": "Prisma", "cores_label": "Cores", "cores_arcoiris": "Arco-íris", "cores_quente": "Quentes", "cores_frio": "Frias"}
    A = {f"anel_{k}": anel(c) for k, c in PALETAS.items()}
    pv = [previa(A, "arcoiris", 10, 8, 5), previa(A, "quente", 3, 45, 20), previa(A, "frio", 7, 22, 40), previa(A, "arcoiris", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Arco-íris", "Quentes", "Frias", "Ambiente (AOD)"], cols=4, nomes_previa=["arcoiris", "quente", "frio", "ambiente"])
