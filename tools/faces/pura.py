"""Watchface "Pura": o mais minimalista da coleção. Analógica sem algarismos, só traços e ponteiros dauphine finos,
data discreta no 6h e segundo ponteiro com uma bolinha de cor. Paleta por ColorConfiguration (fundo, tinta, secundário).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, polar, reduzir_por, tela
from wf.modulo import criar_modulo, nomear_grupos, texto

NOME = "pura"
W = 480
C = 240
TEMAS = [("marfim", "#fff4efe6 #ff1c1a17 #ff8a8378"), ("ardosia", "#ff1d2227 #fff2f4f6 #ff8b97a3"),
         ("preto", "#ff000000 #fff6f6f6 #ff8e8e93"), ("areia", "#ffd9cdb8 #ff2b2418 #ff7d705a")]
ACENTOS = [("terracota", "#d9623b"), ("azul", "#3d7bd9"), ("verde", "#3f9d6b"), ("ouro", "#c99a2e"), ("grafite", "#4a4a4f")]


def _marcas() -> Image.Image:
    n = W * SS
    c = n / 2
    img = tela(n)
    d = ImageDraw.Draw(img)
    for h in range(12):
        a = h * 30
        cardeal = h % 3 == 0
        r0, r1, esp = (176, 214, 5) if cardeal else (194, 214, 3)
        d.line([polar(c, c, r0 * SS, a), polar(c, c, r1 * SS, a)], fill=(255, 255, 255, 255), width=int(esp * SS))
    return reduzir_por(img)


def _dauphine(comp: float, cauda: float, larg: float) -> tuple[Image.Image, float]:
    s = 4
    pad = 4
    w, h = int(larg) + 2 * pad, int(comp + cauda) + 2 * pad
    w += w % 2
    img = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w * s / 2
    hw = larg / 2 * s
    py = (pad + comp) * s
    pts = [(cx, pad * s), (cx + hw, (pad + comp * 0.55) * s), (cx + hw * 0.42, py + cauda * s), (cx - hw * 0.42, py + cauda * s), (cx - hw, (pad + comp * 0.55) * s)]
    d.polygon(pts, fill=(255, 255, 255, 255))
    d.polygon([pts[0], pts[1], pts[2], (cx, py + cauda * s), (cx, pad * s)], fill=(214, 214, 214, 255))     # faceta à direita
    return img.resize((w, h), Image.LANCZOS), pad + comp


def _seg() -> tuple[Image.Image, float]:
    s = 4
    pad, comp, cauda = 4, 208, 40
    w, h = 20, int(comp + cauda) + 2 * pad
    img = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, py = w * s / 2, (pad + comp) * s
    d.rectangle([cx - 0.9 * s, (pad + 22) * s, cx + 0.9 * s, py + cauda * s], fill=(255, 255, 255, 255))
    d.ellipse([cx - 7 * s, (pad + 14) * s, cx + 7 * s, (pad + 28) * s], fill=(255, 255, 255, 255))
    d.ellipse([cx - 4.5 * s, py - 4.5 * s, cx + 4.5 * s, py + 4.5 * s], fill=(255, 255, 255, 255))
    return img.resize((w, h), Image.LANCZOS), pad + comp


def _mao_xml(tipo, nome, m, extra="", filhos=""):
    w, h, py = m[nome]
    t = f'<{tipo} resource="{nome}" x="{C - w // 2}" y="{round(C - py)}" width="{w}" height="{h}" pivotX="0.5" pivotY="{py / h:.6f}"{extra}'
    return f"{t}>{filhos}</{tipo}>" if filhos else t + " />"


def gerar_xml(m: dict) -> str:
    tx, sec, ac = "[CONFIGURATION.tema.1]", "[CONFIGURATION.tema.2]", "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = ['<?xml version="1.0" encoding="utf-8"?>', "<!-- GERADO por tools/gerar.py pura. Não edite à mão. -->",
         f'<WatchFace width="{W}" height="{W}" clipShape="CIRCLE">', '  <Metadata key="CLOCK_TYPE" value="ANALOG" />',
         '  <Metadata key="PREVIEW_TIME" value="10:08:32" />', "  <UserConfigurations>",
         '    <ColorConfiguration id="tema" displayName="tema_label" defaultValue="marfim">']
    L += [f'      <ColorOption id="{i}" displayName="tema_{i}" colors="{c}" />' for i, c in TEMAS]
    L += ["    </ColorConfiguration>", '    <ColorConfiguration id="acento" displayName="acento_label" defaultValue="terracota">']
    L += [f'      <ColorOption id="{n}" displayName="acento_{n}" colors="{c}" />' for n, c in ACENTOS]
    L += ["    </ColorConfiguration>", '    <BooleanConfiguration id="data" displayName="data_label" defaultValue="TRUE" />',
          "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a(f'    <Group name="fundo" {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
      f'<PartDraw {full}><Rectangle x="0" y="0" width="{W}" height="{W}"><Fill color="[CONFIGURATION.tema.0]" /></Rectangle></PartDraw></Group>')
    a(f'    <PartImage {full} tintColor="{sec}"><Variant mode="AMBIENT" target="alpha" value="110" /><Image resource="marcas" /></PartImage>')
    a(f'    <BooleanConfiguration id="data"><BooleanOption id="TRUE"><Group name="data" {full}><Variant mode="AMBIENT" target="alpha" value="0" />'
      + texto(190, 330, 100, 28, 20, sec, "%s", ["[DAY_Z]"], "MEDIUM") + "</Group></BooleanOption></BooleanConfiguration>")
    a(f'    <AnalogClock {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a("      " + _mao_xml("HourHand", "hora", m, f' tintColor="{tx}"'))
    a("      " + _mao_xml("MinuteHand", "min", m, f' tintColor="{tx}"'))
    a("      " + _mao_xml("SecondHand", "seg", m, f' tintColor="{ac}"', '<Sweep frequency="10" />'))
    a("    </AnalogClock>")
    a(f'    <AnalogClock {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />')
    a("      " + _mao_xml("HourHand", "hora", m, ' tintColor="#ffd2d2d6"'))
    a("      " + _mao_xml("MinuteHand", "min", m, ' tintColor="#ffd2d2d6"'))
    a("    </AnalogClock>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def _hex(h):
    h = h.lstrip("#")[-6:]
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _tint(im, cor):
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r.point(lambda v: v * cor[0] // 255), g.point(lambda v: v * cor[1] // 255), b.point(lambda v: v * cor[2] // 255), a))


def previa(A, tema: int, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    bg, tx, sec = (_hex(c) for c in TEMAS[tema][1].split())
    ac = _hex(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255) if ambiente_ else bg + (255,))
    ang = [("hora", (h % 12) * 30 + mi * 0.5), ("min", mi * 6 + s * 0.1)]
    if not ambiente_:
        base.alpha_composite(_tint(A["marcas"], sec))
        ImageDraw.Draw(base).text((C, 344), "31", font=fonte("Medium", 20), fill=sec, anchor="mm")
        ang.append(("seg", s * 6))
    else:
        mk = _tint(A["marcas"], (110, 110, 114))
        base.alpha_composite(mk)
    for nome, an in ang:
        im, py = A[nome]
        cor = ac if nome == "seg" else ((210, 210, 214) if ambiente_ else tx)
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        cam.alpha_composite(_tint(im, cor), (int(C - im.width / 2), int(round(C - py))))
        base.alpha_composite(cam.rotate(-an, center=(C, C), resample=Image.BICUBIC))
    mk = Image.new("L", (W * 4, W * 4), 0)
    ImageDraw.Draw(mk).ellipse([0, 0, W * 4 - 1, W * 4 - 1], fill=255)
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    out.paste(base, (0, 0), mk.resize((W, W), Image.LANCZOS))
    return out


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Pure", "tema_label": "Theme", "acento_label": "Accent color", "data_label": "Show date",
          "tema_marfim": "Ivory", "tema_ardosia": "Slate", "tema_preto": "Black", "tema_areia": "Sand",
          "acento_terracota": "Terracotta", "acento_azul": "Blue", "acento_verde": "Green", "acento_ouro": "Gold", "acento_grafite": "Graphite"}
    pt = {"watch_face_name": "Pura", "tema_label": "Tema", "acento_label": "Cor de destaque", "data_label": "Mostrar data",
          "tema_marfim": "Marfim", "tema_ardosia": "Ardósia", "tema_preto": "Preto", "tema_areia": "Areia",
          "acento_terracota": "Terracota", "acento_azul": "Azul", "acento_verde": "Verde", "acento_ouro": "Ouro", "acento_grafite": "Grafite"}
    res = criar_modulo(raiz, NOME, en, pt, flavors=False)
    dr = res / "drawable-nodpi"
    A = {"marcas": _marcas(), "hora": _dauphine(120, 22, 24), "min": _dauphine(186, 26, 18), "seg": _seg()}
    med = {}
    for n, v in A.items():
        im, py = v if isinstance(v, tuple) else (v, 0.0)
        im.save(dr / f"{n}.png", optimize=True)
        med[n] = (im.width, im.height, py)
    (res / "raw" / "watchface.xml").write_text(nomear_grupos(gerar_xml(med)), encoding="utf-8")
    pv = raiz / "previews"
    pv.mkdir(exist_ok=True)
    imgs = [previa(A, 0, "#d9623b", 10, 8, 32), previa(A, 1, "#3d7bd9", 7, 35, 14), previa(A, 2, "#c99a2e", 2, 50, 48),
            previa(A, 3, "#3f9d6b", 10, 8, 20), previa(A, 2, "#c99a2e", 10, 8, 0, True)]
    for nome, im in zip(["marfim", "ardosia", "preto", "areia", "ambiente"], imgs):
        im.save(pv / f"pura_{nome}.png", optimize=True)
    imgs[0].resize((450, 450), Image.LANCZOS).save(dr / "preview.png", optimize=True)
    from faces.cronos_previa import folha
    folha(imgs, ["Marfim + terracota", "Ardósia + azul", "Preto + ouro", "Areia + verde", "Ambiente (AOD)"], cols=3).save(pv / "pura_folha.png", optimize=True)
    return {"xml_bytes": len(gerar_xml(med))}
