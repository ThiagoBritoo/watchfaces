"""Watchface "Bússola": mostrador de instrumento de navegação (rosa dos ventos com N/L/S/O, graus de 5 em 5) e ponteiros em forma de
agulha de bússola (ponta colorida, cauda branca). Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, grad_radial, polar, reduzir_por, sombra, tela, texto_centrado
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, redondo, rgb, textos_acento, tint, tpl

NOME = "bussola"


def mostrador() -> Image.Image:
    n = W * SS
    c = n / 2
    im = tela(n)
    d = ImageDraw.Draw(im)
    fundo = grad_radial(n, c - 40 * SS, c - 50 * SS, [(0, (40, 44, 50, 255)), (240 * SS, (10, 12, 14, 255))])
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).ellipse([0, 0, n - 1, n - 1], fill=255)
    fundo.putalpha(m)
    im.alpha_composite(fundo)
    d = ImageDraw.Draw(im)
    for r in (236, 200, 140):
        d.ellipse([c - r * SS, c - r * SS, c + r * SS, c + r * SS], outline=(255, 255, 255, 70 if r != 236 else 120), width=int(1.6 * SS))
    for g in range(0, 360, 5):
        mj = g % 30 == 0
        d.line([polar(c, c, (216 if mj else 224) * SS, g), polar(c, c, 234 * SS, g)], fill=(255, 255, 255, 255 if mj else 140), width=int((3.4 if mj else 1.6) * SS))
    f = fonte("Medium", 17 * SS)
    for g in range(30, 360, 30):
        if g % 90 == 0:
            continue
        x, y = polar(c, c, 190 * SS, g)
        texto_centrado(im, str(g), x, y, f, (255, 255, 255, 200), rot=-g)
    fc = fonte("Bold", 34 * SS)
    for g, t in ((0, "N"), (90, "L"), (180, "S"), (270, "O")):
        x, y = polar(c, c, 166 * SS, g)
        texto_centrado(im, t, x, y, fc, (255, 255, 255, 255), rot=-g)
    # rosa dos ventos: losangos finos nos pontos cardeais e intercardeais
    for g, comp, larg in [(0, 136, 11), (90, 136, 11), (180, 136, 11), (270, 136, 11), (45, 88, 8), (135, 88, 8), (225, 88, 8), (315, 88, 8)]:
        p = [polar(c, c, comp * SS, g), polar(c, c, larg * SS, g + 90), polar(c, c, 0, g), polar(c, c, larg * SS, g - 90)]
        d.polygon(p, outline=(255, 255, 255, 110), fill=(255, 255, 255, 18))
    return reduzir_por(im)


def agulha(comp: float, larg: float, cauda: float, parte: str) -> tuple[Image.Image, float]:
    s = 4
    pad = 6
    w, h = int(larg) + 2 * pad, int(comp + cauda) + 2 * pad
    w += w % 2
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, py = w * s / 2, (pad + comp) * s
    hw = larg / 2 * s
    if parte == "tip":
        d.polygon([(cx, pad * s), (cx + hw, py), (cx - hw, py)], fill=(255, 255, 255, 255))
        d.polygon([(cx, pad * s), (cx, py), (cx - hw, py)], fill=(205, 205, 205, 255))
    else:
        d.polygon([(cx, py + cauda * s), (cx + hw, py), (cx - hw, py)], fill=(255, 255, 255, 255))
        d.polygon([(cx, py + cauda * s), (cx, py), (cx - hw, py)], fill=(200, 205, 214, 255))
    return im.resize((w, h), Image.LANCZOS), pad + comp


def seg() -> tuple[Image.Image, float]:
    s = 4
    pad, comp, cauda = 4, 232, 46
    w, h = 18, int(comp + cauda) + 2 * pad
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, py = w * s / 2, (pad + comp) * s
    d.rectangle([cx - 1 * s, pad * s, cx + 1 * s, py + cauda * s], fill=(255, 255, 255, 255))
    d.ellipse([cx - 6 * s, py - 6 * s, cx + 6 * s, py + 6 * s], fill=(255, 255, 255, 255))
    d.ellipse([cx - 2.4 * s, py - 2.4 * s, cx + 2.4 * s, py + 2.4 * s], fill=(20, 20, 24, 255))
    return im.resize((w, h), Image.LANCZOS), pad + comp


def xml(m: dict) -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'

    def mao(tipo, nome, extra="", filhos=""):
        w, h, py = m[nome]
        t = f'<{tipo} resource="{nome}" x="{C - w // 2}" y="{round(C - py)}" width="{w}" height="{h}" pivotX="0.5" pivotY="{py / h:.6f}"{extra}'
        return f"{t}>{filhos}</{tipo}>" if filhos else t + " />"

    L = cabecalho(NOME) + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("mostrador", "", 0) + f'<PartImage {full}><Image resource="mostrador" /></PartImage>'
      + tpl(190, 270, 100, 30, 22, "#ffffffff", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM") + "</Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255) + f'<PartImage {full}><Image resource="mostrador" /><Variant mode="AMBIENT" target="alpha" value="0" /></PartImage></Group>'.replace('<PartImage', '<PartDraw x="0" y="0" width="480" height="480"><Ellipse x="1" y="1" width="478" height="478"><Stroke thickness="2" color="#88ffffff" /></Ellipse></PartDraw><PartImage', 1).replace('<PartImage x="0" y="0" width="480" height="480"><Image resource="mostrador" /><Variant mode="AMBIENT" target="alpha" value="0" /></PartImage>', ''))
    a(f'    <AnalogClock {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    for tipo, nome in (("HourHand", "hora_cauda"), ("MinuteHand", "min_cauda")):
        a("      " + mao(tipo, nome))
    for tipo, nome in (("HourHand", "hora_ponta"), ("MinuteHand", "min_ponta")):
        a("      " + mao(tipo, nome, f' tintColor="{ac}"'))
    a("      " + mao("SecondHand", "seg", f' tintColor="{ac}"', '<Sweep frequency="15" />'))
    a("    </AnalogClock>")
    a(f'    <AnalogClock {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />')
    for tipo, nome in (("HourHand", "hora_cauda"), ("MinuteHand", "min_cauda"), ("HourHand", "hora_ponta"), ("MinuteHand", "min_ponta")):
        a("      " + mao(tipo, nome, ' tintColor="#ffc8c8ce"'))
    a("    </AnalogClock>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    if ambiente_:
        ImageDraw.Draw(base).ellipse([1, 1, W - 2, W - 2], outline=(136, 136, 136), width=2)
    else:
        base.alpha_composite(A["mostrador"])
        ImageDraw.Draw(base).text((C, 285), "SEX 31", font=fonte("Medium", 22), fill=(255, 255, 255), anchor="mm")
    angs = {"hora": (h % 12) * 30 + mi * 0.5, "min": mi * 6 + s * 0.1}

    def cam(nome, ang, cor):
        im, py = A[nome]
        c_ = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        c_.alpha_composite(tint(im, cor), (int(C - im.width / 2), int(round(C - py))))
        base.alpha_composite(c_.rotate(-ang, center=(C, C), resample=Image.BICUBIC))

    neutro = (200, 200, 206) if ambiente_ else (255, 255, 255)
    for k in ("hora", "min"):
        cam(f"{k}_cauda", angs[k], neutro)
    for k in ("hora", "min"):
        cam(f"{k}_ponta", angs[k], neutro if ambiente_ else ac)
    if not ambiente_:
        cam("seg", s * 6, ac)
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Compass", "Bússola")
    A = {"mostrador": mostrador(), "hora_ponta": agulha(120, 26, 30, "tip"), "hora_cauda": agulha(120, 26, 30, "tail"),
         "min_ponta": agulha(186, 20, 34, "tip"), "min_cauda": agulha(186, 20, 34, "tail"), "seg": seg()}
    med = {k: (v[0].width, v[0].height, v[1]) if isinstance(v, tuple) else (v.width, v.height, 0) for k, v in A.items()}
    pv = [previa(A, "#ff7a2f", 10, 8, 32), previa(A, "#33d6ff", 3, 40, 10), previa(A, "#ff5c93", 7, 15, 50), previa(A, "#ff7a2f", 10, 8, 0, True)]
    imgs = {k: (v[0] if isinstance(v, tuple) else v) for k, v in A.items()}
    r = finalizar(raiz, NOME, en, pt, xml(med), imgs, pv, ["Laranja", "Ciano", "Rosa", "Ambiente (AOD)"], cols=4, nomes_previa=["laranja", "ciano", "rosa", "ambiente"])
    return r
