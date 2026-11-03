"""Watchface "Poligonal": fundo de triângulos de baixo relevo (low-poly) em degradê, gerado com semente fixa, e hora grande e limpa por cima.
Cinco paletas. Original."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, finalizar, grupo, hora, img, redondo, strings_opcoes, tpl, rgb

NOME = "poligonal"
PALETAS = [("oceano", (10, 40, 110), (0, 200, 220)), ("brasa", (110, 10, 40), (255, 170, 40)), ("floresta", (6, 60, 50), (170, 230, 90)), ("uva", (50, 12, 110), (255, 110, 190)), ("grafite", (24, 26, 32), (120, 130, 150))]
N = 9


def fundo(c0, c1, semente=4) -> Image.Image:
    rng = np.random.default_rng(semente)
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    passo = (W + 120) / N
    pts = []
    for j in range(N + 1):
        linha = []
        for i in range(N + 1):
            x = -60 + i * passo + (rng.random() - 0.5) * passo * 0.7 * (0 < i < N)
            y = -60 + j * passo + (rng.random() - 0.5) * passo * 0.7 * (0 < j < N)
            linha.append((x, y))
        pts.append(linha)
    a0, a1 = np.array(c0, np.float32), np.array(c1, np.float32)
    for j in range(N):
        for i in range(N):
            p00, p10, p01, p11 = pts[j][i], pts[j][i + 1], pts[j + 1][i], pts[j + 1][i + 1]
            for tri in ((p00, p10, p01), (p10, p11, p01)):
                cx = sum(p[0] for p in tri) / 3
                cy = sum(p[1] for p in tri) / 3
                t = np.clip((cx * 0.6 + (W - cy) * 0.8) / (W * 1.4), 0, 1) + (rng.random() - 0.5) * 0.18
                cor = a0 + (a1 - a0) * float(np.clip(t, 0, 1))
                cor = np.clip(cor * (0.9 + 0.2 * rng.random()), 0, 255).astype(int)
                d.polygon([(p[0] * s, p[1] * s) for p in tri], fill=tuple(cor) + (255,))
    dark = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(dark).ellipse([C * s - 130 * s, C * s - 80 * s, C * s + 130 * s, C * s + 80 * s], fill=(0, 0, 0, 70))
    im.alpha_composite(dark)
    return im.resize((W, W), Image.LANCZOS)


def xml() -> str:
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", '    <ListConfiguration id="paleta" displayName="paleta_label" defaultValue="oceano">'
                                       + "".join(f'<ListOption id="{k}" displayName="paleta_{k}" />' for k, _, _ in PALETAS) + "</ListConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0) + '<ListConfiguration id="paleta">')
    for k, _, _ in PALETAS:
        a(f'      <ListOption id="{k}"><Group name="p_{k}" x="0" y="0" width="{W}" height="{W}">' + img(0, 0, W, W, f"fundo_{k}") + "</Group></ListOption>")
    a("    </ListConfiguration>")
    a("      " + hora(30, 150, 420, 140, "hh:mm", 112, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(110, 282, 260, 30, 22, "#ddffffff", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "SEMI_BOLD"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(30, 160, 420, 140, "hh:mm", 100, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, k: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 230), f"{h:02d}:{mi:02d}", font=fonte("Light", 100), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    base.alpha_composite(A[f"fundo_{k}"])
    d = ImageDraw.Draw(base)
    d.text((C, 220), f"{h:02d}:{mi:02d}", font=fonte("Bold", 112), fill=(255, 255, 255), anchor="mm")
    d.text((C, 297), "SEX 31 OUT", font=fonte("SemiBold", 22), fill=(230, 235, 240), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Low Poly", "paleta_label": "Palette"}
    pt = {"watch_face_name": "Poligonal", "paleta_label": "Paleta"}
    nomes = {"oceano": ("Ocean", "Oceano"), "brasa": ("Ember", "Brasa"), "floresta": ("Forest", "Floresta"), "uva": ("Grape", "Uva"), "grafite": ("Graphite", "Grafite")}
    strings_opcoes(en, pt, "paleta", nomes)
    A = {f"fundo_{k}": fundo(c0, c1) for k, c0, c1 in PALETAS}
    pv = [previa(A, k, 10 + i, 8 + i * 9) for i, (k, _, _) in enumerate(PALETAS)] + [previa(A, "oceano", 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, [n[1] for n in nomes.values()] + ["Ambiente (AOD)"], cols=3, nomes_previa=list(nomes) + ["ambiente"])
