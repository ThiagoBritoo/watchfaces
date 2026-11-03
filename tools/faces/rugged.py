"""Watchface "Rugged": relógio de resistência. Borracha escura com parafusos, anel de segundos que enche com
o ritmo do relógio (e serrilha por cima), tela LCD positiva cinza-esverdeada com hora enorme em 7 segmentos,
dias da semana com o atual sublinhado, data, bateria e barra de 20 segmentos de passos. Sete cores de destaque."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from wf.desenho import SS, reduzir_por
from wf.hud import Cena, Tela, digitos_lcd, fonte_texto, redondo, sombra_interna, xml_bitmapfont
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, rgb, strings_opcoes

NOME = "rugged"
CORES = [("laranja", "#fffe7a12"), ("ciano", "#ff1fd6f2"), ("amarelo", "#ffeedc1c"), ("verde", "#ff3be26b"), ("vermelho", "#fffb3b3b"),
         ("branco", "#fff2f2f2"), ("rosa", "#ffff5fa8")]
NOMES = {"laranja": ("Orange", "Laranja"), "ciano": ("Cyan", "Ciano"), "amarelo": ("Yellow", "Amarelo"), "verde": ("Green", "Verde"),
         "vermelho": ("Red", "Vermelho"), "branco": ("White", "Branco"), "rosa": ("Pink", "Rosa")}
TINTA = "#ff12160e"
GR = dict(w=46, h=88, e=11, pad=3)
PQ = dict(w=20, h=36, e=5, pad=2)
PX0, PY0, PX1, PY1 = 70, 140, 410, 340
DIAS = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"]


def _fundo() -> Image.Image:
    t = Tela()
    t.elipse(C, C, 240, cor=(8, 8, 9, 255))
    t.elipse(C, C, 238, contorno=(54, 55, 58, 255), esp=2)
    t.elipse(C, C, 206, cor=(14, 14, 15, 255), contorno=(48, 49, 52, 255), esp=2)
    for k in range(60):                                           # ranhuras da borracha
        a = math.radians(k * 6 + 3)
        t.linha([(C + 207 * math.sin(a), C - 207 * math.cos(a)), (C + 214 * math.sin(a), C - 214 * math.cos(a))], (30, 31, 33, 255), 2)
    for ang in (45, 135, 225, 315):                               # parafusos
        a = math.radians(ang)
        cx, cy = C + 188 * math.sin(a), C - 188 * math.cos(a)
        t.elipse(cx, cy, 8, cor=(88, 90, 96, 255), contorno=(36, 37, 40, 255), esp=1.5)
        t.linha([(cx - 5 * math.cos(a), cy - 5 * math.sin(a)), (cx + 5 * math.cos(a), cy + 5 * math.sin(a))], (30, 31, 34, 255), 2)
    return t.pronto()


def _lcd() -> Image.Image:
    n = W * SS
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).rounded_rectangle([PX0 * SS, PY0 * SS, PX1 * SS, PY1 * SS], radius=24 * SS, fill=255)
    yy = np.arange(n, dtype=np.float32)[:, None] / SS
    g = np.clip((yy - PY0) / (PY1 - PY0), 0, 1)
    r = 196 - 28 * g
    rng = np.random.default_rng(3)
    gr = rng.normal(0, 3.0, (W, W)).repeat(SS, 0).repeat(SS, 1)
    base = np.stack([r * 0.97 + gr, r * 1.02 + gr, r * 0.88 + gr], -1) * np.ones((1, n, 1), np.float32)
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    interior = m.filter(ImageFilter.MinFilter(9 * SS * 2 + 1))
    # moldura escura (bisel) e filete claro
    moldura = ImageChops.subtract(m, m.filter(ImageFilter.MinFilter(5 * SS * 2 + 1)))
    arr = np.asarray(im).copy()
    arr[np.asarray(moldura) > 0] = (22, 24, 22, 255)
    im = Image.fromarray(arr, "RGBA")
    im.putalpha(m)
    im = reduzir_por(im)
    im = sombra_interna(im, 7, 0.55, 3)
    # reflexo diagonal sutil no canto superior esquerdo
    brilho = Tela()
    brilho.poly([(PX0 + 6, PY0 + 6), (PX0 + 150, PY0 + 6), (PX0 + 6, PY0 + 110)], (255, 255, 255, 26))
    b = brilho.pronto()
    b.putalpha(ImageChops.multiply(b.getchannel("A"), im.getchannel("A")))
    im.alpha_composite(b)
    return im


def _trilha() -> Image.Image:
    t = Tela()
    t.arco(C, C, 224, 0, 359.9, (255, 255, 255, 255), 14)
    return t.pronto()


def _serrilha() -> Image.Image:
    t = Tela()
    for k in range(60):
        a = math.radians(k * 6)
        t.linha([(C + 214 * math.sin(a), C - 214 * math.cos(a)), (C + 236 * math.sin(a), C - 236 * math.cos(a))], (8, 8, 9, 255), 3.2)
    return t.pronto()


def _marcas() -> Image.Image:
    """Quatro marcas grandes (12/3/6/9) e traços finos sobre a borracha, na cor de destaque."""
    t = Tela()
    for k in range(12):
        a = math.radians(k * 30)
        r0, r1, esp = (190, 202, 4) if k % 3 == 0 else (194, 201, 2)
        t.linha([(C + r0 * math.sin(a), C - r0 * math.cos(a)), (C + r1 * math.sin(a), C - r1 * math.cos(a))], (255, 255, 255, 255), esp)
    return t.pronto()


def _sublinhado() -> Image.Image:
    t = Tela()
    t.retangulo(0, 0, 34, 3, (255, 255, 255, 255), 1)
    return t.pronto()


def _icone_bateria() -> Image.Image:
    t = Tela()
    t.retangulo(0, 3, 30, 19, (255, 255, 255, 255), 3)
    t.retangulo(30, 7, 34, 15, (255, 255, 255, 255), 1)
    t.d.rounded_rectangle([3 * SS, 6 * SS, 27 * SS, 16 * SS], radius=1 * SS, fill=(0, 0, 0, 0))
    t.d.rectangle([3 * SS, 6 * SS, 27 * SS, 16 * SS], fill=(0, 0, 0, 0))
    for k in range(4):
        t.d.rectangle([(4 + k * 6) * SS, 7 * SS, (8 + k * 6) * SS, 15 * SS], fill=(255, 255, 255, 255))
    im = reduzir_por(t.im.crop((0, 0, 40 * SS, 24 * SS)).resize((40 * SS, 24 * SS)))
    return im.crop((0, 0, 36, 22))


def assets():
    A = {"fundo": _fundo(), "lcd": _lcd(), "trilha": _trilha(), "serrilha": _serrilha(), "marcas": _marcas(), "sublinhado": _sublinhado(),
         "bateria": _icone_bateria()}
    fam = {}
    for nome, h in (("t12", 12), ("t14", 14), ("t20", 20)):
        i, m = fonte_texto(nome, h)
        A.update(i)
        fam[nome] = m
    i, m = digitos_lcd("g", **GR, colon=20, fantasma=0.085)
    A.update(i)
    fam["grande"] = m
    i, m = digitos_lcd("p", **PQ, colon=8, fantasma=0.085)
    A.update(i)
    fam["peq"] = m
    return A, fam


def _arco_xml() -> str:
    return (f'    <PartDraw x="0" y="0" width="{W}" height="{W}"><Arc centerX="{C}" centerY="{C}" width="448" height="448" startAngle="0" endAngle="0">'
            '<Stroke thickness="14" color="[CONFIGURATION.cor.0]" cap="BUTT" /><Transform target="endAngle" value="[SECOND] * 6" /></Arc></PartDraw>')


def _arco_prev(seg: int):
    def f(base: Image.Image, pal) -> None:
        n = W * SS
        cam = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        ImageDraw.Draw(cam).arc([(C - 224) * SS, (C - 224) * SS, (C + 224) * SS, (C + 224) * SS], -90, -90 + seg * 6, fill=pal["@cor"] + (255,), width=14 * SS)
        base.alpha_composite(reduzir_por(cam))
    return f


def cena(A, fam, ambiente=False, seg=30, bat=100, passos=3457, pct=54, dia=6) -> Cena:
    c = Cena(fam, A)
    if ambiente:
        c.img("lcd", "#ff3a3a3e")
        c.hora("grande", 96, 176, 236, "hh:mm", "10:08", "#ffd2d2d6")
        return c
    c.img("fundo", "#ffffffff")
    c.img("trilha", "@cor", extra="", alfa=55)
    c.cru(_arco_xml(), _arco_prev(seg))
    c.img("serrilha", "#ffffffff")
    c.img("marcas", "@cor", alfa=210)
    c.img("lcd", "#ffffffff")
    for i, nome in enumerate(DIAS):
        x = PX0 + 16 + i * 44
        cond = f'[DAY_OF_WEEK] == {i + 1} ? 255 : 70'
        c.txt("t12", x, 153, 44, "%s", [f'&quot;{nome}&quot;'], nome, TINTA, "CENTER",
              filhos=f'<Transform target="alpha" value="{cond}" />', alfa=255 if i == dia else 70)
        c.img("sublinhado", TINTA, x + 5, 169, filhos=f'<Transform target="alpha" value="[DAY_OF_WEEK] == {i + 1} ? 255 : 0" />', alfa=255 if i == dia else 0)
    c.hora("grande", 96, 182, 236, "hh:mm", "10:08", TINTA)
    c.hora("peq", 336, 232, 56, "ss", "30", TINTA)
    c.txt("t20", 96, 290, 130, "%s %s", ["[DAY]", "[MONTH_S]"], "28 NOV", TINTA, "START")
    c.img("bateria", TINTA, 268, 290)
    c.txt("t20", 308, 290, 90, "%s%%", ["round([BATTERY_PERCENT])"], f"{bat}%", TINTA, "START")
    c.segmentos("meta", 20, 98, 318, 10, 9, 13, "[STEP_PERCENT]", pct, TINTA, apagado=45)
    c.txt("t20", 160, 362, 160, "%s", ["[STEP_COUNT]"], f"{passos}", "@cor")
    c.txt("t14", 190, 98, 100, "RUGGED", [], "RUGGED", "@cor")
    return c


def xml(A, fam) -> str:
    L = cabecalho(NOME, "DIGITAL") + ["  <BitmapFonts>"]
    for nome in ("t12", "t14", "t20"):
        L.append(xml_bitmapfont(nome, fam[nome], True))
    for nome in ("grande", "peq"):
        L.append(xml_bitmapfont(nome, fam[nome]))
    L += ["  </BitmapFonts>", "  <UserConfigurations>", cor_config("cor", "cor_label", CORES), "  </UserConfigurations>",
          '  <Scene backgroundColor="#ff000000">', "    " + grupo("vivo", "", 0), cena(A, fam).xml("v"), "    </Group>",
          "    " + grupo("ambiente", ' alpha="0"', 255), cena(A, fam, True).xml("a"), "    </Group>", "  </Scene>", "</WatchFace>"]
    return "\n".join(L) + "\n"


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Rugged", "cor_label": "Color"}
    pt = {"watch_face_name": "Rugged", "cor_label": "Cor"}
    strings_opcoes(en, pt, "cor", NOMES)
    A, fam = assets()
    previas = []
    for cid, seg, bat, p in (("laranja", 30, 100, 54), ("ciano", 47, 62, 83), ("amarelo", 12, 17, 12), ("verde", 58, 88, 100)):
        previas.append(redondo(cena(A, fam, seg=seg, bat=bat, pct=p).previa({"@cor": rgb(dict(CORES)[cid])})))
    previas.append(redondo(cena(A, fam, True).previa({"@cor": (210, 210, 214)})))
    return finalizar(raiz, NOME, en, pt, xml(A, fam), A, previas, ["Laranja", "Ciano", "Amarelo", "Verde", "Ambiente (AOD)"], cols=5,
                     nomes_previa=["laranja", "ciano", "amarelo", "verde", "ambiente"])
