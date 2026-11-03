"""Watchface "Colmeia": favos hexagonais. Os 12 favos do anel externo são as horas (o da hora atual acende), os 6 do anel interno acendem de 10 em 10
minutos e a hora fica no favo central. Cinco paletas. Original."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, strings_opcoes, tint, tpl, colar

NOME = "colmeia"
PALETAS = [("mel", "#ffb703 #ffe29a"), ("coral", "#ff6b6b #ffc2b3"), ("oceano", "#2ec4ff #a8f0ff"), ("mata", "#4be37a #c4ffd6"), ("uva", "#b18cff #ecd9ff")]
S = 42
HEX = 2 * S + 6


def centro(q: int, r: int) -> tuple[float, float]:
    return C + S * math.sqrt(3) * (q + r / 2), C + S * 1.5 * r


def celulas() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    def dist(q, r):
        return max(abs(q), abs(r), abs(-q - r))
    anel1 = [(q, r) for q in range(-1, 2) for r in range(-1, 2) if dist(q, r) == 1]
    anel2 = [(q, r) for q in range(-2, 3) for r in range(-2, 3) if dist(q, r) == 2]

    def ang(c):
        x, y = centro(*c)
        return math.degrees(math.atan2(x - C, -(y - C))) % 360
    anel1.sort(key=ang)
    anel2.sort(key=ang)
    return [centro(*c) for c in anel1], [centro(*c) for c in anel2]


def hexagono(tipo: str) -> Image.Image:
    s = 4
    im = Image.new("RGBA", (HEX * s, HEX * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = HEX * s / 2
    R = (S - 3) * s
    pts = [(c + R * math.sin(math.radians(60 * k)), c - R * math.cos(math.radians(60 * k))) for k in range(6)]
    if tipo == "cheio":
        d.polygon(pts, fill=(255, 255, 255, 255))
    else:
        d.polygon(pts, outline=(255, 255, 255, 255), fill=(255, 255, 255, 36), width=2 * s)
    return im.resize((HEX, HEX), Image.LANCZOS)


def xml() -> str:
    p = lambda i: f"[CONFIGURATION.paleta.{i}]"  # noqa: E731
    a1, a2 = celulas()
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    todos = [(C, C)] + a1 + a2
    for x, y in todos:
        a("      " + img(round(x - HEX / 2), round(y - HEX / 2), HEX, HEX, "vazio", f' tintColor="{p(0)}" alpha="150"'))
    for k, (x, y) in enumerate(a2):
        a("      " + img(round(x - HEX / 2), round(y - HEX / 2), HEX, HEX, "cheio", f' tintColor="{p(0)}"', f'<Transform target="alpha" value="[HOUR_0_11] == {k} ? 255 : 0" />'))
    for k, (x, y) in enumerate(a1):
        a("      " + img(round(x - HEX / 2), round(y - HEX / 2), HEX, HEX, "cheio", f' tintColor="{p(1)}"', f'<Transform target="alpha" value="[MINUTE] &gt;= {10 * k} ? 255 : 0" />'))
    a("      " + hora(C - 34, C - 22, 68, 44, "hh:mm", 22, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(110, 440, 260, 24, 16, "#ff8e8e96", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for k, (x, y) in enumerate(a2):
        a("      " + img(round(x - HEX / 2), round(y - HEX / 2), HEX, HEX, "vazio", ' alpha="0"', f'<Transform target="alpha" value="[HOUR_0_11] == {k} ? 255 : 0" />'))
    a("      " + hora(C - 34, C - 22, 68, 44, "hh:mm", 22, "#ffc0c0c8", "MEDIUM", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, paleta: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    c0, c1 = (rgb(c) for c in paleta.split())
    a1, a2 = celulas()
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    for x, y in [(C, C)] + a1 + a2:
        if not ambiente_:
            v = tint(A["vazio"], c0)
            r_, g_, b_, al = v.split()
            colar(base, Image.merge("RGBA", (r_, g_, b_, al.point(lambda t: int(t * 150 / 255)))), round(x - HEX / 2), round(y - HEX / 2))
    for k, (x, y) in enumerate(a2):
        if h % 12 == k:
            colar(base, tint(A["vazio"] if ambiente_ else A["cheio"], c0 if not ambiente_ else (255, 255, 255)), round(x - HEX / 2), round(y - HEX / 2))
    if not ambiente_:
        for k, (x, y) in enumerate(a1):
            if mi >= 10 * k:
                colar(base, tint(A["cheio"], c1), round(x - HEX / 2), round(y - HEX / 2))
    d = ImageDraw.Draw(base)
    d.text((C, C), f"{h:02d}:{mi:02d}", font=fonte("Bold", 22), fill=(255, 255, 255) if not ambiente_ else (192, 192, 200), anchor="mm")
    if not ambiente_:
        d.text((C, 452), "SEX 31", font=fonte("Medium", 16), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Honeycomb", "paleta_label": "Palette"}
    pt = {"watch_face_name": "Colmeia", "paleta_label": "Paleta"}
    strings_opcoes(en, pt, "paleta", {"mel": ("Honey", "Mel"), "coral": ("Coral", "Coral"), "oceano": ("Ocean", "Oceano"), "mata": ("Forest", "Mata"), "uva": ("Grape", "Uva")})
    A = {"vazio": hexagono("vazio"), "cheio": hexagono("cheio")}
    pv = [previa(A, PALETAS[0][1], 10, 8), previa(A, PALETAS[1][1], 3, 45), previa(A, PALETAS[2][1], 12, 33), previa(A, PALETAS[4][1], 7, 59), previa(A, PALETAS[0][1], 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Mel 10:08", "Coral 03:45", "Oceano 12:33", "Uva 07:59", "Ambiente (AOD)"], cols=5, nomes_previa=["mel", "coral", "oceano", "uva", "ambiente"])
