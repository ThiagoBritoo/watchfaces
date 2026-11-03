"""Watchface "Cartesiano": um gráfico de coordenadas. O eixo horizontal é a hora do dia (0 a 24) e o vertical os minutos (0 a 60): um ponto desenha
a hora como uma posição no plano. A hora também aparece em texto. Cinco cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, grad_radial, reduzir_por, tela, texto_centrado
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, colar, cor_config, finalizar, grupo, hora, img, redondo, rgb, textos_acento, tint, tpl

NOME = "cartesiano"
X0, X1, Y0, Y1 = 100, 396, 100, 332          # área do gráfico (y0 = 60 min no topo, y1 = 0 embaixo)
P = 40


def eixos() -> Image.Image:
    n = W * SS
    im = tela(n)
    d = ImageDraw.Draw(im)
    for hh in range(0, 25, 4):
        x = X0 + (X1 - X0) * hh / 24
        d.line([(x * SS, Y0 * SS), (x * SS, Y1 * SS)], fill=(255, 255, 255, 70), width=SS)
        texto_centrado(im, str(hh), x * SS, (Y1 + 16) * SS, fonte("Medium", 15 * SS), (255, 255, 255, 190))
    for m in range(0, 61, 15):
        y = Y1 - (Y1 - Y0) * m / 60
        d.line([(X0 * SS, y * SS), (X1 * SS, y * SS)], fill=(255, 255, 255, 70), width=SS)
        texto_centrado(im, str(m), (X0 - 18) * SS, y * SS, fonte("Medium", 15 * SS), (255, 255, 255, 190))
    d.line([(X0 * SS, Y0 * SS), (X0 * SS, Y1 * SS), (X1 * SS, Y1 * SS)], fill=(255, 255, 255, 230), width=int(2.4 * SS))
    return reduzir_por(im)


def ponto() -> Image.Image:
    return grad_radial(P, P / 2, P / 2, [(0, (255, 255, 255, 255)), (6, (255, 255, 255, 255)), (10, (255, 255, 255, 140)), (P / 2, (255, 255, 255, 0))])


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    px = f"{X0} + {X1 - X0} * [HOUR_0_23_MINUTE] / 24"
    py = f"{Y1} - {Y1 - Y0} * ([MINUTE] + [SECOND] / 60) / 60"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + img(0, 0, W, W, "eixos"))
    a(f'      <PartDraw x="{X0}" y="{Y0}" width="2" height="{Y1 - Y0}"><Transform target="alpha" value="0" /><Rectangle x="0" y="0" width="2" height="2"><Fill color="#00000000" /></Rectangle></PartDraw>'.replace('<PartDraw', '<PartDraw', 1) if False else "")
    a("      " + img(C - P // 2, C - P // 2, P, P, "ponto", f' tintColor="{ac}"', f'<Transform target="x" value="{px} - {P // 2}" /><Transform target="y" value="{py} - {P // 2}" />'))
    a("      " + hora(110, 370, 260, 60, "hh:mm", 46, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(110, 40, 260, 30, 20, ac, "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + img(0, 0, W, W, "eixos", ' alpha="90"'))
    a("      " + hora(110, 370, 260, 60, "hh:mm", 46, "#ffc0c0c8", "LIGHT", "CENTER"))
    a(f'      <PartDraw x="{X0}" y="{Y1 - 6}" width="12" height="12"><Transform target="x" value="{px} - 6" /><Transform target="y" value="{py} - 6" /><Ellipse x="0" y="0" width="12" height="12"><Fill color="#ffffffff" /></Ellipse></PartDraw>')
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    x = X0 + (X1 - X0) * (h + mi / 60) / 24
    y = Y1 - (Y1 - Y0) * (mi + (0 if ambiente_ else s / 60)) / 60
    ex = A["eixos"].copy()
    if ambiente_:
        r, g, b, al = ex.split()
        ex = Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * 90 / 255))))
    base.alpha_composite(ex)
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 255, 255))
        d.text((C, 400), f"{h:02d}:{mi:02d}", font=fonte("Light", 46), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    colar(base, tint(A["ponto"], ac), int(x - P / 2), int(y - P / 2))
    d = ImageDraw.Draw(base)
    d.text((C, 400), f"{h:02d}:{mi:02d}", font=fonte("Bold", 46), fill=(255, 255, 255), anchor="mm")
    d.text((C, 55), "SEX 31 OUT", font=fonte("Medium", 20), fill=ac, anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Cartesian", "Cartesiano")
    A = {"eixos": eixos(), "ponto": ponto()}
    pv = [previa(A, "#ff7a2f", 10, 8, 20), previa(A, "#33d6ff", 21, 45, 40), previa(A, "#4be37a", 3, 55, 5), previa(A, "#ff7a2f", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["10:08", "21:45", "03:55", "Ambiente (AOD)"], cols=4, nomes_previa=["h1008", "h2145", "h0355", "ambiente"])
