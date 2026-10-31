"""Assets da watchface "Cronos" (cronógrafo clássico realista).

Espaço de coordenadas: 480x480 (Galaxy Watch6 Classic 47 mm). O relógio de 43 mm
(432 px) recebe a mesma arte reescalada pelo sistema.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from wf.desenho import (SS, Cor, com_mascara, escurecer, fonte, grad_conico, grad_linear, grad_radial,
                        grade, mascara_anel, metal_paradas, polar, reduzir_por, ruido, sombra,
                        tela, texto_centrado)

W = 480
C = W // 2
R_DIAL = 200
SUBDIAIS = {"esq": (C - 88, C), "dir": (C + 88, C), "baixo": (C, C + 88)}
R_SUB = 48
GEAR_C = (C, 112)
GEAR_R = 24


@dataclass(frozen=True)
class Tema:
    id: str
    nome: str
    base: Cor
    padrao: str
    bisel: Cor
    num_bisel: Cor
    acento: Cor
    metal: tuple[Cor, Cor, Cor]
    texto: Cor
    lume: Cor
    claro: bool = False


TEMAS: dict[str, Tema] = {
    "rc": Tema("rc", "Preto e vermelho", (16, 16, 18), "carbono", (12, 12, 14), (236, 236, 240),
               (224, 38, 43), ((252, 252, 255), (170, 172, 180), (70, 72, 80)), (236, 236, 240),
               (226, 240, 204)),
    "frost": Tema("frost", "Branco, bronze e azul", (236, 238, 242), "sunburst", (222, 226, 232),
                  (36, 50, 72), (46, 112, 181), ((240, 200, 152), (186, 136, 86), (92, 62, 34)),
                  (30, 40, 56), (190, 218, 240), claro=True),
    "noir": Tema("noir", "Preto e dourado", (10, 10, 12), "guilloche", (8, 8, 10), (214, 178, 102),
                 (212, 175, 95), ((255, 234, 166), (206, 166, 86), (98, 74, 30)), (232, 216, 172),
                 (242, 228, 172)),
}


# ------------------------------------------------------------------ texturas
def _padrao(t: Tema, n: int) -> Image.Image:
    xx, yy = grade(n)
    c = n / 2
    base = np.array(t.base, np.float32)
    ang = np.arctan2(yy - c, xx - c)
    d = np.hypot(xx - c, yy - c) / (R_DIAL * SS)
    if t.padrao == "carbono":
        cel = 5 * SS
        u, v = (xx + yy) / cel, (xx - yy) / cel
        xadrez = (np.floor(u) + np.floor(v)) % 2
        fino = 0.5 + 0.5 * np.sin(2 * np.pi * u) * np.sin(2 * np.pi * v)
        mod = 0.78 + 0.62 * (0.5 * xadrez + 0.5 * fino)
        brilho = 0.20
    elif t.padrao == "guilloche":
        p = 7 * SS
        tri = lambda a: 1 - np.abs(2 * (a % 1) - 1)  # noqa: E731
        mod = 0.74 + 0.55 * tri(xx / p) * tri(yy / p)
        brilho = 0.16
    else:  # sunburst: raios finos radiais, como metal escovado
        rng = np.random.default_rng(7)
        r = rng.standard_normal(1440).astype(np.float32)
        r = np.convolve(np.r_[r[-4:], r, r[:4]], np.ones(5) / 5, "same")[4:-4]
        k = np.interp((ang + np.pi) / (2 * np.pi) * 1440, np.arange(1440), r, period=1440)
        mod = 0.97 + 0.06 * np.clip(k, -2, 2)
        brilho = 0.10
    sheen = 0.5 + 0.5 * np.cos(2 * (ang + math.radians(135)))  # dois reflexos opostos
    sheen *= np.clip(1.05 - d, 0, 1)
    vinheta = 1 - (0.10 if t.claro else 0.40) * np.clip(d, 0, 1) ** 2.2
    rgb = base * (mod * vinheta)[..., None] * (1 + brilho * sheen[..., None])
    rgb += (ruido(n, 11, 1.6))[..., None]
    a = np.dstack([np.clip(rgb, 0, 255), np.full((n, n), 255, np.float32)])
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def _anel_metal(n: int, t: Tema, r_ext: float, r_int: float, rot: float = 0) -> Image.Image:
    g = grad_conico(n, n / 2, n / 2, metal_paradas(*t.metal), rot)
    return com_mascara(g, mascara_anel(n, n / 2, n / 2, r_ext * SS, r_int * SS))


def _linha(d: ImageDraw.ImageDraw, c: float, ang: float, r0: float, r1: float, larg: float, cor) -> None:
    d.line([polar(c, c, r0 * SS, ang), polar(c, c, r1 * SS, ang)], fill=cor, width=max(1, int(larg * SS)))


# ----------------------------------------------------------------- aplicados
def _barra_aplicada(t: Tema, larg: float, comp: float) -> Image.Image:
    """Índice aplicado: metal facetado + massa luminosa (lume) no miolo."""
    w, h = int(larg * SS) + 8, int(comp * SS) + 8
    p = 4
    g = grad_linear(max(w, h), (p, 0), (w - p, 0),
                    [(0, t.metal[2]), (0.28, t.metal[0]), (0.55, t.metal[1]), (1, t.metal[2])]).crop((0, 0, w, h))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rectangle([p, p, w - p - 1, h - p - 1], fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(g, (0, 0), m)
    d = ImageDraw.Draw(out)
    d.rectangle([p, p, w - p - 1, h - p - 1], outline=(0, 0, 0, 120), width=max(1, SS // 2))
    ins = max(2, int(larg * SS * 0.26))
    d.rectangle([p + ins, p + ins, w - p - ins - 1, h - p - ins - 1], fill=(*t.lume, 255))
    d.rectangle([p + ins, p + ins, w - p - ins - 1, h - p - ins - 1], outline=(0, 0, 0, 90), width=1)
    d.line([(p + 1, p + 1), (p + 1, h - p - 2)], fill=(255, 255, 255, 150), width=1)  # brilho da quina
    return out


def _colar_polar(camada: Image.Image, peca: Image.Image, cx: float, cy: float, raio: float, ang: float,
                 sombra_px: tuple[float, float, float, float] | None = (2.5, 3.5, 2.5, 0.6)) -> None:
    giro = peca.rotate(-ang, expand=True, resample=Image.BICUBIC)
    x, y = polar(cx, cy, raio * SS, ang)
    pos = (int(round(x - giro.width / 2)), int(round(y - giro.height / 2)))
    if sombra_px:
        dx, dy, bl, op = sombra_px
        s = sombra(giro, dx * SS, dy * SS, bl * SS, op)
        camada.alpha_composite(s, pos)
    camada.alpha_composite(giro, pos)


def _subdial(img: Image.Image, t: Tema, cx: float, cy: float) -> None:
    n = img.width
    R = R_SUB * SS
    # cuba rebaixada: miolo mais escuro com anéis concêntricos finos (usinagem)
    xx, yy = grade(n)
    dist = np.hypot(xx - cx * SS, yy - cy * SS)
    base = np.array(t.base, np.float32) * (0.78 if not t.claro else 0.93)
    amp = 0.012 if t.claro else 0.06
    aneis = (1 - amp) + amp * np.sin(dist / (1.6 * SS))
    rgb = base * aneis[..., None]
    # sombra interna: borda superior-esquerda escura, inferior-direita clara
    luz = ((xx - cx * SS) + (yy - cy * SS)) / (2 * R)
    rgb *= (1 + 0.22 * np.clip(luz, -1, 1))[..., None]
    a = np.dstack([np.clip(rgb, 0, 255), np.full((n, n), 255, np.float32)])
    cuba = Image.fromarray(a.astype(np.uint8), "RGBA")
    img.alpha_composite(com_mascara(cuba, mascara_anel(n, cx * SS, cy * SS, R - 1.5 * SS)))
    # aro chanfrado (metal)
    g = grad_conico(n, cx * SS, cy * SS, metal_paradas(*t.metal), 200)
    img.alpha_composite(com_mascara(g, mascara_anel(n, cx * SS, cy * SS, R + 2.2 * SS, R - 1.5 * SS)))
    d = ImageDraw.Draw(img)
    for k in range(12):
        a0 = k * 30
        p0, p1 = polar(cx * SS, cy * SS, R - 3.5 * SS, a0), polar(cx * SS, cy * SS, R - 8 * SS, a0)
        d.line([p0, p1], fill=(*t.num_bisel, 200), width=max(1, int(1.2 * SS)))


def _janela_engrenagem(img: Image.Image, t: Tema) -> None:
    n = img.width
    cx, cy = GEAR_C[0] * SS, GEAR_C[1] * SS
    R = (GEAR_R + 4) * SS
    fundo = grad_radial(n, cx - 4 * SS, cy - 4 * SS, [(0, (6, 6, 8)), (R, (0, 0, 0))])
    img.alpha_composite(com_mascara(fundo, mascara_anel(n, cx, cy, R - 2 * SS)))
    g = grad_conico(n, cx, cy, metal_paradas(*t.metal), 210)
    img.alpha_composite(com_mascara(g, mascara_anel(n, cx, cy, R + 3 * SS, R - 2 * SS)))


def mostrador(t: Tema) -> Image.Image:
    n = W * SS
    c = n / 2
    img = tela(n)
    # 1) mostrador com textura
    img.alpha_composite(com_mascara(_padrao(t, n), mascara_anel(n, c, c, R_DIAL * SS)))
    # 2) bisel escovado + aro de metal + chanfro
    bis = grad_linear(n, (0, 0), (n, n), [(0, tuple(int(min(255, v * 1.45)) for v in t.bisel)),
                                           (0.5, t.bisel), (1, tuple(int(v * 0.7) for v in t.bisel))])
    b = np.asarray(bis).astype(np.float32).copy()
    b[..., :3] += ruido(n, 5, 2.2)[..., None]
    bis = Image.fromarray(np.clip(b, 0, 255).astype(np.uint8), "RGBA")
    img.alpha_composite(com_mascara(bis, mascara_anel(n, c, c, 234 * SS, (R_DIAL + 3) * SS)))
    img.alpha_composite(_anel_metal(n, t, 240, 233.5))
    img.alpha_composite(_anel_metal(n, t, R_DIAL + 4, R_DIAL - 1, 40))
    d = ImageDraw.Draw(img)
    d.ellipse([c - 233.5 * SS, c - 233.5 * SS, c + 233.5 * SS, c + 233.5 * SS], outline=(0, 0, 0, 150), width=SS)
    # 3) escala do bisel: minutos + números
    f = fonte("SemiBold", 15 * SS)
    for m in range(60):
        ang = m * 6
        if m % 5 == 0:
            _linha(d, c, ang, 223, 232, 2.4, (*t.acento, 255))
        else:
            _linha(d, c, ang, 227, 232, 1.2, (*t.num_bisel, 200))
    for k in range(1, 13):
        ang = k * 30 % 360
        x, y = polar(c, c, 213 * SS, ang)
        rot = -ang + (180 if 90 < ang < 270 else 0)
        texto_centrado(img, str(5 * k), x, y, f, (*t.num_bisel, 255), rot=rot)
    # 4) trilho de minutos no mostrador
    for m in range(60):
        if m % 5:
            _linha(d, c, m * 6, 191, 197, 1.1, (*t.texto, 150))
    d.ellipse([c - 198.5 * SS, c - 198.5 * SS, c + 198.5 * SS, c + 198.5 * SS], outline=(*t.texto, 90), width=SS // 2 + 1)
    # 5) índices aplicados
    for h in range(12):
        ang = h * 30
        if h == 0:
            for dx in (-6.5, 6.5):
                b = _barra_aplicada(t, 8, 34)
                giro = b
                x, y = polar(c, c, 172 * SS, 0)
                pos = (int(x + dx * SS - giro.width / 2), int(y - giro.height / 2))
                img.alpha_composite(sombra(giro, 2 * SS, 3 * SS, 2.5 * SS, 0.6), pos)
                img.alpha_composite(giro, pos)
        else:
            _colar_polar(img, _barra_aplicada(t, 12, 34), c, c, 172, ang)
    # 6) subdials + janela da engrenagem
    for cx_, cy_ in SUBDIAIS.values():
        _subdial(img, t, cx_, cy_)
    _janela_engrenagem(img, t)
    # 7) marca
    texto_centrado(img, "CRONOS", c, 151 * SS, fonte("SemiBold", 10.5 * SS), (*t.texto, 210), espaco=3.2 * SS)
    return reduzir_por(img)


def mostrador_ambiente(t: Tema) -> Image.Image:
    """AOD: só contornos finos e cinza. Poucos pixels acesos = economia de bateria e sem burn-in."""
    n = W * SS
    c = n / 2
    img = tela(n)
    d = ImageDraw.Draw(img)
    cinza = (150, 150, 156, 255)
    fraco = (95, 95, 100, 255)
    d.ellipse([c - 237 * SS, c - 237 * SS, c + 237 * SS, c + 237 * SS], outline=fraco, width=SS)
    d.ellipse([c - 202 * SS, c - 202 * SS, c + 202 * SS, c + 202 * SS], outline=fraco, width=SS)
    for m in range(60):
        if m % 5 == 0:
            _linha(d, c, m * 6, 208, 226, 1.4, cinza)
    for h in range(12):
        a = h * 30
        w = 8 if h % 3 == 0 else 6
        giro = Image.new("RGBA", (int(w * SS) + 6, int(34 * SS) + 6), (0, 0, 0, 0))
        ImageDraw.Draw(giro).rectangle([3, 3, giro.width - 4, giro.height - 4], outline=cinza, width=max(1, SS // 2 + 1))
        _colar_polar(img, giro, c, c, 172, a, sombra_px=None)
    for cx_, cy_ in SUBDIAIS.values():
        d.ellipse([(cx_ - R_SUB) * SS, (cy_ - R_SUB) * SS, (cx_ + R_SUB) * SS, (cy_ + R_SUB) * SS], outline=fraco, width=SS)
    px, py = polar(c, c, 232 * SS, 0)
    d.polygon([(px, py + 8 * SS), (px - 5 * SS, py - 4 * SS), (px + 5 * SS, py - 4 * SS)], fill=(*t.acento, 255))
    return reduzir_por(img)


# ------------------------------------------------------------------ ponteiros
def _poligono_ponteiro(estilo: str, cx: float, pad: float, comp: float, cauda: float, hw: float):
    if estilo == "espada":
        return [(cx, pad), (cx + hw, pad + 0.55 * comp), (cx + hw * 0.62, pad + comp),
                (cx + hw * 0.46, pad + comp + cauda), (cx - hw * 0.46, pad + comp + cauda),
                (cx - hw * 0.62, pad + comp), (cx - hw, pad + 0.55 * comp)]
    # bastao: haste reta com ponta chanfrada
    return [(cx, pad), (cx + hw, pad + hw * 1.3), (cx + hw, pad + comp + cauda),
            (cx - hw, pad + comp + cauda), (cx - hw, pad + hw * 1.3)]


def ponteiro(t: Tema, estilo: str, comp: float, cauda: float, larg: float) -> tuple[Image.Image, float]:
    """Retorna (imagem em 1x, y do pivô em px). Largura/altura inteiras; pivô no centro horizontal."""
    pad = 3
    w, h = int(larg) + 2 * pad, int(comp + cauda) + 2 * pad
    w += w % 2
    W_, H_ = w * SS, h * SS
    cx = W_ / 2
    hw = larg / 2 * SS
    pts = _poligono_ponteiro(estilo, cx, pad * SS, comp * SS, cauda * SS, hw)
    n = max(W_, H_)
    mask = Image.new("L", (W_, H_), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    esq = Image.new("L", (W_, H_), 0)
    ImageDraw.Draw(esq).rectangle([0, 0, cx, H_], fill=255)
    cl, md, es = t.metal
    g_esq = grad_linear(n, (cx - hw, 0), (cx, 0), [(0, md), (1, cl)]).crop((0, 0, W_, H_))
    g_dir = grad_linear(n, (cx, 0), (cx + hw, 0), [(0, tuple(int(v * 0.62) for v in md)), (1, es)]).crop((0, 0, W_, H_))
    out = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    out.paste(g_esq, (0, 0), Image.composite(mask, Image.new("L", (W_, H_), 0), esq))
    inv = esq.point(lambda v: 255 - v)
    out.paste(g_dir, (0, 0), Image.composite(mask, Image.new("L", (W_, H_), 0), inv))
    d = ImageDraw.Draw(out)
    d.polygon(pts, outline=(0, 0, 0, 170), width=max(1, SS // 2))
    d.line([(cx, pad * SS + 2 * SS), (cx, (pad + comp + cauda * 0.6) * SS)], fill=(255, 255, 255, 90), width=1)
    # lume
    if estilo == "espada":
        inl = [(cx, pad * SS + 0.22 * comp * SS), (cx + hw * 0.52, pad * SS + 0.56 * comp * SS),
               (cx + hw * 0.36, pad * SS + 0.9 * comp * SS), (cx - hw * 0.36, pad * SS + 0.9 * comp * SS),
               (cx - hw * 0.52, pad * SS + 0.56 * comp * SS)]
    else:
        inl = [(cx, pad * SS + hw * 2.2), (cx + hw * 0.5, pad * SS + hw * 3.0), (cx + hw * 0.5, pad * SS + 0.92 * comp * SS),
               (cx - hw * 0.5, pad * SS + 0.92 * comp * SS), (cx - hw * 0.5, pad * SS + hw * 3.0)]
    d.polygon(inl, fill=(*t.lume, 255), outline=(0, 0, 0, 110))
    return out.resize((w, h), Image.LANCZOS), pad + comp


def ponteiro_sombra(img: Image.Image, pivo_y: float, pad: int = 10) -> tuple[Image.Image, float]:
    """Sombra suave com a mesma geometria do ponteiro (margem `pad` em volta)."""
    w, h = img.width + 2 * pad, img.height + 2 * pad
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    base.alpha_composite(img, (pad, pad))
    return sombra(base, 3, 5, 3.2, 0.55), pivo_y + pad


def ponteiro_contorno(t: Tema, estilo: str, comp: float, cauda: float, larg: float) -> tuple[Image.Image, float]:
    """Versão AOD: só contorno cinza, interior vazio."""
    pad = 3
    w, h = int(larg) + 2 * pad, int(comp + cauda) + 2 * pad
    w += w % 2
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    pts = _poligono_ponteiro(estilo, w * SS / 2, pad * SS, comp * SS, cauda * SS, larg / 2 * SS)
    ImageDraw.Draw(img).line(pts + [pts[0]], fill=(200, 200, 205, 255), width=max(2, int(1.3 * SS)), joint="curve")
    return img.resize((w, h), Image.LANCZOS), pad + comp


def ponteiro_segundos(comp: float = 208, cauda: float = 52) -> tuple[Image.Image, float]:
    """Ponteiro de segundos claro (é tingido com a cor de destaque no XML) + contrapeso."""
    pad = 3
    w, h = 14, int(comp + cauda) + 2 * pad
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w * SS / 2
    py = (pad + comp) * SS
    d.polygon([(cx, pad * SS), (cx + 1.6 * SS, py), (cx - 1.6 * SS, py)], fill=(250, 250, 252, 255))
    d.polygon([(cx, pad * SS), (cx, py), (cx - 1.6 * SS, py)], fill=(205, 205, 212, 255))
    d.rounded_rectangle([cx - 3.4 * SS, py - 2 * SS, cx + 3.4 * SS, py + (cauda - 6) * SS], radius=2 * SS, fill=(236, 236, 240, 255))
    d.rounded_rectangle([cx - 3.4 * SS, py - 2 * SS, cx, py + (cauda - 6) * SS], radius=2 * SS, fill=(196, 196, 204, 255))
    d.ellipse([cx - 5.2 * SS, py + (cauda - 14) * SS, cx + 5.2 * SS, py + (cauda - 3.6) * SS], fill=(246, 246, 250, 255))
    d.ellipse([cx - 2.2 * SS, py + (cauda - 11.6) * SS, cx + 2.2 * SS, py + (cauda - 7.2) * SS], fill=(40, 40, 46, 255))
    return img.resize((w, h), Image.LANCZOS), pad + comp


def tampa_central(t: Tema, tam: int = 48) -> Image.Image:
    n = tam * SS
    c = n / 2
    img = tela(n)
    r = 13 * SS
    sh = tela(n)
    ImageDraw.Draw(sh).ellipse([c - r, c - r, c + r, c + r], fill=(0, 0, 0, 255))
    img.alpha_composite(sombra(sh, 2 * SS, 3 * SS, 2.5 * SS, 0.6))
    g = grad_conico(n, c, c, metal_paradas(*t.metal), 30)
    img.alpha_composite(com_mascara(g, mascara_anel(n, c, c, r)))
    ImageDraw.Draw(img).ellipse([c - r, c - r, c + r, c + r], outline=(0, 0, 0, 150), width=max(1, SS // 2))
    ImageDraw.Draw(img).ellipse([c - 6 * SS, c - 6 * SS, c + 6 * SS, c + 6 * SS], fill=(14, 14, 16, 255))
    ImageDraw.Draw(img).ellipse([c - 2.4 * SS, c - 2.4 * SS, c + 2.4 * SS, c + 2.4 * SS], fill=(*t.acento, 255))
    return reduzir_por(img)


def engrenagem(t: Tema, tam: int = 56) -> Image.Image:
    """Engrenagem aparente (gira no XML com a contagem de segundos)."""
    n = tam * SS
    c = n / 2
    dentes = 16
    R0, R1 = (GEAR_R - 3.2) * SS, GEAR_R * SS
    pts = []
    for i in range(1600):
        a = 2 * math.pi * i / 1600
        s = math.sin(dentes * a)
        k = np.clip(s * 3.0, -1, 1) * 0.5 + 0.5
        r = R0 + (R1 - R0) * k
        pts.append((c + r * math.sin(a), c - r * math.cos(a)))
    m = Image.new("L", (n, n), 0)
    dm = ImageDraw.Draw(m)
    dm.polygon(pts, fill=255)
    for k in range(5):  # raios vazados
        a = k * 72
        x, y = polar(c, c, 12.5 * SS, a)
        dm.ellipse([x - 5.2 * SS, y - 5.2 * SS, x + 5.2 * SS, y + 5.2 * SS], fill=0)
    dm.ellipse([c - 3 * SS, c - 3 * SS, c + 3 * SS, c + 3 * SS], fill=0)
    mm = np.asarray(m.filter(ImageFilter.GaussianBlur(0.6 * SS)), np.float32) / 255
    g = grad_conico(n, c, c, metal_paradas(*t.metal), 20)
    img = com_mascara(g, mm)
    d = ImageDraw.Draw(img)
    d.ellipse([c - 4.6 * SS, c - 4.6 * SS, c + 4.6 * SS, c + 4.6 * SS], fill=(*t.metal[1], 255), outline=(0, 0, 0, 160))
    d.ellipse([c - 2 * SS, c - 2 * SS, c + 2 * SS, c + 2 * SS], fill=(*t.acento, 255))
    d.ellipse([c - 1.0 * SS, c - 1.0 * SS, c + 1.0 * SS, c + 1.0 * SS], fill=(255, 255, 255, 220))
    return reduzir_por(img)


def vidro() -> Image.Image:
    """Reflexo discreto do cristal (some no modo ambiente)."""
    n = W * SS
    c = n / 2
    g = grad_radial(n, 150 * SS, 120 * SS, [(0, (255, 255, 255, 46)), (230 * SS, (255, 255, 255, 14)),
                                           (330 * SS, (255, 255, 255, 0))])
    img = com_mascara(g, mascara_anel(n, c, c, 236 * SS))
    d = ImageDraw.Draw(img)
    d.arc([c - 232 * SS, c - 232 * SS, c + 232 * SS, c + 232 * SS], 200, 262, fill=(255, 255, 255, 56), width=2 * SS)
    return reduzir_por(img)


def icone_tema(previa: Image.Image, tam: int = 192) -> Image.Image:
    return previa.resize((tam, tam), Image.LANCZOS)
