"""Watchface "Topo": curvas de nível de um mapa topográfico (geradas por ruído, sempre iguais) ao fundo; a hora vai grande no centro com um
marcador de hora e outro de minuto percorrendo anéis, como pinos num mapa. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from wf.desenho import fonte, grad_radial, polar
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, strings_opcoes, tint, tpl

NOME = "topo"
TERRENOS = [("floresta", "#6bd68a #ffffff"), ("deserto", "#e8b86d #ffffff"), ("gelo", "#8fd3ff #ffffff"), ("lava", "#ff8a5c #ffe9d6")]
RH, RM = 124, 188
PINO = 44


def contorno() -> Image.Image:
    rng = np.random.default_rng(8)
    campo = np.zeros((W, W), np.float32)
    for esc, amp in ((90, 1.0), (45, 0.5), (22, 0.25)):
        r = rng.random((W // esc + 3, W // esc + 3)).astype(np.float32)
        im = Image.fromarray((r * 255).astype(np.uint8)).resize((W + 2 * esc, W + 2 * esc), Image.BICUBIC).filter(ImageFilter.GaussianBlur(esc / 3))
        campo += np.asarray(im, np.float32)[esc:esc + W, esc:esc + W] / 255 * amp
    campo /= campo.max()
    niveis = campo * 22
    frac = np.abs(niveis - np.round(niveis))
    linha = np.clip(1 - frac / 0.12, 0, 1)
    mestra = np.abs(niveis / 4 - np.round(niveis / 4)) < 0.02
    a = np.clip(linha * (0.55 + 0.45 * mestra), 0, 1)
    out = np.zeros((W, W, 4), np.uint8)
    out[..., :3] = 255
    out[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def pino() -> Image.Image:
    return grad_radial(PINO, PINO / 2, PINO / 2, [(0, (255, 255, 255, 255)), (7, (255, 255, 255, 255)), (9, (20, 20, 20, 255)), (11, (255, 255, 255, 255)), (13, (255, 255, 255, 220)), (PINO / 2, (255, 255, 255, 0))])


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    t = "[CONFIGURATION.terreno.0]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("terreno", "terreno_label", TERRENOS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + img(0, 0, W, W, "contorno", f' tintColor="{t}" alpha="170"'))
    a(f'      <PartDraw {full}><Ellipse x="{C - RH}" y="{C - RH}" width="{2 * RH}" height="{2 * RH}"><Stroke thickness="1.5" color="#55ffffff" /></Ellipse></PartDraw>')
    a(f'      <PartDraw {full}><Ellipse x="{C - RM}" y="{C - RM}" width="{2 * RM}" height="{2 * RM}"><Stroke thickness="1.5" color="#55ffffff" /></Ellipse></PartDraw>')
    a(f'      <PartDraw {full}><Ellipse x="{C - 104}" y="{C - 54}" width="208" height="108"><Fill color="#cc000000" /></Ellipse></PartDraw>')
    for nome, r, expr, cor in (("h", RH, "[HOUR_0_11_MINUTE] * 30", "[CONFIGURATION.terreno.1]"), ("m", RM, "([MINUTE] + [SECOND] / 60) * 6", t)):
        a(f'      <Group name="pino_{nome}" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="{expr}" />'
          + img(C - PINO // 2, C - r - PINO // 2, PINO, PINO, "pino", f' tintColor="{cor}"') + "</Group>")
    a("      " + hora(80, 188, 320, 90, "hh:mm", 76, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(130, 262, 220, 24, 18, "#ccffffff", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw {full}><Ellipse x="{C - RH}" y="{C - RH}" width="{2 * RH}" height="{2 * RH}"><Stroke thickness="2" color="#55ffffff" /></Ellipse></PartDraw>')
    a("      " + hora(80, 200, 320, 90, "hh:mm", 70, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, terreno: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c0, c1 = (rgb(x) for x in terreno.split())
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.ellipse([C - RH, C - RH, C + RH, C + RH], outline=(85, 85, 85), width=2)
        d.text((C, 245), f"{h:02d}:{mi:02d}", font=fonte("Light", 70), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    ct = tint(A["contorno"], c0)
    r, g, b, al = ct.split()
    base.alpha_composite(Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * 170 / 255)))))
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    dc = ImageDraw.Draw(cam)
    for r_ in (RH, RM):
        dc.ellipse([C - r_, C - r_, C + r_, C + r_], outline=(255, 255, 255, 85), width=2)
    dc.ellipse([C - 104, C - 54, C + 104, C + 54], fill=(0, 0, 0, 204))
    base.alpha_composite(cam)
    for r_, ang, cor in ((RH, (h % 12 + mi / 60) * 30, c1), (RM, (mi + s / 60) * 6, c0)):
        x, y = polar(C, C, r_, ang)
        base.alpha_composite(tint(A["pino"], cor), (int(x - PINO / 2), int(y - PINO / 2)))
    d = ImageDraw.Draw(base)
    d.text((C, 233), f"{h:02d}:{mi:02d}", font=fonte("Bold", 76), fill=(255, 255, 255), anchor="mm")
    d.text((C, 274), "SEX 31 OUT", font=fonte("Medium", 18), fill=(204, 204, 204), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Topo", "terreno_label": "Terrain"}
    pt = {"watch_face_name": "Topo", "terreno_label": "Terreno"}
    strings_opcoes(en, pt, "terreno", {"floresta": ("Forest", "Floresta"), "deserto": ("Desert", "Deserto"), "gelo": ("Ice", "Gelo"), "lava": ("Lava", "Lava")})
    A = {"contorno": contorno(), "pino": pino()}
    pv = [previa(A, TERRENOS[0][1], 10, 8, 20), previa(A, TERRENOS[1][1], 4, 47, 5), previa(A, TERRENOS[2][1], 8, 20, 40), previa(A, TERRENOS[3][1], 22, 2, 10), previa(A, TERRENOS[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Floresta", "Deserto", "Gelo", "Lava", "Ambiente (AOD)"], cols=5, nomes_previa=["floresta", "deserto", "gelo", "lava", "ambiente"])
