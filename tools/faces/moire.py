"""Watchface "Moiré": dois conjuntos de círculos concêntricos se sobrepõem e formam padrões hipnóticos; o segundo conjunto orbita com o
tempo (os minutos mudam a figura). Hora pequena no centro. Abstrata. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grade
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, strings_opcoes, tint, tpl

NOME = "moire"
CORES = [("branco", "#ffffff"), ("ciano", "#33d6ff"), ("laranja", "#ff7a2f"), ("rosa", "#ff5c93"), ("verde", "#4be37a")]
LADO = 560
ORB = 46


def aneis(passo: float = 12.0, esp: float = 3.6) -> Image.Image:
    xx, yy = grade(LADO)
    r = np.hypot(xx + 0.5 - LADO / 2, yy + 0.5 - LADO / 2)
    m = np.mod(r, passo)
    a = np.clip(1 - np.abs(m - passo / 2) / (esp / 2 + 0.7), 0, 1)
    out = np.zeros((LADO, LADO, 4), np.uint8)
    out[..., :3] = 255
    out[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def xml() -> str:
    cor = "[CONFIGURATION.cor]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("cor", "cor_label", CORES), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + img(C - LADO // 2, C - LADO // 2, LADO, LADO, "aneis", f' tintColor="{cor}" alpha="170"'))
    ang = "([MINUTE] + [SECOND] / 60) * 0.10472"          # 6 graus em radianos por minuto
    a("      " + img(C - LADO // 2, C - LADO // 2, LADO, LADO, "aneis", f' tintColor="{cor}" alpha="170"',
                     f'<Transform target="x" value="{C - LADO // 2} + {ORB} * sin({ang})" /><Transform target="y" value="{C - LADO // 2} - {ORB} * cos({ang})" />'))
    a(f'      <PartDraw {full}><Ellipse x="{C - 88}" y="{C - 60}" width="176" height="120"><Fill color="#e6000000" /></Ellipse></PartDraw>')
    a("      " + hora(110, 190, 260, 80, "hh:mm", 62, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(130, 252, 220, 26, 18, "#ccffffff", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(110, 200, 260, 80, "hh:mm", 62, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, cor: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c = rgb(cor)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 240), f"{h:02d}:{mi:02d}", font=fonte("Light", 62), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    ang = math.radians((mi + s / 60) * 6)
    lay = tint(A["aneis"], c)
    r, g, b, al = lay.split()
    lay = Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * 170 / 255))))
    from wf.kit import colar
    colar(base, lay, C - LADO // 2, C - LADO // 2)
    colar(base, lay, int(C - LADO // 2 + ORB * math.sin(ang)), int(C - LADO // 2 - ORB * math.cos(ang)))
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(cam).ellipse([C - 88, C - 60, C + 88, C + 60], fill=(0, 0, 0, 230))
    base.alpha_composite(cam)
    d = ImageDraw.Draw(base)
    d.text((C, 232), f"{h:02d}:{mi:02d}", font=fonte("Bold", 62), fill=(255, 255, 255), anchor="mm")
    d.text((C, 265), "SEX 31", font=fonte("Medium", 18), fill=(204, 204, 204), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Moire", "cor_label": "Color"}
    pt = {"watch_face_name": "Moiré", "cor_label": "Cor"}
    strings_opcoes(en, pt, "cor", {"branco": ("White", "Branco"), "ciano": ("Cyan", "Ciano"), "laranja": ("Orange", "Laranja"), "rosa": ("Pink", "Rosa"), "verde": ("Green", "Verde")})
    A = {"aneis": aneis()}
    pv = [previa(A, "#ffffff", 10, 8, 20), previa(A, "#33d6ff", 10, 25, 0), previa(A, "#ff5c93", 4, 47, 30), previa(A, "#ffffff", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Branco (min 8)", "Ciano (min 25)", "Rosa (min 47)", "Ambiente (AOD)"], cols=4, nomes_previa=["branco", "ciano", "rosa", "ambiente"])
