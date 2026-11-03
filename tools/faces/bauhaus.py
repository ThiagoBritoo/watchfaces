"""Watchface "Bauhaus": composição geométrica (círculo, quadrado e triângulo). O círculo anda com a hora, o quadrado gira com os minutos e o
triângulo com os segundos. Hora em texto bem limpo. Quatro paletas. Original."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rect, rgb, strings_opcoes, tint, tpl, colar

NOME = "bauhaus"
# fundo, texto, forma1, forma2, forma3
PALETAS = [("classica", "#f2ead8 #14120f #d9362b #f2b632 #2457a6"), ("noite", "#16171d #f4f1e8 #e0482f #f4b942 #3a78d8"), ("menta", "#e4f2ec #112019 #ee6c4d #2a9d8f #264653"), ("rosa", "#fbe9ee #2b1020 #e5446d #ffb703 #3a0ca3")]
TRI = 150
CD = 200


def triangulo() -> Image.Image:
    s = 4
    im = Image.new("RGBA", (TRI * s, TRI * s), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon([(TRI * s / 2, 8 * s), (TRI * s - 8 * s, TRI * s - 14 * s), (8 * s, TRI * s - 14 * s)], fill=(255, 255, 255, 255))
    return im.resize((TRI, TRI), Image.LANCZOS)


def xml() -> str:
    p = lambda i: f"[CONFIGURATION.paleta.{i}]"  # noqa: E731
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + rect(0, 0, W, W, p(0)))
    a(f'      <PartDraw {full}><Ellipse x="30" y="34" width="{CD}" height="{CD}"><Fill color="{p(2)}" /><Transform target="x" value="30 + 220 * [HOUR_0_11_MINUTE] / 12" /></Ellipse></PartDraw>')
    a(f'      <PartDraw x="300" y="140" width="120" height="120" pivotX="0.5" pivotY="0.5"><Transform target="angle" value="([MINUTE] + [SECOND] / 60) * 6" />'
      f'<Rectangle x="0" y="0" width="120" height="120"><Fill color="{p(3)}" /></Rectangle></PartDraw>')
    a("      " + img(70, 250, TRI, TRI, "triangulo", f' tintColor="{p(4)}" pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="[SECOND] * 6" />'))
    a("      " + rect(0, 322, W, 5, p(1)))
    a("      " + hora(80, 336, 320, 90, "hh:mm", 80, p(1), "BOLD", "CENTER"))
    a("      " + tpl(130, 426, 220, 26, 20, p(1), "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "BOLD"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw {full}><Ellipse x="30" y="34" width="{CD}" height="{CD}"><Stroke thickness="2" color="#77ffffff" /><Transform target="x" value="30 + 220 * [HOUR_0_11_MINUTE] / 12" /></Ellipse></PartDraw>')
    a("      " + hora(80, 300, 320, 100, "hh:mm", 80, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, paleta: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    bg, tx, c1, c2, c3 = (rgb(c) for c in paleta.split())
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255) if ambiente_ else bg + (255,))
    d = ImageDraw.Draw(base)
    x = 30 + 220 * (h % 12 + mi / 60) / 12
    if ambiente_:
        d.ellipse([x, 34, x + CD, 34 + CD], outline=(119, 119, 119), width=2)
        d.text((C, 350), f"{h:02d}:{mi:02d}", font=fonte("Light", 80), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    d.ellipse([x, 34, x + CD, 34 + CD], fill=c1)
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(cam).rectangle([300, 140, 420, 260], fill=c2 + (255,))
    base.alpha_composite(cam.rotate(-(mi + s / 60) * 6, center=(360, 200), resample=Image.BICUBIC))
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cam.paste(tint(A["triangulo"], c3), (70, 250))
    base.alpha_composite(cam.rotate(-s * 6, center=(70 + TRI / 2, 250 + TRI / 2), resample=Image.BICUBIC))
    d = ImageDraw.Draw(base)
    d.rectangle([0, 322, W, 327], fill=tx)
    d.text((C, 376), f"{h:02d}:{mi:02d}", font=fonte("Bold", 80), fill=tx, anchor="mm")
    d.text((C, 439), "SEX 31", font=fonte("Bold", 20), fill=tx, anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Bauhaus", "paleta_label": "Palette"}
    pt = {"watch_face_name": "Bauhaus", "paleta_label": "Paleta"}
    strings_opcoes(en, pt, "paleta", {"classica": ("Classic", "Clássica"), "noite": ("Night", "Noite"), "menta": ("Mint", "Menta"), "rosa": ("Rose", "Rosa")})
    A = {"triangulo": triangulo()}
    pv = [previa(A, PALETAS[0][1], 10, 8, 15), previa(A, PALETAS[1][1], 3, 45, 40), previa(A, PALETAS[2][1], 8, 20, 5), previa(A, PALETAS[3][1], 6, 33, 50), previa(A, PALETAS[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Clássica", "Noite", "Menta", "Rosa", "Ambiente (AOD)"], cols=5, nomes_previa=["classica", "noite", "menta", "rosa", "ambiente"])
