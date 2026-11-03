"""Watchface "Osciloscópio": tela de osciloscópio com grade, uma onda que desliza a cada segundo e leituras (canal, hora, bateria).
Fósforo em 4 cores. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, strings_opcoes, tint, tpl

NOME = "osciloscopio"
FOSFOROS = [("verde", "#39ff7a"), ("ambar", "#ffb000"), ("ciano", "#33e0ff"), ("branco", "#eef2ee")]
ONDA_Y = 330                        # linha central da onda
AMP = 38
PASSO_X = 36                        # px por segundo


def grade_png() -> Image.Image:
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(-5, 6):
        v = (C + k * 48) * s
        mj = k == 0
        d.line([(v, 40 * s), (v, 440 * s)], fill=(255, 255, 255, 120 if mj else 46), width=int((2 if mj else 1) * s))
        d.line([(40 * s, v), (440 * s, v)], fill=(255, 255, 255, 120 if mj else 46), width=int((2 if mj else 1) * s))
    for k in range(-50, 51):
        v = (C + k * 9.6) * s
        d.line([(v, (C - 4) * s), (v, (C + 4) * s)], fill=(255, 255, 255, 90), width=s)
        d.line([((C - 4) * s, v), ((C + 4) * s, v)], fill=(255, 255, 255, 90), width=s)
    return im.resize((W, W), Image.LANCZOS)


def onda() -> Image.Image:
    s = 3
    w_, h_ = 960, 130
    im = Image.new("L", (w_ * s, h_ * s), 0)
    d = ImageDraw.Draw(im)
    pts = []
    for x in range(0, w_ * s + 1):
        t = 2 * math.pi * (x / s) / 480
        y = h_ / 2 + AMP * (0.62 * math.sin(t * 2) + 0.28 * math.sin(t * 5 + 1) + 0.18 * math.sin(t * 11 + 0.5)) * 0.9
        pts.append((x, y * s))
    d.line(pts, fill=255, width=int(3.4 * s))
    glow = im.filter(ImageFilter.GaussianBlur(5 * s)).point(lambda v: int(v * 0.8))
    a = np.maximum(np.asarray(im, np.float32), np.asarray(glow, np.float32))
    out = np.zeros((h_ * s, w_ * s, 4), np.uint8)
    out[..., :3] = 255
    out[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA").resize((w_, h_), Image.LANCZOS)


def xml() -> str:
    fo = "[CONFIGURATION.fosforo]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("fosforo", "fosforo_label", FOSFOROS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("tela", f' tintColor="{fo}"', 0))
    a("      " + img(0, 0, W, W, "grade"))
    a("      " + img(0, ONDA_Y - 65, 960, 130, "onda", "", f'<Transform target="x" value="0 - (([SECOND] * {PASSO_X}) % 480)" />'))
    a("      " + hora(40, 96, 400, 110, "hh:mm", 96, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(96, 66, 120, 24, 16, "#ccffffff", "%s", ["&quot;CH1&quot;"], "MEDIUM", "START"))
    a("      " + tpl(264, 66, 120, 24, 16, "#ccffffff", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM", "END"))
    a("      " + tpl(96, 408, 150, 24, 16, "#ccffffff", "%s%%", ["round([BATTERY_PERCENT])"], "MEDIUM", "START"))
    a("      " + tpl(244, 408, 140, 24, 16, "#ccffffff", "%ss", ["[SECOND_Z]"], "MEDIUM", "END"))
    a("    </Group>")
    a("    " + grupo("ambiente", f' alpha="0" tintColor="{fo}"', 255))
    a("      " + img(0, 0, W, W, "grade", ' alpha="70"'))
    a("      " + hora(40, 150, 400, 110, "hh:mm", 90, "#ffb8b8b8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, cor: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c = rgb(cor)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    if ambiente_:
        g = A["grade"].copy()
        r, gg, b, al = g.split()
        cam.alpha_composite(Image.merge("RGBA", (r, gg, b, al.point(lambda v: int(v * 70 / 255)))))
        d.text((C, 205), f"{h:02d}:{mi:02d}", font=fonte("Light", 90), fill=(184, 184, 184, 255), anchor="mm")
    else:
        cam.alpha_composite(A["grade"])
        x = -((s * PASSO_X) % 480)
        wv = A["onda"]
        full = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        full.paste(wv, (x, ONDA_Y - 65))
        cam.alpha_composite(full)
        d.text((C, 150), f"{h:02d}:{mi:02d}", font=fonte("Bold", 96), fill=(255, 255, 255, 255), anchor="mm")
        d.text((96, 78), "CH1", font=fonte("Medium", 16), fill=(255, 255, 255, 204), anchor="lm")
        d.text((384, 78), "SEX 31", font=fonte("Medium", 16), fill=(255, 255, 255, 204), anchor="rm")
        d.text((96, 420), "89%", font=fonte("Medium", 16), fill=(255, 255, 255, 204), anchor="lm")
        d.text((384, 420), f"{s:02d}s", font=fonte("Medium", 16), fill=(255, 255, 255, 204), anchor="rm")
    base.alpha_composite(tint(cam, c))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Oscilloscope", "fosforo_label": "Phosphor"}
    pt = {"watch_face_name": "Osciloscópio", "fosforo_label": "Fósforo"}
    strings_opcoes(en, pt, "fosforo", {"verde": ("Green", "Verde"), "ambar": ("Amber", "Âmbar"), "ciano": ("Cyan", "Ciano"), "branco": ("White", "Branco")})
    A = {"grade": grade_png(), "onda": onda()}
    pv = [previa(A, "#39ff7a", 10, 8, 5), previa(A, "#ffb000", 4, 47, 21), previa(A, "#33e0ff", 8, 20, 40), previa(A, "#39ff7a", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Verde", "Âmbar", "Ciano", "Ambiente (AOD)"], cols=4, nomes_previa=["verde", "ambar", "ciano", "ambiente"])
