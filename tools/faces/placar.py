"""Watchface "Placar": placar de jogo: a hora no time da casa e os minutos no visitante, relógio de partida (segundos) embaixo e a data como "rodada".
Cinco paletas de times. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rect, rgb, strings_opcoes, tpl

NOME = "placar"
PALETAS = [("verde", "#0b3d2a #f4f1e8 #ffd23d #12b886"), ("azul", "#0a1f4d #ffffff #ffd23d #3d8bff"), ("vinho", "#3a0f1e #fff0e8 #ffb347 #e5446d"), ("noite", "#101114 #f2f2f2 #ff7a2f #33d6ff")]


def xml() -> str:
    p = lambda i: f"[CONFIGURATION.paleta.{i}]"  # noqa: E731
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + rect(0, 0, W, W, p(0)))
    a("      " + rect(44, 112, 188, 220, "#26ffffff", 22) + rect(248, 112, 188, 220, "#26ffffff", 22))
    a("      " + rect(44, 112, 188, 8, p(3), 4) + rect(248, 112, 188, 8, p(2), 4))
    a("      " + tpl(44, 76, 188, 30, 20, p(3), "%s", ["&quot;HORA&quot;"], "BOLD") + tpl(248, 76, 188, 30, 20, p(2), "%s", ["&quot;MINUTO&quot;"], "BOLD"))
    a("      " + hora(44, 124, 188, 200, "hh", 112, p(1), "BLACK", "CENTER"))
    a("      " + hora(248, 124, 188, 200, "mm", 112, p(1), "BLACK", "CENTER"))
    a("      " + tpl(C - 20, 188, 40, 60, 54, p(2), "%s", ["&quot;x&quot;"], "BLACK"))
    a("      " + tpl(100, 346, 280, 36, 28, p(1), "%s", ["&quot;TEMPO &quot; + [SECOND_Z]"], "BOLD"))
    a("      " + tpl(110, 386, 260, 28, 20, p(2), "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "SEMI_BOLD"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(30, 150, 210, 180, "hh", 100, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("      " + hora(240, 150, 210, 180, "mm", 100, "#ff8e8e96", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(paleta: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c0, c1, c2, c3 = (rgb(c) for c in paleta.split())
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255) if ambiente_ else c0 + (255,))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((135, 240), f"{h:02d}", font=fonte("Light", 100), fill=(192, 192, 200), anchor="mm")
        d.text((345, 240), f"{mi:02d}", font=fonte("Light", 100), fill=(142, 142, 150), anchor="mm")
        return redondo(base)
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    dc = ImageDraw.Draw(cam)
    dc.rounded_rectangle([44, 112, 232, 332], radius=22, fill=(255, 255, 255, 38))
    dc.rounded_rectangle([248, 112, 436, 332], radius=22, fill=(255, 255, 255, 38))
    base.alpha_composite(cam)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([44, 112, 232, 120], radius=4, fill=c3)
    d.rounded_rectangle([248, 112, 436, 120], radius=4, fill=c2)
    d.text((138, 91), "HORA", font=fonte("Bold", 20), fill=c3, anchor="mm")
    d.text((342, 91), "MINUTO", font=fonte("Bold", 20), fill=c2, anchor="mm")
    d.text((138, 232), f"{h:02d}", font=fonte("Black", 112), fill=c1, anchor="mm")
    d.text((342, 232), f"{mi:02d}", font=fonte("Black", 112), fill=c1, anchor="mm")
    d.text((C, 218), "x", font=fonte("Black", 54), fill=c2, anchor="mm")
    d.text((C, 364), f"TEMPO {s:02d}", font=fonte("Bold", 28), fill=c1, anchor="mm")
    d.text((C, 400), "SEX 31 OUT", font=fonte("SemiBold", 20), fill=c2, anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Scoreboard", "paleta_label": "Teams"}
    pt = {"watch_face_name": "Placar", "paleta_label": "Times"}
    strings_opcoes(en, pt, "paleta", {"verde": ("Green", "Verde"), "azul": ("Blue", "Azul"), "vinho": ("Wine", "Vinho"), "noite": ("Night", "Noite")})
    pv = [previa(PALETAS[0][1], 10, 8, 20), previa(PALETAS[1][1], 3, 45, 40), previa(PALETAS[2][1], 18, 22, 5), previa(PALETAS[3][1], 7, 15, 50), previa(PALETAS[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Verde", "Azul", "Vinho", "Noite", "Ambiente (AOD)"], cols=5, nomes_previa=["verde", "azul", "vinho", "noite", "ambiente"])
