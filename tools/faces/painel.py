"""Watchface "Painel": digital esportiva e informativa. Hora grande, data, clima (fontes WEATHER.*, WFF v2),
3 mostradores circulares com complicação (passos, frequência cardíaca, bateria por padrão) e arco dos segundos.

Os ícones do clima são imagens brancas em uma BitmapFont indexada pelo código [WEATHER.CONDITION], como no exemplo
oficial "Weather" do Google (mapeamento 0..15 conferido nele); a cor vem de tintColor.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, polar, reduzir_por, tela
from wf.modulo import criar_modulo, nomear_grupos, texto

NOME = "painel"
W = 480
C = 240
TEMAS = [("escuro", "#ff000000 #fff6f6f8 #ff8f95a3 #1fffffff"), ("claro", "#fff3f4f7 #ff15171c #ff6a7080 #14000000"),
         ("azul", "#ff06101f #ffeaf2ff #ff8aa4cf #2a7fb4ff"), ("floresta", "#ff07130e #ffe9f7ee #ff8fb3a0 #2a3ddc84")]
ACENTOS = [("laranja", "#ff8a3d"), ("ciano", "#33d6ff"), ("verde", "#4be37a"), ("rosa", "#ff5c93"), ("amarelo", "#ffd23d")]
GAUGE = 104
GAUGES = {"esq": (76, 322), "meio": (C - GAUGE // 2, 342), "dir": (C + 76, 322)}
PADROES = {"esq": ("STEP_COUNT", "RANGED_VALUE"), "meio": ("HEART_RATE", "SHORT_TEXT"), "dir": ("WATCH_BATTERY", "RANGED_VALUE")}
# condição do clima (0..15, igual ao exemplo oficial) -> ícone
ICONE = {0: "?", 1: "sol", 2: "nuvem", 3: "nevoa", 4: "chuvaforte", 5: "nevada", 6: "chuva", 7: "neve", 8: "sol", 9: "raio",
         10: "chuva", 11: "neve", 12: "chuva", 13: "nevoa", 14: "parcial", 15: "vento"}


# ------------------------------------------------------------------ ícones do clima (64x64, brancos)
def _nuvem(d: ImageDraw.ImageDraw, s: int, dx=0, dy=0, esc=1.0) -> None:
    def e(x0, y0, x1, y1):
        d.ellipse([(x0 * esc + dx) * s, (y0 * esc + dy) * s, (x1 * esc + dx) * s, (y1 * esc + dy) * s], fill=255)
    e(10, 30, 32, 52)
    e(20, 20, 44, 46)
    e(32, 28, 54, 52)
    d.rectangle([(21 * esc + dx) * s, (36 * esc + dy) * s, (43 * esc + dx) * s, (52 * esc + dy) * s], fill=255)


def _sol(d: ImageDraw.ImageDraw, s: int, cx=32, cy=32, r=11, raios=True) -> None:
    d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], fill=255)
    if raios:
        for k in range(8):
            a = k * 45
            d.line([polar(cx * s, cy * s, (r + 5) * s, a), polar(cx * s, cy * s, (r + 11) * s, a)], fill=255, width=3 * s)


def _lua(d: ImageDraw.ImageDraw, s: int, cx=32, cy=32, r=16) -> None:
    d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], fill=255)
    d.ellipse([(cx - r + 9) * s, (cy - r - 4) * s, (cx + r + 9) * s, (cy + r - 4) * s], fill=0)


def _icone(nome: str, noite: bool) -> Image.Image:
    s = 4
    im = Image.new("L", (64 * s, 64 * s), 0)
    d = ImageDraw.Draw(im)
    if nome == "sol":
        _lua(d, s) if noite else _sol(d, s)
    elif nome == "nuvem":
        _nuvem(d, s, 0, 2)
    elif nome == "parcial":
        _lua(d, s, 22, 22, 12) if noite else _sol(d, s, 22, 22, 8)
        d.rectangle([0, 0, 0, 0], fill=0)
        sub = Image.new("L", im.size, 0)
        _nuvem(ImageDraw.Draw(sub), s, 6, 6, 0.9)
        # recorte em volta da nuvem para separar do sol
        from PIL import ImageFilter
        halo = sub.filter(ImageFilter.MaxFilter(9))
        im.paste(0, mask=halo)
        im.paste(255, mask=sub)
    elif nome in ("chuva", "chuvaforte"):
        _nuvem(d, s, 0, -6)
        n = 3 if nome == "chuva" else 4
        for k in range(n):
            x = 18 + k * (28 / (n - 1)) if n > 1 else 32
            d.line([(x * s, 46 * s), ((x - 5) * s, 58 * s)], fill=255, width=3 * s)
    elif nome in ("neve", "nevada"):
        _nuvem(d, s, 0, -6)
        for x, y in ((20, 52), (32, 57), (44, 52), (26, 46), (38, 46)) if nome == "nevada" else ((20, 53), (32, 57), (44, 53)):
            d.ellipse([(x - 3) * s, (y - 3) * s, (x + 3) * s, (y + 3) * s], fill=255)
    elif nome == "raio":
        _nuvem(d, s, 0, -8)
        d.polygon([(34 * s, 40 * s), (24 * s, 54 * s), (31 * s, 54 * s), (28 * s, 64 * s), (42 * s, 48 * s), (34 * s, 48 * s), (38 * s, 40 * s)], fill=255)
    elif nome == "nevoa":
        for y in (22, 32, 42, 52):
            d.line([(10 * s, y * s), (54 * s, y * s)], fill=255, width=4 * s)
    elif nome == "vento":
        for y, x1 in ((24, 46), (34, 52), (44, 40)):
            d.arc([(x1 - 14) * s, (y - 8) * s, (x1 + 4) * s, (y + 8) * s], 270, 90, fill=255, width=4 * s)
            d.line([(8 * s, y * s), ((x1 - 5) * s, y * s)], fill=255, width=4 * s)
    else:
        d.arc([16 * s, 12 * s, 48 * s, 44 * s], 200, 360, fill=255, width=5 * s)
        d.line([(48 * s, 28 * s), (32 * s, 44 * s)], fill=255, width=5 * s)
        d.ellipse([29 * s, 52 * s, 36 * s, 59 * s], fill=255)
    rgba = Image.new("RGBA", im.size, (255, 255, 255, 0))
    rgba.putalpha(im)
    return rgba.resize((64, 64), Image.LANCZOS)


# ------------------------------------------------------------------ XML
def _slot(nome: str, sid: int, x: int, y: int) -> str:
    g = GAUGE
    sec, txt, ac = "[CONFIGURATION.tema.2]", "[CONFIGURATION.tema.1]", "[CONFIGURATION.acento]"
    norm = ("(clamp([COMPLICATION.RANGED_VALUE_VALUE], [COMPLICATION.RANGED_VALUE_MIN], [COMPLICATION.RANGED_VALUE_MAX])"
            " - [COMPLICATION.RANGED_VALUE_MIN]) / ([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN])")
    trilho = (f'<Arc centerX="{g // 2}" centerY="{g // 2}" width="{g - 12}" height="{g - 12}" startAngle="-135" endAngle="135">'
              f'<Stroke thickness="7" color="[CONFIGURATION.tema.3]" cap="ROUND" /></Arc>')
    prog = (f'<Arc centerX="{g // 2}" centerY="{g // 2}" width="{g - 12}" height="{g - 12}" startAngle="-135" endAngle="135">'
            f'<Stroke thickness="7" color="{ac}" cap="ROUND" /><Transform target="endAngle" value="-135 + ({norm}) * 270" /></Arc>')
    cheio = (f'<Arc centerX="{g // 2}" centerY="{g // 2}" width="{g - 12}" height="{g - 12}" startAngle="-135" endAngle="135">'
             f'<Stroke thickness="7" color="{ac}" cap="ROUND" /></Arc>')

    def valor(cond: bool) -> str:
        return (texto(6, 24, g - 12, 34, 28, txt, "%s", ["[COMPLICATION.TEXT]"], "BOLD")
                + (texto(10, 58, g - 20, 18, 13, sec, "%s", ["[COMPLICATION.TITLE]"], "MEDIUM") if cond else ""))

    return f"""<ComplicationSlot name="{nome}" slotId="{sid}" x="{x}" y="{y}" width="{g}" height="{g}" displayName="slot_{nome}"
        supportedTypes="RANGED_VALUE SHORT_TEXT MONOCHROMATIC_IMAGE SMALL_IMAGE EMPTY" isCustomizable="TRUE">
      <BoundingOval x="0" y="0" width="{g}" height="{g}" />
      <DefaultProviderPolicy defaultSystemProvider="{PADROES[nome][0]}" defaultSystemProviderType="{PADROES[nome][1]}" />
      <Variant mode="AMBIENT" target="alpha" value="0" />
      <Complication type="RANGED_VALUE">
        <PartDraw x="0" y="0" width="{g}" height="{g}">{trilho}{prog}</PartDraw>
        {valor(True)}
      </Complication>
      <Complication type="SHORT_TEXT">
        <PartDraw x="0" y="0" width="{g}" height="{g}">{cheio}</PartDraw>
        {valor(True)}
      </Complication>
      <Complication type="MONOCHROMATIC_IMAGE">
        <PartDraw x="0" y="0" width="{g}" height="{g}">{cheio}</PartDraw>
        <PartImage x="{g // 2 - 22}" y="{g // 2 - 22}" width="44" height="44" tintColor="{ac}"><Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]" /></PartImage>
      </Complication>
      <Complication type="SMALL_IMAGE">
        <PartDraw x="0" y="0" width="{g}" height="{g}">{cheio}</PartDraw>
        <PartImage x="{g // 2 - 22}" y="{g // 2 - 22}" width="44" height="44"><Image resource="[COMPLICATION.SMALL_IMAGE]" /></PartImage>
      </Complication>
    </ComplicationSlot>"""


def _bmfont(nome: str, noite: bool) -> str:
    linhas = [f'      <Character name="{k}" resource="clima_{ICONE[k]}{"_n" if noite else ""}" width="64" height="64" />' for k in range(16)]
    return f'    <BitmapFont name="{nome}">\n' + "\n".join(linhas) + "\n    </BitmapFont>"


def gerar_xml() -> str:
    tx, sec, ac = "[CONFIGURATION.tema.1]", "[CONFIGURATION.tema.2]", "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = ['<?xml version="1.0" encoding="utf-8"?>', "<!-- GERADO por tools/gerar.py painel. Não edite à mão. -->",
         f'<WatchFace width="{W}" height="{W}" clipShape="CIRCLE">', '  <Metadata key="CLOCK_TYPE" value="DIGITAL" />',
         '  <Metadata key="PREVIEW_TIME" value="10:08:32" />', "  <BitmapFonts>", _bmfont("clima_dia", False), _bmfont("clima_noite", True),
         "  </BitmapFonts>", "  <UserConfigurations>", '    <ColorConfiguration id="tema" displayName="tema_label" defaultValue="escuro">']
    L += [f'      <ColorOption id="{i}" displayName="tema_{i}" colors="{c}" />' for i, c in TEMAS]
    L += ["    </ColorConfiguration>", '    <ColorConfiguration id="acento" displayName="acento_label" defaultValue="laranja">']
    L += [f'      <ColorOption id="{n}" displayName="acento_{n}" colors="{c}" />' for n, c in ACENTOS]
    L += ["    </ColorConfiguration>", '    <BooleanConfiguration id="segundos" displayName="segundos_label" defaultValue="TRUE" />',
          "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a(f'    <Group name="fundo" {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
      f'<PartDraw {full}><Rectangle x="0" y="0" width="{W}" height="{W}"><Fill color="[CONFIGURATION.tema.0]" /></Rectangle></PartDraw></Group>')
    a(f'    <BooleanConfiguration id="segundos"><BooleanOption id="TRUE"><Group name="arco_segundos" {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
      f'<PartDraw {full}><Arc centerX="{C}" centerY="{C}" width="456" height="456" startAngle="0" endAngle="360">'
      f'<Stroke thickness="4" color="[CONFIGURATION.tema.3]" cap="ROUND" /></Arc>'
      f'<Arc centerX="{C}" centerY="{C}" width="456" height="456" startAngle="0" endAngle="360">'
      f'<Stroke thickness="4" color="{ac}" cap="ROUND" /><Transform target="endAngle" value="[SECOND] * 6" /></Arc></PartDraw></Group></BooleanOption></BooleanConfiguration>')
    # data e clima
    a(f'    <Group name="data" {full}><Variant mode="AMBIENT" target="alpha" value="150" />')
    a("      " + texto(90, 44, 300, 30, 22, sec, "%s  %s  %s", ["[DAY_OF_WEEK_F]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a(f'    <Group name="clima" {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a('      <Condition><Expressions><Expression name="clima"><![CDATA[[WEATHER.IS_AVAILABLE] == 1]]></Expression>'
      '<Expression name="dia"><![CDATA[[WEATHER.IS_DAY] == 1]]></Expression></Expressions><Compare expression="clima">')
    a(f'        <Group name="clima_dados" {full}>')
    a(f'          <Condition><Expressions><Expression name="dia"><![CDATA[[WEATHER.IS_DAY] == 1]]></Expression></Expressions>'
      f'<Compare expression="dia"><PartText x="128" y="80" width="60" height="60" tintColor="{ac}"><Text align="CENTER"><BitmapFont family="clima_dia" size="60">'
      f'<Template><![CDATA[%s]]><Parameter expression="[WEATHER.CONDITION]" /></Template></BitmapFont></Text></PartText></Compare>'
      f'<Default><PartText x="128" y="80" width="60" height="60" tintColor="{ac}"><Text align="CENTER"><BitmapFont family="clima_noite" size="60">'
      f'<Template><![CDATA[%s]]><Parameter expression="[WEATHER.CONDITION]" /></Template></BitmapFont></Text></PartText></Default></Condition>')
    a("          " + texto(192, 78, 80, 56, 44, tx, "%s°", ["[WEATHER.TEMPERATURE]"], "BOLD", "START"))
    a("          " + texto(276, 84, 100, 22, 17, sec, "máx %s°", ["[WEATHER.DAY_TEMPERATURE_HIGH]"], "MEDIUM", "START"))
    a("          " + texto(276, 108, 100, 22, 17, sec, "mín %s°", ["[WEATHER.DAY_TEMPERATURE_LOW]"], "MEDIUM", "START"))
    a("        </Group></Compare></Condition>")
    a("    </Group>")
    # hora
    a(f'    <DigitalClock x="0" y="136" width="{W}" height="150"><Variant mode="AMBIENT" target="alpha" value="0" />'
      f'<TimeText x="0" y="0" width="{W}" height="150" format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER">'
      f'<Font family="SYNC_TO_DEVICE" size="128" weight="BOLD" color="{tx}" /></TimeText></DigitalClock>')
    a(f'    <DigitalClock x="0" y="150" width="{W}" height="150" alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />'
      f'<TimeText x="0" y="0" width="{W}" height="150" format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER">'
      '<Font family="SYNC_TO_DEVICE" size="112" weight="LIGHT" color="#ffc8c8ce" /></TimeText></DigitalClock>')
    for sid, (nome, (x, y)) in enumerate(GAUGES.items()):
        a("    " + _slot(nome, sid, x, y))
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ prévia
def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")[-6:]
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def previa(tema: int, acento: str, h: int, mi: int, s: int, ambiente_: bool = False, noite: bool = False) -> Image.Image:
    paleta = TEMAS[tema][1].split()
    bg, tx, sec = _hex(paleta[0]), _hex(paleta[1]), _hex(paleta[2])
    capa = int(paleta[3][1:3], 16)
    cap = _hex(paleta[3])
    ac = _hex(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255) if ambiente_ else bg + (255,))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 210), f"{h:02d}:{mi:02d}", font=fonte("Light", 112), fill=(200, 200, 206), anchor="mm")
        d.text((C, 78), "SEXTA-FEIRA  31  OUT", font=fonte("Medium", 20), fill=tuple(int(v * 0.6) for v in sec), anchor="mm")
    else:
        lay = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        dl.ellipse([C - 228, C - 228, C + 228, C + 228], outline=cap + (capa,), width=4)
        dl.arc([C - 228, C - 228, C + 228, C + 228], -90, -90 + s * 6, fill=ac + (255,), width=4)
        base.alpha_composite(lay)
        d = ImageDraw.Draw(base)
        d.text((C, 58), "SEXTA-FEIRA  31  OUT", font=fonte("Medium", 22), fill=sec, anchor="mm")
        ic = _icone("parcial" if not noite else "sol", noite)
        r, g, b, a = ic.split()
        ic = Image.merge("RGBA", (r.point(lambda v: v * ac[0] // 255), g.point(lambda v: v * ac[1] // 255), b.point(lambda v: v * ac[2] // 255), a))
        base.alpha_composite(ic, (128, 80))
        d.text((192, 108), "24°", font=fonte("Bold", 44), fill=tx, anchor="lm")
        d.text((276, 95), "máx 28°", font=fonte("Medium", 17), fill=sec, anchor="lm")
        d.text((276, 119), "mín 19°", font=fonte("Medium", 17), fill=sec, anchor="lm")
        d.text((C, 210), f"{h:02d}:{mi:02d}", font=fonte("Bold", 128), fill=tx, anchor="mm")
        for (nome, (x, y)), frac, valor, titulo in zip(GAUGES.items(), (0.62, None, 0.76), ("6,2k", "72", "76%"), ("PASSOS", "BPM", "BATERIA")):
            box = [x + 6, y + 6, x + GAUGE - 6, y + GAUGE - 6]
            d.arc(box, 90 + 45, 90 + 45 + 270, fill=cap + (255,) if False else tuple(int(bg[i] + (cap[i] - bg[i]) * capa / 255) for i in range(3)), width=7)
            d.arc(box, 90 + 45, 90 + 45 + (270 * frac if frac else 270), fill=ac, width=7)
            d.text((x + GAUGE / 2, y + 42), valor, font=fonte("Bold", 28), fill=tx, anchor="mm")
            d.text((x + GAUGE / 2, y + 68), titulo, font=fonte("Medium", 13), fill=sec, anchor="mm")
    mk = Image.new("L", (W * 4, W * 4), 0)
    ImageDraw.Draw(mk).ellipse([0, 0, W * 4 - 1, W * 4 - 1], fill=255)
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    out.paste(base, (0, 0), mk.resize((W, W), Image.LANCZOS))
    return out


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Dashboard", "tema_label": "Theme", "tema_escuro": "Dark", "tema_claro": "Light", "tema_azul": "Deep blue",
          "tema_floresta": "Forest", "acento_label": "Accent color", "acento_laranja": "Orange", "acento_ciano": "Cyan",
          "acento_verde": "Green", "acento_rosa": "Pink", "acento_amarelo": "Yellow", "segundos_label": "Seconds ring",
          "slot_esq": "Left gauge", "slot_meio": "Center gauge", "slot_dir": "Right gauge"}
    pt = {"watch_face_name": "Painel", "tema_label": "Tema", "tema_escuro": "Escuro", "tema_claro": "Claro", "tema_azul": "Azul profundo",
          "tema_floresta": "Floresta", "acento_label": "Cor de destaque", "acento_laranja": "Laranja", "acento_ciano": "Ciano",
          "acento_verde": "Verde", "acento_rosa": "Rosa", "acento_amarelo": "Amarelo", "segundos_label": "Anel dos segundos",
          "slot_esq": "Mostrador esquerdo", "slot_meio": "Mostrador central", "slot_dir": "Mostrador direito"}
    res = criar_modulo(raiz, NOME, en, pt, flavors=False)
    dr = res / "drawable-nodpi"
    for k, nome in ICONE.items():
        for noite in (False, True):
            _icone(nome, noite).save(dr / f"clima_{nome}{'_n' if noite else ''}.png", optimize=True)
    (res / "raw" / "watchface.xml").write_text(nomear_grupos(gerar_xml()), encoding="utf-8")
    pv = raiz / "previews"
    pv.mkdir(exist_ok=True)
    imgs = [previa(0, "#ff8a3d", 10, 8, 32), previa(1, "#33d6ff", 10, 8, 32), previa(2, "#ff5c93", 22, 41, 45, noite=True),
            previa(3, "#4be37a", 7, 15, 12), previa(0, "#ff8a3d", 10, 8, 0, True), previa(1, "#33d6ff", 10, 8, 0, True)]
    for nome, im in zip(["escuro_laranja", "claro_ciano", "azul_rosa_noite", "floresta_verde", "ambiente"], imgs[:5]):
        im.save(pv / f"painel_{nome}.png", optimize=True)
    imgs[0].resize((450, 450), Image.LANCZOS).save(dr / "preview.png", optimize=True)
    from faces.cronos_previa import folha
    folha(imgs[:5], ["Escuro + laranja", "Claro + ciano", "Azul + rosa (noite)", "Floresta + verde", "Ambiente (AOD)"], cols=3).save(pv / "painel_folha.png", optimize=True)
    return {"xml_bytes": len(gerar_xml())}
