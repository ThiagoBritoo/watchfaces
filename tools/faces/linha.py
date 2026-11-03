"""Watchface "Linha": minimalista elegante. Hora grande e fina (digital) ou ponteiros finos (analógico),
dois anéis de progresso (passos e bateria) e três complicações em cápsula.

Sem texturas: pouquíssimos pixels acesos, ótima para AMOLED e bateria. Cores por paleta (ColorConfiguration):
cada tema define fundo, texto, texto secundário e fundo das cápsulas; o destaque é escolhido à parte.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, polar, reduzir_por, sombra, tela
from wf.modulo import criar_modulo, texto

NOME = "linha"
W = 480
C = 240
# fundo, texto, secundário, cápsula (ARGB)
TEMAS = [("escuro", "#ff000000 #fff4f4f6 #ff9a9aa4 #26ffffff"), ("claro", "#fff2f2f4 #ff16161a #ff6c6c76 #14000000"),
         ("grafite", "#ff15171c #ffe8ebf2 #ff8d93a3 #26ffffff"), ("cobre", "#ff120c08 #fff6e6d6 #ffa88b73 #2ad4a373")]
ACENTOS = [("gelo", "#6ec6ff"), ("coral", "#ff6b57"), ("menta", "#4be3b0"), ("ouro", "#f2c14e"), ("lilas", "#b38cff")]
SLOTS = {"topo": (160, 66, 160, 58), "esq": (84, 338, 150, 62), "dir": (246, 338, 150, 62)}
PADROES = {"topo": "DAY_OF_WEEK", "esq": "STEP_COUNT", "dir": "WATCH_BATTERY"}


def _paleta(i: int) -> list[str]:
    return TEMAS[i][1].split()


def _mao(comp: float, cauda: float, larg: float, ponta: float = 0) -> tuple[Image.Image, float]:
    s = 4
    pad = 4
    w, h = int(larg) + 2 * pad, int(comp + cauda) + 2 * pad
    w += w % 2
    img = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w * s / 2
    d.rounded_rectangle([cx - larg / 2 * s, pad * s, cx + larg / 2 * s, (pad + comp + cauda) * s], radius=larg / 2 * s, fill=(255, 255, 255, 255))
    return img.resize((w, h), Image.LANCZOS), pad + comp


def _ponteiro_seg() -> tuple[Image.Image, float]:
    s = 4
    pad, comp, cauda = 4, 206, 34
    w, h = 14, int(comp + cauda) + 2 * pad
    img = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, py = w * s / 2, (pad + comp) * s
    d.rectangle([cx - 1.1 * s, pad * s, cx + 1.1 * s, py + cauda * s], fill=(255, 255, 255, 255))
    d.ellipse([cx - 5 * s, py - 5 * s, cx + 5 * s, py + 5 * s], fill=(255, 255, 255, 255))
    return img.resize((w, h), Image.LANCZOS), pad + comp


def marcas() -> Image.Image:
    """12 marcas finas (4 maiores) para o estilo analógico; branco, pintado pelo tema."""
    n = W * SS
    c = n / 2
    img = tela(n)
    d = ImageDraw.Draw(img)
    for h in range(60):
        a = h * 6
        if h % 5:
            continue
        maior = h % 15 == 0
        d.line([polar(c, c, (188 if maior else 194) * SS, a), polar(c, c, 206 * SS, a)], fill=(255, 255, 255, 255), width=int((4.0 if maior else 2.4) * SS))
    return reduzir_por(img)


def _por_hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip('#')[-6:]
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


# ------------------------------------------------------------------ XML
def _capsula(w: int, h: int) -> str:
    return (f'<PartDraw x="0" y="0" width="{w}" height="{h}"><RoundRectangle x="0" y="0" width="{w}" height="{h}" '
            f'cornerRadiusX="{h // 2}" cornerRadiusY="{h // 2}"><Fill color="[CONFIGURATION.tema.3]" /></RoundRectangle></PartDraw>')


def _slot(nome: str, sid: int, x: int, y: int, w: int, h: int) -> str:
    sec, txt, ac = "[CONFIGURATION.tema.2]", "[CONFIGURATION.tema.1]", "[CONFIGURATION.acento]"
    norm = ("(clamp([COMPLICATION.RANGED_VALUE_VALUE], [COMPLICATION.RANGED_VALUE_MIN], [COMPLICATION.RANGED_VALUE_MAX])"
            " - [COMPLICATION.RANGED_VALUE_MIN]) / ([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN])")
    barra = (f'<PartDraw x="26" y="{h - 14}" width="{w - 52}" height="5"><RoundRectangle x="0" y="0" width="{w - 52}" height="5" cornerRadiusX="2.5" cornerRadiusY="2.5">'
             f'<Fill color="{sec}" /></RoundRectangle></PartDraw>'
             f'<PartDraw x="26" y="{h - 14}" width="{w - 52}" height="5"><RoundRectangle x="0" y="0" width="{w - 52}" height="5" cornerRadiusX="2.5" cornerRadiusY="2.5">'
             f'<Fill color="{ac}" /><Transform target="width" value="({w - 52}) * ({norm})" /></RoundRectangle></PartDraw>')
    return f"""<ComplicationSlot name="{nome}" slotId="{sid}" x="{x}" y="{y}" width="{w}" height="{h}" displayName="slot_{nome}"
        supportedTypes="SHORT_TEXT RANGED_VALUE MONOCHROMATIC_IMAGE SMALL_IMAGE EMPTY" isCustomizable="TRUE">
      <BoundingRoundBox x="0" y="0" width="{w}" height="{h}" cornerRadius="{h // 2}" />
      <DefaultProviderPolicy defaultSystemProvider="{PADROES[nome]}" defaultSystemProviderType="SHORT_TEXT" />
      <Variant mode="AMBIENT" target="alpha" value="0" />
      <Complication type="SHORT_TEXT">
        {_capsula(w, h)}
        <Condition>
          <Expressions><Expression name="titulo"><![CDATA[[COMPLICATION.TITLE] != null]]></Expression></Expressions>
          <Compare expression="titulo"><Group x="0" y="0" width="{w}" height="{h}">
            {texto(10, 8, w - 20, 18, 14, sec, "%s", ["[COMPLICATION.TITLE]"], "MEDIUM")}
            {texto(10, 24, w - 20, h - 28, 27, txt, "%s", ["[COMPLICATION.TEXT]"], "SEMI_BOLD")}
          </Group></Compare>
          <Default><Group x="0" y="0" width="{w}" height="{h}">
            {texto(10, 10, w - 20, h - 20, 28, txt, "%s", ["[COMPLICATION.TEXT]"], "SEMI_BOLD")}
          </Group></Default>
        </Condition>
      </Complication>
      <Complication type="RANGED_VALUE">
        {_capsula(w, h)}
        {texto(10, 6, w - 20, h - 22, 27, txt, "%s", ["[COMPLICATION.TEXT]"], "SEMI_BOLD")}
        {barra}
      </Complication>
      <Complication type="MONOCHROMATIC_IMAGE">
        {_capsula(w, h)}
        <PartImage x="{w // 2 - 18}" y="{h // 2 - 18}" width="36" height="36" tintColor="{ac}"><Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]" /></PartImage>
      </Complication>
      <Complication type="SMALL_IMAGE">
        {_capsula(w, h)}
        <PartImage x="{w // 2 - 18}" y="{h // 2 - 18}" width="36" height="36"><Image resource="[COMPLICATION.SMALL_IMAGE]" /></PartImage>
      </Complication>
    </ComplicationSlot>"""


def _mao_xml(tipo: str, nome: str, m, extra="", filhos="") -> str:
    w, h, py = m[nome]
    t = f'<{tipo} resource="{nome}" x="{C - w // 2}" y="{round(C - py)}" width="{w}" height="{h}" pivotX="0.5" pivotY="{py / h:.6f}"{extra}'
    return f"{t}>{filhos}</{tipo}>" if filhos else t + " />"


def gerar_xml(m: dict) -> str:
    tx, sec, ac = "[CONFIGURATION.tema.1]", "[CONFIGURATION.tema.2]", "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'

    def aro(r, esp, cor, expr=None) -> str:
        t = f'<Transform target="endAngle" value="{expr}" />' if expr else ""
        return (f'<Arc centerX="{C}" centerY="{C}" width="{2 * r}" height="{2 * r}" startAngle="0" endAngle="360">'
                f'<Stroke thickness="{esp}" color="{cor}" cap="ROUND" />{t}</Arc>')

    L = ['<?xml version="1.0" encoding="utf-8"?>', "<!-- GERADO por tools/gerar.py linha. Não edite à mão. -->",
         f'<WatchFace width="{W}" height="{W}" clipShape="CIRCLE">', '  <Metadata key="CLOCK_TYPE" value="DIGITAL" />',
         '  <Metadata key="PREVIEW_TIME" value="10:08:32" />', "  <UserConfigurations>",
         '    <ColorConfiguration id="tema" displayName="tema_label" defaultValue="escuro">']
    L += [f'      <ColorOption id="{i}" displayName="tema_{i}" colors="{c}" />' for i, c in TEMAS]
    L += ["    </ColorConfiguration>", '    <ColorConfiguration id="acento" displayName="acento_label" defaultValue="gelo">']
    L += [f'      <ColorOption id="{n}" displayName="acento_{n}" colors="{c}" />' for n, c in ACENTOS]
    L += ["    </ColorConfiguration>", '    <ListConfiguration id="estilo" displayName="estilo_label" defaultValue="digital">',
          '      <ListOption id="digital" displayName="estilo_digital" />', '      <ListOption id="analogico" displayName="estilo_analogico" />',
          "    </ListConfiguration>", '    <BooleanConfiguration id="aneis" displayName="aneis_label" defaultValue="TRUE" />',
          "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a(f'    <Group name="fundo" {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
      f'<PartDraw {full}><Rectangle x="0" y="0" width="{W}" height="{W}"><Fill color="[CONFIGURATION.tema.0]" /></Rectangle></PartDraw></Group>')
    # anéis de passos (externo) e bateria (interno)
    a(f'    <BooleanConfiguration id="aneis"><BooleanOption id="TRUE"><Group name="aneis" {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
      f'<PartDraw {full}>{aro(226, 8, "[CONFIGURATION.tema.3]")}{aro(226, 8, ac, "clamp([STEP_PERCENT], 0, 100) * 3.6")}</PartDraw>'
      f'<PartDraw {full}>{aro(212, 4, "[CONFIGURATION.tema.3]")}{aro(212, 4, sec, "clamp([BATTERY_PERCENT], 0, 100) * 3.6")}</PartDraw></Group></BooleanOption></BooleanConfiguration>')
    # estilo digital
    a('    <ListConfiguration id="estilo"><ListOption id="digital">')
    a(f'      <Group name="digital" {full}>')
    a(f'        <DigitalClock x="0" y="150" width="{W}" height="150"><Variant mode="AMBIENT" target="alpha" value="0" />'
      f'<TimeText x="0" y="0" width="{W}" height="150" format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER">'
      f'<Font family="SYNC_TO_DEVICE" size="132" weight="THIN" color="{tx}" /></TimeText></DigitalClock>')
    a(f'        <DigitalClock x="0" y="150" width="{W}" height="150" alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />'
      f'<TimeText x="0" y="0" width="{W}" height="150" format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER">'
      '<Font family="SYNC_TO_DEVICE" size="132" weight="THIN" color="#ffc8c8ce" /></TimeText></DigitalClock>')
    a(f'        <Group {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
      f'{texto(120, 286, 240, 30, 20, sec, "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM")}'
      f'<PartDraw x="{C - 18}" y="318" width="36" height="4"><RoundRectangle x="0" y="0" width="36" height="4" cornerRadiusX="2" cornerRadiusY="2"><Fill color="{ac}" /></RoundRectangle></PartDraw></Group>')
    a("      </Group></ListOption>")
    # estilo analógico
    a('      <ListOption id="analogico">')
    a(f'      <Group name="analogico" {full}>')
    a(f'        <PartImage {full} tintColor="{sec}"><Image resource="marcas" /><Variant mode="AMBIENT" target="alpha" value="120" /></PartImage>')
    a(f'        <Group {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
      f'{texto(190, 190, 100, 26, 18, sec, "%s", ["[DAY_Z]"], "MEDIUM")}</Group>')
    a("      </Group></ListOption></ListConfiguration>")
    a("    " + _slot("topo", 0, *SLOTS["topo"]))
    a("    " + _slot("esq", 1, *SLOTS["esq"]))
    a("    " + _slot("dir", 2, *SLOTS["dir"]))
    # ponteiros do estilo analógico (interativo, tingido pelo tema)
    a('    <ListConfiguration id="estilo"><ListOption id="digital"><Group x="0" y="0" width="1" height="1" /></ListOption><ListOption id="analogico">')
    a(f'      <AnalogClock {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a("        " + _mao_xml("HourHand", "hora", m, f' tintColor="{tx}"'))
    a("        " + _mao_xml("MinuteHand", "min", m, f' tintColor="{tx}"'))
    a("        " + _mao_xml("SecondHand", "seg", m, f' tintColor="{ac}"', '<Sweep frequency="15" />'))
    a("      </AnalogClock>")
    a(f'      <AnalogClock {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />')
    a("        " + _mao_xml("HourHand", "hora", m, ' tintColor="#ffd0d0d6"'))
    a("        " + _mao_xml("MinuteHand", "min", m, ' tintColor="#ffd0d0d6"'))
    a("      </AnalogClock>")
    a("    </ListOption></ListConfiguration>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ prévia (Inter no lugar da fonte do relógio)
def previa(A: dict, tema: int, acento: str, estilo: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    bg, tx, sec, cap = (_por_hex(c) for c in _paleta(tema))
    capa = int(_paleta(tema)[3][1:3], 16)
    ac = _por_hex(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d0 = ImageDraw.Draw(base)
    if not ambiente_:
        d0.rectangle([0, 0, W, W], fill=bg + (255,))
        layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        for r, esp, cor, frac in ((226, 8, ac, 0.82), (212, 4, sec, 0.76)):
            dl.ellipse([C - r, C - r, C + r, C + r], outline=cap + (capa,), width=esp)
            dl.arc([C - r, C - r, C + r, C + r], -90, -90 + 360 * frac, fill=cor + (255,), width=esp)
        base.alpha_composite(layer)
        cl = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        dc = ImageDraw.Draw(cl)
        for nome, (x, y, w, hh) in SLOTS.items():
            dc.rounded_rectangle([x, y, x + w, y + hh], radius=hh // 2, fill=cap + (capa,))
        base.alpha_composite(cl)
        d = ImageDraw.Draw(base)
        for nome, (x, y, w, hh), titulo, valor in (("topo", SLOTS["topo"], "SEXTA", "31"), ("esq", SLOTS["esq"], "PASSOS", "8,2k"), ("dir", SLOTS["dir"], "BATERIA", "76%")):
            d.text((x + w / 2, y + 14), titulo, font=fonte("Medium", 14), fill=sec, anchor="mm")
            d.text((x + w / 2, y + hh / 2 + 10), valor, font=fonte("SemiBold", 27), fill=tx, anchor="mm")
        if estilo == "digital":
            d.text((C, 224), f"{h:02d}:{mi:02d}", font=fonte("Thin", 132), fill=tx, anchor="mm")
            d.text((C, 300), "SEX 31 OUT", font=fonte("Medium", 20), fill=sec, anchor="mm")
            d.rounded_rectangle([C - 18, 318, C + 18, 322], radius=2, fill=ac)
        else:
            mk = Image.merge("RGBA", [Image.new("L", (W, W), sec[i]) for i in range(3)] + [A["marcas"].getchannel("A").point(lambda v: v)])
            base.alpha_composite(mk)
            d.text((C, 203), "31", font=fonte("Medium", 18), fill=sec, anchor="mm")
            _maos(base, A, tx, ac, h, mi, s)
    else:
        if estilo == "digital":
            ImageDraw.Draw(base).text((C, 224), f"{h:02d}:{mi:02d}", font=fonte("Thin", 132), fill=(200, 200, 206), anchor="mm")
        else:
            _maos(base, A, (208, 208, 214), None, h, mi, s)
    mk = Image.new("L", (W * 4, W * 4), 0)
    ImageDraw.Draw(mk).ellipse([0, 0, W * 4 - 1, W * 4 - 1], fill=255)
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    out.paste(base, (0, 0), mk.resize((W, W), Image.LANCZOS))
    return out


def _maos(base: Image.Image, A: dict, tx, ac, h: int, mi: int, s: int) -> None:
    def tint(im, cor):
        r, g, b, a = im.split()
        return Image.merge("RGBA", (r.point(lambda v: v * cor[0] // 255), g.point(lambda v: v * cor[1] // 255), b.point(lambda v: v * cor[2] // 255), a))

    seq = [("hora", (h % 12) * 30 + mi * 0.5, tx), ("min", mi * 6 + s * 0.1, tx)]
    if ac:
        seq.append(("seg", s * 6, ac))
    for nome, ang, cor in seq:
        im, py = A[nome]
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        cam.alpha_composite(tint(im, cor), (int(C - im.width / 2), int(round(C - py))))
        base.alpha_composite(cam.rotate(-ang, center=(C, C), resample=Image.BICUBIC))


# ------------------------------------------------------------------ orquestração
def gerar(raiz: Path) -> dict:
    nomes = {"escuro": ("Dark", "Escuro"), "claro": ("Light", "Claro"), "grafite": ("Graphite", "Grafite"), "cobre": ("Copper", "Cobre")}
    ac = {"gelo": ("Ice", "Gelo"), "coral": ("Coral", "Coral"), "menta": ("Mint", "Menta"), "ouro": ("Gold", "Ouro"), "lilas": ("Lilac", "Lilás")}
    en = {"watch_face_name": "Line", "tema_label": "Theme", "acento_label": "Accent color", "estilo_label": "Style",
          "estilo_digital": "Digital", "estilo_analogico": "Analog", "aneis_label": "Progress rings",
          "slot_topo": "Top", "slot_esq": "Bottom left", "slot_dir": "Bottom right"}
    pt = {"watch_face_name": "Linha", "tema_label": "Tema", "acento_label": "Cor de destaque", "estilo_label": "Estilo",
          "estilo_digital": "Digital", "estilo_analogico": "Analógico", "aneis_label": "Anéis de progresso",
          "slot_topo": "Superior", "slot_esq": "Inferior esquerdo", "slot_dir": "Inferior direito"}
    for k, (e, p) in nomes.items():
        en[f"tema_{k}"], pt[f"tema_{k}"] = e, p
    for k, (e, p) in ac.items():
        en[f"acento_{k}"], pt[f"acento_{k}"] = e, p
    res = criar_modulo(raiz, NOME, en, pt, flavors=False)
    dr = res / "drawable-nodpi"
    A = {"hora": _mao(122, 22, 8), "min": _mao(178, 26, 5), "seg": _ponteiro_seg(), "marcas": marcas()}
    med = {}
    for n, v in A.items():
        im, py = v if isinstance(v, tuple) else (v, 0.0)
        im.save(dr / f"{n}.png", optimize=True)
        med[n] = (im.width, im.height, py)
    (res / "raw" / "watchface.xml").write_text(gerar_xml(med), encoding="utf-8")
    pv = raiz / "previews"
    pv.mkdir(exist_ok=True)
    imgs = [previa(A, 0, "#6ec6ff", "digital", 10, 8, 32), previa(A, 1, "#ff6b57", "digital", 10, 8, 32),
            previa(A, 3, "#f2c14e", "analogico", 10, 8, 32), previa(A, 2, "#4be3b0", "analogico", 7, 42, 15),
            previa(A, 0, "#6ec6ff", "digital", 10, 8, 0, True), previa(A, 0, "#6ec6ff", "analogico", 10, 8, 0, True)]
    nomes_p = ["escuro_digital", "claro_digital", "cobre_analogico", "grafite_analogico", "ambiente_digital", "ambiente_analogico"]
    for n, im in zip(nomes_p, imgs):
        im.save(pv / f"linha_{n}.png", optimize=True)
    imgs[0].resize((450, 450), Image.LANCZOS).save(dr / "preview.png", optimize=True)
    from faces.cronos_previa import folha
    folha(imgs, ["Escuro + gelo (digital)", "Claro + coral (digital)", "Cobre + ouro (analógico)", "Grafite + menta (analógico)", "Ambiente digital", "Ambiente analógico"], cols=3).save(pv / "linha_folha.png", optimize=True)
    return {"xml_bytes": len(gerar_xml(med))}
