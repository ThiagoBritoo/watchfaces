"""Watchface "Parallax": quatro camadas de montanhas em profundidade sobre um céu em degradê; ao inclinar o pulso (Gyro) as camadas deslizam em
velocidades diferentes, criando efeito 3D. Hora grande no céu. Cinco paisagens. Original."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, colar, finalizar, grupo, hora, img, redondo, strings_opcoes, tpl, rgb

NOME = "parallax"
# céu topo, céu horizonte, cores das 4 camadas (do fundo à frente)
CENAS = [("crepusculo", (40, 20, 90), (255, 140, 110), [(120, 70, 130), (86, 50, 110), (54, 32, 86), (24, 14, 50)]),
         ("neve", (30, 70, 130), (200, 230, 255), [(150, 180, 220), (110, 145, 195), (70, 105, 160), (30, 55, 100)]),
         ("deserto", (240, 120, 70), (255, 220, 150), [(220, 140, 90), (190, 105, 70), (150, 76, 56), (96, 46, 40)]),
         ("floresta", (20, 60, 70), (150, 220, 190), [(90, 160, 140), (60, 124, 110), (36, 88, 80), (14, 50, 46)]),
         ("noite", (4, 8, 30), (40, 60, 130), [(30, 40, 90), (22, 30, 70), (14, 20, 50), (6, 10, 28)])]
LARG = 640                              # camadas mais largas que a tela para poder deslizar
FATORES = [0.18, 0.42, 0.8, 1.4]        # quanto cada camada desliza por grau de inclinação


def ceu(c0, c1) -> Image.Image:
    yy = np.linspace(0, 1, W)[:, None, None]
    a = np.array(c0, np.float32)[None, None, :] * (1 - yy) + np.array(c1, np.float32)[None, None, :] * yy
    out = np.dstack([np.broadcast_to(a, (W, W, 3)), np.full((W, W), 255, np.float32)])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def camada(i: int, cor) -> Image.Image:
    rng = np.random.default_rng(40 + i)
    xs = np.arange(LARG)
    base_y = 250 + i * 46
    y = base_y - (np.abs(np.sin(xs / (90 - i * 15) + i)) * (60 - i * 8) + np.abs(np.sin(xs / (31 - i * 4) + 2 * i)) * (22 - i * 3))
    y += np.convolve(rng.normal(0, 3, LARG), np.ones(7) / 7, mode="same") * (1 - i * 0.2)
    im = Image.new("RGBA", (LARG, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(x, float(yy)) for x, yy in zip(xs, y)] + [(LARG, W), (0, W)], fill=cor + (255,))
    return im


def xml() -> str:
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", '    <ListConfiguration id="cena" displayName="cena_label" defaultValue="crepusculo">'
                                       + "".join(f'<ListOption id="{k}" displayName="cena_{k}" />' for k, *_ in CENAS) + "</ListConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0) + '<ListConfiguration id="cena">')
    off = (LARG - W) // 2
    for k, *_ in CENAS:
        a(f'      <ListOption id="{k}"><Group name="c_{k}" x="0" y="0" width="{W}" height="{W}">' + img(0, 0, W, W, f"ceu_{k}"))
        for i, f in enumerate(FATORES):
            a(f'        <PartImage x="{-off}" y="0" width="{LARG}" height="{W}"><Image resource="cam_{k}_{i}" /><Gyro x="ACCELEROMETER_ANGLE_X * {f}" /></PartImage>')
        a("      </Group></ListOption>")
    a("    </ListConfiguration>")
    a("      " + hora(40, 56, 400, 130, "hh:mm", 108, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(110, 168, 260, 28, 20, "#ddffffff", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "SEMI_BOLD"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(40, 160, 400, 130, "hh:mm", 100, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, k: str, h: int, mi: int, inclin: float, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 225), f"{h:02d}:{mi:02d}", font=fonte("Light", 100), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    base.alpha_composite(A[f"ceu_{k}"])
    off = (LARG - W) // 2
    for i, f in enumerate(FATORES):
        colar(base, A[f"cam_{k}_{i}"], int(-off + inclin * f), 0)
    d = ImageDraw.Draw(base)
    d.text((C, 120), f"{h:02d}:{mi:02d}", font=fonte("Bold", 108), fill=(255, 255, 255), anchor="mm")
    d.text((C, 182), "SEX 31 OUT", font=fonte("SemiBold", 20), fill=(240, 240, 240), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Parallax", "cena_label": "Landscape"}
    pt = {"watch_face_name": "Parallax", "cena_label": "Paisagem"}
    nomes = {"crepusculo": ("Twilight", "Crepúsculo"), "neve": ("Snow", "Neve"), "deserto": ("Desert", "Deserto"), "floresta": ("Forest", "Floresta"), "noite": ("Night", "Noite")}
    strings_opcoes(en, pt, "cena", nomes)
    A: dict[str, Image.Image] = {}
    for k, c0, c1, cores in CENAS:
        A[f"ceu_{k}"] = ceu(c0, c1)
        for i, cor in enumerate(cores):
            A[f"cam_{k}_{i}"] = camada(i, cor)
    pv = [previa(A, "crepusculo", 10, 8, 0), previa(A, "neve", 10, 8, 40), previa(A, "deserto", 15, 30, -40), previa(A, "floresta", 7, 45, 25), previa(A, "noite", 23, 5, -20), previa(A, "crepusculo", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Crepúsculo (reto)", "Neve (inclinado +40)", "Deserto (inclinado -40)", "Floresta", "Noite", "Ambiente (AOD)"], cols=3,
                     nomes_previa=["crepusculo", "neve", "deserto", "floresta", "noite", "ambiente"])
