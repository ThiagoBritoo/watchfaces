"""Watchface "Aviador": relógio de piloto clássico e realista. Algarismos grandes com lume, triângulo no 12h,
janela de data no 6h, mostrador fosco (preto, oliva ou azul), ponteiros facetados com sombra e segundos suave.

Reaproveita ponteiros, tampa central e vidro da Cronos (tools/faces/cronos_assets.py).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import (SS, com_mascara, fonte, grad_conico, grad_linear, mascara_anel, metal_paradas, polar,
                        reduzir_por, ruido, sombra, tela, texto_centrado)
from wf.modulo import caixa, criar_modulo, hexcor, nomear_grupos, texto

from . import cronos_assets as CA
from .cronos_previa import _girar

NOME = "aviador"
W = 480
C = 240
ACENTOS = ["#ff5a1f", "#e0262b", "#f2c14e", "#33d6ff", "#ffffff"]
ESTILOS = ["espada", "bastao"]
DATA = (196, 330, 88, 40)       # janela de data (x, y, largura, altura)
SLOT = (180, 142, 120, 40)      # complicação abaixo do 12h

# (id, nome, mostrador, padrão, bisel, algarismos, lume, metal)
TEMAS = {
    "preto": CA.Tema("preto", "Preto fosco", (14, 14, 16), "fosco", (28, 29, 32), (240, 240, 242), (172, 24, 24),
                     ((236, 238, 244), (150, 154, 164), (60, 62, 70)), (240, 240, 242), (232, 244, 214),
                     ((236, 238, 244), (150, 154, 164), (60, 62, 70)), (14, 14, 16), (240, 240, 242)),
    "oliva": CA.Tema("oliva", "Oliva militar", (64, 72, 48), "fosco", (34, 38, 28), (236, 230, 200), (210, 90, 30),
                     ((226, 224, 208), (140, 140, 124), (58, 58, 48)), (236, 230, 200), (246, 238, 190),
                     ((226, 224, 208), (140, 140, 124), (58, 58, 48)), (64, 72, 48), (236, 230, 200)),
    "azul": CA.Tema("azul", "Azul sunburst", (22, 52, 104), "sunburst", (16, 24, 44), (236, 242, 252), (240, 240, 244),
                    ((246, 248, 252), (176, 184, 198), (74, 82, 100)), (236, 242, 252), (190, 226, 255),
                    ((246, 248, 252), (176, 184, 198), (74, 82, 100)), (22, 52, 104), (236, 242, 252)),
}


def _fundo(t: CA.Tema) -> Image.Image:
    n = W * SS
    c = n / 2
    img = tela(n)
    # caixa de aço escovado + aro
    g = grad_conico(n, c, c, metal_paradas(*t.metal), 30)
    img.alpha_composite(com_mascara(g, mascara_anel(n, c, c, 240 * SS, 226 * SS)))
    d = ImageDraw.Draw(img)
    d.ellipse([c - 240 * SS, c - 240 * SS, c + 240 * SS, c + 240 * SS], outline=(0, 0, 0, 160), width=SS)
    d.ellipse([c - 226 * SS, c - 226 * SS, c + 226 * SS, c + 226 * SS], outline=(0, 0, 0, 200), width=2 * SS)
    for k in range(120):                                     # serrilhado do aro
        a = k * 3
        d.line([polar(c, c, 232 * SS, a), polar(c, c, 238 * SS, a)], fill=(0, 0, 0, 90), width=max(1, SS // 2))
    # mostrador
    img.alpha_composite(com_mascara(CA._padrao(t, n), mascara_anel(n, c, c, 224 * SS)))
    d = ImageDraw.Draw(img)
    # trilho de minutos
    for m in range(60):
        a = m * 6
        if m % 5 == 0:
            continue
        d.line([polar(c, c, 208 * SS, a), polar(c, c, 218 * SS, a)], fill=(*t.num_bisel, 230), width=int(1.8 * SS))
    for h in range(12):                                     # pontos de lume nas horas
        x, y = polar(c, c, 213 * SS, h * 30)
        r = 4.6 * SS
        d.ellipse([x - r, y - r, x + r, y + r], fill=(*t.lume, 255), outline=(0, 0, 0, 120), width=max(1, SS // 2))
    # algarismos (3 fica no lugar; 6 cede espaço à janela de data; 12 vira triângulo)
    fn = fonte("SemiBold", 56 * SS)
    for h in range(1, 12):
        if h == 6:
            continue
        x, y = polar(c, c, 168 * SS, h * 30)
        sh = tela(n)
        texto_centrado(sh, str(h), x, y, fn, (0, 0, 0, 255))
        img.alpha_composite(sombra(sh, 1.5 * SS, 2.5 * SS, 1.8 * SS, 0.55))
        texto_centrado(img, str(h), x, y, fn, (*t.num_bisel, 255))
    # triângulo do 12h
    pts = [(c - 24 * SS, 50 * SS), (c + 24 * SS, 50 * SS), (c, 108 * SS)]
    cam = tela(n)
    dc = ImageDraw.Draw(cam)
    dc.polygon(pts, fill=(*t.num_bisel, 255))
    dc.polygon([(c - 15 * SS, 58 * SS), (c + 15 * SS, 58 * SS), (c, 92 * SS)], fill=(*t.lume, 255))
    dc.polygon(pts, outline=(0, 0, 0, 170), width=max(1, SS // 2))
    img.alpha_composite(sombra(cam, 2 * SS, 3 * SS, 2.5 * SS, 0.6))
    img.alpha_composite(cam)
    # janela de data
    x0, y0, w, h = DATA
    sh = tela(n)
    ImageDraw.Draw(sh).rounded_rectangle([x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS], radius=6 * SS, fill=(0, 0, 0, 255))
    img.alpha_composite(sombra(sh, 0, 2 * SS, 3 * SS, 0.5))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([(x0 - 3) * SS, (y0 - 3) * SS, (x0 + w + 3) * SS, (y0 + h + 3) * SS], radius=8 * SS, fill=t.metal[1] + (255,))
    d.rounded_rectangle([x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS], radius=6 * SS, fill=(246, 246, 248, 255))
    # nome
    texto_centrado(img, "AVIADOR", c, 272 * SS, fonte("SemiBold", 14 * SS), (*t.num_bisel, 200), espaco=3.4 * SS)
    return reduzir_por(img)


def _ambiente(t: CA.Tema) -> Image.Image:
    n = W * SS
    c = n / 2
    img = tela(n)
    d = ImageDraw.Draw(img)
    cinza, fraco = (170, 170, 176, 255), (90, 90, 96, 255)
    d.ellipse([c - 237 * SS, c - 237 * SS, c + 237 * SS, c + 237 * SS], outline=fraco, width=SS)
    d.ellipse([c - 224 * SS, c - 224 * SS, c + 224 * SS, c + 224 * SS], outline=fraco, width=SS)
    for h in range(12):
        x, y = polar(c, c, 213 * SS, h * 30)
        r = 3.6 * SS
        d.ellipse([x - r, y - r, x + r, y + r], outline=cinza, width=max(1, SS // 2 + 1))
    fn = fonte("Medium", 52 * SS)
    for h in (3, 9):
        x, y = polar(c, c, 168 * SS, h * 30)
        texto_centrado(img, str(h), x, y, fn, (130, 130, 136, 255))
    pts = [(c - 20 * SS, 56 * SS), (c + 20 * SS, 56 * SS), (c, 100 * SS)]
    d.polygon(pts, outline=cinza, width=max(1, SS // 2 + 1))
    return reduzir_por(img)


# ------------------------------------------------------------------ XML
def _mao(tipo, nome, m, extra="", filhos=""):
    w, h, py = m[nome]
    t = f'<{tipo} resource="{nome}" x="{C - w // 2}" y="{round(C - py)}" width="{w}" height="{h}" pivotX="0.5" pivotY="{py / h:.6f}"{extra}'
    return f"{t}>{filhos}</{tipo}>" if filhos else t + " />"


def gerar_xml(m: dict) -> str:
    ac = "[CONFIGURATION.acento]"
    x0, y0, w, h = DATA
    L = ['<?xml version="1.0" encoding="utf-8"?>', "<!-- GERADO por tools/gerar.py aviador. Não edite à mão. -->",
         f'<WatchFace width="{W}" height="{W}" clipShape="CIRCLE">', '  <Metadata key="CLOCK_TYPE" value="ANALOG" />',
         '  <Metadata key="PREVIEW_TIME" value="10:08:32" />', "  <UserConfigurations>",
         '    <ListConfiguration id="tema" displayName="tema_label" defaultValue="preto">']
    L += [f'      <ListOption id="{i}" displayName="tema_{i}" />' for i in TEMAS]
    L += ["    </ListConfiguration>", '    <ListConfiguration id="estilo" displayName="estilo_label" defaultValue="espada">']
    L += [f'      <ListOption id="{e}" displayName="estilo_{e}" />' for e in ESTILOS]
    L += ["    </ListConfiguration>", '    <ColorConfiguration id="acento" displayName="acento_label" defaultValue="0">']
    L += [f'      <ColorOption id="{i}" displayName="acento_{i}" colors="{c}" />' for i, c in enumerate(ACENTOS)]
    L += ["    </ColorConfiguration>", '    <ListConfiguration id="segundos" displayName="segundos_label" defaultValue="suave">',
          '      <ListOption id="suave" displayName="segundos_suave" />', '      <ListOption id="mecanico" displayName="segundos_mecanico" />',
          "    </ListConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    full = caixa(W, W)
    a(f'    <Group name="mostrador" {full}><Variant mode="AMBIENT" target="alpha" value="0" /><ListConfiguration id="tema">')
    for t in TEMAS:
        a(f'      <ListOption id="{t}"><Group {full}><PartImage {full}><Image resource="fundo_{t}" /></PartImage></Group></ListOption>')
    a("    </ListConfiguration></Group>")
    a(f'    <Group name="ambiente" {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" /><ListConfiguration id="tema">')
    for t in TEMAS:
        a(f'      <ListOption id="{t}"><Group {full}><PartImage {full}><Image resource="ambiente_{t}" /></PartImage></Group></ListOption>')
    a("    </ListConfiguration></Group>")
    # data (texto escuro na janela branca) e complicação
    a(f'    <Group name="data" {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
      + texto(x0, y0 + 2, w, h - 4, 30, "#ff101012", "%s", ["[DAY_Z]"], "BOLD") + "</Group>")
    sx, sy, sw, sh = SLOT
    a(f'    <ComplicationSlot name="topo" slotId="0" x="{sx}" y="{sy}" width="{sw}" height="{sh}" displayName="slot_topo" '
      f'supportedTypes="SHORT_TEXT RANGED_VALUE EMPTY" isCustomizable="TRUE">')
    a(f'      <BoundingBox x="0" y="0" width="{sw}" height="{sh}" />')
    a('      <DefaultProviderPolicy defaultSystemProvider="WATCH_BATTERY" defaultSystemProviderType="SHORT_TEXT" />')
    a('      <Variant mode="AMBIENT" target="alpha" value="0" />')
    for tp in ("SHORT_TEXT", "RANGED_VALUE"):
        a(f'      <Complication type="{tp}"><Group {caixa(sw, sh)}><ListConfiguration id="tema">')
        for t, th in TEMAS.items():
            a(f'        <ListOption id="{t}"><Group {caixa(sw, sh)}>'
              + texto(0, 0, sw, sh, 28, ac, "%s", ["[COMPLICATION.TEXT]"], "SEMI_BOLD") + "</Group></ListOption>")
        a("      </ListConfiguration></Group></Complication>")
    a("    </ComplicationSlot>")
    # ponteiros
    a(f'    <Group name="ponteiros" {full}><ListConfiguration id="tema">')
    for t in TEMAS:
        a(f'      <ListOption id="{t}"><Group {full}><ListConfiguration id="estilo">')
        for e in ESTILOS:
            a(f'        <ListOption id="{e}"><AnalogClock {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
              + _mao("HourHand", f"hora_sombra_{e}", m) + _mao("MinuteHand", f"min_sombra_{e}", m)
              + _mao("HourHand", f"hora_{e}_{t}", m) + _mao("MinuteHand", f"min_{e}_{t}", m) + "</AnalogClock></ListOption>")
        a("      </ListConfiguration></Group></ListOption>")
    a("    </ListConfiguration>")
    a('    <ListConfiguration id="estilo">')
    for e in ESTILOS:
        a(f'      <ListOption id="{e}"><AnalogClock {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />'
          + _mao("HourHand", f"hora_contorno_{e}", m) + _mao("MinuteHand", f"min_contorno_{e}", m) + "</AnalogClock></ListOption>")
    a("    </ListConfiguration>")
    a('    <ListConfiguration id="segundos">')
    for modo in ("suave", "mecanico"):
        mov = '<Sweep frequency="15" />' if modo == "suave" else '<Tick strength="0.4" duration="0.25" />'
        a(f'      <ListOption id="{modo}"><AnalogClock {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
          + _mao("SecondHand", "seg_sombra", m, filhos=mov) + _mao("SecondHand", "seg", m, f' tintColor="{ac}"', mov) + "</AnalogClock></ListOption>")
    a("    </ListConfiguration></Group>")
    a(f'    <Group name="tampa" {full}><ListConfiguration id="tema">')
    for t in TEMAS:
        a(f'      <ListOption id="{t}"><Group {full}><PartImage x="{C - 24}" y="{C - 24}" width="48" height="48"><Image resource="tampa_{t}" /></PartImage></Group></ListOption>')
    a("    </ListConfiguration></Group>")
    a(f'    <Group name="vidro" {full}><Variant mode="AMBIENT" target="alpha" value="0" /><PartImage {full}><Image resource="vidro" /></PartImage></Group>')
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ prévia
def _tint(im, cor):
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r.point(lambda v: v * cor[0] // 255), g.point(lambda v: v * cor[1] // 255), b.point(lambda v: v * cor[2] // 255), a))


def previa(A, tema: str, estilo: str, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    t = TEMAS[tema]
    cor = tuple(int(acento[i:i + 2], 16) for i in (1, 3, 5))
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    ang_h, ang_m, ang_s = (h % 12) * 30 + mi * 0.5 + s / 120, mi * 6 + s * 0.1, s * 6
    if ambiente_:
        base.alpha_composite(A[f"ambiente_{tema}"])
        for nome, ang in ((f"hora_contorno_{estilo}", ang_h), (f"min_contorno_{estilo}", ang_m)):
            im, py = A[nome]
            base.alpha_composite(_girar(W, im, py, ang))
    else:
        base.alpha_composite(A[f"fundo_{tema}"])
        d = ImageDraw.Draw(base)
        x0, y0, w, hh = DATA
        d.text((x0 + w / 2, y0 + hh / 2), "31", font=fonte("Bold", 30), fill=(16, 16, 18), anchor="mm")
        d.text((SLOT[0] + SLOT[2] / 2, SLOT[1] + SLOT[3] / 2), "76%", font=fonte("SemiBold", 28), fill=cor, anchor="mm")
        for nome, ang in ((f"hora_sombra_{estilo}", ang_h), (f"min_sombra_{estilo}", ang_m)):
            im, py = A[nome]
            base.alpha_composite(_girar(W, im, py, ang))
        for nome, ang in ((f"hora_{estilo}_{tema}", ang_h), (f"min_{estilo}_{tema}", ang_m)):
            im, py = A[nome]
            base.alpha_composite(_girar(W, im, py, ang))
        im, py = A["seg_sombra"]
        base.alpha_composite(_girar(W, im, py, ang_s))
        im, py = A["seg"]
        base.alpha_composite(_girar(W, _tint(im, cor), py, ang_s))
        base.alpha_composite(A[f"tampa_{tema}"], (C - 24, C - 24))
        base.alpha_composite(A["vidro"])
    mk = Image.new("L", (W * 4, W * 4), 0)
    ImageDraw.Draw(mk).ellipse([0, 0, W * 4 - 1, W * 4 - 1], fill=255)
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    out.paste(base, (0, 0), mk.resize((W, W), Image.LANCZOS))
    return out


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Aviator", "tema_label": "Dial", "tema_preto": "Matte black", "tema_oliva": "Military olive", "tema_azul": "Blue sunburst",
          "estilo_label": "Hand style", "estilo_espada": "Sword", "estilo_bastao": "Baton", "acento_label": "Accent color",
          "segundos_label": "Seconds hand", "segundos_suave": "Smooth sweep", "segundos_mecanico": "Mechanical tick", "slot_topo": "Top field"}
    pt = {"watch_face_name": "Aviador", "tema_label": "Mostrador", "tema_preto": "Preto fosco", "tema_oliva": "Oliva militar", "tema_azul": "Azul sunburst",
          "estilo_label": "Estilo dos ponteiros", "estilo_espada": "Espada", "estilo_bastao": "Bastão", "acento_label": "Cor de destaque",
          "segundos_label": "Ponteiro de segundos", "segundos_suave": "Contínuo (suave)", "segundos_mecanico": "Com salto mecânico", "slot_topo": "Campo superior"}
    for i, (e, p) in enumerate((("Orange", "Laranja"), ("Red", "Vermelho"), ("Gold", "Dourado"), ("Cyan", "Ciano"), ("White", "Branco"))):
        en[f"acento_{i}"], pt[f"acento_{i}"] = e, p
    res = criar_modulo(raiz, NOME, en, pt, flavors=False)
    dr = res / "drawable-nodpi"
    A: dict = {}
    for tid, t in TEMAS.items():
        A[f"fundo_{tid}"] = _fundo(t)
        A[f"ambiente_{tid}"] = _ambiente(t)
        A[f"tampa_{tid}"] = CA.tampa_central(t)
    ref = TEMAS["preto"]
    for est in ESTILOS:
        for nome, (comp, cauda, larg) in (("hora", (124, 26, 30 if est == "espada" else 22)), ("min", (186, 30, 22 if est == "espada" else 16))):
            for tid, t in TEMAS.items():
                A[f"{nome}_{est}_{tid}"] = CA.ponteiro(t, est, comp, cauda, larg)
            im, py = A[f"{nome}_{est}_preto"]
            A[f"{nome}_sombra_{est}"] = CA.ponteiro_sombra(im, py, 10)
            A[f"{nome}_contorno_{est}"] = CA.ponteiro_contorno(ref, est, comp, cauda, larg)
    A["seg"] = CA.ponteiro_segundos(212, 52)
    A["seg_sombra"] = CA.ponteiro_sombra(*A["seg"], 10)
    A["vidro"] = CA.vidro()
    med = {}
    for nome, v in A.items():
        im, py = v if isinstance(v, tuple) else (v, 0.0)
        im.save(dr / f"{nome}.png", optimize=True)
        med[nome] = (im.width, im.height, py)
    (res / "raw" / "watchface.xml").write_text(nomear_grupos(gerar_xml(med)), encoding="utf-8")
    pv = raiz / "previews"
    pv.mkdir(exist_ok=True)
    cfg = [("preto", "espada", ACENTOS[0], 10, 8, 32), ("oliva", "bastao", ACENTOS[2], 4, 20, 45), ("azul", "espada", ACENTOS[4], 7, 50, 12)]
    imgs = [previa(A, tid, est, ac, h, mi, s) for tid, est, ac, h, mi, s in cfg] + [previa(A, "preto", "espada", ACENTOS[0], 10, 8, 0, True)]
    for nome, im in zip(["preto", "oliva", "azul", "ambiente"], imgs):
        im.save(pv / f"aviador_{nome}.png", optimize=True)
    imgs[0].resize((450, 450), Image.LANCZOS).save(dr / "preview.png", optimize=True)
    from faces.cronos_previa import folha
    folha(imgs, ["Preto fosco", "Oliva militar", "Azul sunburst", "Ambiente (AOD)"], cols=4).save(pv / "aviador_folha.png", optimize=True)
    return {"xml_bytes": len(gerar_xml(med))}
