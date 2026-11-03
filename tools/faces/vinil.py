"""Watchface "Vinil": um disco de vinil gira (um passo a cada segundo) sob uma agulha; a hora fica no rótulo. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grade, polar, sombra, tela
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, textos_acento, tint, tpl, colar

NOME = "vinil"
RD = 214
RL = 82


def disco() -> Image.Image:
    xx, yy = grade(W)
    dx, dy = xx - C, yy - C
    r = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)
    sulcos = 0.07 + 0.05 * np.sin(r * 2.3) * np.sin(r * 0.37 + 1)
    brilho = np.clip(np.cos(2 * (ang - 0.9)) ** 8 * 0.9 + np.clip(np.cos(2 * (ang + 2.2)) ** 10, 0, 1) * 0.6, 0, 1)
    v = sulcos + brilho * 0.38 * np.clip(1 - np.abs(r - 150) / 90, 0.15, 1)
    faixas = ((r > 120) & (r < 124)) | ((r > 168) & (r < 171))
    v = np.where(faixas, 0.02, v)
    out = np.zeros((W, W, 4), np.uint8)
    g = np.clip(v * 255, 0, 255).astype(np.uint8)
    out[..., 0] = out[..., 1] = g
    out[..., 2] = np.clip(g.astype(np.int32) + 6, 0, 255).astype(np.uint8)
    out[..., 3] = (np.clip((RD - r) / 1.2, 0, 1) * np.clip((r - RL * 0.18) / 1.2, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def rotulo() -> Image.Image:
    t = 2 * RL
    xx, yy = grade(t)
    dx, dy = xx - t / 2, yy - t / 2
    r = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)
    v = 235 - 45 * (np.sin(ang * 12) > 0.85) - 30 * (np.abs(r - 60) < 1.4)
    out = np.zeros((t, t, 4), np.uint8)
    out[..., :3] = np.clip(v, 0, 255).astype(np.uint8)[..., None]
    out[..., 3] = (np.clip((RL - r) / 1.2, 0, 1) * np.clip((r - 5) / 1.0, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def braco() -> Image.Image:
    s = 3
    n = W * s
    im = tela(n)
    d = ImageDraw.Draw(im)
    p0, p1, p2 = (440 * s, 78 * s), (440 * s, 150 * s), (330 * s, 300 * s)
    sh = tela(n)
    ImageDraw.Draw(sh).line([p0, p1, p2], fill=(0, 0, 0, 255), width=7 * s, joint="curve")
    im.alpha_composite(sombra(sh.resize((n, n)), 6 * s, 8 * s, 6 * s, 0.6))
    d.line([p0, p1, p2], fill=(205, 208, 214, 255), width=6 * s, joint="curve")
    d.line([p0, p1, p2], fill=(250, 250, 252, 255), width=2 * s, joint="curve")
    d.ellipse([p0[0] - 20 * s, p0[1] - 20 * s, p0[0] + 20 * s, p0[1] + 20 * s], fill=(70, 72, 80, 255), outline=(200, 202, 210, 255), width=3 * s)
    d.polygon([(p2[0] - 8 * s, p2[1] - 4 * s), (p2[0] + 12 * s, p2[1] - 12 * s), (p2[0] + 20 * s, p2[1] + 8 * s), (p2[0] - 2 * s, p2[1] + 16 * s)], fill=(40, 42, 48, 255), outline=(220, 222, 228, 255))
    return im.resize((W, W), Image.LANCZOS)


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("disco", "", 0))
    a("      " + img(0, 0, W, W, "disco", ' pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="[SECOND] * 6" />'))
    a("      " + img(C - RL, C - RL, 2 * RL, 2 * RL, "rotulo", f' tintColor="{ac}" pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="[SECOND] * 6" />'))
    a("      " + hora(C - RL, C - 38, 2 * RL, 56, "hh:mm", 40, "#ff141418", "BOLD", "CENTER"))
    a("      " + tpl(C - RL, C + 14, 2 * RL, 26, 16, "#cc141418", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a("      " + img(0, 0, W, W, "braco"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw {full}><Ellipse x="{C - RD}" y="{C - RD}" width="{2 * RD}" height="{2 * RD}"><Stroke thickness="2" color="#66ffffff" /></Ellipse></PartDraw>')
    a(f'      <PartDraw {full}><Ellipse x="{C - RL}" y="{C - RL}" width="{2 * RL}" height="{2 * RL}"><Stroke thickness="2" color="#66ffffff" /></Ellipse></PartDraw>')
    a("      " + hora(C - RL, C - 28, 2 * RL, 56, "hh:mm", 38, "#ffb8b8c0", "MEDIUM", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.ellipse([C - RD, C - RD, C + RD, C + RD], outline=(102, 102, 102), width=2)
        d.ellipse([C - RL, C - RL, C + RL, C + RL], outline=(102, 102, 102), width=2)
        d.text((C, C), f"{h:02d}:{mi:02d}", font=fonte("Medium", 38), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    base.alpha_composite(A["disco"].rotate(-s * 6, center=(C, C), resample=Image.BICUBIC))
    lab = tint(A["rotulo"], ac)
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cam.paste(lab, (C - RL, C - RL))
    base.alpha_composite(cam.rotate(-s * 6, center=(C, C), resample=Image.BICUBIC))
    d = ImageDraw.Draw(base)
    d.text((C, C - 8), f"{h:02d}:{mi:02d}", font=fonte("Bold", 40), fill=(20, 20, 24), anchor="mm")
    d.text((C, C + 26), "SEX 31", font=fonte("Medium", 16), fill=(40, 40, 46), anchor="mm")
    base.alpha_composite(A["braco"])
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Vinyl", "Vinil")
    A = {"disco": disco(), "rotulo": rotulo(), "braco": braco()}
    pv = [previa(A, "#ff7a2f", 10, 8, 5), previa(A, "#33d6ff", 10, 8, 40), previa(A, "#ff5c93", 4, 20, 15), previa(A, "#ff7a2f", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Laranja", "Ciano", "Rosa", "Ambiente (AOD)"], cols=4, nomes_previa=["laranja", "ciano", "rosa", "ambiente"])
