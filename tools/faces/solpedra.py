"""Watchface "Sol de Pedra": um relógio de sol. O gnômon projeta uma sombra que gira com a hora (de 6h a 18h na metade de baixo da pedra);
a hora digital fica na metade de cima. Três pedras: arenito, basalto e mármore. Original."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from wf.desenho import SS, fonte, polar, reduzir_por, sombra, tela, texto_centrado
from wf.kit import C, W, cabecalho, finalizar, girar, grupo, hora, img, redondo, rgb, strings_opcoes, tpl

NOME = "solpedra"
PEDRAS = [("arenito", (214, 188, 148), (92, 68, 40)), ("basalto", (92, 96, 104), (230, 232, 238)), ("marmore", (236, 236, 238), (70, 72, 80))]
CY = 262                                         # centro do gnômon
COMP = 190                                       # comprimento da sombra


def pedra(base, tinta) -> Image.Image:
    n = W * SS
    c = n / 2
    rng = np.random.default_rng(6)
    ruido = np.zeros((W, W), np.float32)
    for esc in (60, 24, 9, 4):
        r = rng.random((W // esc + 3, W // esc + 3)).astype(np.float32)
        ruido += np.asarray(Image.fromarray((r * 255).astype(np.uint8)).resize((W, W), Image.BICUBIC), np.float32) / 255 * (esc / 60) ** 0.5
    ruido /= ruido.max()
    yy, xx = np.mgrid[0:W, 0:W]
    dist = np.hypot(xx - C, yy - C)
    luz = 1.05 - 0.28 * (dist / 238) ** 2 + 0.06 * np.cos(np.arctan2(yy - C, xx - C) + 0.8)
    cor = np.array(base, np.float32)[None, None, :] * (luz * (0.86 + 0.24 * ruido))[..., None]
    a = np.clip((236 - dist) / 1.5, 0, 1)
    out = np.dstack([np.clip(cor, 0, 255), a * 255]).astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    big = im.resize((n, n), Image.LANCZOS)
    d = ImageDraw.Draw(big)
    d.ellipse([c - 236 * SS, c - 236 * SS, c + 236 * SS, c + 236 * SS], outline=tuple(int(v * 0.55) for v in base) + (255,), width=3 * SS)
    f = fonte("SemiBold", 22 * SS)
    for h_ in range(6, 19):
        a_ = (h_ - 12) * 15 + 180
        longo = h_ % 3 == 0
        d.line([polar(c, c + (CY - C) * SS, 70 * SS, a_), polar(c, c + (CY - C) * SS, 206 * SS, a_)], fill=tuple(int(v) for v in tinta) + (200 if longo else 120,), width=int((3 if longo else 1.8) * SS))
        x, y = polar(c, c + (CY - C) * SS, 220 * SS, a_)
        if longo or True:
            texto_centrado(big, str(h_), x, y, f if longo else fonte("Medium", 16 * SS), tuple(int(v) for v in tinta) + (255 if longo else 170,), rot=-a_ + 180)
    return reduzir_por(big)


def sombra_png() -> tuple[Image.Image, float]:
    s = 4
    pad = 10
    w, h = 44, COMP + 2 * pad
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = w * s / 2
    d.polygon([(cx - 22 * s, pad * s), (cx + 22 * s, pad * s), (cx + 6 * s, (pad + COMP) * s), (cx - 6 * s, (pad + COMP) * s)], fill=(0, 0, 0, 255))
    im = im.filter(ImageFilter.GaussianBlur(2.2 * s))
    a = np.asarray(im).astype(np.float32).copy()
    a[..., 3] *= 0.52
    return Image.fromarray(a.astype(np.uint8), "RGBA").resize((w, h), Image.LANCZOS), pad + COMP        # pivô na base (centro do gnômon)


def gnomon() -> Image.Image:
    t = 60
    im = Image.new("RGBA", (t * 4, t * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = t * 2
    d.polygon([(c, c - 22 * 4), (c + 22 * 4, c + 18 * 4), (c - 22 * 4, c + 18 * 4)], fill=(188, 190, 196, 255))
    d.polygon([(c, c - 22 * 4), (c + 22 * 4, c + 18 * 4), (c, c + 18 * 4)], fill=(120, 122, 130, 255))
    d.polygon([(c, c - 22 * 4), (c - 22 * 4, c + 18 * 4), (c, c + 18 * 4)], fill=(222, 224, 230, 255))
    return im.resize((t, t), Image.LANCZOS)


def xml(med) -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    w, h, py = med
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", '    <ListConfiguration id="pedra" displayName="pedra_label" defaultValue="arenito">'
                                       + "".join(f'<ListOption id="{k}" displayName="pedra_{k}" />' for k, _, _ in PEDRAS) + "</ListConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0) + '<ListConfiguration id="pedra">')
    for k, base, tinta in PEDRAS:
        cor = "#ff%02x%02x%02x" % tuple(tinta)
        a(f'      <ListOption id="{k}"><Group name="p_{k}" {full}>' + img(0, 0, W, W, f"pedra_{k}")
          + hora(90, 70, 300, 100, "hh:mm", 80, cor, "BOLD", "CENTER") + tpl(130, 160, 220, 26, 18, cor, "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM") + "</Group></ListOption>")
    a("    </ListConfiguration>")
    a(f'      <Group name="sombra" {full} pivotX="0.5" pivotY="{CY / W:.5f}"><Transform target="angle" value="(clamp([HOUR_0_23_MINUTE], 6, 18) - 12) * 15 + 180" />'
      + img(C - w // 2, round(CY - py), w, h, "sombra") + "</Group>")
    a("      " + img(C - 30, CY - 30, 60, 60, "gnomon"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw {full}><Ellipse x="1" y="1" width="478" height="478"><Stroke thickness="2" color="#66ffffff" /></Ellipse></PartDraw>')
    a("      " + hora(90, 100, 300, 100, "hh:mm", 80, "#ffc0c0c8", "MEDIUM", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, pedra_id: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    base_c, tinta = next((b, t) for k, b, t in PEDRAS if k == pedra_id)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.ellipse([1, 1, W - 2, W - 2], outline=(102, 102, 102), width=2)
        d.text((C, 150), f"{h:02d}:{mi:02d}", font=fonte("Medium", 80), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    base.alpha_composite(A[f"pedra_{pedra_id}"])
    d = ImageDraw.Draw(base)
    d.text((C, 120), f"{h:02d}:{mi:02d}", font=fonte("Bold", 80), fill=tinta, anchor="mm")
    d.text((C, 172), "SEX 31", font=fonte("Medium", 18), fill=tinta, anchor="mm")
    hh = max(6, min(18, h + mi / 60))
    ang = (hh - 12) * 15 + 180
    im, py = A["sombra"]
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cam.alpha_composite(im, (int(C - im.width / 2), int(round(CY - py))))
    base.alpha_composite(cam.rotate(-ang, center=(C, CY), resample=Image.BICUBIC))
    base.alpha_composite(A["gnomon"], (C - 30, CY - 30))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Stone Sundial", "pedra_label": "Stone", "pedra_arenito": "Sandstone", "pedra_basalto": "Basalt", "pedra_marmore": "Marble"}
    pt = {"watch_face_name": "Sol de Pedra", "pedra_label": "Pedra", "pedra_arenito": "Arenito", "pedra_basalto": "Basalto", "pedra_marmore": "Mármore"}
    A = {f"pedra_{k}": pedra(b, t) for k, b, t in PEDRAS}
    sh, py = sombra_png()
    A["sombra"] = (sh, py)
    A["gnomon"] = gnomon()
    med = (sh.width, sh.height, py)
    imgs = {k: (v[0] if isinstance(v, tuple) else v) for k, v in A.items()}
    pv = [previa(A, "arenito", 10, 8), previa(A, "basalto", 15, 30), previa(A, "marmore", 7, 45), previa(A, "arenito", 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(med), imgs, pv, ["Arenito 10:08", "Basalto 15:30", "Mármore 07:45", "Ambiente (AOD)"], cols=4, nomes_previa=["arenito", "basalto", "marmore", "ambiente"])
