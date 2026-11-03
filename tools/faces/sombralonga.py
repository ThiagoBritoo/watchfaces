"""Watchface "Sombra Longa": design plano (flat) com a hora em branco lançando uma sombra comprida na diagonal. Cinco combinações de cor. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rect, rgb, strings_opcoes, tpl

NOME = "sombralonga"
PALETAS = [("azul", "#2d7ff9 #ffffff #164fa8"), ("coral", "#ff5a5f #ffffff #b3282d"), ("menta", "#12b886 #ffffff #0a6a50"), ("amarelo", "#ffc83d #1d1a14 #c28b00"), ("roxo", "#7c4dff #ffffff #4527a8")]
N = 16


def xml() -> str:
    p = lambda i: f"[CONFIGURATION.paleta.{i}]"  # noqa: E731
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + rect(0, 0, W, W, p(0)))
    for k in range(N, 0, -1):
        a("      " + hora(30 + k, 150 + k, 420, 140, "hh:mm", 112, p(2), "BOLD", "CENTER"))
    a("      " + hora(30, 150, 420, 140, "hh:mm", 112, p(1), "BOLD", "CENTER"))
    for k in range(6, 0, -1):
        a("      " + tpl(110 + k, 300 + k, 260, 30, 22, p(2), "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "BOLD"))
    a("      " + tpl(110, 300, 260, 30, 22, p(1), "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "BOLD"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(30, 160, 420, 140, "hh:mm", 100, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(paleta: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    bg, tx, sh = (rgb(c) for c in paleta.split())
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255) if ambiente_ else bg + (255,))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 230), f"{h:02d}:{mi:02d}", font=fonte("Light", 100), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    for k in range(N, 0, -1):
        d.text((C + k, 220 + k), f"{h:02d}:{mi:02d}", font=fonte("Bold", 112), fill=sh, anchor="mm")
    d.text((C, 220), f"{h:02d}:{mi:02d}", font=fonte("Bold", 112), fill=tx, anchor="mm")
    for k in range(6, 0, -1):
        d.text((C + k, 315 + k), "SEX 31 OUT", font=fonte("Bold", 22), fill=sh, anchor="mm")
    d.text((C, 315), "SEX 31 OUT", font=fonte("Bold", 22), fill=tx, anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Long Shadow", "paleta_label": "Colors"}
    pt = {"watch_face_name": "Sombra Longa", "paleta_label": "Cores"}
    strings_opcoes(en, pt, "paleta", {"azul": ("Blue", "Azul"), "coral": ("Coral", "Coral"), "menta": ("Mint", "Menta"), "amarelo": ("Yellow", "Amarelo"), "roxo": ("Purple", "Roxo")})
    pv = [previa(PALETAS[i][1], 10 + i, 8 + i * 7) for i in range(5)] + [previa(PALETAS[0][1], 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Azul", "Coral", "Menta", "Amarelo", "Roxo", "Ambiente (AOD)"], cols=3, nomes_previa=["azul", "coral", "menta", "amarelo", "roxo", "ambiente"])
