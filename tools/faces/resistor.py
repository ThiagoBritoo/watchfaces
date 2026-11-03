"""Watchface "Resistor": um resistor de eletrônica cujas 4 faixas coloridas são os dígitos da hora, pelo código de cores (0 preto, 1 marrom, 2 vermelho,
3 laranja, 4 amarelo, 5 verde, 6 azul, 7 violeta, 8 cinza, 9 branco). Hora também em texto pequeno. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_linear
from wf.kit import C, W, cabecalho, finalizar, grupo, hora, img, redondo, rect, tpl

NOME = "resistor"
CORES = ["#ff161616", "#ff7a4a1e", "#ffd62828", "#fff77f00", "#fffcd116", "#ff3a9d3a", "#ff2a62d6", "#ff8a4fd1", "#ff8e8e96", "#fffafafa"]
NOMES = ["PRETO", "MARROM", "VERMELHO", "LARANJA", "AMARELO", "VERDE", "AZUL", "VIOLETA", "CINZA", "BRANCO"]
CORPO = (92, 190, 296, 100)
FX = [140, 202, 264, 326]
FL = 30
VAL = ["floor([HOUR_0_23] / 10)", "[HOUR_0_23] % 10", "floor([MINUTE] / 10)", "[MINUTE] % 10"]


def corpo() -> Image.Image:
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x, y, w, h = CORPO
    for lado in (-1, 1):                                          # terminais de metal
        xx = x - 70 if lado < 0 else x + w
        d.rectangle([xx * s, (y + h // 2 - 5) * s, (xx + 70) * s, (y + h // 2 + 5) * s], fill=(190, 192, 198, 255))
    d.rounded_rectangle([x * s, y * s, (x + w) * s, (y + h) * s], radius=34 * s, fill=(222, 190, 140, 255))
    d.rounded_rectangle([x * s, (y + 6) * s, (x + w) * s, (y + 30) * s], radius=24 * s, fill=(240, 214, 170, 120))
    d.rounded_rectangle([x * s, (y + h - 26) * s, (x + w) * s, (y + h) * s], radius=24 * s, fill=(150, 112, 70, 110))
    return im.resize((W, W), Image.LANCZOS)


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    x, y, w, h = CORPO
    L = cabecalho(NOME, "DIGITAL") + ['  <Scene backgroundColor="#ff101012">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + img(0, 0, W, W, "corpo"))
    for fx, v in zip(FX, VAL):
        for k, cor in enumerate(CORES):
            a("      " + rect(fx, y + 4, FL, h - 8, cor, 0, "Fill", 2, f'<Transform target="alpha" value="{v} == {k} ? 255 : 0" />'))
    a("      " + tpl(40, 110, 400, 70, 56, "#ffffffff", "%s", ["[HOUR_0_23_Z] + &quot;:&quot; + [MINUTE_Z]"], "BOLD").replace("[HOUR_0_23_Z] + &quot;:&quot; + [MINUTE_Z]", "[HOUR_0_23_Z]:[MINUTE_Z]").replace('<Template><![CDATA[%s]]><Parameter expression="[HOUR_0_23_Z]:[MINUTE_Z]" />', '<Template><![CDATA[%s:%s]]><Parameter expression="[HOUR_0_23_Z]" /><Parameter expression="[MINUTE_Z]" />'))
    a("      " + tpl(110, 330, 260, 26, 18, "#ff8e8e96", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(60, 150, 360, 150, "hh:mm", 100, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (16, 16, 18, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
        ImageDraw.Draw(base).text((C, 225), f"{h:02d}:{mi:02d}", font=fonte("Light", 100), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    base.alpha_composite(A["corpo"])
    d = ImageDraw.Draw(base)
    vals = [h // 10, h % 10, mi // 10, mi % 10]
    x, y, w, hh = CORPO
    for fx, v in zip(FX, vals):
        d.rectangle([fx, y + 4, fx + FL, y + hh - 4], fill=tuple(int(CORES[v][i:i + 2], 16) for i in (3, 5, 7)))
    d.text((C, 145), f"{h:02d}:{mi:02d}", font=fonte("Bold", 56), fill=(255, 255, 255), anchor="mm")
    d.text((C, 343), "SEX 31 OUT", font=fonte("Medium", 18), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Resistor"}
    pt = {"watch_face_name": "Resistor"}
    A = {"corpo": corpo()}
    pv = [previa(A, 10, 8), previa(A, 21, 45), previa(A, 3, 59), previa(A, 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["10:08", "21:45", "03:59", "Ambiente (AOD)"], cols=4, nomes_previa=["h1008", "h2145", "h0359", "ambiente"])
