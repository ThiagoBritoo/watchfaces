"""Watchface "Synthwave": pôr do sol retrô-futurista com sol listrado, horizonte e chão em grade de perspectiva; hora grande por cima.
Três paisagens (poente, gelo, miami). Arte e código originais."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, reduzir_por, tela
from wf.kit import C, W, cabecalho, finalizar, grupo, hora, img, redondo, rgb, tpl

NOME = "synthwave"
HOR = 292
# topo, horizonte, sol_topo, sol_base, grade
CENAS = [("poente", (14, 0, 40), (120, 20, 110), (255, 226, 80), (255, 60, 160), (255, 70, 200)),
         ("gelo", (4, 8, 36), (30, 60, 140), (170, 240, 255), (130, 90, 255), (90, 200, 255)),
         ("miami", (24, 4, 50), (200, 40, 150), (255, 150, 200), (60, 220, 230), (255, 100, 220))]


def cena(topo, horiz, st, sb, grade) -> Image.Image:
    s = SS
    n = W * s
    yy = np.linspace(0, 1, n)[:, None]
    ceu_t = np.clip((yy * W) / HOR, 0, 1)
    cor_ceu = np.array(topo, np.float32)[None, None, :] * (1 - ceu_t[..., None]) + np.array(horiz, np.float32)[None, None, :] * ceu_t[..., None]
    img_ = np.repeat(cor_ceu, n, axis=1)
    chao = (np.arange(n)[:, None] >= HOR * s)
    img_ = np.where(chao[..., None], np.array((8, 2, 22), np.float32)[None, None, :], img_)
    im = Image.fromarray(np.clip(img_, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(3)
    for _ in range(60):                                         # estrelas
        x, y = rng.integers(0, n), rng.integers(0, int(150 * s))
        r = rng.choice([1, 1, 2]) * s * 0.6
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(rng.integers(80, 220))))
    # sol com listras
    cx, cy, R = C * s, 232 * s, 112 * s
    sol = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ys = np.arange(n)[:, None]
    xs = np.arange(n)[None, :]
    dentro = ((xs - cx) ** 2 + (ys - cy) ** 2) <= R * R
    t = np.clip((ys - (cy - R)) / (2 * R), 0, 1)
    cor = np.array(st, np.float32)[None, None, :] * (1 - t[..., None]) + np.array(sb, np.float32)[None, None, :] * t[..., None]
    a = (dentro & (ys < HOR * s)).astype(np.float32) * 255
    # listras (cortes) na metade de baixo
    for k in range(7):
        y0 = cy + 6 * s + k * 17 * s
        esp = (2 + k * 1.7) * s
        a[int(y0):int(y0 + esp), :] = 0
    sol = Image.fromarray(np.dstack([np.clip(np.broadcast_to(cor, (n, n, 3)), 0, 255), a]).astype(np.uint8), "RGBA")
    glow = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    im.alpha_composite(sol)
    d = ImageDraw.Draw(im)
    # linha do horizonte e grade
    d.line([(0, HOR * s), (n, HOR * s)], fill=grade + (255,), width=3 * s)
    for k in range(-14, 15):
        x_fim = C * s + k * 70 * s
        d.line([(C * s + k * 7 * s, HOR * s), (x_fim, W * s)], fill=grade + (200,), width=int(1.6 * s))
    for j in range(1, 9):
        y = HOR + (W - HOR) * (j / 8) ** 2.1
        d.line([(0, y * s), (n, y * s)], fill=grade + (170,), width=int(1.6 * s))
    return reduzir_por(im)


def xml() -> str:
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", '    <ListConfiguration id="cena" displayName="cena_label" defaultValue="poente">'
                                      + "".join(f'<ListOption id="{k}" displayName="cena_{k}" />' for k, *_ in CENAS) + "</ListConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0) + '<ListConfiguration id="cena">')
    for k, *_ in CENAS:
        a(f'      <ListOption id="{k}"><Group name="c_{k}" x="0" y="0" width="{W}" height="{W}">' + img(0, 0, W, W, f"cena_{k}") + "</Group></ListOption>")
    a("    </ListConfiguration>")
    a("      " + hora(30, 130, 420, 130, "hh:mm", 100, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(110, 388, 260, 28, 20, "#ffffd6f2", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "SEMI_BOLD"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw x="0" y="0" width="{W}" height="{W}"><Rectangle x="0" y="{HOR}" width="{W}" height="2"><Fill color="#88ffffff" /></Rectangle></PartDraw>')
    a("      " + hora(30, 150, 420, 130, "hh:mm", 92, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, id_: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.line([(0, HOR), (W, HOR)], fill=(136, 136, 136), width=2)
        d.text((C, 215), f"{h:02d}:{mi:02d}", font=fonte("Light", 92), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    base.alpha_composite(A[f"cena_{id_}"])
    d = ImageDraw.Draw(base)
    d.text((C + 3, 198), f"{h:02d}:{mi:02d}", font=fonte("Bold", 100), fill=(0, 0, 0, 255), anchor="mm")
    d.text((C, 195), f"{h:02d}:{mi:02d}", font=fonte("Bold", 100), fill=(255, 255, 255), anchor="mm")
    d.text((C, 402), "SEX 31 OUT", font=fonte("SemiBold", 20), fill=(255, 214, 242), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Synthwave", "cena_label": "Scene", "cena_poente": "Sunset", "cena_gelo": "Ice", "cena_miami": "Miami"}
    pt = {"watch_face_name": "Synthwave", "cena_label": "Cenário", "cena_poente": "Poente", "cena_gelo": "Gelo", "cena_miami": "Miami"}
    A = {f"cena_{k}": cena(t, h, st, sb, g) for k, t, h, st, sb, g in CENAS}
    pv = [previa(A, "poente", 10, 8), previa(A, "gelo", 21, 45), previa(A, "miami", 3, 12), previa(A, "poente", 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Poente", "Gelo", "Miami", "Ambiente (AOD)"], cols=4, nomes_previa=["poente", "gelo", "miami", "ambiente"])
