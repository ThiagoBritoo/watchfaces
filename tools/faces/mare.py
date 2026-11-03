"""Watchface "Maré": abstrata. Um nível de água sobe ao longo do dia (vazio à meia-noite, cheio à meia-noite seguinte) com
ondas que se movem; a hora aparece em números grandes e finos por cima. Régua de maré na lateral esquerda.
Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, colar, cor_config, finalizar, hora, img, redondo, rect, rgb, strings_opcoes, tint, tpl

NOME = "mare"
# crista clara, corpo da água, fundo escuro
PALETAS = [("mar", "#7fd8ff #1c6fb8 #04121f"), ("lava", "#ffb26b #e0431f #1a0804"), ("mata", "#9dffb8 #1f9d55 #04140a"),
           ("neon", "#ff9fd0 #c2187a #14040f"), ("gelo", "#e6fbff #4aa9c9 #061218")]
OND_W, OND_H = 960, 120
OFF = 60                                  # a crista fica 60 px acima do topo do corpo


def onda(h1: float, h2: float, h3: float, fase: float) -> Image.Image:
    s = 3
    im = Image.new("L", (OND_W * s, OND_H * s), 0)
    d = ImageDraw.Draw(im)
    pts = []
    for x in range(0, OND_W * s + 1, 2):
        t = 2 * math.pi * (x / s) / 480
        y = (34 + h1 * math.sin(t + fase) + h2 * math.sin(2 * t + fase * 2) + h3 * math.sin(3 * t - fase)) * s
        pts.append((x, y))
    d.polygon(pts + [(OND_W * s, OND_H * s), (0, OND_H * s)], fill=255)
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(im)
    return out.resize((OND_W, OND_H), Image.LANCZOS)


def profundidade() -> Image.Image:
    a = np.zeros((W, W, 4), np.uint8)
    t = np.linspace(0, 1, W)[:, None]
    a[..., 3] = (np.clip(t - 0.15, 0, 1) ** 1.2 * 175).astype(np.uint8) * np.ones((1, W), np.uint8)
    return Image.fromarray(a, "RGBA")


def regua() -> Image.Image:
    s = 3
    im = Image.new("RGBA", (W * s, W * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = fonte("Medium", 18 * s)
    for h in range(1, 24):
        y = W * (1 - h / 24) * s
        mj = h % 6 == 0
        d.line([(40 * s, y), ((66 if mj else 54) * s, y)], fill=(255, 255, 255, 235 if mj else 110), width=int((2.6 if mj else 1.6) * s))
        if mj:
            d.text((74 * s, y), f"{h:02d}", font=f, fill=(255, 255, 255, 210), anchor="lm")
    return im.resize((W, W), Image.LANCZOS)


def y_nivel() -> str:
    return "480 * (1 - [SECONDS_IN_DAY] / 86400)"


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>",
                                       '  <Scene backgroundColor="#ff000000">']
    a = L.append
    yn = y_nivel()
    a(f'    <Group name="mar" {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a("      " + rect(0, 0, W, W, "[CONFIGURATION.paleta.2]", 0))
    a("      " + img(0, 0, 960, OND_H, "onda_a", ' alpha="150" tintColor="[CONFIGURATION.paleta.0]"', f'<Transform target="x" value="-480 + (([SECOND_MILLISECOND] * 8) % 480)" /><Transform target="y" value="{yn} - {OFF} - 14" />'))
    a("      " + rect(0, 0, W, W, "[CONFIGURATION.paleta.1]", 0, "Fill", 2, f'<Transform target="y" value="{yn} + 8" />'))
    a("      " + img(0, 0, 960, OND_H, "onda_b", f' tintColor="[CONFIGURATION.paleta.1]"', f'<Transform target="x" value="0 - (([SECOND_MILLISECOND] * 16) % 480)" /><Transform target="y" value="{yn} - {OFF}" />'))
    a("      " + img(0, 0, W, W, "profundidade"))
    a("      " + img(0, 0, W, W, "regua"))
    a("      " + rect(22, 0, 12, 12, "#ffffffff", 6, "Fill", 2, f'<Transform target="y" value="{yn} - 6" />'))
    a("      " + hora(30, 150, 420, 170, "hh:mm", 124, "#ffffffff", "LIGHT", "CENTER"))
    a("      " + tpl(110, 80, 260, 30, 22, "#ccffffff", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("      " + tpl(110, 392, 260, 34, 26, "#ccffffff", "%s%%", ["round([SECONDS_IN_DAY] / 864)"], "MEDIUM"))
    a("    </Group>")
    a(f'    <Group name="ambiente" {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />')
    a("      " + rect(0, 0, W, 2, "[CONFIGURATION.paleta.0]", 0, "Fill", 2, f'<Transform target="y" value="{yn}" />'))
    a("      " + hora(30, 150, 420, 170, "hh:mm", 112, "#ffb0b0b8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A: dict, paleta: str, seg_dia: int, ms: float = 12.3, ambiente_: bool = False) -> Image.Image:
    c0, c1, c2 = (rgb(c) for c in paleta.split())
    yn = 480 * (1 - seg_dia / 86400)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255) if ambiente_ else c2 + (255,))
    d = ImageDraw.Draw(base)
    hh, mm = seg_dia // 3600, seg_dia % 3600 // 60
    if ambiente_:
        d.rectangle([0, int(yn), W, int(yn) + 1], fill=c0)
        d.text((C, 235), f"{hh:02d}:{mm:02d}", font=fonte("Light", 112), fill=(176, 176, 184), anchor="mm")
        return redondo(base)
    xa = int(-480 + (ms * 8) % 480)
    xb = int(-((ms * 16) % 480))
    wa = tint(A["onda_a"], c0)
    r, g, b, al = wa.split()
    colar(base, Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * 150 / 255)))), xa, int(yn - OFF - 14))
    d.rectangle([0, int(yn) + 8, W, W], fill=c1)
    colar(base, tint(A["onda_b"], c1), xb, int(yn - OFF))
    base.alpha_composite(A["profundidade"])
    base.alpha_composite(A["regua"])
    d = ImageDraw.Draw(base)
    d.ellipse([22, yn - 6, 34, yn + 6], fill=(255, 255, 255))
    d.text((C, 235), f"{hh:02d}:{mm:02d}", font=fonte("Light", 124), fill=(255, 255, 255), anchor="mm")
    d.text((C, 95), "SEX 31 OUT", font=fonte("Medium", 22), fill=(220, 224, 230), anchor="mm")
    d.text((C, 409), f"{round(seg_dia / 864)}%", font=fonte("Medium", 26), fill=(220, 224, 230), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Tide", "paleta_label": "Water"}
    pt = {"watch_face_name": "Maré", "paleta_label": "Água"}
    strings_opcoes(en, pt, "paleta", {"mar": ("Sea", "Mar"), "lava": ("Lava", "Lava"), "mata": ("Forest", "Mata"), "neon": ("Neon", "Neon"), "gelo": ("Ice", "Gelo")})
    A = {"onda_a": onda(11, 5, 3, 0.8), "onda_b": onda(9, 4, 2, 2.4), "profundidade": profundidade(), "regua": regua()}
    pv = [previa(A, PALETAS[0][1], 10 * 3600 + 8 * 60), previa(A, PALETAS[1][1], 17 * 3600 + 45 * 60, 40.1), previa(A, PALETAS[2][1], 3 * 3600 + 20 * 60, 5.5),
          previa(A, PALETAS[0][1], 10 * 3600 + 8 * 60, ambiente_=True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Mar (10:08)", "Lava (17:45)", "Mata (03:20)", "Ambiente (AOD)"], cols=4, nomes_previa=["mar", "lava", "mata", "ambiente"])
