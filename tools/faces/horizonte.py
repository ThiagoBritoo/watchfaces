"""Watchface "Horizonte": minimalismo nórdico. A hora gigante e fina no alto, uma linha de horizonte com um ponto que anda durante a hora (minutos) e o
minuto escrito embaixo. Seis cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rect, rgb, textos_acento, tpl

NOME = "horizonte"
X0, X1, Y = 70, 410, 262


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + hora(60, 60, 360, 200, "hh", 190, "#ffffffff", "LIGHT", "CENTER"))
    a("      " + rect(X0, Y, X1 - X0, 2, "#55ffffff", 0))
    for m in range(0, 61, 15):
        a("      " + rect(X0 + (X1 - X0) * m // 60 - 1, Y - 8, 2, 18, "#99ffffff", 0))
    a("      " + rect(X0, Y - 1, X1 - X0, 4, ac, 2, "Fill", 2, f'<Transform target="width" value="{X1 - X0} * ([MINUTE] + [SECOND] / 60) / 60" />'))
    a(f'      <PartDraw x="{X0 - 9}" y="{Y - 8}" width="18" height="18"><Transform target="x" value="{X0 - 9} + {X1 - X0} * ([MINUTE] + [SECOND] / 60) / 60" />'
      f'<Ellipse x="0" y="0" width="18" height="18"><Fill color="{ac}" /></Ellipse></PartDraw>')
    a("      " + hora(60, 282, 360, 90, "mm", 64, ac, "MEDIUM", "CENTER"))
    a("      " + tpl(110, 366, 260, 26, 18, "#ff8e8e96", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(60, 70, 360, 200, "hh", 170, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("      " + rect(X0, Y, X1 - X0, 2, "#44ffffff", 0))
    a("      " + hora(60, 282, 360, 90, "mm", 60, "#ff8e8e96", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    frac = (mi + (0 if ambiente_ else s / 60)) / 60
    if ambiente_:
        d.text((C, 160), f"{h:02d}", font=fonte("Light", 170), fill=(192, 192, 200), anchor="mm")
        d.rectangle([X0, Y, X1, Y + 2], fill=(68, 68, 68))
        d.text((C, 327), f"{mi:02d}", font=fonte("Light", 60), fill=(142, 142, 150), anchor="mm")
        return redondo(base)
    d.text((C, 165), f"{h:02d}", font=fonte("Light", 190), fill=(255, 255, 255), anchor="mm")
    d.rectangle([X0, Y, X1, Y + 2], fill=(85, 85, 85))
    for m in range(0, 61, 15):
        x = X0 + (X1 - X0) * m // 60
        d.rectangle([x - 1, Y - 8, x + 1, Y + 10], fill=(153, 153, 153))
    d.rounded_rectangle([X0, Y - 1, X0 + (X1 - X0) * frac, Y + 3], radius=2, fill=ac)
    x = X0 + (X1 - X0) * frac
    d.ellipse([x - 9, Y - 8, x + 9, Y + 10], fill=ac)
    d.text((C, 327), f"{mi:02d}", font=fonte("Medium", 64), fill=ac, anchor="mm")
    d.text((C, 379), "SEX 31 OUT", font=fonte("Medium", 18), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Horizon", "Horizonte")
    pv = [previa("#f2c14e", 10, 8, 20), previa("#33d6ff", 3, 45, 40), previa("#ff5c93", 7, 22, 5), previa("#f2c14e", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Ouro", "Ciano", "Rosa", "Ambiente (AOD)"], cols=4, nomes_previa=["ouro", "ciano", "rosa", "ambiente"])
