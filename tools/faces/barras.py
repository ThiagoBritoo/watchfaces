"""Watchface "Barras": painel minimalista de barras de progresso (dia, hora, passos, bateria) com hora grande no alto.
Quatro cores por paleta. Arte e código originais."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rect, rgb, strings_opcoes, tpl

NOME = "barras"
PALETAS = [("sorvete", "#ff7ab6 #ffb347 #5ee6c8 #7aa7ff"), ("neon", "#39ff88 #2ee6ff #ff4fd8 #ffe14a"), ("terra", "#e07a4f #d9b44a #8fae6b #6fa3a8"), ("mono", "#ffffff #d8d8d8 #a8a8a8 #787878")]
BX, BW, BH = 84, 250, 26
MIN = 78
YS = [226, 266, 306, 346]
ROTULOS = [("DIA", "round([SECONDS_IN_DAY] / 864)"), ("HORA", "round(([MINUTE] * 60 + [SECOND]) / 36)"), ("PASSOS", "round(clamp([STEP_PERCENT], 0, 100))"),
           ("BAT", "round(clamp([BATTERY_PERCENT], 0, 100))")]
FRAC = ["[SECONDS_IN_DAY] / 86400", "([MINUTE] * 60 + [SECOND]) / 3600", "clamp([STEP_PERCENT], 0, 100) / 100", "clamp([BATTERY_PERCENT], 0, 100) / 100"]


def xml() -> str:
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + hora(40, 58, 400, 130, "hh:mm", 112, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(110, 176, 260, 28, 20, "#ff8e8e96", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    for i, (y, (rot, val), fr) in enumerate(zip(YS, ROTULOS, FRAC)):
        cor = f"[CONFIGURATION.paleta.{i}]"
        a("      " + rect(BX, y, BW, BH, "#26ffffff", BH // 2))
        a("      " + rect(BX, y, BW, BH, cor, BH // 2, "Fill", 2, f'<Transform target="width" value="{MIN} + {BW - MIN} * ({fr})" />'))
        a("      " + tpl(BX + 12, y + 3, 120, BH - 6, 16, "#ff101014", "%s", [f'&quot;{rot}&quot;'], "BOLD", "START"))
        a("      " + tpl(BX + BW + 8, y + 2, 84, BH - 4, 20, "#ffffffff", "%s%%", [val], "BOLD", "START"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(40, 130, 400, 140, "hh:mm", 112, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(paleta: str, h: int, mi: int, s: int, dia: float, passos: float, bat: float, ambiente_: bool = False) -> Image.Image:
    cs = [rgb(c) for c in paleta.split()]
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 200), f"{h:02d}:{mi:02d}", font=fonte("Light", 112), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    d.text((C, 125), f"{h:02d}:{mi:02d}", font=fonte("Bold", 112), fill=(255, 255, 255), anchor="mm")
    d.text((C, 190), "SEX 31 OUT", font=fonte("Medium", 20), fill=(142, 142, 150), anchor="mm")
    fracs = [dia, (mi * 60 + s) / 3600, passos, bat]
    for i, (y, (rot, _), f) in enumerate(zip(YS, ROTULOS, fracs)):
        d.rounded_rectangle([BX, y, BX + BW, y + BH], radius=BH // 2, fill=(38, 38, 38))
        d.rounded_rectangle([BX, y, BX + MIN + (BW - MIN) * f, y + BH], radius=BH // 2, fill=cs[i])
        d.text((BX + 14, y + BH / 2), rot, font=fonte("Bold", 16), fill=(16, 16, 20), anchor="lm")
        d.text((BX + BW + 8, y + BH / 2), f"{round(f * 100)}%", font=fonte("Bold", 20), fill=(255, 255, 255), anchor="lm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Bars", "paleta_label": "Palette"}
    pt = {"watch_face_name": "Barras", "paleta_label": "Paleta"}
    strings_opcoes(en, pt, "paleta", {"sorvete": ("Sorbet", "Sorvete"), "neon": ("Neon", "Neon"), "terra": ("Earth", "Terra"), "mono": ("Mono", "Mono")})
    pv = [previa(PALETAS[0][1], 10, 8, 30, 0.42, 0.62, 0.88), previa(PALETAS[1][1], 21, 45, 10, 0.9, 0.2, 0.5), previa(PALETAS[2][1], 7, 15, 50, 0.3, 0.9, 0.15), previa(PALETAS[0][1], 10, 8, 0, 0.4, 0, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Sorvete", "Neon", "Terra", "Ambiente (AOD)"], cols=4, nomes_previa=["sorvete", "neon", "terra", "ambiente"])
