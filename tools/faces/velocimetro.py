"""Watchface "Velocímetro": painel de carro. O ponteiro marca o minuto (0 a 60) num arco de 270 graus com zona vermelha no fim, a hora vai grande
no meio e um anel fino mostra os segundos. Original."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, grad_radial, polar, reduzir_por, tela, texto_centrado
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, girar, grupo, hora, img, redondo, rgb, textos_acento, tint, tpl

NOME = "velocimetro"
A0, A1 = -135, 135


def mostrador() -> Image.Image:
    n = W * SS
    c = n / 2
    im = tela(n)
    fundo = grad_radial(n, c - 30 * SS, c - 40 * SS, [(0, (30, 33, 40, 255)), (240 * SS, (6, 7, 10, 255))])
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).ellipse([0, 0, n - 1, n - 1], fill=255)
    fundo.putalpha(m)
    im.alpha_composite(fundo)
    d = ImageDraw.Draw(im)
    for k in range(0, 61):
        a = A0 + k * (A1 - A0) / 60
        mj = k % 10 == 0
        vermelho = k >= 50
        cor = (255, 70, 60, 255) if vermelho else (255, 255, 255, 255 if mj else 170)
        d.line([polar(c, c, (196 if mj else 206) * SS, a), polar(c, c, 222 * SS, a)], fill=cor, width=int((5 if mj else 2.4) * SS))
    f = fonte("SemiBold", 24 * SS)
    for k in range(0, 61, 10):
        a = A0 + k * (A1 - A0) / 60
        x, y = polar(c, c, 168 * SS, a)
        texto_centrado(im, str(k), x, y, f, (255, 90, 80, 255) if k >= 50 else (255, 255, 255, 235), rot=0)
    d.arc([c - 232 * SS, c - 232 * SS, c + 232 * SS, c + 232 * SS], 90 + 135 - 90 + 0, 90 + 135 + 90 - 0 + 0, fill=(255, 255, 255, 0), width=1)
    return reduzir_por(im)


def agulha() -> tuple[Image.Image, float]:
    s = 4
    pad, comp, cauda = 4, 196, 40
    w, h = 22, comp + cauda + 2 * pad
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, py = w * s / 2, (pad + comp) * s
    d.polygon([(cx, pad * s), (cx + 4.5 * s, py), (cx + 3 * s, py + cauda * s), (cx - 3 * s, py + cauda * s), (cx - 4.5 * s, py)], fill=(255, 255, 255, 255))
    d.ellipse([cx - 11 * s, py - 11 * s, cx + 11 * s, py + 11 * s], fill=(255, 255, 255, 255))
    d.ellipse([cx - 5 * s, py - 5 * s, cx + 5 * s, py + 5 * s], fill=(22, 24, 28, 255))
    return im.resize((w, h), Image.LANCZOS), pad + comp


def xml(med) -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    w, h, py = med
    L = cabecalho(NOME) + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("painel", "", 0) + img(0, 0, W, W, "mostrador")
      + f'<PartDraw {full}><Arc centerX="{C}" centerY="{C}" width="236" height="236" startAngle="{A0}" endAngle="{A0}"><Stroke thickness="6" color="{ac}" cap="ROUND" /><Transform target="endAngle" value="{A0} + [SECOND] * 4.5" /></Arc></PartDraw>'
      + hora(130, 258, 220, 100, "hh", 92, "#ffffffff", "BOLD", "CENTER") + tpl(150, 350, 180, 26, 18, ac, "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM") + "</Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255) + f'<PartDraw {full}><Ellipse x="1" y="1" width="478" height="478"><Stroke thickness="2" color="#66ffffff" /></Ellipse></PartDraw>'
      + hora(90, 190, 300, 110, "hh:mm", 84, "#ffc0c0c8", "LIGHT", "CENTER") + "</Group>")
    a(f'    <Group name="agulha" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="{A0} + ([MINUTE] + [SECOND] / 60) * 4.5" />'
      f'<PartImage x="{C - w // 2}" y="{round(C - py)}" width="{w}" height="{h}" tintColor="{ac}"><Image resource="agulha" /><Variant mode="AMBIENT" target="alpha" value="0" /></PartImage></Group>')
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.ellipse([1, 1, W - 2, W - 2], outline=(102, 102, 102), width=2)
        d.text((C, 245), f"{h:02d}:{mi:02d}", font=fonte("Light", 84), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    base.alpha_composite(A["mostrador"])
    d = ImageDraw.Draw(base)
    d.arc([C - 118, C - 118, C + 118, C + 118], 90 + A0 - 90 + 90 - 90 + 0 - 0 - 0 + (-90 + 0) * 0 - 0 + 0 + 0 + 0 - 0, 0, fill=ac, width=1) if False else None
    ang_fim = A0 + s * 4.5
    d.arc([C - 118, C - 118, C + 118, C + 118], -90 + A0, -90 + ang_fim, fill=ac, width=6)
    d.text((C, 312), f"{h:02d}", font=fonte("Bold", 92), fill=(255, 255, 255), anchor="mm")
    d.text((C, 360), "SEX 31", font=fonte("Medium", 18), fill=ac, anchor="mm")
    im, py = A["agulha"]
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cam.alpha_composite(tint(im, ac), (int(C - im.width / 2), int(round(C - py))))
    base.alpha_composite(cam.rotate(-(A0 + (mi + s / 60) * 4.5), center=(C, C), resample=Image.BICUBIC))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Speedometer", "Velocímetro")
    A = {"mostrador": mostrador(), "agulha": agulha()}
    med = (A["agulha"][0].width, A["agulha"][0].height, A["agulha"][1])
    imgs = {"mostrador": A["mostrador"], "agulha": A["agulha"][0]}
    pv = [previa(A, "#ff7a2f", 10, 8, 20), previa(A, "#33d6ff", 3, 47, 5), previa(A, "#4be37a", 8, 30, 45), previa(A, "#ff7a2f", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(med), imgs, pv, ["Laranja", "Ciano", "Verde", "Ambiente (AOD)"], cols=4, nomes_previa=["laranja", "ciano", "verde", "ambiente"])
