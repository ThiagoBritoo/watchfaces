"""Watchface "24 Horas": relógio de 24 horas (a hora dá uma volta por DIA), com metade escura para a noite, ponteiro de hora com ponta de
sol, minuto num subdial e data. Estilo instrumento. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, grad_radial, polar, reduzir_por, sombra, tela, texto_centrado
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, textos_acento, tint, tpl, girar

NOME = "vintequatro"
SUB = (C, 340, 54)


def mostrador() -> Image.Image:
    n = W * SS
    c = n / 2
    im = tela(n)
    base = grad_radial(n, c - 40 * SS, c - 50 * SS, [(0, (34, 38, 46, 255)), (240 * SS, (8, 10, 14, 255))])
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).ellipse([0, 0, n - 1, n - 1], fill=255)
    base.putalpha(m)
    im.alpha_composite(base)
    d = ImageDraw.Draw(im)
    # metade da noite (18h..06h, parte de baixo no 24h com 12h ao topo? usamos 0h embaixo): faixa escurecida
    ring = Image.new("L", (n, n), 0)
    dr = ImageDraw.Draw(ring)
    dr.pieslice([c - 228 * SS, c - 228 * SS, c + 228 * SS, c + 228 * SS], 90 + 90 + 0, 90 + 270, fill=255)   # metade inferior (noite)
    dr.ellipse([c - 160 * SS, c - 160 * SS, c + 160 * SS, c + 160 * SS], fill=0)
    nr = Image.new("RGBA", (n, n), (70, 90, 170, 0))
    nr.putalpha(ring.point(lambda v: int(v * 0.35)))
    im.alpha_composite(nr)
    d = ImageDraw.Draw(im)
    for hh in range(24):                                  # 24 horas, 12h no topo e 0h embaixo
        a = (hh - 12) * 15 + 180 if False else hh * 15 + 180
        mj = hh % 6 == 0
        d.line([polar(c, c, (200 if mj else 212) * SS, a), polar(c, c, 226 * SS, a)], fill=(255, 255, 255, 255 if mj else 170), width=int((4 if mj else 2) * SS))
    f = fonte("SemiBold", 28 * SS)
    f2 = fonte("Medium", 20 * SS)
    for hh in range(0, 24, 2):
        a = hh * 15 + 180
        x, y = polar(c, c, 176 * SS, a)
        texto_centrado(im, f"{hh:02d}" if hh not in (0, 12) else str(hh), x, y, f if hh % 6 == 0 else f2, (255, 255, 255, 255 if hh % 6 == 0 else 190), rot=-a + (180 if 90 < a % 360 < 270 else 0))
    for m_ in range(60):
        pass
    d.ellipse([c - 232 * SS, c - 232 * SS, c + 232 * SS, c + 232 * SS], outline=(255, 255, 255, 140), width=int(2 * SS))
    # subdial dos minutos
    sx, sy, sr = SUB
    d.ellipse([(sx - sr) * SS, (sy - sr) * SS, (sx + sr) * SS, (sy + sr) * SS], fill=(14, 16, 20, 255), outline=(255, 255, 255, 170), width=int(2 * SS))
    for m_ in range(0, 60, 5):
        a = m_ * 6
        d.line([polar(sx * SS, sy * SS, (sr - 8) * SS, a), polar(sx * SS, sy * SS, (sr - 2) * SS, a)], fill=(255, 255, 255, 220), width=int(2 * SS))
    return reduzir_por(im)


def ponteiro_24() -> tuple[Image.Image, float]:
    s = 4
    pad, comp, cauda = 6, 164, 30
    w, h = 36, int(comp + cauda) + 2 * pad
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, py = w * s / 2, (pad + comp) * s
    hw = 7 * s
    d.polygon([(cx, (pad + 24) * s), (cx + hw, py), (cx + hw * 0.6, py + cauda * s), (cx - hw * 0.6, py + cauda * s), (cx - hw, py)], fill=(255, 255, 255, 255))
    d.polygon([(cx, (pad + 24) * s), (cx, py + cauda * s), (cx - hw * 0.6, py + cauda * s), (cx - hw, py)], fill=(196, 200, 210, 255))
    d.ellipse([cx - 11 * s, pad * s - 2 * s, cx + 11 * s, (pad + 22) * s], fill=(255, 255, 255, 255))    # sol na ponta (será tingido)
    return im.resize((w, h), Image.LANCZOS), pad + comp


def min_agulha() -> tuple[Image.Image, float]:
    s = 4
    pad, comp, cauda = 3, 44, 8
    w, h = 12, comp + cauda + 2 * pad
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, py = w * s / 2, (pad + comp) * s
    d.polygon([(cx, pad * s), (cx + 2.2 * s, py), (cx + 2.2 * s, py + cauda * s), (cx - 2.2 * s, py + cauda * s), (cx - 2.2 * s, py)], fill=(255, 255, 255, 255))
    return im.resize((w, h), Image.LANCZOS), pad + comp


def xml(m: dict) -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    w, h, py = m["p24"]
    mw, mh, mpy = m["pmin"]
    sx, sy, sr = SUB
    L = cabecalho(NOME) + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("mostrador", "", 0) + img(0, 0, W, W, "mostrador") + tpl(176, 240, 128, 30, 22, "#ffffffff", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM") + "</Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255)
      + f'<PartDraw {full}><Ellipse x="1" y="1" width="478" height="478"><Stroke thickness="2" color="#88ffffff" /></Ellipse></PartDraw>'
      + hora(150, 280, 180, 60, "hh:mm", 44, "#ffc0c0c8", "MEDIUM", "CENTER") + "</Group>")
    # ponteiro de 24 h: uma volta por dia, 0h embaixo -> ângulo = 180 + hora*15
    a(f'    <Group name="p24" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="180 + [HOUR_0_23_MINUTE] * 15" />'
      f'<PartImage x="{C - w // 2}" y="{round(C - py)}" width="{w}" height="{h}" tintColor="{ac}"><Image resource="p24" /></PartImage></Group>')
    a(f'    <Group name="minuto" x="0" y="0" width="{W}" height="{W}"><Variant mode="AMBIENT" target="alpha" value="0" />'
      f'<Group name="pmin" x="{sx - mw // 2}" y="{sy - round(mpy)}" width="{mw}" height="{mh}" pivotX="0.5" pivotY="{mpy / mh:.6f}"><Transform target="angle" value="[MINUTE] * 6" />'
      f'<PartImage x="0" y="0" width="{mw}" height="{mh}"><Image resource="pmin" /></PartImage></Group></Group>')
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.ellipse([1, 1, W - 2, W - 2], outline=(136, 136, 136), width=2)
        d.text((C, 310), f"{h:02d}:{mi:02d}", font=fonte("Medium", 44), fill=(192, 192, 200), anchor="mm")
    else:
        base.alpha_composite(A["mostrador"])
        d.text((C, 255), "SEX 31", font=fonte("Medium", 22), fill=(255, 255, 255), anchor="mm")
        im, py = A["pmin"]
        c_ = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        c_.alpha_composite(im, (int(SUB[0] - im.width / 2), int(round(SUB[1] - py))))
        base.alpha_composite(c_.rotate(-mi * 6, center=(SUB[0], SUB[1]), resample=Image.BICUBIC))
    im, py = A["p24"]
    c_ = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    c_.alpha_composite(tint(im, ac), (int(C - im.width / 2), int(round(C - py))))
    base.alpha_composite(c_.rotate(-(180 + (h + mi / 60) * 15), center=(C, C), resample=Image.BICUBIC))
    d = ImageDraw.Draw(base)
    d.ellipse([C - 7, C - 7, C + 7, C + 7], fill=(20, 20, 24), outline=(255, 255, 255), width=2)
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "24 Hours", "24 Horas")
    A = {"mostrador": mostrador(), "p24": ponteiro_24(), "pmin": min_agulha()}
    med = {k: (v[0].width, v[0].height, v[1]) for k, v in A.items() if isinstance(v, tuple)}
    imgs = {k: (v[0] if isinstance(v, tuple) else v) for k, v in A.items()}
    pv = [previa(A, "#ff7a2f", 10, 8, 0), previa(A, "#33d6ff", 19, 40, 0), previa(A, "#f2c14e", 3, 15, 0), previa(A, "#ff7a2f", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(med), imgs, pv, ["10:08", "19:40 (noite)", "03:15", "Ambiente (AOD)"], cols=4, nomes_previa=["dia", "noite", "madrugada", "ambiente"])
