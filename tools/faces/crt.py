"""Watchface "Terminal CRT": retrô, inspirada em terminais de fósforo verde/âmbar (estilo Pip-Boy).

Arte 100% original (inclusive o mascote), para poder ser publicada. Toda a "tela" é desenhada em tons de
cinza e pintada no relógio com `tintColor` (Group), então a mesma imagem serve para verde, âmbar, ciano...
O texto usa BitmapFont (fonte pixel gerada por script a partir da JetBrains Mono, OFL).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from wf.desenho import (SS, com_mascara, grad_linear, grad_radial, mascara_anel, metal_paradas, grad_conico,
                        polar, reduzir_por, ruido, sombra, tela)
from wf.modulo import caixa, criar_modulo, hexcor, nomear_grupos

NOME = "crt"
W = 480
FONTE = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf"
SCR = (72, 92, 336, 296)           # x, y, largura, altura da tela de vidro
FOSFOROS = [("verde", "#33ff66"), ("ambar", "#ffb000"), ("ciano", "#33e0ff"), ("branco", "#e8f0e8")]
GRANDE = dict(tam=17, esc=5, pad=8, cw=10, ch=15, dy=-1)     # dígitos da hora
PEQUENA = dict(tam=12, esc=2, pad=2, cw=8, ch=17, dy=2)     # textos
CARS_PEQ = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ:./%-+, "


# ----------------------------------------------------------------------------- fonte pixel
def _glifo(ch: str, tam: int, esc: int, pad: int, cw: int, ch_: int, dy: int, cor: int = 255, halo: bool = True) -> Image.Image:
    f = ImageFont.truetype(FONTE, tam)
    im = Image.new("L", (cw, ch_), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.text((cw / 2, dy), ch, font=f, fill=255, anchor="mt")
    g = im.resize((cw * esc, ch_ * esc), Image.NEAREST)
    big = Image.new("L", (cw * esc + 2 * pad, ch_ * esc + 2 * pad), 0)
    big.paste(g, (pad, pad))
    a = np.asarray(big, np.float32)
    if halo:
        h = np.asarray(big.filter(ImageFilter.GaussianBlur(max(1.0, pad / 2.2))), np.float32) * 0.55
        a = np.maximum(a, h)
    rgba = np.zeros(a.shape + (4,), np.uint8)
    rgba[..., :3] = cor
    rgba[..., 3] = a.astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def _fonte_pixel(dr: Path, prefixo: str, chars: str, p: dict, cor: int = 255, halo: bool = True) -> dict[str, tuple[str, int, int]]:
    """Salva um PNG por caractere. Retorna {caractere: (recurso, largura, altura)}."""
    out = {}
    for c in chars:
        if c == " ":
            continue
        nome = f"{prefixo}_{ord(c):02x}"
        g = _glifo(c, p["tam"], p["esc"], p["pad"], p["cw"], p["ch"], p["dy"], cor, halo)
        g.save(dr / f"{nome}.png", optimize=True)
        out[c] = (nome, g.width, g.height)
    return out


def _xml_bitmapfont(nome: str, m: dict[str, tuple[str, int, int]], com_minusculas: bool) -> str:
    """Mapeia também minúsculas e acentos para as mesmas imagens (dia da semana vem como 'sex', 'sáb')."""
    linhas = []
    usados = dict(m)
    if com_minusculas:
        for c in "abcdefghijklmnopqrstuvwxyz":
            usados[c] = m[c.upper()]
        for c, base in (("á", "A"), ("à", "A"), ("ã", "A"), ("é", "E"), ("ê", "E"), ("í", "I"), ("ó", "O"), ("ô", "O"),
                        ("ú", "U"), ("ç", "C")):
            usados[c] = m[base]
    for c, (r, w, h) in usados.items():
        n = {"&": "&amp;", "<": "&lt;", '"': "&quot;"}.get(c, c)
        linhas.append(f'      <Character name="{n}" resource="{r}" width="{w}" height="{h}" />')
    return f'    <BitmapFont name="{nome}">\n' + "\n".join(linhas) + "\n    </BitmapFont>"


# ----------------------------------------------------------------------------- pixel art
def _sprite(frame: int) -> Image.Image:
    """Mascote original: robozinho retrô de 24x32 'pixels', 2 quadros de caminhada. Tons de cinza."""
    g = Image.new("L", (24, 34), 0)
    d = ImageDraw.Draw(g)
    r = lambda x0, y0, x1, y1, c: d.rectangle([x0, y0, x1, y1], fill=c)  # noqa: E731
    bob = 1 if frame else 0
    # antena
    r(11, 0 + bob, 12, 3 + bob, 255)
    r(10, 0 + bob, 13, 1 + bob, 255)
    # cabeça
    r(5, 4 + bob, 18, 14 + bob, 255)
    r(6, 5 + bob, 17, 13 + bob, 150)
    r(3, 7 + bob, 4, 11 + bob, 255)
    r(19, 7 + bob, 20, 11 + bob, 255)
    r(8, 7 + bob, 10, 9 + bob, 20)      # olhos
    r(13, 7 + bob, 15, 9 + bob, 20)
    r(8, 11 + bob, 15, 11 + bob, 20)    # sorriso
    r(7, 10 + bob, 7, 10 + bob, 20)
    r(16, 10 + bob, 16, 10 + bob, 20)
    # pescoço + tronco
    r(10, 15 + bob, 13, 16 + bob, 200)
    r(6, 17 + bob, 17, 26 + bob, 255)
    r(7, 18 + bob, 16, 25 + bob, 150)
    r(9, 20 + bob, 14, 23 + bob, 30)
    r(10, 21 + bob, 11, 21 + bob, 255)
    r(13, 21 + bob, 13, 21 + bob, 255)
    # braços (balançam em sentidos opostos)
    ya, yb = (18, 20) if frame == 0 else (20, 18)
    r(3, ya + bob, 5, ya + 6 + bob, 255)
    r(18, yb + bob, 20, yb + 6 + bob, 255)
    # pernas
    if frame == 0:
        r(7, 27, 10, 33, 255); r(8, 28, 9, 32, 120); r(6, 32, 11, 33, 255)
        r(13, 27, 16, 31, 255); r(14, 28, 15, 30, 120); r(13, 30, 17, 31, 255)
    else:
        r(13, 27, 16, 33, 255); r(14, 28, 15, 32, 120); r(12, 32, 17, 33, 255)
        r(7, 27, 10, 31, 255); r(8, 28, 9, 30, 120); r(6, 30, 10, 31, 255)
    return g


def _icone(grade: list[str]) -> Image.Image:
    h, w = len(grade), len(grade[0])
    im = Image.new("L", (w, h), 0)
    for y, linha in enumerate(grade):
        for x, c in enumerate(linha):
            if c != ".":
                im.putpixel((x, y), 255)
    return im


ICONE_PASSOS = ["..........", "....####..", "...######.", "...######.", "..#######.", ".########.", "##########", "##########", ".########."]
ICONE_SOL = ["....#....", ".#..#..#.", "..#####..", "#.#####.#", "..#####..", ".#..#..#.", "....#....", "#########", "........."]
ICONE_RAIO = ["...###", "..###.", ".###..", "######", "..###.", ".##...", ".#...."]


def _colar_pixel(dest: Image.Image, g: Image.Image, x: int, y: int, esc: int, halo: bool = True) -> None:
    big = g.resize((g.width * esc, g.height * esc), Image.NEAREST)
    a = np.asarray(big, np.float32)
    if halo:
        a = np.maximum(a, np.asarray(big.filter(ImageFilter.GaussianBlur(esc * 0.9)), np.float32) * 0.5)
    rgba = np.zeros(a.shape + (4,), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = a.astype(np.uint8)
    dest.alpha_composite(Image.fromarray(rgba, "RGBA"), (x, y))


# ----------------------------------------------------------------------------- imagens
def carcaca() -> Image.Image:
    """Corpo do relógio: metal verde-oliva escuro com parafusos, placa superior, botões laranja e botão lateral."""
    n = W * SS
    c = n / 2
    img = tela(n)
    base = grad_radial(n, c - 60 * SS, c - 80 * SS, [(0, (92, 98, 78)), (300 * SS, (48, 52, 40)), (360 * SS, (30, 33, 26))])
    a = np.asarray(base).astype(np.float32)
    a[..., :3] += ruido(n, 3, 3.0)[..., None]
    img.alpha_composite(com_mascara(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"), mascara_anel(n, c, c, 240 * SS)))
    d = ImageDraw.Draw(img)
    d.ellipse([c - 238 * SS, c - 238 * SS, c + 238 * SS, c + 238 * SS], outline=(20, 22, 16, 255), width=3 * SS)
    d.ellipse([c - 230 * SS, c - 230 * SS, c + 230 * SS, c + 230 * SS], outline=(128, 134, 108, 200), width=SS)
    # moldura chanfrada da tela
    x, y, w, h = SCR
    for k, (cor, ex) in enumerate([((18, 20, 15, 255), 14), ((70, 76, 60, 255), 9), ((26, 28, 21, 255), 4)]):
        d.rounded_rectangle([(x - ex) * SS, (y - ex) * SS, (x + w + ex) * SS, (y + h + ex) * SS], radius=(34 + ex) * SS, fill=cor)
    d.rounded_rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS], radius=30 * SS, fill=(0, 0, 0, 255))
    # parafusos
    for ang in (45, 135, 225, 315):
        px, py = polar(c, c, 222 * SS, ang)
        d.ellipse([px - 6 * SS, py - 6 * SS, px + 6 * SS, py + 6 * SS], fill=(36, 39, 30, 255), outline=(14, 15, 11, 255), width=SS)
        d.line([(px - 4 * SS, py - 1 * SS), (px + 4 * SS, py + 1 * SS)], fill=(110, 116, 92, 255), width=SS)
    # placa de cima
    d.rounded_rectangle([188 * SS, 30 * SS, 292 * SS, 60 * SS], radius=10 * SS, fill=(40, 43, 33, 255), outline=(120, 126, 100, 255), width=SS)
    f = ImageFont.truetype(FONTE, 13 * SS)
    d.text((c, 45 * SS), "TERMINAL", font=f, fill=(150, 158, 128, 255), anchor="mm")
    # três botões laranja embaixo
    for dx in (-44, 0, 44):
        bx, by = c + dx * SS, 424 * SS
        r = 14 * SS
        d.ellipse([bx - r - 3 * SS, by - r - 3 * SS, bx + r + 3 * SS, by + r + 3 * SS], fill=(22, 24, 18, 255))
        g = grad_radial(n, bx - 5 * SS, by - 6 * SS, [(0, (255, 214, 140)), (r, (226, 120, 24)), (r * 1.4, (130, 56, 8))])
        img.alpha_composite(com_mascara(g, mascara_anel(n, bx, by, r)))
        d.ellipse([bx - r, by - r, bx + r, by + r], outline=(80, 34, 4, 255), width=SS)
    # botão lateral (direita) e tecla
    d.rounded_rectangle([412 * SS, 214 * SS, 442 * SS, 266 * SS], radius=6 * SS, fill=(28, 30, 22, 255), outline=(110, 116, 92, 255), width=SS)
    for k in range(7):
        yy = (220 + k * 7) * SS
        d.line([(416 * SS, yy), (438 * SS, yy)], fill=(70, 74, 58, 255), width=2 * SS)
    d.rounded_rectangle([418 * SS, 282 * SS, 430 * SS, 312 * SS], radius=5 * SS, fill=(226, 130, 34, 255), outline=(90, 44, 6, 255), width=SS)
    return reduzir_por(img)


def tela_vidro() -> Image.Image:
    """Painel da tela em cinza (pintado por tintColor): brilho de fósforo, grade de molduras, ícones e rótulos fixos."""
    x, y, w, h = SCR
    n = max(w, h)
    # fundo: centro mais claro, bordas escuras + leve gradiente vertical
    g = grad_radial(n, w * 0.5, h * 0.42, [(0, (74, 74, 74)), (h * 0.55, (44, 44, 44)), (h * 0.95, (14, 14, 14))]).crop((0, 0, w, h))
    a = np.asarray(g).astype(np.float32)
    a[..., :3] += ruido(max(w, h), 9, 1.5)[:h, :w, None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(img)
    ox, oy = x, y
    luz = (255, 255, 255, 255)
    # linha superior (colchete) e divisórias
    d.line([(16, 50), (w - 16, 50)], fill=luz, width=2)
    d.line([(16, 50), (16, 58)], fill=luz, width=2)
    d.line([(w - 16, 50), (w - 16, 58)], fill=luz, width=2)
    _colar_pixel(img, _icone(ICONE_PASSOS), 16, 14, 2)
    _colar_pixel(img, _icone(ICONE_SOL), w - 36, 14, 2)
    # caixa do dia da semana (preenchida; o texto escuro vem do XML)
    d.rectangle([4, 78, 66, 110], fill=luz)
    d.rectangle([20, 154, 54, 157], fill=luz)               # traço sob o dia
    # barra de bateria
    _colar_pixel(img, _icone(ICONE_RAIO), 18, h - 38, 2)
    pf = ImageFont.truetype(FONTE, 14)
    d.rectangle([14, h - 44, 80, h - 16], outline=luz, width=2)
    d.fontmode = "1"
    d.text((52, h - 30), "PWR", font=pf, fill=luz, anchor="mm")
    d.rectangle([88, h - 42, 196, h - 18], outline=luz, width=2)
    # mascote: marcas do chão
    d.line([(250, h - 56), (w - 14, h - 56)], fill=(255, 255, 255, 90), width=1)
    # scanlines e vinheta final
    arr = np.asarray(img).astype(np.float32)
    arr[::3, :, :3] *= 0.80
    yy, xx = np.mgrid[0:h, 0:w]
    v = 1 - 0.35 * (np.clip((np.abs(xx - w / 2) / (w / 2)) ** 3 + (np.abs(yy - h / 2) / (h / 2)) ** 3, 0, 1.4))
    arr[..., :3] *= v[..., None]
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    m = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 4 - 1, h * 4 - 1], radius=30 * 4, fill=255)
    out.putalpha(m.resize((w, h), Image.LANCZOS))
    return out


def vidro_cristal() -> Image.Image:
    """Reflexo do vidro e scanlines pretas finas por cima do texto (não tingido)."""
    x, y, w, h = SCR
    a = np.zeros((h, w, 4), np.float32)
    a[::3, :, 3] = 46                     # scanlines escuras
    yy, xx = np.mgrid[0:h, 0:w]
    reflexo = np.clip(1 - (xx + yy * 0.8 - 70) / 90, 0, 1) * np.clip((xx + yy * 0.8 - 8) / 20, 0, 1)
    a[..., :3] += 255 * reflexo[..., None]
    a[..., 3] = np.maximum(a[..., 3], 22 * reflexo)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    m = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 4 - 1, h * 4 - 1], radius=30 * 4, fill=255)
    al = np.minimum(np.asarray(img.getchannel("A"), np.float32), np.asarray(m.resize((w, h), Image.LANCZOS), np.float32))
    img.putalpha(Image.fromarray(al.astype(np.uint8)))
    return img


def ambiente() -> Image.Image:
    """AOD: só um aro fino; o horário vem do XML em verde apagado."""
    n = W * SS
    c = n / 2
    img = tela(n)
    d = ImageDraw.Draw(img)
    d.ellipse([c - 236 * SS, c - 236 * SS, c + 236 * SS, c + 236 * SS], outline=(70, 70, 70, 255), width=SS)
    x, y, w, h = SCR
    d.rounded_rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS], radius=30 * SS, outline=(60, 60, 60, 255), width=SS)
    return reduzir_por(img)


# ----------------------------------------------------------------------------- XML
def _slot(nome, sid, x, y, w, h, padrao, align, ph) -> str:
    inner = ('<Group x="0" y="0" width="%d" height="%d"><PartText x="0" y="0" width="%d" height="%d">'
             '<Text align="%s"><BitmapFont family="pequena" size="%d"><Template><![CDATA[%%s]]>'
             '<Parameter expression="[COMPLICATION.TEXT]" /></Template></BitmapFont></Text></PartText></Group>') % (w, h, w, h, align, ph)
    return f"""<ComplicationSlot name="{nome}" slotId="{sid}" x="{x}" y="{y}" width="{w}" height="{h}" displayName="slot_{nome}"
        supportedTypes="SHORT_TEXT RANGED_VALUE EMPTY" isCustomizable="TRUE" tintColor="[CONFIGURATION.fosforo]">
      <BoundingBox x="0" y="0" width="{w}" height="{h}" />
      <DefaultProviderPolicy defaultSystemProvider="{padrao}" defaultSystemProviderType="SHORT_TEXT" />
      <Variant mode="AMBIENT" target="alpha" value="0" />
      <Complication type="SHORT_TEXT">{inner}</Complication>
      <Complication type="RANGED_VALUE">{inner}</Complication>
    </ComplicationSlot>"""


def _hora(x, y, w, h, fmt, fonte, tam, alpha_ambiente=None, extra="") -> str:
    v = f'<Variant mode="AMBIENT" target="alpha" value="{alpha_ambiente}" />' if alpha_ambiente is not None else ""
    return (f'<DigitalClock x="{x}" y="{y}" width="{w}" height="{h}">{v}<TimeText x="0" y="0" width="{w}" height="{h}" '
            f'format="{fmt}" hourFormat="SYNC_TO_DEVICE" align="START"><BitmapFont family="{fonte}" size="{tam}" /></TimeText></DigitalClock>')


def _bmp(x, y, w, h, fonte, tam, fmt, params, align="START", extra="") -> str:
    ps = "".join(f'<Parameter expression="{p}" />' for p in params)
    return (f'<PartText x="{x}" y="{y}" width="{w}" height="{h}"{extra}><Text align="{align}"><BitmapFont family="{fonte}" size="{tam}">'
            f'<Template><![CDATA[{fmt}]]>{ps}</Template></BitmapFont></Text></PartText>')


def gerar_xml(gr: tuple[int, int], pq: tuple[int, int], sprites: tuple[tuple[int, int], tuple[int, int]], bmfonts: str) -> str:
    X, Y, SW, SH = SCR
    gw, gh = gr
    pw, ph = pq
    gx, gy = X + 70, Y + 62                          # hora: coluna dos dígitos grandes
    mx = X + 250                                      # mascote
    sw_, sh_ = sprites[0]
    corpo = [
        f'<Group name="tela" x="0" y="0" width="{W}" height="{W}" tintColor="[CONFIGURATION.fosforo]">',
        '  <Variant mode="AMBIENT" target="alpha" value="0" />',
        f'  <PartImage x="{X}" y="{Y}" width="{SW}" height="{SH}"><Image resource="tela" /></PartImage>',
        f'  {_hora(gx, gy - 2, gw * 2, gh, "hh", "grande", gh)}',
        f'  {_hora(gx, gy + gh - 8, gw * 2, gh, "mm", "grande", gh)}',
        f'  {_hora(gx + gw * 2 + 4, gy + gh * 2 - 8 - ph, pw * 2, ph, "ss", "pequena", ph)}',
        # dia da semana (texto escuro sobre a caixa clara) e dia do mês
        f'  <PartText x="{X + 4}" y="{Y + 75}" width="62" height="{ph}"><Text align="CENTER"><BitmapFont family="escura" size="{ph}">'
        '<Template><![CDATA[%s]]><Parameter expression="[DAY_OF_WEEK_S]" /></Template></BitmapFont></Text></PartText>',
        f'  {_bmp(X + 8, Y + 112, 58, ph, "pequena", ph, "%s", ["[DAY_Z]"], "CENTER")}',
        # mascote: dois quadros alternando a cada segundo
        f'  <PartImage x="{mx}" y="{Y + 100}" width="{sw_}" height="{sh_}"><Image resource="mascote_a" />'
        '<Transform target="alpha" value="[SECOND] % 2 == 0 ? 255 : 0" /></PartImage>',
        f'  <PartImage x="{mx}" y="{Y + 100}" width="{sw_}" height="{sh_}"><Image resource="mascote_b" />'
        '<Transform target="alpha" value="[SECOND] % 2 == 0 ? 0 : 255" /></PartImage>',
        # barra de bateria + número
        f'  <PartDraw x="{X + 92}" y="{Y + SH - 38}" width="100" height="16"><Rectangle x="0" y="0" width="100" height="16">'
        '<Fill color="#ffffff" /><Transform target="width" value="100 * clamp([BATTERY_PERCENT], 0, 100) / 100" /></Rectangle></PartDraw>',
        f'  {_bmp(X + 200, Y + SH - 49, 124, ph, "pequena", ph, "%s/100", ["round([BATTERY_PERCENT])"], "END")}',
        '</Group>',
        f'<Group name="vidro" x="{X}" y="{Y}" width="{SW}" height="{SH}"><Variant mode="AMBIENT" target="alpha" value="0" />'
        f'<PartImage x="0" y="0" width="{SW}" height="{SH}"><Image resource="vidro" /></PartImage></Group>',
        _slot("esq", 0, X + 40, Y + 6, 120, ph, "STEP_COUNT", "START", ph),
        _slot("dir", 1, X + SW - 160, Y + 6, 120, ph, "SUNRISE_SUNSET", "END", ph),
        # modo ambiente: hora fina em cinza
        f'<Group name="ambiente" x="0" y="0" width="{W}" height="{W}" alpha="0" tintColor="[CONFIGURATION.fosforo]">'
        '<Variant mode="AMBIENT" target="alpha" value="150" />'
        f'<PartImage x="0" y="0" width="{W}" height="{W}"><Image resource="ambiente" /></PartImage>'
        f'{_hora(X + 80, Y + 80, 180, gh, "hh", "grande", gh)}'
        f'{_hora(X + 80, Y + 80 + gh - 6, 180, gh, "mm", "grande", gh)}</Group>',
    ]
    L = ['<?xml version="1.0" encoding="utf-8"?>',
         "<!-- GERADO por tools/gerar.py crt. Não edite à mão. -->",
         f'<WatchFace width="{W}" height="{W}" clipShape="CIRCLE">',
         '  <Metadata key="CLOCK_TYPE" value="DIGITAL" />', '  <Metadata key="PREVIEW_TIME" value="10:08:32" />',
         "  <BitmapFonts>", bmfonts, "  </BitmapFonts>", "  <UserConfigurations>",
         '    <ColorConfiguration id="fosforo" displayName="fosforo_label" defaultValue="0">']
    L += [f'      <ColorOption id="{i}" displayName="fosforo_{n}" colors="{c}" />' for i, (n, c) in enumerate(FOSFOROS)]
    L += ["    </ColorConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">',
          f'    <Group name="carcaca" x="0" y="0" width="{W}" height="{W}"><Variant mode="AMBIENT" target="alpha" value="0" />'
          f'<PartImage x="0" y="0" width="{W}" height="{W}"><Image resource="carcaca" /></PartImage></Group>']
    L += ["    " + c for c in corpo]
    L += ["  </Scene>", "</WatchFace>"]
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- prévia (simulação)
def _previa(dr: Path, cor_hex: str, h: str, m: str, s: str, ambiente_: bool = False) -> Image.Image:
    X, Y, SW, SH = SCR
    cor = tuple(int(cor_hex[i:i + 2], 16) for i in (1, 3, 5))
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    tint = lambda im: Image.merge("RGBA", [im.getchannel(k).point(lambda v, c=cor[i]: v * c // 255) for i, k in enumerate("RGB")] + [im.getchannel("A")])  # noqa: E731
    if ambiente_:
        base.alpha_composite(tint(Image.open(dr / "ambiente.png")))
        for i, ch in enumerate(h):
            base.alpha_composite(tint(Image.open(dr / f"grande_{ord(ch):02x}.png")), (X + 80 + i * 50, Y + 80))
        for i, ch in enumerate(m):
            base.alpha_composite(tint(Image.open(dr / f"grande_{ord(ch):02x}.png")), (X + 80 + i * 50, Y + 80 + 74))
        out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        mk = Image.new("L", (W * 4, W * 4), 0)
        ImageDraw.Draw(mk).ellipse([0, 0, W * 4 - 1, W * 4 - 1], fill=255)
        out.paste(base, (0, 0), mk.resize((W, W), Image.LANCZOS))
        return out
    base.alpha_composite(Image.open(dr / "carcaca.png"))
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cam.alpha_composite(Image.open(dr / "tela.png"), (X, Y))

    def txt(prefixo: str, texto: str, x: int, y: int, alinhar: str = "START", largura: int = 0, escura: bool = False) -> None:
        ims = [Image.open(dr / f"{prefixo}_{ord(c.upper() if prefixo != 'grande' else c):02x}.png") for c in texto if c != " "]
        tot = sum(i.width for i in ims)
        xx = x if alinhar == "START" else (x + largura - tot if alinhar == "END" else x + (largura - tot) // 2)
        for i in ims:
            cam.alpha_composite(i, (xx, y))
            xx += i.width

    gw = Image.open(dr / "grande_30.png").size
    pw = Image.open(dr / "pequena_30.png").size
    gx, gy = X + 70, Y + 62
    txt("grande", h, gx, gy - 2)
    txt("grande", m, gx, gy + gw[1] - 8)
    txt("pequena", s, gx + gw[0] * 2 + 4, gy + gw[1] * 2 - 8 - pw[1])
    txt("escura", "SEX", X + 4, Y + 75, "CENTER", 62)
    txt("pequena", "23", X + 8, Y + 112, "CENTER", 58)
    cam.alpha_composite(Image.open(dr / ("mascote_a.png" if int(s) % 2 == 0 else "mascote_b.png")), (X + 250, Y + 100))
    d = ImageDraw.Draw(cam)
    d.rectangle([X + 92, Y + SH - 38, X + 92 + 89, Y + SH - 22], fill=(255, 255, 255, 255))
    txt("pequena", "89/100", X + 200, Y + SH - 49, "END", 124)
    txt("pequena", "5623", X + 40, Y + 6)
    txt("pequena", "18:56", X + SW - 160, Y + 6, "END", 120)
    cam = tint(cam)
    base.alpha_composite(cam)
    base.alpha_composite(Image.open(dr / "vidro.png"), (X, Y))
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    mk = Image.new("L", (W * 4, W * 4), 0)
    ImageDraw.Draw(mk).ellipse([0, 0, W * 4 - 1, W * 4 - 1], fill=255)
    out.paste(base, (0, 0), mk.resize((W, W), Image.LANCZOS))
    return out


# ----------------------------------------------------------------------------- orquestração
def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "CRT Terminal", "fosforo_label": "Phosphor color", "fosforo_verde": "Green",
          "fosforo_ambar": "Amber", "fosforo_ciano": "Cyan", "fosforo_branco": "White",
          "slot_esq": "Top left", "slot_dir": "Top right"}
    pt = {"watch_face_name": "Terminal CRT", "fosforo_label": "Cor do fósforo", "fosforo_verde": "Verde",
          "fosforo_ambar": "Âmbar", "fosforo_ciano": "Ciano", "fosforo_branco": "Branco",
          "slot_esq": "Superior esquerdo", "slot_dir": "Superior direito"}
    res = criar_modulo(raiz, NOME, en, pt, flavors=False)
    dr = res / "drawable-nodpi"
    print("  fontes pixel...")
    mg = _fonte_pixel(dr, "grande", "0123456789", GRANDE)
    mp = _fonte_pixel(dr, "pequena", CARS_PEQ, PEQUENA)
    me = _fonte_pixel(dr, "escura", CARS_PEQ, PEQUENA, cor=0, halo=False)
    # a fonte escura precisa ser opaca-escura: cor 0 já é preta; o halo está desligado
    gr = (mg["0"][1], mg["0"][2])
    pq = (mp["0"][1], mp["0"][2])
    print("  imagens...")
    carcaca().save(dr / "carcaca.png", optimize=True)
    tela_vidro().save(dr / "tela.png", optimize=True)
    vidro_cristal().save(dr / "vidro.png", optimize=True)
    ambiente().save(dr / "ambiente.png", optimize=True)
    esc = 3
    for nome, fr in (("mascote_a", 0), ("mascote_b", 1)):
        im = Image.new("RGBA", (24 * esc + 8, 34 * esc + 8), (0, 0, 0, 0))
        _colar_pixel(im, _sprite(fr), 4, 4, esc)
        im.save(dr / f"{nome}.png", optimize=True)
    sz = Image.open(dr / "mascote_a.png").size
    bm = "\n".join([_xml_bitmapfont("grande", mg, False), _xml_bitmapfont("pequena", mp, True), _xml_bitmapfont("escura", me, True)])
    xml = gerar_xml(gr, pq, (sz, sz), bm)
    (res / "raw" / "watchface.xml").write_text(nomear_grupos(xml), encoding="utf-8")
    (res / "values" / "strings.xml").write_text(
        (res / "values" / "strings.xml").read_text(encoding="utf-8"), encoding="utf-8")
    print("  prévias...")
    pv = raiz / "previews"
    pv.mkdir(exist_ok=True)
    imgs = [_previa(dr, c, "10", "08", "32") for _, c in FOSFOROS] + [_previa(dr, FOSFOROS[0][1], "10", "08", "33"), _previa(dr, FOSFOROS[0][1], "10", "08", "00", True)]
    for (n, _), im in zip(FOSFOROS, imgs):
        im.save(pv / f"crt_{n}.png", optimize=True)
    imgs[5].save(pv / "crt_ambiente.png", optimize=True)
    imgs[0].resize((450, 450), Image.LANCZOS).save(dr / "preview.png", optimize=True)
    from faces.cronos_previa import folha
    folha(imgs, ["Verde", "Âmbar", "Ciano", "Branco", "Verde (quadro B do mascote)", "Ambiente (AOD)"], cols=3).save(pv / "crt_folha.png", optimize=True)
    return {"xml_bytes": len(xml)}
