"""Primitivas de desenho para gerar os assets (mostradores, ponteiros, texturas).

Tudo é desenhado em super-resolução (SS x) e reduzido no final, para ficar com
borda suave (antialias). Luz global vem do canto superior esquerdo.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

SS = 3  # fator de super-resolução
FONTES = Path(__file__).resolve().parent.parent / "fonts"

Cor = tuple[int, int, int]


def fonte(peso: str, tamanho: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTES / f"Inter-{peso}.otf"), int(round(tamanho)))


def fonte_serifa(tamanho: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTES / "LiberationSerif-Bold.ttf"), int(round(tamanho)))


def tela(n: int) -> Image.Image:
    return Image.new("RGBA", (n, n), (0, 0, 0, 0))


def _arr_interp(t: np.ndarray, paradas: list[tuple[float, tuple]]) -> np.ndarray:
    pos = [p for p, _ in paradas]
    cols = np.array([c if len(c) == 4 else (*c, 255) for _, c in paradas], dtype=np.float32)
    return np.stack([np.interp(t, pos, cols[:, k]) for k in range(4)], axis=-1)


def _para_img(a: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def grade(n: int) -> tuple[np.ndarray, np.ndarray]:
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    return xx, yy


def grad_radial(n, cx, cy, paradas) -> Image.Image:
    xx, yy = grade(n)
    return _para_img(_arr_interp(np.hypot(xx - cx, yy - cy), paradas))


def grad_linear(n, p0, p1, paradas) -> Image.Image:
    xx, yy = grade(n)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    t = ((xx - p0[0]) * dx + (yy - p0[1]) * dy) / (dx * dx + dy * dy)
    return _para_img(_arr_interp(t, paradas))


def grad_conico(n, cx, cy, paradas, rot=0.0) -> Image.Image:
    """Gradiente cônico (0..1 volta completa) — dá o brilho de metal usinado."""
    xx, yy = grade(n)
    t = ((np.arctan2(yy - cy, xx - cx) + math.radians(rot)) / (2 * math.pi)) % 1.0
    return _para_img(_arr_interp(t, paradas))


def mascara_anel(n, cx, cy, r_ext, r_int=0.0) -> np.ndarray:
    """Cobertura 0..1 (com antialias de 1px) de um anel/disco."""
    xx, yy = grade(n)
    d = np.hypot(xx - cx, yy - cy)
    return np.clip(r_ext - d + 0.5, 0, 1) * np.clip(d - r_int + 0.5, 0, 1)


def com_mascara(img: Image.Image, mascara: np.ndarray) -> Image.Image:
    a = np.asarray(img).astype(np.float32).copy()
    a[..., 3] *= mascara
    return _para_img(a)


def escurecer(img: Image.Image, fator: float) -> Image.Image:
    a = np.asarray(img).astype(np.float32).copy()
    a[..., :3] *= fator
    return _para_img(a)


def metal_paradas(clara: Cor, media: Cor, escura: Cor) -> list:
    """Paradas periódicas que imitam metal polido com reflexos opostos."""
    return [(0.00, media), (0.10, clara), (0.22, media), (0.38, escura), (0.50, media),
            (0.60, clara), (0.72, media), (0.88, escura), (1.00, media)]


def sombra(alfa_src: Image.Image, dx: float, dy: float, desfoque: float, opac: float,
           cor: Cor = (0, 0, 0)) -> Image.Image:
    """Sombra suave a partir do canal alfa de uma imagem."""
    a = alfa_src.getchannel("A")
    a = ImageChops.offset(a, int(round(dx)), int(round(dy))).filter(ImageFilter.GaussianBlur(desfoque))
    a = a.point(lambda v: int(v * opac))
    out = Image.new("RGBA", alfa_src.size, (*cor, 0))
    out.putalpha(a)
    return out


def reduzir(img: Image.Image, tam: int) -> Image.Image:
    return img.resize((tam, tam), Image.LANCZOS)


def reduzir_por(img: Image.Image, fator: int = SS) -> Image.Image:
    return img.resize((img.width // fator, img.height // fator), Image.LANCZOS)


def texto_centrado(camada: Image.Image, txt: str, cx: float, cy: float, f: ImageFont.FreeTypeFont,
                   cor, rot: float = 0.0, espaco: float = 0.0) -> None:
    """Escreve texto centrado em (cx,cy), girado `rot` graus (anti-horário, como PIL)."""
    larg = [f.getlength(c) for c in txt]
    total = sum(larg) + espaco * (len(txt) - 1)
    asc, desc = f.getmetrics()
    w, h = int(total) + 8, asc + desc + 8
    t = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    x = 4.0
    for c, lw in zip(txt, larg):
        d.text((x, 4), c, font=f, fill=cor)
        x += lw + espaco
    bbox = t.getbbox()
    if bbox:
        t = t.crop(bbox)
    if rot:
        t = t.rotate(rot, expand=True, resample=Image.BICUBIC)
    camada.alpha_composite(t, (int(round(cx - t.width / 2)), int(round(cy - t.height / 2))))


def polar(cx: float, cy: float, raio: float, ang_graus: float) -> tuple[float, float]:
    """Ângulo em graus no relógio: 0 = 12h, sentido horário."""
    a = math.radians(ang_graus)
    return cx + raio * math.sin(a), cy - raio * math.cos(a)


def ruido(n: int, semente: int, escala: float = 1.0) -> np.ndarray:
    rng = np.random.default_rng(semente)
    return rng.standard_normal((n, n)).astype(np.float32) * escala


def texto_arco(camada: Image.Image, txt: str, cx: float, cy: float, raio: float, ang_centro: float,
               f: ImageFont.FreeTypeFont, cor, espaco: float = 0.0) -> None:
    """Texto ao longo de um arco, sempre legível (metade de baixo é invertida para ficar em pé)."""
    larg = [f.getlength(c) + espaco for c in txt]
    inferior = 90 < (ang_centro % 360) < 270
    total = sum(larg)
    graus = math.degrees(total / raio)
    pos = -graus / 2
    letras = []
    for c, lw in zip(txt, larg):
        letras.append((c, pos + math.degrees(lw / raio) / 2))
        pos += math.degrees(lw / raio)
    for c, off in letras:
        a = ang_centro + (-off if inferior else off)
        x, y = polar(cx, cy, raio, a)
        texto_centrado(camada, c, x, y, f, cor, rot=-a + (180 if inferior else 0))
