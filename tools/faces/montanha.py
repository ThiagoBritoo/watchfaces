"""Watchface "Montanha": arte de linha (montanhas, sol que gira, nuvens) com a hora numa cápsula no pé da tela;
a régua dos minutos gira por baixo da cápsula. Texto curvo no alto e duas informações laterais.
Inspirada em mostradores outdoor de arte de linha. Arte e código originais."""
from __future__ import annotations

import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from wf.desenho import SS, fonte, polar, reduzir_por, tela, texto_arco, texto_centrado
from wf.kit import C, W, cabecalho, colar, cor_config, finalizar, girar, hora, img, redondo, rect, rgb, strings_opcoes, tint

NOME = "montanha"
ACENTOS = [("laranja", "#ff7a1a"), ("ciano", "#33d6ff"), ("verde", "#4be37a"), ("amarelo", "#ffd23d"), ("rosa", "#ff5c93"), ("branco", "#ffffff")]
PILULA = (210, 390, 60, 86)
LAT = {"esq": (14, 176, 76, 128, -84), "dir": (390, 176, 76, 128, 72)}


def _nuvem(d_mask: ImageDraw.ImageDraw, cx, cy, s, esc=1.0):
    for dx, dy, r in ((-28, 6, 15), (-8, -4, 21), (16, 0, 18), (32, 8, 13)):
        d_mask.ellipse([(cx + dx * esc - r * esc) * s, (cy + dy * esc - r * esc) * s, (cx + dx * esc + r * esc) * s, (cy + dy * esc + r * esc) * s], fill=255)
    d_mask.rectangle([(cx - 36 * esc) * s, (cy + 6 * esc) * s, (cx + 40 * esc) * s, (cy + 21 * esc) * s], fill=255)


def paisagem() -> Image.Image:
    s = 3
    n = W * s
    lin = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(lin)
    rnd = random.Random(11)
    base = 346
    pts = [(104, base), (150, 292), (172, 304), (214, 238), (232, 262), (252, 244), (296, 292), (318, 280), (376, base)]
    # picos principais com neve (zigue-zague) e sombras de face (linhas diagonais)
    fill = Image.new("L", (n, n), 0)
    ImageDraw.Draw(fill).polygon([(x * s, y * s) for x, y in pts], fill=255)
    d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(3.2 * s), joint="curve")
    d.line([(100 * s, base * s), (380 * s, base * s)], fill=255, width=int(3.2 * s))
    for (px, py, w_) in ((214, 238, 34), (252, 244, 22), (150, 292, 20)):
        zz = [(px - w_, py + 40 * (w_ / 34)), (px - w_ * 0.55, py + 30 * (w_ / 34)), (px - w_ * 0.2, py + 42 * (w_ / 34)), (px + w_ * 0.2, py + 32 * (w_ / 34)),
              (px + w_ * 0.6, py + 44 * (w_ / 34)), (px + w_, py + 38 * (w_ / 34))]
        d.line([(x * s, y * s) for x, y in zz], fill=255, width=int(2.4 * s), joint="curve")
    for k in range(9):                                  # linhas de rocha
        x0 = 168 + rnd.random() * 150
        d.line([(x0 * s, (300 + rnd.random() * 20) * s), ((x0 - 14) * s, (335 + rnd.random() * 8) * s)], fill=255, width=int(1.8 * s))
    # nuvens (contorno = máscara - máscara erodida)
    nm = Image.new("L", (n, n), 0)
    dn = ImageDraw.Draw(nm)
    for cx, cy, esc in ((148, 214, 1.0), (338, 176, 1.05), (326, 232, 0.55)):
        _nuvem(dn, cx, cy, s, esc)
    inner = nm.filter(ImageFilter.MinFilter(int(3.4 * s) | 1))
    contorno = Image.fromarray(np.clip(np.asarray(nm, np.int16) - np.asarray(inner, np.int16), 0, 255).astype(np.uint8))
    a = np.maximum(np.maximum(np.asarray(lin), np.asarray(contorno)), 0)
    # apaga o que estiver atrás das montanhas (preenchimento preto) mantendo o traço branco
    out = np.zeros((n, n, 4), np.uint8)
    out[..., 3] = np.maximum(np.asarray(fill, np.uint8), a)
    br = a
    out[..., 0] = out[..., 1] = out[..., 2] = br
    return Image.fromarray(out, "RGBA").resize((W, W), Image.LANCZOS)


def sol() -> Image.Image:
    s = 4
    t = 120
    im = Image.new("L", (t * s, t * s), 0)
    d = ImageDraw.Draw(im)
    c = t * s / 2
    d.ellipse([c - 20 * s, c - 20 * s, c + 20 * s, c + 20 * s], outline=255, width=int(3 * s))
    for k in range(16):
        a = k * 22.5
        d.line([polar(c, c, (28 if k % 2 == 0 else 28) * s, a), polar(c, c, (46 if k % 2 == 0 else 38) * s, a)], fill=255, width=int(3 * s))
    out = Image.new("RGBA", im.size, (255, 255, 255, 0))
    out.putalpha(im)
    return out.resize((t, t), Image.LANCZOS)


def escala() -> Image.Image:
    n = W * SS
    c = n / 2
    im = tela(n)
    d = ImageDraw.Draw(im)
    f = fonte("Medium", 22 * SS)
    for m in range(60):
        a = m * 6
        mj = m % 5 == 0
        d.line([polar(c, c, (212 if mj else 217) * SS, a), polar(c, c, 226 * SS, a)], fill=(255, 255, 255, 255 if mj else 150), width=int((3 if mj else 1.8) * SS))
        if mj:
            x, y = polar(c, c, 194 * SS, a)
            texto_centrado(im, f"{m:02d}", x, y, f, (255, 255, 255, 200), rot=-a + 180)
    return reduzir_por(im)


def cobertura() -> Image.Image:
    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
    dx, dy = xx + 0.5 - C, yy + 0.5 - C
    r = np.hypot(dx, dy)
    th = np.degrees(np.arctan2(dx, -dy)) % 360
    janela = (th > 118) & (th < 242) & (r > 178)
    a = np.where(janela, 0, 255).astype(np.uint8)
    out = np.zeros((W, W, 4), np.uint8)
    out[..., 3] = a
    return Image.fromarray(out, "RGBA")


def bisel() -> Image.Image:
    n = W * SS
    c = n / 2
    im = tela(n)
    d = ImageDraw.Draw(im)
    for k in range(12):
        a = k * 30
        if k == 0:
            continue
        d.line([polar(c, c, 229 * SS, a), polar(c, c, 238 * SS, a)], fill=(255, 255, 255, 255), width=int(4 * SS))
    p = [polar(c, c, 238 * SS, -3.4), polar(c, c, 238 * SS, 3.4), polar(c, c, 226 * SS, 0)]
    d.polygon(p, fill=(255, 255, 255, 255))
    return reduzir_por(im)


def _slot(nome: str, sid: int, x, y, w, h, ang, prov) -> str:
    gw, gh = 124, 30
    return f"""<ComplicationSlot name="{nome}" slotId="{sid}" x="{x}" y="{y}" width="{w}" height="{h}" displayName="slot_{nome}" supportedTypes="SHORT_TEXT RANGED_VALUE EMPTY" isCustomizable="TRUE">
      <BoundingBox x="0" y="0" width="{w}" height="{h}" />
      <DefaultProviderPolicy defaultSystemProvider="{prov}" defaultSystemProviderType="SHORT_TEXT" />
      <Variant mode="AMBIENT" target="alpha" value="0" />
      <Complication type="SHORT_TEXT"><Group x="{(w - gw) // 2}" y="{(h - gh) // 2}" width="{gw}" height="{gh}" angle="{ang}" pivotX="0.5" pivotY="0.5">
        <PartText x="0" y="0" width="{gw}" height="{gh}"><Text align="CENTER"><Font family="SYNC_TO_DEVICE" size="24" weight="MEDIUM" color="#ffffffff"><Template><![CDATA[%s]]><Parameter expression="[COMPLICATION.TEXT]" /></Template></Font></Text></PartText></Group></Complication>
      <Complication type="RANGED_VALUE"><Group x="{(w - gw) // 2}" y="{(h - gh) // 2}" width="{gw}" height="{gh}" angle="{ang}" pivotX="0.5" pivotY="0.5">
        <PartText x="0" y="0" width="{gw}" height="{gh}"><Text align="CENTER"><Font family="SYNC_TO_DEVICE" size="24" weight="MEDIUM" color="#ffffffff"><Template><![CDATA[%s]]><Parameter expression="[COMPLICATION.TEXT]" /></Template></Font></Text></PartText></Group></Complication>
    </ComplicationSlot>"""


def xml() -> str:
    px, py, pw, ph = PILULA
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS), "  </UserConfigurations>",
                                       '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a(f'    <Group name="regua" {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a("      " + img(0, 0, W, W, "escala", ' pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="180 - ([MINUTE] + [SECOND] / 60) * 6" />'))
    a("      " + img(0, 0, W, W, "cobertura"))
    a("      " + img(0, 0, W, W, "bisel", f' tintColor="{ac}"'))
    a("    </Group>")
    a(f'    <Group name="cena" {full}>')
    a("      " + img(0, 0, W, W, "paisagem", ' alpha="255"', '<Variant mode="AMBIENT" target="alpha" value="150" />'))
    a("      " + img(C - 60, 108, 120, 120, "sol", ' pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="[SECOND] * 6" /><Variant mode="AMBIENT" target="alpha" value="200" />'))
    a("    </Group>")
    a(f'    <Group name="dados" {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a(f'      <PartText x="0" y="0" width="{W}" height="{W}"><TextCircular centerX="{C}" centerY="{C}" width="428" height="428" startAngle="-52" endAngle="52" align="CENTER">'
      '<Font family="SYNC_TO_DEVICE" size="24" weight="MEDIUM" color="#ffffffff"><Template><![CDATA[%s°C | %s | %s]]>'
      '<Parameter expression="[WEATHER.TEMPERATURE]" /><Parameter expression="[DAY_OF_WEEK_S]" /><Parameter expression="[DAY]" /></Template></Font></TextCircular></PartText>')
    a("    </Group>")
    a("    " + _slot("esq", 0, *LAT["esq"][:4], LAT["esq"][4], "STEP_COUNT"))
    a("    " + _slot("dir", 1, *LAT["dir"][:4], LAT["dir"][4], "WATCH_BATTERY"))
    a(f'    <Group name="capsula" {full}>')
    a("      " + rect(px, py, pw, ph, ac, pw // 2, "Stroke", 3.2, "", ""))
    a("      " + hora(px, py + 4, pw, 38, "hh", 36, "#ffffffff", "BOLD", "CENTER"))
    a(f'      <Group name="min_ambiente" x="0" y="0" width="{W}" height="{W}" alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />'
      + hora(px, py + 44, pw, 34, "mm", 30, "#ffa0a0a8", "MEDIUM", "CENTER") + "</Group>")
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A: dict, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    ac = rgb(acento)
    px, py, pw, ph = PILULA
    if not ambiente_:
        base.alpha_composite(girar(A["escala"], (C, C), 180 - (mi + s / 60) * 6))
        base.alpha_composite(A["cobertura"])
        base.alpha_composite(tint(A["bisel"], ac))
    land = A["paisagem"].copy()
    if ambiente_:
        r, g, b, al = land.split()
        land = Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * 150 / 255))))
    base.alpha_composite(land)
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cam.paste(A["sol"], (C - 60, 108))
    base.alpha_composite(cam.rotate(-(s * 6), center=(C, 168), resample=Image.BICUBIC))
    d = ImageDraw.Draw(base)
    if not ambiente_:
        texto_arco(base, f"25°C | {'SEG'} | 28", C, C, 214 * SS if False else 214, 0, fonte("Medium", 24), (255, 255, 255, 255))
        for key, txt in (("esq", "12755"), ("dir", "86%")):
            x, y, w, hh, ang = LAT[key]
            t = Image.new("RGBA", (124, 30), (0, 0, 0, 0))
            ImageDraw.Draw(t).text((62, 15), txt, font=fonte("Medium", 24), fill=(255, 255, 255, 255), anchor="mm")
            t = t.rotate(-ang, expand=True, resample=Image.BICUBIC)
            colar(base, t, x + w // 2 - t.width // 2, y + hh // 2 - t.height // 2)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=pw // 2, outline=ac if not ambiente_ else (110, 110, 116), width=3)
    d.text((px + pw / 2, py + 22), f"{h:02d}", font=fonte("Bold", 36), fill=(255, 255, 255), anchor="mm")
    if ambiente_:
        d.text((px + pw / 2, py + 60), f"{mi:02d}", font=fonte("Medium", 30), fill=(160, 160, 168), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Mountain", "acento_label": "Accent color", "slot_esq": "Left (rotated)", "slot_dir": "Right (rotated)"}
    pt = {"watch_face_name": "Montanha", "acento_label": "Cor de destaque", "slot_esq": "Esquerda (girado)", "slot_dir": "Direita (girado)"}
    strings_opcoes(en, pt, "acento", {"laranja": ("Orange", "Laranja"), "ciano": ("Cyan", "Ciano"), "verde": ("Green", "Verde"), "amarelo": ("Yellow", "Amarelo"),
                                       "rosa": ("Pink", "Rosa"), "branco": ("White", "Branco")})
    A = {"paisagem": paisagem(), "sol": sol(), "escala": escala(), "cobertura": cobertura(), "bisel": bisel()}
    pv = [previa(A, "#ff7a1a", 9, 45, 12), previa(A, "#33d6ff", 3, 15, 40), previa(A, "#4be37a", 12, 5, 30), previa(A, "#ff7a1a", 9, 45, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Laranja", "Ciano", "Verde", "Ambiente (AOD)"], cols=4, nomes_previa=["laranja", "ciano", "verde", "ambiente"])
