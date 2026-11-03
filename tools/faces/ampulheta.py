"""Watchface "Ampulheta": uma ampulheta de vidro cuja areia escorre ao longo de cada hora (a de cima esvazia e a de baixo enche
conforme o minuto); a hora aparece ao lado. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_linear, grade, sombra, tela
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, colar, cor_config, finalizar, grupo, hora, img, redondo, rect, rgb, textos_acento, tint, tpl

NOME = "ampulheta"
CX = 240
TOPO, BASE, PESC = 84, 396, 240           # topo, base e altura do pescoço (y) da ampulheta
LARG = 170                                 # meia-largura máxima de cada bulbo
CAM_H = (BASE - TOPO) // 2 - 6             # altura de cada câmara


def perfil(y: float) -> float:
    """Meia-largura interna da ampulheta em y (afunila até o pescoço)."""
    t = (y - TOPO) / (PESC - TOPO) if y < PESC else (BASE - y) / (BASE - PESC)
    t = max(0.0, min(1.0, t))
    return 7 + (LARG - 7) * (math.sin(t * math.pi / 2)) ** 1.4 * 1.0


def vidro() -> Image.Image:
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ext, intr = [], []
    ys = np.linspace(TOPO, BASE, 200)
    for y in ys:
        ext.append((CX + perfil(y) * 0.62 + 6, y))
    pts = [(CX - (x - CX), y) for x, y in ext[::-1]]
    d.polygon([(x * s, y * s) for x, y in ext + pts], outline=(255, 255, 255, 235), fill=(255, 255, 255, 22), width=int(4 * s))
    d.rectangle([(CX - 110) * s, (TOPO - 14) * s, (CX + 110) * s, (TOPO + 2) * s], fill=(255, 255, 255, 235))
    d.rectangle([(CX - 110) * s, (BASE - 2) * s, (CX + 110) * s, (BASE + 14) * s], fill=(255, 255, 255, 235))
    # reflexo
    d.line([((CX - 62) * s, (TOPO + 24) * s), ((CX - 30) * s, (PESC - 20) * s)], fill=(255, 255, 255, 120), width=int(5 * s))
    return im.resize((W, W), Image.LANCZOS)


def areia(cheia_ate: float, de_cima: bool) -> Image.Image:
    """Não usada no relógio (a areia é feita com retângulos mascarados por imagem): máscara do interior da ampulheta."""
    return Image.new("RGBA", (1, 1))


def mascara_areia() -> Image.Image:
    """Interior da ampulheta em branco (alpha) para tingir e dimensionar; a areia vira dois PartImage cortados por Transform."""
    s = 3
    n = W * s
    im = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(im)
    ys = np.linspace(TOPO + 4, BASE - 4, 240)
    ext = [(CX + perfil(y) * 0.62 + 1, y) for y in ys]
    pts = [(CX - (x - CX), y) for x, y in ext[::-1]]
    d.polygon([(x * s, y * s) for x, y in ext + pts], fill=255)
    out = Image.new("RGBA", (n, n), (255, 255, 255, 0))
    out.putalpha(im)
    return out.resize((W, W), Image.LANCZOS)


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    fr = "(([MINUTE] * 60 + [SECOND]) / 3600)"
    a("    " + grupo("vivo", "", 0))
    # areia de cima: a máscara inteira fica recortada por uma faixa que esvazia; usamos dois grupos com 'height' animada via retângulo de corte (alpha mask não existe),
    # então a areia é a imagem da máscara (cheia) coberta por um retângulo preto que desce (cima) e sobe (baixo).
    a("      " + img(0, 0, W, W, "interior", f' tintColor="{ac}" alpha="235"'))
    # cobertura preta sobre a câmara superior: cresce de cima para baixo (esvazia)
    a("      " + rect(CX - 190, TOPO, 380, 100, "#ff000000", 0, "Fill", 2, f'<Transform target="height" value="{CAM_H} * {fr}" />'))
    # cobertura preta sobre a câmara inferior: encolhe de cima para baixo (a areia sobe)
    a("      " + rect(CX - 190, PESC, 380, 100, "#ff000000", 0, "Fill", 2, f'<Transform target="height" value="{CAM_H + 4} * (1 - {fr})" />'))
    a("      " + rect(CX - 1, PESC - 4, 2, 100, ac, 0, "Fill", 2, f'<Transform target="height" value="{CAM_H} - 4 + 8" />'))
    a("      " + img(0, 0, W, W, "vidro"))
    a("      " + hora(300, 150, 170, 90, "hh", 84, "#ffffffff", "BOLD", "CENTER"))
    a("      " + hora(300, 235, 170, 90, "mm", 84, ac, "BOLD", "CENTER"))
    a("      " + tpl(8, 190, 120, 28, 20, "#ff9aa0aa", "%s", ["[DAY_OF_WEEK_S]"], "MEDIUM", "END"))
    a("      " + tpl(8, 214, 120, 40, 34, "#ffffffff", "%s", ["[DAY]"], "BOLD", "END"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + img(0, 0, W, W, "vidro", ' alpha="150"'))
    a("      " + hora(300, 160, 170, 90, "hh", 72, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("      " + hora(300, 240, 170, 90, "mm", 72, "#ff8e8e96", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        v = A["vidro"].copy()
        r, g, b, al = v.split()
        base.alpha_composite(Image.merge("RGBA", (r, g, b, al.point(lambda t: int(t * 150 / 255)))))
        d.text((385, 205), f"{h:02d}", font=fonte("Light", 72), fill=(192, 192, 200), anchor="mm")
        d.text((385, 285), f"{mi:02d}", font=fonte("Light", 72), fill=(142, 142, 150), anchor="mm")
        return redondo(base)
    fr = (mi * 60 + s) / 3600
    inte = tint(A["interior"], ac)
    r, g, b, al = inte.split()
    inte = Image.merge("RGBA", (r, g, b, al.point(lambda t: int(t * 235 / 255))))
    base.alpha_composite(inte)
    d = ImageDraw.Draw(base)
    d.rectangle([CX - 190, TOPO, CX + 190, TOPO + CAM_H * fr], fill=(0, 0, 0))
    d.rectangle([CX - 190, PESC, CX + 190, PESC + (CAM_H + 4) * (1 - fr)], fill=(0, 0, 0))
    d.rectangle([CX - 1, PESC - 4, CX + 1, PESC + CAM_H + 4 - 4], fill=ac)
    base.alpha_composite(A["vidro"])
    d = ImageDraw.Draw(base)
    d.text((385, 195), f"{h:02d}", font=fonte("Bold", 84), fill=(255, 255, 255), anchor="mm")
    d.text((385, 280), f"{mi:02d}", font=fonte("Bold", 84), fill=ac, anchor="mm")
    d.text((120, 204), "SEX", font=fonte("Medium", 20), fill=(154, 160, 170), anchor="rm")
    d.text((120, 234), "31", font=fonte("Bold", 34), fill=(255, 255, 255), anchor="rm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Hourglass", "Ampulheta")
    A = {"vidro": vidro(), "interior": mascara_areia()}
    pv = [previa(A, "#f2c14e", 10, 8, 20), previa(A, "#33d6ff", 10, 30, 0), previa(A, "#ff5c93", 10, 52, 40), previa(A, "#f2c14e", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Minuto 8", "Minuto 30", "Minuto 52", "Ambiente (AOD)"], cols=4, nomes_previa=["m08", "m30", "m52", "ambiente"])
