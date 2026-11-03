"""Watchface "Duo": tela dividida em dois blocos de cor; a hora no bloco da esquerda e o minuto no da direita, em números enormes.
Uma barra no pé mostra os segundos. Cinco pares de cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rect, rgb, strings_opcoes, tpl

NOME = "duo"
# esquerda, direita, texto esquerda, texto direita
PARES = [("coral", "#ff5a4d #1c1c24 #ffffff #ff8a7f"), ("oceano", "#1f6feb #f5c542 #ffffff #1b2a52"), ("menta", "#12b886 #101820 #08201a #6ff0c8"), ("uva", "#7b3fe4 #f4e9ff #ffffff #2c1457"), ("sol", "#ffc233 #14120d #14120d #ffc233")]


def xml() -> str:
    p = lambda i: f"[CONFIGURATION.par.{i}]"  # noqa: E731
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("par", "par_label", PARES), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + rect(0, 0, C, W, p(0)) + rect(C, 0, C, W, p(1)))
    a("      " + hora(0, 110, C, 250, "hh", 132, p(2), "BLACK", "CENTER"))
    a("      " + hora(C, 110, C, 250, "mm", 132, p(3), "BLACK", "CENTER"))
    a("      " + tpl(90, 58, 300, 30, 22, p(2), "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "SEMI_BOLD"))
    a("      " + rect(C - 100, 396, 200, 8, "#44000000", 4) + rect(C - 100, 396, 200, 8, "#ffffffff", 4, "Fill", 2, '<Transform target="width" value="200 * [SECOND] / 60" />'))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw x="0" y="0" width="{W}" height="{W}"><Rectangle x="{C - 1}" y="0" width="2" height="{W}"><Fill color="#55ffffff" /></Rectangle></PartDraw>')
    a("      " + hora(0, 140, C, 220, "hh", 110, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("      " + hora(C, 140, C, 220, "mm", 110, "#ff8e8e96", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(par: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c0, c1, t0, t1 = (rgb(c) for c in par.split())
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.line([(C, 0), (C, W)], fill=(85, 85, 85), width=2)
        d.text((C / 2, 250), f"{h:02d}", font=fonte("Light", 110), fill=(192, 192, 200), anchor="mm")
        d.text((C * 1.5, 250), f"{mi:02d}", font=fonte("Light", 110), fill=(142, 142, 150), anchor="mm")
        return redondo(base)
    d.rectangle([0, 0, C, W], fill=c0)
    d.rectangle([C, 0, W, W], fill=c1)
    d.text((C / 2, 245), f"{h:02d}", font=fonte("Black", 132), fill=t0, anchor="mm")
    d.text((C * 1.5, 245), f"{mi:02d}", font=fonte("Black", 132), fill=t1, anchor="mm")
    d.text((C, 73), "SEX 31 OUT", font=fonte("SemiBold", 22), fill=t0, anchor="mm")
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(cam).rounded_rectangle([C - 100, 396, C + 100, 404], radius=4, fill=(0, 0, 0, 68))
    base.alpha_composite(cam)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([C - 100, 396, C - 100 + max(8, 200 * s / 60), 404], radius=4, fill=(255, 255, 255))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Duo", "par_label": "Colors"}
    pt = {"watch_face_name": "Duo", "par_label": "Cores"}
    strings_opcoes(en, pt, "par", {"coral": ("Coral", "Coral"), "oceano": ("Ocean", "Oceano"), "menta": ("Mint", "Menta"), "uva": ("Grape", "Uva"), "sol": ("Sun", "Sol")})
    pv = [previa(PARES[0][1], 10, 8, 20), previa(PARES[1][1], 3, 45, 40), previa(PARES[2][1], 18, 22, 5), previa(PARES[3][1], 7, 15, 50), previa(PARES[4][1], 12, 0, 30), previa(PARES[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Coral", "Oceano", "Menta", "Uva", "Sol", "Ambiente (AOD)"], cols=3, nomes_previa=["coral", "oceano", "menta", "uva", "sol", "ambiente"])
