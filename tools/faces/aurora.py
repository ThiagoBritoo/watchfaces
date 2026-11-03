"""Watchface "Aurora": bolhas de cor desfocadas que flutuam devagar (a posição depende da hora do dia) sobre fundo escuro, com a hora
em texto fino por cima. Abstrata e calma. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial
from wf.kit import C, W, cabecalho, colar, cor_config, finalizar, grupo, hora, img, redondo, rgb, strings_opcoes, tint, tpl

NOME = "aurora"
PALETAS = [("boreal", "#2de2a6 #3a7bff #b45cff #0a1020"), ("poente", "#ff7a59 #ff3d81 #ffb347 #1a0a14"), ("oceano", "#27d3ff #3a5bff #28ffd0 #06121c"), ("lavanda", "#c79bff #7f8cff #ff9ad5 #120c1c")]
BOLHA = 380


def bolha() -> Image.Image:
    return grad_radial(BOLHA, BOLHA / 2, BOLHA / 2, [(0, (255, 255, 255, 235)), (BOLHA * 0.18, (255, 255, 255, 190)), (BOLHA * 0.34, (255, 255, 255, 80)), (BOLHA / 2, (255, 255, 255, 0))])


def pos(i: int, t: float) -> tuple[float, float]:
    """t em horas (0..24): cada bolha percorre uma elipse lenta."""
    ang = t / 24 * 2 * math.pi * (1 + i) + i * 2.1
    return C + 70 * math.cos(ang) * (1 + 0.3 * i), C + 60 * math.sin(ang * 0.8 + i)


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a(f'      <PartDraw {full}><Rectangle x="0" y="0" width="{W}" height="{W}"><Fill color="[CONFIGURATION.paleta.3]" /></Rectangle></PartDraw>')
    for i in range(3):
        ang = f"([SECONDS_IN_DAY] / 86400 * 6.2832 * {1 + i} + {i * 2.1})"
        a("      " + img(C - BOLHA // 2, C - BOLHA // 2, BOLHA, BOLHA, "bolha", f' tintColor="[CONFIGURATION.paleta.{i}]" alpha="200"',
                         f'<Transform target="x" value="{C - BOLHA // 2} + 70 * cos({ang}) * {1 + 0.3 * i}" /><Transform target="y" value="{C - BOLHA // 2} + 60 * sin({ang} * 0.8 + {i})" />'))
    a("      " + hora(30, 150, 420, 140, "hh:mm", 112, "#ffffffff", "LIGHT", "CENTER"))
    a("      " + tpl(110, 278, 260, 30, 22, "#ddffffff", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(30, 160, 420, 140, "hh:mm", 100, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, paleta: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    cs = [rgb(c) for c in paleta.split()]
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255) if ambiente_ else cs[3] + (255,))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 230), f"{h:02d}:{mi:02d}", font=fonte("Light", 100), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    t = h + mi / 60
    for i in range(3):
        x, y = pos(i, t)
        b = tint(A["bolha"], cs[i])
        r, g, bl, al = b.split()
        b = Image.merge("RGBA", (r, g, bl, al.point(lambda v: int(v * 200 / 255))))
        colar(base, b, int(x - BOLHA / 2), int(y - BOLHA / 2))
    d = ImageDraw.Draw(base)
    d.text((C, 220), f"{h:02d}:{mi:02d}", font=fonte("Light", 112), fill=(255, 255, 255), anchor="mm")
    d.text((C, 293), "SEX 31 OUT", font=fonte("Medium", 22), fill=(230, 230, 236), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Aurora", "paleta_label": "Palette"}
    pt = {"watch_face_name": "Aurora", "paleta_label": "Paleta"}
    strings_opcoes(en, pt, "paleta", {"boreal": ("Boreal", "Boreal"), "poente": ("Sunset", "Poente"), "oceano": ("Ocean", "Oceano"), "lavanda": ("Lavender", "Lavanda")})
    A = {"bolha": bolha()}
    pv = [previa(A, PALETAS[0][1], 10, 8), previa(A, PALETAS[1][1], 17, 45), previa(A, PALETAS[2][1], 3, 20), previa(A, PALETAS[3][1], 22, 5), previa(A, PALETAS[0][1], 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Boreal", "Poente", "Oceano", "Lavanda", "Ambiente (AOD)"], cols=5, nomes_previa=["boreal", "poente", "oceano", "lavanda", "ambiente"])
