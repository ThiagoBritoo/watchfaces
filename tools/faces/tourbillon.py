"""Watchface "Tourbillon": relógio de luxo clássico. Mostrador sunburst com índices dourados e, na janela das 6h, uma gaiola de tourbillon que gira
uma volta por minuto (um passo por segundo) com o balancim oscilando. Ponteiros facetados com sombra. Reaproveita peças da Cronos. Original."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import SS, com_mascara, fonte, grad_conico, mascara_anel, metal_paradas, polar, reduzir_por, sombra, tela, texto_centrado
from wf.kit import C, W, cabecalho, cor_config, finalizar, girar, grupo, hora, img, redondo, strings_opcoes, tpl

from . import cronos_assets as CA
from .cronos_previa import _girar

NOME = "tourbillon"
JAN = (C, 336, 58)
OURO = ((255, 234, 166), (206, 166, 86), (98, 74, 30))
MOSTRADORES = [("azul", (14, 28, 62)), ("preto", (14, 14, 16)), ("verde", (10, 44, 34))]


def tema(base) -> CA.Tema:
    return CA.Tema("t", "t", base, "sunburst", (10, 12, 18), (222, 200, 150), (212, 175, 95), OURO, (232, 216, 172), (242, 228, 172), OURO, (10, 16, 34), (222, 200, 150))


def dial(base) -> Image.Image:
    t = tema(base)
    n = W * SS
    c = n / 2
    img_ = tela(n)
    img_.alpha_composite(com_mascara(CA._padrao(t, n), mascara_anel(n, c, c, 226 * SS)))
    img_.alpha_composite(CA._anel_metal(n, t, 240, 226))
    d = ImageDraw.Draw(img_)
    d.ellipse([c - 226 * SS, c - 226 * SS, c + 226 * SS, c + 226 * SS], outline=(0, 0, 0, 180), width=2 * SS)
    for m in range(60):
        if m % 5:
            a = m * 6
            d.line([polar(c, c, 206 * SS, a), polar(c, c, 214 * SS, a)], fill=(*OURO[1], 200), width=int(1.6 * SS))
    for h in range(12):
        if h in (5, 6, 7):
            continue
        CA._colar_polar(img_, CA._barra_aplicada(t, 14, 38), c, c, 176, h * 30)
    cx, cy, r = JAN
    # janela do tourbillon
    cav = tela(n)
    ImageDraw.Draw(cav).ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=(4, 6, 10, 255))
    img_.alpha_composite(sombra(cav, 0, 3 * SS, 4 * SS, 0.5))
    img_.alpha_composite(cav)
    g = grad_conico(n, cx * SS, cy * SS, metal_paradas(*OURO), 30)
    img_.alpha_composite(com_mascara(g, mascara_anel(n, cx * SS, cy * SS, (r + 7) * SS, (r - 1) * SS)))
    texto_centrado(img_, "TOURBILLON", c, 138 * SS, fonte("SemiBold", 14 * SS), (*OURO[0], 220), espaco=3.6 * SS)
    return reduzir_por(img_)


def ponte() -> Image.Image:
    """Ponte dourada por cima da gaiola (barra com parafusos)."""
    n = W * SS
    im = tela(n)
    cx, cy, r = JAN
    d = ImageDraw.Draw(im)
    barra = tela(n)
    ImageDraw.Draw(barra).rounded_rectangle([(cx - r + 6) * SS, (cy - 6) * SS, (cx + r - 6) * SS, (cy + 6) * SS], radius=6 * SS, fill=(0, 0, 0, 255))
    im.alpha_composite(sombra(barra, 2 * SS, 3 * SS, 3 * SS, 0.6))
    g = grad_conico(n, cx * SS, cy * SS, metal_paradas(*OURO), 80)
    im.alpha_composite(com_mascara(g, np.asarray(barra.getchannel("A"), np.float32) / 255))
    for dx in (-r + 14, r - 14):
        px, py = (cx + dx) * SS, cy * SS
        d.ellipse([px - 4 * SS, py - 4 * SS, px + 4 * SS, py + 4 * SS], fill=(40, 30, 10, 255), outline=(255, 234, 166, 255), width=SS)
        d.line([(px - 3 * SS, py - 1 * SS), (px + 3 * SS, py + 1 * SS)], fill=(255, 234, 166, 255), width=SS)
    d.ellipse([(cx - 7) * SS, (cy - 7) * SS, (cx + 7) * SS, (cy + 7) * SS], fill=(60, 44, 14, 255), outline=(255, 234, 166, 255), width=2 * SS)
    return reduzir_por(im)


def gaiola() -> Image.Image:
    t = 2 * JAN[2] + 8
    s = 4
    im = Image.new("RGBA", (t * s, t * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = t * s / 2
    R = (JAN[2] - 10) * s
    d.ellipse([c - R, c - R, c + R, c + R], outline=(*OURO[1], 255), width=3 * s)
    for k in range(3):
        a = k * 120 + 30
        d.line([(c, c), polar(c, c, R, a)], fill=(*OURO[1], 255), width=3 * s)
    for k in range(3):
        x, y = polar(c, c, R, k * 120 + 30)
        d.ellipse([x - 4 * s, y - 4 * s, x + 4 * s, y + 4 * s], fill=(*OURO[0], 255))
    eng = CA.engrenagem(tema((0, 0, 0)), 13, 11).resize((26 * s, 26 * s), Image.LANCZOS) if False else None
    d.ellipse([c - 3 * s, c - 3 * s, c + 3 * s, c + 3 * s], fill=(*OURO[0], 255))
    return im.resize((t, t), Image.LANCZOS)


def balancim() -> Image.Image:
    t = 70
    s = 4
    im = Image.new("RGBA", (t * s, t * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = t * s / 2
    R = 26 * s
    d.ellipse([c - R, c - R, c + R, c + R], outline=(210, 214, 222, 255), width=3 * s)
    for a in (0, 90, 180, 270):
        d.line([(c, c), polar(c, c, R, a)], fill=(210, 214, 222, 255), width=2 * s)
    for a in (45, 135, 225, 315):
        x, y = polar(c, c, R, a)
        d.ellipse([x - 4 * s, y - 4 * s, x + 4 * s, y + 4 * s], fill=(255, 230, 160, 255))
    return im.resize((t, t), Image.LANCZOS)


def maos() -> dict:
    t = tema((0, 0, 0))
    out = {}
    for nome, (comp, cauda, larg) in (("hora", (120, 26, 28)), ("min", (186, 30, 20))):
        out[nome] = CA.ponteiro(t, "espada", comp, cauda, larg)
        out[f"{nome}_sombra"] = CA.ponteiro_sombra(*out[nome], 10)
        out[f"{nome}_contorno"] = CA.ponteiro_contorno(t, "espada", comp, cauda, larg)
    return out


def ambiente() -> Image.Image:
    n = W * SS
    c = n / 2
    im = tela(n)
    d = ImageDraw.Draw(im)
    d.ellipse([c - 237 * SS, c - 237 * SS, c + 237 * SS, c + 237 * SS], outline=(95, 95, 100, 255), width=SS)
    d.ellipse([c - 226 * SS, c - 226 * SS, c + 226 * SS, c + 226 * SS], outline=(95, 95, 100, 255), width=SS)
    for h in range(12):
        if h in (5, 6, 7):
            continue
        x, y = polar(c, c, 190 * SS, h * 30)
        d.ellipse([x - 4 * SS, y - 4 * SS, x + 4 * SS, y + 4 * SS], outline=(190, 190, 196, 255), width=SS)
    cx, cy, r = JAN
    d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], outline=(95, 95, 100, 255), width=SS)
    return reduzir_por(im)


def xml(med) -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    cx, cy, r = JAN
    tg = 2 * r + 8
    L = cabecalho(NOME) + ["  <UserConfigurations>", '    <ListConfiguration id="dial" displayName="dial_label" defaultValue="azul">'
                           + "".join(f'<ListOption id="{k}" displayName="dial_{k}" />' for k, _ in MOSTRADORES) + "</ListConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append

    def mao(tipo, nome, extra=""):
        w, h, py = med[nome]
        return f'<{tipo} resource="{nome}" x="{C - w // 2}" y="{round(C - py)}" width="{w}" height="{h}" pivotX="0.5" pivotY="{py / h:.6f}"{extra} />'
    a("    " + grupo("mostrador", "", 0) + '<ListConfiguration id="dial">')
    for k, _ in MOSTRADORES:
        a(f'      <ListOption id="{k}"><Group name="d_{k}" {full}>' + img(0, 0, W, W, f"dial_{k}") + "</Group></ListOption>")
    a("    </ListConfiguration></Group>")
    a("    " + grupo("tourbillon", "", 0)
      + f'<Group name="gaiola" x="{cx - tg // 2}" y="{cy - tg // 2}" width="{tg}" height="{tg}" pivotX="0.5" pivotY="0.5"><Transform target="angle" value="[SECOND] * 6" />'
      + img(0, 0, tg, tg, "gaiola")
      + f'<PartImage x="{tg // 2 - 35}" y="{tg // 2 - 35}" width="70" height="70" pivotX="0.5" pivotY="0.5"><Image resource="balancim" /><Transform target="angle" value="120 * cos([SECOND] * 3.14159)" /></PartImage></Group>'
      + img(0, 0, W, W, "ponte") + "</Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255) + img(0, 0, W, W, "ambiente") + "</Group>")
    a(f'    <AnalogClock {full}><Variant mode="AMBIENT" target="alpha" value="0" />' + mao("HourHand", "hora_sombra") + mao("MinuteHand", "min_sombra") + mao("HourHand", "hora") + mao("MinuteHand", "min") + "</AnalogClock>")
    a(f'    <AnalogClock {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />' + mao("HourHand", "hora_contorno") + mao("MinuteHand", "min_contorno") + "</AnalogClock>")
    a("    " + grupo("tampa", "", 0) + img(C - 24, C - 24, 48, 48, "tampa") + "</Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, dial_id: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    ang_h, ang_m = (h % 12) * 30 + mi * 0.5 + s / 120, mi * 6 + s * 0.1
    cx, cy, r = JAN
    if ambiente_:
        base.alpha_composite(A["ambiente"])
        for nome, ang in (("hora_contorno", ang_h), ("min_contorno", ang_m)):
            im, py = A[nome]
            base.alpha_composite(_girar(W, im, py, ang))
        return redondo(base)
    base.alpha_composite(A[f"dial_{dial_id}"])
    tg = 2 * r + 8
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    gb = A["gaiola"].copy()
    bl = A["balancim"].rotate(-120 * math.cos(s * math.pi), resample=Image.BICUBIC)
    gb.alpha_composite(bl, (tg // 2 - 35, tg // 2 - 35))
    cam.alpha_composite(gb, (cx - tg // 2, cy - tg // 2))
    base.alpha_composite(cam.rotate(-s * 6, center=(cx, cy), resample=Image.BICUBIC))
    base.alpha_composite(A["ponte"])
    for nome, ang in (("hora_sombra", ang_h), ("min_sombra", ang_m), ("hora", ang_h), ("min", ang_m)):
        im, py = A[nome]
        base.alpha_composite(_girar(W, im, py, ang))
    base.alpha_composite(CA.tampa_central(tema((0, 0, 0))), (C - 24, C - 24))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Tourbillon", "dial_label": "Dial", "dial_azul": "Midnight blue", "dial_preto": "Black", "dial_verde": "Emerald"}
    pt = {"watch_face_name": "Tourbillon", "dial_label": "Mostrador", "dial_azul": "Azul-noite", "dial_preto": "Preto", "dial_verde": "Esmeralda"}
    A: dict = {f"dial_{k}": dial(b) for k, b in MOSTRADORES}
    A.update(maos())
    A["gaiola"], A["balancim"], A["ponte"], A["ambiente"] = gaiola(), balancim(), ponte(), ambiente()
    A["tampa"] = CA.tampa_central(tema((0, 0, 0)))
    med = {k: (v[0].width, v[0].height, v[1]) for k, v in A.items() if isinstance(v, tuple)}
    imgs = {k: (v[0] if isinstance(v, tuple) else v) for k, v in A.items()}
    pv = [previa(A, "azul", 10, 8, 3), previa(A, "preto", 3, 45, 17), previa(A, "verde", 7, 22, 40), previa(A, "azul", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(med), imgs, pv, ["Azul-noite", "Preto", "Esmeralda", "Ambiente (AOD)"], cols=4, nomes_previa=["azul", "preto", "verde", "ambiente"])
