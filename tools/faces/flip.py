"""Watchface "Flip": relógio de cartões (dois cartões grandes com a hora e o minuto, linha de dobradiça ao meio), segundos numa barra fina
e data no alto. Cinco paletas. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rect, rgb, strings_opcoes, tpl

NOME = "flip"
PALETAS = [("grafite", "#222226 #f4f4f6 #ff7a2f"), ("marfim", "#ece8df #1c1c20 #d6502b"), ("azul", "#16233f #eaf1ff #4aa8ff"), ("vinho", "#3a1520 #ffe9ee #ff6b8a"), ("mata", "#142a1d #e8fff0 #4be37a")]
CARD = (146, 196)
POS = [(C - 12 - CARD[0], 118), (C + 12, 118)]


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    p = lambda i: f"[CONFIGURATION.paleta.{i}]"  # noqa: E731
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + tpl(110, 60, 260, 32, 22, p(2), "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "SEMI_BOLD"))
    for (x, y), fmt in zip(POS, ("hh", "mm")):
        w, h = CARD
        a("      " + rect(x, y, w, h, p(0), 18))
        a("      " + rect(x, y + h // 2, w, h // 2, "#26000000", 0))
        a("      " + hora(x, y + 8, w, h - 16, fmt, 108, p(1), "BOLD", "CENTER"))
        a("      " + rect(x, y + h // 2 - 1, w, 3, "#cc000000", 0))
        a("      " + rect(x - 3, y + h // 2 - 8, 8, 16, "#ff0b0b0d", 4) + rect(x + w - 5, y + h // 2 - 8, 8, 16, "#ff0b0b0d", 4))
    a("      " + rect(C - 120, 338, 240, 8, "#33808080", 4))
    a("      " + rect(C - 120, 338, 240, 8, p(2), 4, "Fill", 2, '<Transform target="width" value="240 * [SECOND] / 60" />'))
    a("      " + tpl(110, 358, 260, 28, 20, "#ff8e8e96", "%s", ["[AMPM_STRING]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for (x, y), fmt in zip(POS, ("hh", "mm")):
        w, h = CARD
        a("      " + rect(x, y, w, h, "#88ffffff", 18, "Stroke", 2))
        a("      " + hora(x, y + 8, w, h - 16, fmt, 100, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(paleta: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c0, c1, c2 = (rgb(c) for c in paleta.split())
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    vals = [f"{h:02d}", f"{mi:02d}"]
    if not ambiente_:
        d.text((C, 76), "SEX 31 OUT", font=fonte("SemiBold", 22), fill=c2, anchor="mm")
    for (x, y), v in zip(POS, vals):
        w, hh = CARD
        if ambiente_:
            d.rounded_rectangle([x, y, x + w, y + hh], radius=18, outline=(136, 136, 136), width=2)
            d.text((x + w / 2, y + hh / 2 + 2), v, font=fonte("Light", 100), fill=(192, 192, 200), anchor="mm")
            continue
        d.rounded_rectangle([x, y, x + w, y + hh], radius=18, fill=c0)
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(cam).rectangle([x, y + hh // 2, x + w, y + hh - 6], fill=(0, 0, 0, 38))
        base.alpha_composite(cam)
        d = ImageDraw.Draw(base)
        d.text((x + w / 2, y + hh / 2 + 4), v, font=fonte("Bold", 108), fill=c1, anchor="mm")
        d.rectangle([x, y + hh // 2 - 1, x + w, y + hh // 2 + 1], fill=(0, 0, 0))
        d.rounded_rectangle([x - 3, y + hh // 2 - 8, x + 5, y + hh // 2 + 8], radius=4, fill=(11, 11, 13))
        d.rounded_rectangle([x + w - 5, y + hh // 2 - 8, x + w + 3, y + hh // 2 + 8], radius=4, fill=(11, 11, 13))
    if not ambiente_:
        d.rounded_rectangle([C - 120, 338, C + 120, 346], radius=4, fill=(128, 128, 128, 51) if False else (50, 50, 50))
        d.rounded_rectangle([C - 120, 338, C - 120 + 240 * s / 60, 346], radius=4, fill=c2)
        d.text((C, 372), "PM" if h >= 12 else "AM", font=fonte("Medium", 20), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Flip", "paleta_label": "Cards"}
    pt = {"watch_face_name": "Flip", "paleta_label": "Cartões"}
    strings_opcoes(en, pt, "paleta", {"grafite": ("Graphite", "Grafite"), "marfim": ("Ivory", "Marfim"), "azul": ("Blue", "Azul"), "vinho": ("Wine", "Vinho"), "mata": ("Forest", "Mata")})
    pv = [previa(PALETAS[0][1], 10, 8, 20), previa(PALETAS[1][1], 3, 45, 40), previa(PALETAS[2][1], 18, 22, 5), previa(PALETAS[3][1], 7, 15, 50), previa(PALETAS[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Grafite", "Marfim", "Azul", "Vinho", "Ambiente (AOD)"], cols=5, nomes_previa=["grafite", "marfim", "azul", "vinho", "ambiente"])
