"""Watchface "Matriz": abstrata e retrô-futurista. Hora e minuto empilhados em pontos de LED, quatro segmentos de anel
(passos, dia, segundos, bateria) e duas linhas de dados. Dez cores de destaque.
Inspirada em relógios de "matriz de pontos". Fonte de pontos 5x7 desenhada à mão (original)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.kit import C, W, cabecalho, cor_config, finalizar, redondo, rgb, strings_opcoes, tint
from wf.matriz_fonte import GLIFOS, glifo, tamanho

NOME = "matriz"
ACENTOS = [("laranja", "#ff7a2f"), ("vermelho", "#ff4040"), ("ambar", "#ffb300"), ("lima", "#c6ff33"), ("verde", "#3dff8b"),
           ("ciano", "#2de2ff"), ("azul", "#4d8dff"), ("violeta", "#a07bff"), ("rosa", "#ff5fa8"), ("branco", "#f0f0f0")]
GRANDE = dict(passo=13, raio=4.9, pad=6, apagado=0.12, halo=True)
MEDIA = dict(passo=9, raio=3.2, pad=3, apagado=0.0, halo=False)
PEQ = dict(passo=4.0, raio=1.45, pad=2, apagado=0.0, halo=False)
CHARS_P = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ:./%°-+, "


def fonte_png(prefixo: str, chars: str, p: dict) -> tuple[dict[str, Image.Image], dict[str, tuple[str, int, int]]]:
    imgs, mapa = {}, {}
    for ch in chars:
        if ch == " ":
            continue
        im = glifo(ch, p["passo"], p["raio"], p["pad"], p["apagado"], p["halo"])
        nome = f"{prefixo}_{ord(ch):x}"
        imgs[nome] = im
        mapa[ch] = (nome, im.width, im.height)
    return imgs, mapa


def bmfont(nome: str, mapa: dict, minusc: bool) -> str:
    usados = dict(mapa)
    if minusc:
        for c in "abcdefghijklmnopqrstuvwxyz":
            usados[c] = mapa[c.upper()]
        for c, b in (("á", "A"), ("ã", "A"), ("â", "A"), ("é", "E"), ("ê", "E"), ("í", "I"), ("ó", "O"), ("ô", "O"), ("ú", "U"), ("ç", "C")):
            usados[c] = mapa[b]
    linhas = [f'      <Character name="{ {"&": "&amp;", "<": "&lt;"}.get(c, c) }" resource="{r}" width="{w}" height="{h}" />' for c, (r, w, h) in usados.items()]
    return f'    <BitmapFont name="{nome}">\n' + "\n".join(linhas) + "\n    </BitmapFont>"


def bm_texto(x, y, w, h, fam: str, tam: int, fmt: str, params: list[str], align="CENTER") -> str:
    ps = "".join(f'<Parameter expression="{p}" />' for p in params)
    return (f'<PartText x="{x}" y="{y}" width="{w}" height="{h}"><Text align="{align}"><BitmapFont family="{fam}" size="{tam}">'
            f'<Template><![CDATA[{fmt}]]>{ps}</Template></BitmapFont></Text></PartText>')


def bm_hora(x, y, w, h, fmt: str, fam: str, tam: int, align="CENTER") -> str:
    return (f'<DigitalClock x="{x}" y="{y}" width="{w}" height="{h}"><TimeText x="0" y="0" width="{w}" height="{h}" format="{fmt}" '
            f'hourFormat="SYNC_TO_DEVICE" align="{align}"><BitmapFont family="{fam}" size="{tam}" /></TimeText></DigitalClock>')


def arco(r: int, ini: float, fim: float, esp: int, cor: str, expr: str | None = None) -> str:
    t = f'<Transform target="endAngle" value="{expr}" />' if expr else ""
    return (f'<Arc centerX="{C}" centerY="{C}" width="{2 * r}" height="{2 * r}" startAngle="{ini}" endAngle="{fim}">'
            f'<Stroke thickness="{esp}" color="{cor}" cap="ROUND" />{t}</Arc>')


def ys(gh: int, ph: int) -> dict[str, int]:
    t = 56
    return {"temp": t, "data": t + ph + 2, "h": t + 2 * ph + 12, "m": t + 2 * ph + 12 + gh + 4,
            "l1": t + 2 * ph + 12 + 2 * gh + 18, "l2": t + 2 * ph + 12 + 2 * gh + 18 + ph + 4}


# segmentos de anel: (início, fim) em graus, 0 = 12h
SEG = {"passos": (-50, 50), "dia": (255, 285), "seg": (132, 228), "bateria": (75, 105)}


def xml(gh: int, ph: int, mh: int) -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    ac = "[CONFIGURATION.acento]"
    dim = "#33808080"
    R = 218
    L = cabecalho(NOME, "DIGITAL") + ["  <BitmapFonts>", "@@FONTES@@", "  </BitmapFonts>", "  <UserConfigurations>",
                                       cor_config("acento", "acento_label", ACENTOS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a(f'    <Group name="vivo" {full} tintColor="{ac}"><Variant mode="AMBIENT" target="alpha" value="0" />')
    a(f'      <PartDraw {full}>' + arco(R, *SEG["passos"], 12, dim) + arco(R, SEG["passos"][0], SEG["passos"][1], 12, "#ffffffff",
        f"{SEG['passos'][0]} + {SEG['passos'][1] - SEG['passos'][0]} * clamp([STEP_PERCENT], 0, 100) / 100") + "</PartDraw>")
    a(f'      <PartDraw {full}>' + arco(R, *SEG["dia"], 12, dim) + arco(R, SEG["dia"][0], SEG["dia"][1], 12, "#ffffffff",
        f"{SEG['dia'][0]} + {SEG['dia'][1] - SEG['dia'][0]} * [SECONDS_IN_DAY] / 86400") + "</PartDraw>")
    a(f'      <PartDraw {full}>' + arco(R, *SEG["seg"], 12, dim) + arco(R, SEG["seg"][0], SEG["seg"][1], 12, "#ffffffff",
        f"{SEG['seg'][0]} + {SEG['seg'][1] - SEG['seg'][0]} * [SECOND] / 60") + "</PartDraw>")
    a(f'      <PartDraw {full}>' + arco(R, *SEG["bateria"], 12, dim) + arco(R, SEG["bateria"][0], SEG["bateria"][1], 12, "#ffffffff",
        f"{SEG['bateria'][0]} + {SEG['bateria'][1] - SEG['bateria'][0]} * clamp([BATTERY_PERCENT], 0, 100) / 100") + "</PartDraw>")
    Y = ys(gh, ph)
    a("      " + bm_texto(120, Y["temp"], 240, ph, "pequena", ph, "%s°", ["[WEATHER.TEMPERATURE]"]))
    a("      " + bm_texto(80, Y["data"], 320, ph, "pequena", ph, "%s %s", ["[MONTH_S]", "[DAY]"]))
    a("      " + bm_hora(90, Y["h"], 300, gh, "hh", "grande", gh))
    a("      " + bm_hora(90, Y["m"], 300, gh, "mm", "grande", gh))
    a("      " + bm_texto(60, Y["l1"], 360, ph, "pequena", ph, "%s  %s", ["[DAY_OF_WEEK_S]", "[STEP_COUNT]"]))
    a("      " + bm_texto(60, Y["l2"], 360, ph, "pequena", ph, "%s%%", ["round([BATTERY_PERCENT])"]))
    a("    </Group>")
    a(f'    <Group name="ambiente" {full} alpha="0" tintColor="{ac}"><Variant mode="AMBIENT" target="alpha" value="255" />')
    a("      " + bm_hora(120, 150, 240, mh, "hh", "media", mh))
    a("      " + bm_hora(120, 150 + mh + 6, 240, mh, "mm", "media", mh))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(F: dict, dims: dict, acento: str, h: int, mi: int, ambiente_: bool = False, passos=0.62, bat=0.89, dia=0.44, seg=0.5) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    ac = rgb(acento)
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))

    def texto(pref: str, txt: str, y: int, largura: int = W):
        ims = [F[f"{pref}_{ord(c):x}"] for c in txt if c != " "]
        esp = 0 if pref != "pequena" else 0
        tot = sum(i.width for i in ims) + (len(txt) - len(ims)) * ims[0].width // 2
        x = C - tot // 2
        for c in txt:
            if c == " ":
                x += F[f"{pref}_{ord('0'):x}"].width // 2
                continue
            i = F[f"{pref}_{ord(c):x}"]
            cam.alpha_composite(i, (x, y))
            x += i.width

    if ambiente_:
        texto("media", f"{h:02d}", 150)
        texto("media", f"{mi:02d}", 150 + dims["media"] + 6)
        r, g, b, a = cam.split()
        base.alpha_composite(tint(cam, ac))
        return redondo(base)
    d = ImageDraw.Draw(cam)
    R = 218
    for key, frac in (("passos", passos), ("dia", dia), ("seg", seg), ("bateria", bat)):
        i0, i1 = SEG[key]
        box = [C - R, C - R, C + R, C + R]
        d.arc(box, i0 - 90, i1 - 90, fill=(128, 128, 128, 51), width=12)
        d.arc(box, i0 - 90, i0 - 90 + (i1 - i0) * frac, fill=(255, 255, 255, 255), width=12)
    Y = ys(dims["grande"], dims["pequena"])
    texto("pequena", "28°", Y["temp"])
    texto("pequena", "OUT 31", Y["data"])
    texto("grande", f"{h:02d}", Y["h"])
    texto("grande", f"{mi:02d}", Y["m"])
    texto("pequena", "SEX 6234", Y["l1"])
    texto("pequena", f"{int(bat * 100)}%", Y["l2"])
    base.alpha_composite(tint(cam, ac))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Matrix", "acento_label": "Accent color"}
    pt = {"watch_face_name": "Matriz", "acento_label": "Cor de destaque"}
    strings_opcoes(en, pt, "acento", {"laranja": ("Orange", "Laranja"), "vermelho": ("Red", "Vermelho"), "ambar": ("Amber", "Âmbar"),
                                       "lima": ("Lime", "Lima"), "verde": ("Green", "Verde"), "ciano": ("Cyan", "Ciano"),
                                       "azul": ("Blue", "Azul"), "violeta": ("Violet", "Violeta"), "rosa": ("Pink", "Rosa"), "branco": ("White", "Branco")})
    A: dict[str, Image.Image] = {}
    mapas = {}
    for pref, chars, p in (("grande", "0123456789", GRANDE), ("media", "0123456789", MEDIA), ("pequena", CHARS_P, PEQ)):
        imgs, mapa = fonte_png(pref, chars, p)
        A.update(imgs)
        mapas[pref] = mapa
    dims = {k: next(iter(m.values()))[2] for k, m in mapas.items()}
    fontes = "\n".join([bmfont("grande", mapas["grande"], False), bmfont("media", mapas["media"], False), bmfont("pequena", mapas["pequena"], True)])
    xm = xml(dims["grande"], dims["pequena"], dims["media"]).replace("@@FONTES@@", fontes)
    pv = [previa(A, dims, "#ff7a2f", 10, 34), previa(A, dims, "#2de2ff", 7, 5, passos=0.9, bat=0.3), previa(A, dims, "#c6ff33", 23, 58, dia=0.99),
          previa(A, dims, "#ff7a2f", 10, 34, True)]
    return finalizar(raiz, NOME, en, pt, xm, A, pv, ["Laranja", "Ciano", "Lima", "Ambiente (AOD)"], cols=4, nomes_previa=["laranja", "ciano", "lima", "ambiente"])
