"""Watchface "Sol e Lua": calendário em anel (meses e dias), dia da semana em subdial e janela com
sol/lua que percorre o céu ao longo do dia (a lua mostra a fase real).

Ideia de referência: relógios com calendário em anel. Arte e código originais.
Os marcadores (mês, dia, semana, sol, céu, ponteiro de segundos) são cinza/branco e recebem a cor de destaque
por `tintColor`, então uma imagem só serve para laranja, azul, verde, rosa ou roxo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from wf.desenho import (SS, com_mascara, fonte, grad_conico, grad_linear, grad_radial, grade, mascara_anel,
                        metal_paradas, polar, reduzir_por, ruido, sombra, tela, texto_arco, texto_centrado)
from wf.modulo import caixa, criar_modulo, hexcor, texto

NOME = "lunar"
W = 480
C = 240
R_BEZEL, R_MES, R_DIA, R_MIN, R_DIAL = 240, 232, 206, 178, 176
JAN = (C, 226, 106)               # janela do céu: centro x, y, raio (só a metade de cima)
SEM = (C, 338, 50)                # subdial do dia da semana
RAIO_SOL = 80
MESES = ["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
SEMANA = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]
ACENTOS = [("laranja", "#ff7a1a"), ("azul", "#3d8bff"), ("verde", "#2fa365"), ("rosa", "#ff4f8b"), ("roxo", "#9a6cff")]
SLOTS = {"esq": (126, 298, 62, 40), "dir": (292, 298, 62, 40)}


@dataclass(frozen=True)
class Tema:
    id: str
    anel_mes: tuple
    anel_dia: tuple
    dial: tuple
    texto: tuple
    barra: tuple
    moldura: tuple


TEMAS = {
    "claro": Tema("claro", (236, 236, 240), (222, 222, 228), (232, 232, 236), (26, 26, 30), (16, 16, 18), (170, 172, 180)),
    "escuro": Tema("escuro", (40, 40, 46), (30, 30, 36), (30, 30, 34), (236, 236, 242), (240, 240, 244), (110, 112, 122)),
}


# ------------------------------------------------------------------ texturas
def _tecido(n: int, base: tuple, contraste: float) -> np.ndarray:
    """Trama diagonal (como tecido/carbono claro) com brilho radial."""
    xx, yy = grade(n)
    p = 7.0 * SS
    u, v = (xx + yy) / p, (xx - yy) / p
    t = 0.5 + 0.5 * np.sin(2 * np.pi * u) * np.sin(2 * np.pi * v)
    d = np.hypot(xx - n / 2, yy - n / 2) / (R_DIAL * SS)
    luz = 1.04 - 0.22 * d ** 2 + 0.05 * np.cos(2 * np.arctan2(yy - n / 2, xx - n / 2) + 0.8)
    rgb = np.array(base, np.float32)[None, None, :] * (luz * (1 - contraste + contraste * 2 * t))[..., None]
    return np.dstack([np.clip(rgb, 0, 255), np.full((n, n), 255, np.float32)])


def _escamas(w: int, h: int, passo: float, claro: float = 1.0) -> np.ndarray:
    """Textura de escamas hexagonais em tons de cinza (0..255) com relevo."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dy = passo * 0.866
    r1 = np.round(yy / dy)
    off = (r1 % 2) * passo / 2
    cx1 = np.round((xx - off) / passo) * passo + off
    cy1 = r1 * dy
    r2 = np.floor(yy / dy)
    off2 = (r2 % 2) * passo / 2
    cx2 = np.round((xx - off2) / passo) * passo + off2
    cy2 = r2 * dy + dy
    d1 = np.hypot(xx - cx1, yy - cy1)
    d2 = np.hypot(xx - cx2, yy - cy2)
    d = np.minimum(d1, d2)
    relevo = 1 - 0.55 * np.clip(d / (passo * 0.62), 0, 1) ** 2
    luz = 0.5 + 0.5 * np.clip(((xx - cx1) * -0.5 + (yy - cy1) * -0.5) / passo, -1, 1) * (d1 <= d2) \
        + 0.5 * np.clip(((xx - cx2) * -0.5 + (yy - cy2) * -0.5) / passo, -1, 1) * (d1 > d2)
    return np.clip(255 * claro * relevo * (0.82 + 0.28 * luz), 0, 255)


# ------------------------------------------------------------------ mostrador
def _forma_janela(n: int, folga: float = 0) -> Image.Image:
    cx, cy, r = JAN
    m = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(m)
    s = n / W
    d.pieslice([(cx - r + folga) * s, (cy - r + folga) * s, (cx + r - folga) * s, (cy + r - folga) * s], 180, 360, fill=255)
    return m


def fundo(t: Tema) -> Image.Image:
    n = W * SS
    c = n / 2
    img = tela(n)
    d = ImageDraw.Draw(img)
    # aro externo escuro com brilho
    g = grad_conico(n, c, c, metal_paradas((120, 122, 132), (46, 47, 54), (14, 14, 18)), 30)
    img.alpha_composite(com_mascara(g, mascara_anel(n, c, c, R_BEZEL * SS, R_MES * SS)))
    # anéis de meses e dias
    for (ri, re), cor in (((R_DIA, R_MES), t.anel_mes), ((R_MIN, R_DIA), t.anel_dia)):
        faixa = grad_linear(n, (0, 0), (n, n), [(0, tuple(min(255, int(v * 1.05)) for v in cor)), (1, tuple(int(v * 0.93) for v in cor))])
        img.alpha_composite(com_mascara(faixa, mascara_anel(n, c, c, re * SS, ri * SS)))
    # divisórias dos meses (12) e dos dias (31)
    sep = (*t.moldura, 255)
    for k in range(12):
        a = k * 30
        d.line([polar(c, c, R_DIA * SS, a), polar(c, c, R_MES * SS, a)], fill=sep, width=SS)
    for k in range(31):
        a = k * 360 / 31
        d.line([polar(c, c, R_MIN * SS, a), polar(c, c, R_DIA * SS, a)], fill=(*t.moldura, 150), width=max(1, SS // 2))
    for r in (R_MES, R_DIA, R_MIN):
        d.ellipse([c - r * SS, c - r * SS, c + r * SS, c + r * SS], outline=sep, width=SS)
    # texto: meses e dias
    fm, fd = fonte("SemiBold", 14.5 * SS), fonte("Medium", 13 * SS)
    for i, nome in enumerate(MESES):
        texto_arco(img, nome, c, c, 219 * SS, 15 + 30 * i, fm, (*t.texto, 255), espaco=1.2 * SS)
    for dia in range(1, 32):
        texto_arco(img, f"{dia:02d}", c, c, 192 * SS, (dia - 1) * 360 / 31 + 180 / 31, fd, (*t.texto, 255))
    # mostrador interno com trama
    arr = _tecido(n, t.dial, 0.16 if t.id == "claro" else 0.22)
    face = Image.fromarray(arr.astype(np.uint8), "RGBA")
    img.alpha_composite(com_mascara(face, mascara_anel(n, c, c, R_DIAL * SS)))
    d = ImageDraw.Draw(img)
    # trilho de minutos
    for m in range(60):
        a = m * 6
        d.line([polar(c, c, 166 * SS, a), polar(c, c, 172 * SS, a)], fill=(*t.barra, 200 if m % 5 == 0 else 110), width=max(1, int((1.6 if m % 5 == 0 else 1) * SS)))
    # barras das horas
    for h in range(12):
        a = h * 30
        larg = 8 if h % 3 == 0 else 6
        p0, p1 = polar(c, c, 138 * SS, a), polar(c, c, 162 * SS, a)
        sh = tela(n)
        ImageDraw.Draw(sh).line([p0, p1], fill=(0, 0, 0, 255), width=int(larg * SS))
        img.alpha_composite(sombra(sh, 1.5 * SS, 2.5 * SS, 2 * SS, 0.35))
        d.line([p0, p1], fill=(*t.barra, 255), width=int(larg * SS))
    # moldura da janela do céu e do subdial da semana
    cx, cy, r = JAN
    ring = Image.new("L", (n, n), 0)
    dr = ImageDraw.Draw(ring)
    s = SS
    dr.pieslice([(cx - r - 5) * s, (cy - r - 5) * s, (cx + r + 5) * s, (cy + r + 5) * s], 180, 360, fill=255)
    dr.pieslice([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], 180, 360, fill=0)
    dr.rectangle([(cx - r - 5) * s, (cy) * s, (cx + r + 5) * s, (cy + 5) * s], fill=255)
    g2 = grad_conico(n, c, c, metal_paradas((246, 246, 250), (170, 172, 180), (86, 88, 98)), 120)
    img.alpha_composite(com_mascara(g2, np.asarray(ring, np.float32) / 255))
    sx, sy, sr = SEM
    sub = grad_radial(n, (sx - 10) * SS, (sy - 12) * SS, [(0, (250, 250, 252) if t.id == "claro" else (74, 74, 82)),
                                                         (sr * SS, (206, 206, 212) if t.id == "claro" else (38, 38, 44))])
    img.alpha_composite(sombra(com_mascara(sub, mascara_anel(n, sx * SS, sy * SS, (sr + 3) * SS)), 2 * SS, 3 * SS, 3 * SS, 0.45))
    img.alpha_composite(com_mascara(sub, mascara_anel(n, sx * SS, sy * SS, sr * SS)))
    g3 = grad_conico(n, sx * SS, sy * SS, metal_paradas((246, 246, 250), (170, 172, 180), (86, 88, 98)), 200)
    img.alpha_composite(com_mascara(g3, mascara_anel(n, sx * SS, sy * SS, (sr + 3) * SS, (sr - 1) * SS)))
    fs = fonte("SemiBold", 10.5 * SS)
    for i, nome in enumerate(SEMANA):
        texto_arco(img, nome, sx * SS, sy * SS, (sr - 14) * SS, i * 360 / 7, fs, (*t.texto, 255), espaco=0.6 * SS)
    d = ImageDraw.Draw(img)
    for i in range(7):
        a = i * 360 / 7 + 180 / 7
        d.line([polar(sx * SS, sy * SS, (sr - 24) * SS, a), polar(sx * SS, sy * SS, (sr - 3) * SS, a)], fill=(*t.moldura, 140), width=max(1, SS // 2))
    return reduzir_por(img)


def ceu(noite: bool) -> Image.Image:
    """Janela do céu (metade de cima). Dia = escamas em cinza (recebe a cor de destaque); noite = azul-marinho com estrelas."""
    cx, cy, r = JAN
    w, h = 2 * r, r + 1
    n = max(w, h)
    if noite:
        g = grad_linear(n, (0, 0), (0, h), [(0, (8, 14, 40)), (1, (30, 40, 86))]).crop((0, 0, w, h))
        a = np.asarray(g).astype(np.float32)
        a[..., :3] *= (_escamas(w, h, 10.0, 1.0)[..., None] / 255 * 0.35 + 0.72)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
        d = ImageDraw.Draw(img)
        rng = np.random.default_rng(4)
        for _ in range(46):
            x, y = rng.integers(8, w - 8), rng.integers(6, h - 10)
            t = rng.choice([1, 1, 2])
            d.ellipse([x - t, y - t, x + t, y + t], fill=(255, 255, 255, int(rng.integers(150, 255))))
    else:
        v = _escamas(w, h, 11.0)
        img = Image.fromarray(np.dstack([v, v, v, np.full((h, w), 255)]).astype(np.uint8), "RGBA")
        yy, xx = np.mgrid[0:h, 0:w]
        sombra_int = np.clip(((xx - r) ** 2 + (yy - h) ** 2) ** 0.5 / r, 0, 1) ** 4
        a = np.asarray(img).astype(np.float32)
        a[..., :3] *= (1 - 0.28 * sombra_int)[..., None]
        img = Image.fromarray(a.astype(np.uint8), "RGBA")
    m = _forma_janela(w * 4).resize((w * 4, w * 4))
    mm = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(mm).pieslice([0, 0, w * 4 - 1, w * 4 - 1], 180, 360, fill=255)
    mm = mm.resize((w, h), Image.LANCZOS)
    img.putalpha(mm)
    return img


def sol() -> tuple[Image.Image, float]:
    """Sol em relevo (branco, recebe a cor de destaque só no céu; o sol fica branco-quente) com raios.
    Imagem alta: o sol fica no topo e o pivô (centro da janela) na base, para girar em arco."""
    s = 4
    w, raio = 100, RAIO_SOL
    cx0, cy0 = w / 2, 52
    h = int(cy0 + raio + 6)
    img = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for k in range(14):
        a = k * 360 / 14
        p = polar(cx0 * s, cy0 * s, 0, a)
        tri = [polar(cx0 * s, cy0 * s, 30 * s, a - 6.5), polar(cx0 * s, cy0 * s, 46 * s, a), polar(cx0 * s, cy0 * s, 30 * s, a + 6.5)]
        d.polygon(tri, fill=(255, 250, 240, 255))
    d.ellipse([(cx0 - 27) * s, (cy0 - 27) * s, (cx0 + 27) * s, (cy0 + 27) * s], fill=(255, 252, 244, 255))
    arr = np.asarray(img).astype(np.float32)
    yy, xx = np.mgrid[0:h * s, 0:w * s]
    dist = np.hypot(xx - cx0 * s, yy - cy0 * s) / (46 * s)
    shade = 1 - 0.22 * np.clip(((xx - cx0 * s) * 0.6 + (yy - cy0 * s) * 0.8) / (46 * s), -1, 1) - 0.1 * dist
    arr[..., :3] *= shade[..., None]
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    sh = sombra(out, 2 * s, 3 * s, 3 * s, 0.38)
    comp = sh.copy()
    comp.alpha_composite(out)
    return comp.resize((w, h), Image.LANCZOS), cy0 + raio


def lua(fase: int) -> tuple[Image.Image, float]:
    """Lua com fase 0..7 (0 nova, 2 quarto crescente, 4 cheia, 6 quarto minguante): sombra do terminador por cálculo."""
    s = 4
    w, raio = 100, RAIO_SOL
    cx0, cy0, rl = w / 2, 52, 30
    h = int(cy0 + raio + 6)
    yy, xx = np.mgrid[0:h * s, 0:w * s].astype(np.float32)
    X, Y = (xx - cx0 * s) / (rl * s), (yy - cy0 * s) / (rl * s)
    dentro = (X ** 2 + Y ** 2) <= 1
    z = np.sqrt(np.clip(1 - X ** 2 - Y ** 2, 0, 1))
    ang = fase * math.pi / 4                      # 0 nova ... pi cheia ... 2pi nova
    # direção da luz no plano XZ: crescente ilumina a direita (hemisfério norte)
    lx, lz = -math.sin(ang), -math.cos(ang)
    ilum = np.clip(X * lx + z * lz, 0, 1)
    ilum = np.clip(ilum * 1.6, 0, 1)
    cratera = 0.9 + 0.1 * np.sin(X * 11) * np.cos(Y * 9)
    base = (210 + 40 * ilum * cratera)
    escuro = 36
    cor = escuro + (base - escuro) * ilum
    a = np.zeros((h * s, w * s, 4), np.float32)
    a[..., 0] = cor * 0.96
    a[..., 1] = cor * 0.98
    a[..., 2] = cor
    a[..., 3] = dentro * 255
    img = Image.fromarray(a.astype(np.uint8), "RGBA")
    # contorno fraco da parte escura, para a lua não sumir no céu
    d = ImageDraw.Draw(img)
    d.ellipse([(cx0 - rl) * s, (cy0 - rl) * s, (cx0 + rl) * s, (cy0 + rl) * s], outline=(150, 160, 200, 120), width=s)
    halo = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hh = grad_radial(max(img.size), cx0 * s, cy0 * s, [(rl * s * 0.9, (180, 200, 255, 70)), (rl * s * 1.7, (180, 200, 255, 0))]).crop((0, 0, w * s, h * s))
    halo.alpha_composite(hh)
    halo.alpha_composite(img)
    return halo.resize((w, h), Image.LANCZOS), cy0 + raio


def _marcador_arco(r_in: float, r_out: float, graus: float, w: int, h: int, py: float, tam=1) -> Image.Image:
    """Trecho de anel centrado em 12h; pivô na base (centro do relógio) para girar com Transform."""
    s = 4
    img = Image.new("L", (w * s, h * s), 0)
    d = ImageDraw.Draw(img)
    cx = w * s / 2
    cy = py * s
    d.pieslice([cx - r_out * s, cy - r_out * s, cx + r_out * s, cy + r_out * s], -90 - graus / 2, -90 + graus / 2, fill=255)
    d.ellipse([cx - r_in * s, cy - r_in * s, cx + r_in * s, cy + r_in * s], fill=0)
    a = np.asarray(img.resize((w, h), Image.LANCZOS))
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = a
    return Image.fromarray(rgba, "RGBA")


def marcador_mes() -> Image.Image:
    return _marcador_arco(R_MES - 5, R_MES - 0.5, 26, 130, C - 8, C - 8)       # fita fina na borda externa


def marcador_dia() -> Image.Image:
    return _marcador_arco(R_DIA - 5, R_DIA - 0.5, 360 / 31 - 1.2, 56, C - 8, C - 8)


def marcador_sem() -> Image.Image:
    sx, sy, sr = SEM
    return _marcador_arco(sr - 7, sr - 1, 360 / 7 - 4, 60, sr + 4, sr)


# ------------------------------------------------------------------ ponteiros
def _mao(comp: float, cauda: float, larg: float, contorno: bool = False, preencher: bool = True) -> tuple[Image.Image, float]:
    s = 4
    pad = 6
    w, h = int(larg) + 2 * pad, int(comp + cauda) + 2 * pad
    w += w % 2
    img = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w * s / 2
    hw = larg / 2 * s
    pts = [(cx, pad * s), (cx + hw, (pad + larg * 0.9) * s), (cx + hw, (pad + comp + cauda) * s),
           (cx - hw, (pad + comp + cauda) * s), (cx - hw, (pad + larg * 0.9) * s)]
    if contorno:
        d.line(pts + [pts[0]], fill=(210, 210, 216, 255), width=int(1.6 * s), joint="curve")
    else:
        d.polygon(pts, fill=(14, 14, 16, 255))
        k = 2.4 * s
        inner = [(cx, pad * s + k * 1.7), (cx + hw - k, (pad + larg * 0.9) * s + k * 0.4), (cx + hw - k, (pad + comp + cauda) * s - k),
                 (cx - hw + k, (pad + comp + cauda) * s - k), (cx - hw + k, (pad + larg * 0.9) * s + k * 0.4)]
        d.polygon(inner, fill=(250, 250, 252, 255))
        d.polygon([inner[0], inner[1], inner[2], (cx, inner[2][1]), (cx, inner[0][1])], fill=(226, 228, 236, 255))
    return img.resize((w, h), Image.LANCZOS), pad + comp


def seg_mao() -> tuple[Image.Image, float]:
    s = 4
    pad, comp, cauda = 4, 214, 56
    w, h = 16, int(comp + cauda) + 2 * pad
    img = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, py = w * s / 2, (pad + comp) * s
    d.polygon([(cx - 1.2 * s, pad * s), (cx + 1.2 * s, pad * s), (cx + 2.2 * s, py + cauda * s), (cx - 2.2 * s, py + cauda * s)], fill=(255, 255, 255, 255))
    d.ellipse([cx - 6 * s, py - 6 * s, cx + 6 * s, py + 6 * s], fill=(255, 255, 255, 255))
    d.ellipse([cx - 2.4 * s, py - 2.4 * s, cx + 2.4 * s, py + 2.4 * s], fill=(30, 30, 34, 255))
    return img.resize((w, h), Image.LANCZOS), pad + comp


def sombra_mao(img: Image.Image, py: float, pad: int = 10) -> tuple[Image.Image, float]:
    base = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    base.alpha_composite(img, (pad, pad))
    return sombra(base, 3, 5, 3, 0.45), py + pad


def ambiente() -> Image.Image:
    n = W * SS
    c = n / 2
    img = tela(n)
    d = ImageDraw.Draw(img)
    fr, ff = (110, 110, 116, 255), (70, 70, 76, 255)
    for r in (R_BEZEL - 3, R_MES, R_MIN):
        d.ellipse([c - r * SS, c - r * SS, c + r * SS, c + r * SS], outline=fr if r != R_MES else ff, width=SS)
    for h in range(12):
        a = h * 30
        d.line([polar(c, c, 138 * SS, a), polar(c, c, 162 * SS, a)], fill=(200, 200, 206, 255), width=int((4 if h % 3 == 0 else 3) * SS))
    cx, cy, r = JAN
    d.arc([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], 180, 360, fill=ff, width=SS)
    d.line([((cx - r) * SS, cy * SS), ((cx + r) * SS, cy * SS)], fill=ff, width=SS)
    sx, sy, sr = SEM
    d.ellipse([(sx - sr) * SS, (sy - sr) * SS, (sx + sr) * SS, (sy + sr) * SS], outline=ff, width=SS)
    return reduzir_por(img)


# ------------------------------------------------------------------ XML
def _por_tema(w: int, h: int, fabrica) -> str:
    ops = "".join(f'<ListOption id="{i}"><Group x="0" y="0" width="{w}" height="{h}">{fabrica(t)}</Group></ListOption>' for i, t in TEMAS.items())
    return f'<Group x="0" y="0" width="{w}" height="{h}"><ListConfiguration id="tema">{ops}</ListConfiguration></Group>'


def _slot(nome, sid, x, y, w, h, padrao) -> str:
    def um(t):
        return texto(0, 0, w, h, 24, hexcor(t.texto), "%s", ["[COMPLICATION.TEXT]"], "SEMI_BOLD")

    def dois(t):
        return (texto(0, 0, w, 16, 12, "[CONFIGURATION.acento]", "%s", ["[COMPLICATION.TITLE]"], "MEDIUM")
                + texto(0, 14, w, h - 14, 22, hexcor(t.texto), "%s", ["[COMPLICATION.TEXT]"], "SEMI_BOLD"))

    return f"""<ComplicationSlot name="{nome}" slotId="{sid}" x="{x}" y="{y}" width="{w}" height="{h}" displayName="slot_{nome}"
        supportedTypes="SHORT_TEXT RANGED_VALUE EMPTY" isCustomizable="TRUE">
      <BoundingBox x="0" y="0" width="{w}" height="{h}" />
      <DefaultProviderPolicy defaultSystemProvider="{padrao}" defaultSystemProviderType="SHORT_TEXT" />
      <Variant mode="AMBIENT" target="alpha" value="0" />
      <Complication type="SHORT_TEXT"><Condition><Expressions><Expression name="titulo"><![CDATA[[COMPLICATION.TITLE] != null]]></Expression></Expressions>
        <Compare expression="titulo">{_por_tema(w, h, dois)}</Compare><Default>{_por_tema(w, h, um)}</Default></Condition></Complication>
      <Complication type="RANGED_VALUE">{_por_tema(w, h, um)}</Complication>
    </ComplicationSlot>"""


def _mao_xml(tipo: str, nome: str, m, extra="", filhos="") -> str:
    w, h, py = m[nome]
    t = (f'<{tipo} resource="{nome}" x="{C - w // 2}" y="{round(C - py)}" width="{w}" height="{h}" pivotX="0.5" pivotY="{py / h:.6f}"{extra}')
    return f"{t}>{filhos}</{tipo}>" if filhos else t + " />"


def gerar_xml(m: dict[str, tuple[int, int, float]], dim_sol: tuple[int, int, float], dim_mes, dim_dia, dim_sem) -> str:
    cx, cy, r = JAN
    sw, sh, spy = dim_sol
    noite = '([HOUR_0_23] &gt;= 18 || [HOUR_0_23] &lt; 6)'
    dia = '([HOUR_0_23] &gt;= 6 &amp;&amp; [HOUR_0_23] &lt; 18)'
    ang_sol = "-78 + 156 * clamp(([HOUR_0_23_MINUTE] - 6) / 12, 0, 1)"
    ang_lua = "-78 + 156 * clamp((([HOUR_0_23_MINUTE] &gt;= 18 ? [HOUR_0_23_MINUTE] - 18 : [HOUR_0_23_MINUTE] + 6)) / 12, 0, 1)"
    L = ['<?xml version="1.0" encoding="utf-8"?>', "<!-- GERADO por tools/gerar.py lunar. Não edite à mão. -->",
         f'<WatchFace width="{W}" height="{W}" clipShape="CIRCLE">', '  <Metadata key="CLOCK_TYPE" value="ANALOG" />',
         '  <Metadata key="PREVIEW_TIME" value="10:08:32" />', "  <UserConfigurations>",
         '    <ListConfiguration id="tema" displayName="tema_label" defaultValue="claro">']
    L += [f'      <ListOption id="{i}" displayName="tema_{i}" />' for i in TEMAS]
    L += ["    </ListConfiguration>", '    <ColorConfiguration id="acento" displayName="acento_label" defaultValue="0">']
    L += [f'      <ColorOption id="{i}" displayName="acento_{n}" colors="{c}" />' for i, (n, c) in enumerate(ACENTOS)]
    L += ["    </ColorConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a(f'    <Group name="fundo" {caixa(W, W)}><Variant mode="AMBIENT" target="alpha" value="0" /><ListConfiguration id="tema">')
    for i in TEMAS:
        a(f'      <ListOption id="{i}"><Group {caixa(W, W)}><PartImage {caixa(W, W)}><Image resource="fundo_{i}" /></PartImage></Group></ListOption>')
    a("    </ListConfiguration></Group>")
    # janela do céu
    a(f'    <Group name="janela" {caixa(W, W)}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a(f'      <PartImage x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{r + 1}" tintColor="[CONFIGURATION.acento]"><Image resource="ceu_dia" /></PartImage>')
    a(f'      <PartImage x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{r + 1}"><Image resource="ceu_noite" />'
      f'<Transform target="alpha" value="{noite} ? 255 : 0" /></PartImage>')
    a(f'      <PartImage x="{cx - sw // 2}" y="{round(cy - spy)}" width="{sw}" height="{sh}" pivotX="0.5" pivotY="{spy / sh:.6f}">'
      f'<Image resource="sol" /><Transform target="angle" value="{ang_sol}" /><Transform target="alpha" value="{dia} ? 255 : 0" /></PartImage>')
    for i in range(8):
        a(f'      <PartImage x="{cx - sw // 2}" y="{round(cy - spy)}" width="{sw}" height="{sh}" pivotX="0.5" pivotY="{spy / sh:.6f}">'
          f'<Image resource="lua_{i}" /><Transform target="angle" value="{ang_lua}" />'
          f'<Transform target="alpha" value="{noite} &amp;&amp; [MOON_PHASE_TYPE] == {i} ? 255 : 0" /></PartImage>')
    a("    </Group>")
    # marcadores de mês, dia e dia da semana
    a(f'    <Group name="marcadores" {caixa(W, W)}><Variant mode="AMBIENT" target="alpha" value="0" />')
    for nome, dim, ang, ox, oy, piv in (("marcador_mes", dim_mes, "15 + [MONTH_0_11] * 30", C - dim_mes[0] // 2, C - dim_mes[1], 1.0),
                                          ("marcador_dia", dim_dia, "([DAY] - 1) * 360 / 31 + 180 / 31", C - dim_dia[0] // 2, C - dim_dia[1], 1.0),
                                          ("marcador_sem", dim_sem, "([DAY_OF_WEEK] - 1) * 360 / 7", SEM[0] - dim_sem[0] // 2, SEM[1] - dim_sem[1] + 4, 1.0)):
        w, h = dim[0], dim[1]
        piv = (h - 4) / h if nome == "marcador_sem" else 1.0
        a(f'      <PartImage x="{ox}" y="{oy}" width="{w}" height="{h}" pivotX="0.5" pivotY="{piv:.6f}" tintColor="[CONFIGURATION.acento]">'
          f'<Image resource="{nome}" /><Transform target="angle" value="{ang}" /></PartImage>')
    a("    </Group>")
    a("    " + _slot("esq", 0, *SLOTS["esq"], "STEP_COUNT"))
    a("    " + _slot("dir", 1, *SLOTS["dir"], "WATCH_BATTERY"))
    # ambiente (AOD)
    a(f'    <Group name="ambiente" {caixa(W, W)} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />')
    a(f'      <PartImage {caixa(W, W)}><Image resource="ambiente" /></PartImage>')
    a("      " + texto(140, 352, 200, 26, 19, "#9a9aa2", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY_Z]"], "MEDIUM"))
    a("    </Group>")
    # ponteiros
    a(f'    <AnalogClock {caixa(W, W)}><Variant mode="AMBIENT" target="alpha" value="0" />')
    for tipo, nome in (("HourHand", "hora_sombra"), ("MinuteHand", "min_sombra"), ("HourHand", "hora"), ("MinuteHand", "min")):
        a("      " + _mao_xml(tipo, nome, m))
    a("    </AnalogClock>")
    a(f'    <AnalogClock {caixa(W, W)} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />')
    a("      " + _mao_xml("HourHand", "hora_contorno", m))
    a("      " + _mao_xml("MinuteHand", "min_contorno", m))
    a("    </AnalogClock>")
    a(f'    <AnalogClock {caixa(W, W)}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a("      " + _mao_xml("SecondHand", "seg_sombra", m, filhos='<Sweep frequency="15" />'))
    a("      " + _mao_xml("SecondHand", "seg", m, ' tintColor="[CONFIGURATION.acento]"', '<Sweep frequency="15" />'))
    a("    </AnalogClock>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ prévia
def _tint(im: Image.Image, cor) -> Image.Image:
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r.point(lambda v: v * cor[0] // 255), g.point(lambda v: v * cor[1] // 255), b.point(lambda v: v * cor[2] // 255), a))


def _girar(base_size: int, img: Image.Image, pos: tuple[float, float], pivo: tuple[float, float], ang: float) -> Image.Image:
    """Cola `img` em pos (x,y do canto) e gira `ang` graus (horário) em torno de `pivo` (coordenadas da tela)."""
    cam = Image.new("RGBA", (base_size, base_size), (0, 0, 0, 0))
    cam.alpha_composite(img, (int(round(pos[0])), int(round(pos[1]))))
    return cam.rotate(-ang, center=pivo, resample=Image.BICUBIC)


def previa(A: dict, tema: str, acento: str, h: int, mi: int, s: int, dia: int, mes0: int, dsem: int, fase: int, ambiente_: bool = False) -> Image.Image:
    cor = tuple(int(acento[i:i + 2], 16) for i in (1, 3, 5))
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    ang_h, ang_m, ang_s = (h % 12) * 30 + mi * 0.5 + s / 120, mi * 6 + s * 0.1, s * 6
    if ambiente_:
        base.alpha_composite(A["ambiente"])
        d = ImageDraw.Draw(base)
        d.text((C, 365), "QUA 28", font=fonte("Medium", 19), fill=(154, 154, 162), anchor="mm")
        for nome, ang in (("hora_contorno", ang_h), ("min_contorno", ang_m)):
            im, py = A[nome]
            base.alpha_composite(_girar(W, im, (C - im.width / 2, C - py), (C, C), ang))
    else:
        base.alpha_composite(A[f"fundo_{tema}"])
        cx, cy, r = JAN
        hm = h + mi / 60
        noite = hm >= 18 or hm < 6
        base.alpha_composite(A["ceu_noite"] if noite else _tint(A["ceu_dia"], cor), (cx - r, cy - r))
        if not noite:
            im, py = A["sol"]
            t = max(0, min(1, (hm - 6) / 12))
            base.alpha_composite(_girar(W, im, (cx - im.width / 2, cy - py), (cx, cy), -78 + 156 * t))
        else:
            im, py = A[f"lua_{fase}"]
            t = max(0, min(1, ((hm - 18) if hm >= 18 else hm + 6) / 12))
            base.alpha_composite(_girar(W, im, (cx - im.width / 2, cy - py), (cx, cy), -78 + 156 * t))
        for nome, ang, piv in (("marcador_mes", 15 + mes0 * 30, (C, C)), ("marcador_dia", (dia - 1) * 360 / 31 + 180 / 31, (C, C)),
                               ("marcador_sem", dsem * 360 / 7, (SEM[0], SEM[1]))):
            im = _tint(A[nome], cor)
            if nome == "marcador_sem":
                pos = (SEM[0] - im.width / 2, SEM[1] - im.height + 4)
            else:
                pos = (C - im.width / 2, C - im.height)
            base.alpha_composite(_girar(W, im, pos, piv, ang))
        d = ImageDraw.Draw(base)
        tc = TEMAS[tema].texto
        d.text((SLOTS["esq"][0] + 31, SLOTS["esq"][1] + 20), "8,2k", font=fonte("SemiBold", 22), fill=tc, anchor="mm")
        d.text((SLOTS["dir"][0] + 31, SLOTS["dir"][1] + 20), "76%", font=fonte("SemiBold", 22), fill=tc, anchor="mm")
        for nome, ang in (("hora_sombra", ang_h), ("min_sombra", ang_m)):
            im, py = A[nome]
            base.alpha_composite(_girar(W, im, (C - im.width / 2, C - py), (C, C), ang))
        for nome, ang in (("hora", ang_h), ("min", ang_m)):
            im, py = A[nome]
            base.alpha_composite(_girar(W, im, (C - im.width / 2, C - py), (C, C), ang))
        im, py = A["seg_sombra"]
        base.alpha_composite(_girar(W, im, (C - im.width / 2, C - py), (C, C), ang_s))
        im, py = A["seg"]
        base.alpha_composite(_girar(W, _tint(im, cor), (C - im.width / 2, C - py), (C, C), ang_s))
    mk = Image.new("L", (W * 4, W * 4), 0)
    ImageDraw.Draw(mk).ellipse([0, 0, W * 4 - 1, W * 4 - 1], fill=255)
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    out.paste(base, (0, 0), mk.resize((W, W), Image.LANCZOS))
    return out


# ------------------------------------------------------------------ orquestração
def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Sun and Moon", "tema_label": "Dial", "tema_claro": "Light", "tema_escuro": "Dark",
          "acento_label": "Accent color", "slot_esq": "Left field", "slot_dir": "Right field"}
    pt = {"watch_face_name": "Sol e Lua", "tema_label": "Mostrador", "tema_claro": "Claro", "tema_escuro": "Escuro",
          "acento_label": "Cor de destaque", "slot_esq": "Campo esquerdo", "slot_dir": "Campo direito"}
    for i, (n, _) in enumerate(ACENTOS):
        en[f"acento_{n}"] = {"laranja": "Orange", "azul": "Blue", "verde": "Green", "rosa": "Pink", "roxo": "Purple"}[n]
        pt[f"acento_{n}"] = {"laranja": "Laranja", "azul": "Azul", "verde": "Verde", "rosa": "Rosa", "roxo": "Roxo"}[n]
    res = criar_modulo(raiz, NOME, en, pt, flavors=False)
    dr = res / "drawable-nodpi"
    print("  mostradores...")
    A: dict[str, Image.Image | tuple] = {}
    med: dict[str, tuple[int, int, float]] = {}
    for i, t in TEMAS.items():
        A[f"fundo_{i}"] = fundo(t)
    A["ambiente"] = ambiente()
    A["ceu_dia"], A["ceu_noite"] = ceu(False), ceu(True)
    A["sol"] = sol()
    for f in range(8):
        A[f"lua_{f}"] = lua(f)
    A["marcador_mes"], A["marcador_dia"], A["marcador_sem"] = marcador_mes(), marcador_dia(), marcador_sem()
    hh = _mao(112, 24, 26)
    mm = _mao(168, 26, 20)
    A["hora"], A["min"] = hh, mm
    A["hora_sombra"], A["min_sombra"] = sombra_mao(*hh), sombra_mao(*mm)
    A["hora_contorno"], A["min_contorno"] = _mao(112, 24, 26, contorno=True), _mao(168, 26, 20, contorno=True)
    A["seg"] = seg_mao()
    A["seg_sombra"] = sombra_mao(*A["seg"])
    for nome, v in A.items():
        im, py = (v if isinstance(v, tuple) else (v, 0.0))
        im.save(dr / f"{nome}.png", optimize=True)
        med[nome] = (im.width, im.height, py)
    # previsualização: imagens "puras" (sem tupla) e (img, pivô) para as que giram
    P: dict = {k: (v if isinstance(v, tuple) else v) for k, v in A.items()}
    xml = gerar_xml(med, med["sol"], (med["marcador_mes"][0], med["marcador_mes"][1]), (med["marcador_dia"][0], med["marcador_dia"][1]),
                    (med["marcador_sem"][0], med["marcador_sem"][1]))
    (res / "raw" / "watchface.xml").write_text(xml, encoding="utf-8")
    print("  prévias...")
    pv = raiz / "previews"
    pv.mkdir(exist_ok=True)
    imgs = [previa(P, "claro", "#ff7a1a", 10, 8, 32, 28, 9, 3, 6), previa(P, "escuro", "#3d8bff", 20, 10, 15, 3, 10, 1, 4),
            previa(P, "claro", "#2fa365", 16, 45, 50, 14, 4, 5, 2), previa(P, "escuro", "#ff4f8b", 3, 20, 40, 21, 0, 0, 0),
            previa(P, "claro", "#ff7a1a", 10, 8, 0, 28, 9, 3, 6, True)]
    for nome, im in zip(["claro_laranja", "escuro_azul", "claro_verde_dia", "escuro_rosa_noite", "ambiente"], imgs):
        im.save(pv / f"lunar_{nome}.png", optimize=True)
    imgs[0].resize((450, 450), Image.LANCZOS).save(dr / "preview.png", optimize=True)
    from faces.cronos_previa import folha
    folha(imgs, ["Claro + laranja", "Escuro + azul (noite)", "Claro + verde", "Escuro + rosa (noite)", "Ambiente (AOD)"], cols=3).save(pv / "lunar_folha.png", optimize=True)
    return {"xml_bytes": len(xml)}
