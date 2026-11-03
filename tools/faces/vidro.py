"""Watchface "Vidro": fundo de malha de gradientes suaves e dois cartões de vidro fosco (translúcidos) com a hora e as informações do dia. Quatro
fundos. Original."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from wf.desenho import fonte, grad_radial
from wf.kit import C, W, cabecalho, colar, finalizar, grupo, hora, img, redondo, rect, strings_opcoes, tpl

NOME = "vidro"
FUNDOS = [("aurora", [(70, 20, 120), (20, 140, 200), (230, 80, 160), (20, 200, 140)]), ("ouro", [(60, 30, 10), (250, 170, 40), (200, 70, 30), (255, 220, 120)]),
          ("oceano", [(6, 30, 70), (30, 150, 230), (10, 210, 190), (120, 90, 255)]), ("rosa", [(60, 10, 40), (255, 100, 150), (255, 170, 90), (150, 70, 220)])]
CARTAO = (50, 112, 380, 170)
CARTAO2 = (80, 300, 320, 64)


def fundo(cores) -> Image.Image:
    base = np.zeros((W, W, 3), np.float32)
    base[:] = np.array(cores[0], np.float32)
    im = Image.fromarray(base.astype(np.uint8), "RGB").convert("RGBA")
    pos = [(120, 120), (380, 160), (200, 400), (400, 380)]
    for (x, y), cor in zip(pos, cores[1:] + [cores[1]]):
        b = grad_radial(W * 2, W, W, [(0, cor + (255,)), (150, cor + (160,)), (360, cor + (0,))])
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        cam.paste(b, (x - W, y - W))
        im.alpha_composite(cam)
    a = np.asarray(im).astype(np.float32)
    a[..., :3] += np.random.default_rng(2).normal(0, 1.5, a[..., :3].shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def xml() -> str:
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", '    <ListConfiguration id="fundo" displayName="fundo_label" defaultValue="aurora">'
                                       + "".join(f'<ListOption id="{k}" displayName="fundo_{k}" />' for k, _ in FUNDOS) + "</ListConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    x, y, w, h = CARTAO
    x2, y2, w2, h2 = CARTAO2
    a("    " + grupo("vivo", "", 0) + '<ListConfiguration id="fundo">')
    for k, _ in FUNDOS:
        a(f'      <ListOption id="{k}"><Group name="f_{k}" x="0" y="0" width="{W}" height="{W}">' + img(0, 0, W, W, f"fundo_{k}") + "</Group></ListOption>")
    a("    </ListConfiguration>")
    a("      " + rect(x, y, w, h, "#33ffffff", 34) + rect(x, y, w, h, "#66ffffff", 34, "Stroke", 2))
    a("      " + hora(x, y + 14, w, h - 28, "hh:mm", 104, "#ffffffff", "BOLD", "CENTER"))
    a("      " + rect(x2, y2, w2, h2, "#2effffff", 28) + rect(x2, y2, w2, h2, "#55ffffff", 28, "Stroke", 2))
    a("      " + tpl(x2 + 14, y2 + 14, 150, 36, 24, "#ffffffff", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "SEMI_BOLD", "START"))
    a("      " + tpl(x2 + w2 - 150, y2 + 14, 136, 36, 24, "#ffffffff", "%s%%", ["round([BATTERY_PERCENT])"], "SEMI_BOLD", "END"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + rect(x, y, w, h, "#77ffffff", 34, "Stroke", 2))
    a("      " + hora(x, y + 14, w, h - 28, "hh:mm", 96, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, k: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    x, y, w, hh = CARTAO
    x2, y2, w2, h2 = CARTAO2
    if ambiente_:
        d = ImageDraw.Draw(base)
        d.rounded_rectangle([x, y, x + w, y + hh], radius=34, outline=(119, 119, 119), width=2)
        d.text((x + w / 2, y + hh / 2), f"{h:02d}:{mi:02d}", font=fonte("Light", 96), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    base.alpha_composite(A[f"fundo_{k}"])
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    d.rounded_rectangle([x, y, x + w, y + hh], radius=34, fill=(255, 255, 255, 51), outline=(255, 255, 255, 102), width=2)
    d.rounded_rectangle([x2, y2, x2 + w2, y2 + h2], radius=28, fill=(255, 255, 255, 46), outline=(255, 255, 255, 85), width=2)
    base.alpha_composite(cam)
    d = ImageDraw.Draw(base)
    d.text((x + w / 2, y + hh / 2 + 4), f"{h:02d}:{mi:02d}", font=fonte("Bold", 104), fill=(255, 255, 255), anchor="mm")
    d.text((x2 + 24, y2 + h2 / 2), "SEX 31", font=fonte("SemiBold", 24), fill=(255, 255, 255), anchor="lm")
    d.text((x2 + w2 - 24, y2 + h2 / 2), "89%", font=fonte("SemiBold", 24), fill=(255, 255, 255), anchor="rm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Glass", "fundo_label": "Background"}
    pt = {"watch_face_name": "Vidro", "fundo_label": "Fundo"}
    strings_opcoes(en, pt, "fundo", {"aurora": ("Aurora", "Aurora"), "ouro": ("Gold", "Ouro"), "oceano": ("Ocean", "Oceano"), "rosa": ("Rose", "Rosa")})
    A = {f"fundo_{k}": fundo(c) for k, c in FUNDOS}
    pv = [previa(A, "aurora", 10, 8), previa(A, "ouro", 21, 45), previa(A, "oceano", 3, 12), previa(A, "rosa", 7, 30), previa(A, "aurora", 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Aurora", "Ouro", "Oceano", "Rosa", "Ambiente (AOD)"], cols=5, nomes_previa=["aurora", "ouro", "oceano", "rosa", "ambiente"])
