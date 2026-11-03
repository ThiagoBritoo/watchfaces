"""Watchface "Pixel": o céu do dia (como o Céu do Dia) em pixel art: fundo em blocos de 6 px com cores quantizadas, sol e lua pixelados e silhueta de
montanhas em degraus. Reaproveita o XML e as ideias do Céu do Dia. Original."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, finalizar, redondo

from . import ceu as CE

NOME = "pixel"
BLOCO = 6


def pixelar(im: Image.Image, bloco: int = BLOCO, niveis: int | None = None) -> Image.Image:
    w, h = im.size
    p = im.resize((max(1, w // bloco), max(1, h // bloco)), Image.BOX)
    if niveis:
        a = np.asarray(p).astype(np.int32)
        a[..., :3] = (a[..., :3] // niveis) * niveis + niveis // 2
        a[..., 3] = np.where(a[..., 3] > 127, 255, 0)
        p = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    return p.resize((w, h), Image.NEAREST)


def previa(A, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    hd = h + mi / 60
    if ambiente_:
        ImageDraw.Draw(base).text((C, 220), f"{h:02d}:{mi:02d}", font=fonte("Light", 92), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    off = int(hd / 24 * (CE.FAIXA - W))
    base.alpha_composite(A["faixa"].crop((off, 0, off + W, W)))
    if hd >= 18.5 or hd < 5.5:
        base.alpha_composite(A["estrelas"])
    dia = 6 <= hd < 18
    t = max(0, min(1, ((hd - 6) if dia else ((hd - 18) if hd >= 18 else hd + 6)) / 12))
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cam.paste(A["astro_sol" if dia else "astro_lua"], (C - 40, CE.PIV_Y - CE.RAIO - 40))
    base.alpha_composite(cam.rotate(-(-84 + 168 * t), center=(C, CE.PIV_Y), resample=Image.NEAREST))
    base.alpha_composite(A["silhueta"])
    d = ImageDraw.Draw(base)
    d.text((C, 295), f"{h:02d}:{mi:02d}", font=fonte("Bold", 92), fill=(255, 255, 255), anchor="mm")
    d.text((C, 350), "SEX 31 OUT", font=fonte("Bold", 20), fill=(220, 224, 230), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Pixel Sky"}
    pt = {"watch_face_name": "Céu Pixel"}
    A = {"faixa": pixelar(CE.faixa(), BLOCO, 28), "estrelas": pixelar(CE.estrelas(), 4, 64), "astro_sol": pixelar(CE.astro(False), 4, 32),
         "astro_lua": pixelar(CE.astro(True), 4, 32), "silhueta": pixelar(CE.silhueta(), BLOCO, 8)}
    xm = CE.xml().replace("DIGITAL", "DIGITAL")
    xm = xm.replace('weight="LIGHT"', 'weight="BOLD"', 1)
    pv = [previa(A, 6, 40), previa(A, 12, 5), previa(A, 18, 20), previa(A, 23, 15), previa(A, 12, 5, True)]
    return finalizar(raiz, NOME, en, pt, xm, A, pv, ["06:40 aurora", "12:05 dia", "18:20 entardecer", "23:15 noite", "Ambiente (AOD)"], cols=5, nomes_previa=["aurora", "dia", "tarde", "noite", "ambiente"])
