"""Watchface "Odômetro": quatro colunas de dígitos que rolam na vertical, como um odômetro mecânico (rolam só nos últimos 10 segundos
de cada minuto, com o vai-um para as casas da esquerda). Arte e código originais."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rect, rgb, textos_acento, tpl

NOME = "odometro"
TAM = 128
PASSO = 112                          # distância vertical entre dígitos
CENTROS_X = [96, 184, 296, 384]
CY = 232
LARG = 80
ROLA = "clamp(([SECOND] - 50) / 10, 0, 1)"
H, M, S = "[HOUR_0_23]", "[MINUTE]", "[SECOND]"
# (valor do dígito no deslocamento k, fração de rolagem)
COLUNAS = [
    (lambda k: f"floor((({H} + {k} + 24) % 24) / 10)", f"({M} == 59 &amp;&amp; ({H} % 10 == 9 || {H} == 23)) ? {ROLA} : 0"),
    (lambda k: f"(({H} + {k} + 24) % 24) % 10", f"({M} == 59) ? {ROLA} : 0"),
    (lambda k: f"floor((({M} + {k} + 60) % 60) / 10)", f"({M} % 10 == 9) ? {ROLA} : 0"),
    (lambda k: f"({M} + {k} + 60) % 10".replace("({M} + ", "(" + M + " + "), ROLA),
]


def sombras() -> Image.Image:
    a = np.zeros((W, W, 4), np.uint8)
    yy = np.arange(W)[:, None]
    topo = np.clip((CY - 62 - yy) / -50.0, 0, 1) * 0 + np.clip(1 - np.abs(yy - (CY - 90)) / 90.0, 0, 1) * (yy < CY - 40)
    base = np.clip((yy - (CY + 40)) / 50.0, 0, 1) * (yy > CY + 40) * np.clip(1 - np.abs(yy - (CY + 130)) / 100.0, 0, 1)
    a[..., 3] = (np.clip(topo + base, 0, 1) * 235).astype(np.uint8) * np.ones((1, W), np.uint8)
    return Image.fromarray(a, "RGBA")


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    for cx, (val, frac) in zip(CENTROS_X, COLUNAS):
        for k in (0, 1):
            d = f"abs({k} - ({frac}))"
            a(f'      <PartText x="{cx - LARG // 2}" y="{CY - PASSO // 2}" width="{LARG}" height="{PASSO}">'
              f'<Transform target="y" value="{CY - PASSO // 2} + ({k} - ({frac})) * {PASSO}" />'
              f'<Transform target="alpha" value="255 * clamp(1.15 - 1.15 * {d}, 0, 1)" />'
              f'<Text align="CENTER"><Font family="SYNC_TO_DEVICE" size="{TAM}" weight="BOLD" color="#ffffffff"><Template><![CDATA[%s]]>'
              f'<Parameter expression="numberFormat(&quot;0&quot;, {val(k)})" /></Template></Font></Text></PartText>')
    a("      " + img(0, 0, W, W, "sombras"))
    a("      " + rect(C - 5, CY - 30, 10, 10, ac, 5) + rect(C - 5, CY + 20, 10, 10, ac, 5))
    a("      " + rect(48, CY - PASSO // 2 - 4, 384, 2, ac, 0) + rect(48, CY + PASSO // 2 + 2, 384, 2, ac, 0))
    a("      " + tpl(110, 392, 260, 28, 20, "#ff8e8e96", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(30, 150, 420, 160, "hh:mm", 120, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 232), f"{h:02d}:{mi:02d}", font=fonte("Light", 120), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    rola = max(0, min(1, (s - 50) / 10))
    fr = [rola if (mi == 59 and (h % 10 == 9 or h == 23)) else 0, rola if mi == 59 else 0, rola if mi % 10 == 9 else 0, rola]
    for cx, (f, vf) in zip(CENTROS_X, zip(fr, [lambda k: ((h + k) % 24) // 10, lambda k: ((h + k) % 24) % 10, lambda k: ((mi + k) % 60) // 10, lambda k: (mi + k) % 10])):
        for k in (0, 1):
            alpha = max(0, min(1, 1.15 - 1.15 * abs(k - f)))
            cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
            ImageDraw.Draw(cam).text((cx, CY + (k - f) * PASSO), str(vf(k)), font=fonte("Bold", TAM), fill=(255, 255, 255, int(255 * alpha)), anchor="mm")
            base.alpha_composite(cam)
    base.alpha_composite(A["sombras"])
    d = ImageDraw.Draw(base)
    for yy in (CY - 25, CY + 25):
        d.ellipse([C - 5, yy - 5, C + 5, yy + 5], fill=ac)
    d.rectangle([48, CY - PASSO // 2 - 4, 432, CY - PASSO // 2 - 2], fill=ac)
    d.rectangle([48, CY + PASSO // 2 + 2, 432, CY + PASSO // 2 + 4], fill=ac)
    d.text((C, 406), "SEX 31 OUT", font=fonte("Medium", 20), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Odometer", "Odômetro")
    A = {"sombras": sombras()}
    pv = [previa(A, "#ff7a2f", 10, 8, 20), previa(A, "#33d6ff", 10, 9, 55), previa(A, "#f2c14e", 19, 59, 56), previa(A, "#ff7a2f", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["10:08", "10:09 rolando", "19:59 virando (vai-um)", "Ambiente (AOD)"], cols=4, nomes_previa=["normal", "rolando", "vaium", "ambiente"])
