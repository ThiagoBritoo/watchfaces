"""Watchface "Holo": painel holográfico futurista. Fundo azul-noite com malha hexagonal e vidro, hora em 7 segmentos com
brilho (halo) neon, dois medidores em arco (bateria à esquerda, passos à direita) com preenchimento animado, data no topo
e passos embaixo. Seis cores neon."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from wf.desenho import SS, grad_radial, reduzir_por
from wf.hud import Cena, Tela, fonte_texto, redondo, xml_bitmapfont
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, rgb, strings_opcoes
from wf.lcd_fonte import digito

NOME = "holo"
CORES = [("ciano", "#ff24e6ff"), ("magenta", "#ffff3dd2"), ("lima", "#ffb6ff2e"), ("ambar", "#ffffb020"), ("branco", "#fff0f6ff"), ("vermelho", "#ffff4a4a")]
NOMES = {"ciano": ("Cyan", "Ciano"), "magenta": ("Magenta", "Magenta"), "lima": ("Lime", "Lima"), "ambar": ("Amber", "Âmbar"),
         "branco": ("White", "Branco"), "vermelho": ("Red", "Vermelho")}
DIM = "#ffa3adbd"
GR = dict(w=36, h=82, e=9, pad=12)
PQ = dict(w=16, h=28, e=4, pad=6)
R_G = 212                       # raio dos medidores
ARCOS = {"bat": (218, 322, "[BATTERY_PERCENT]"), "pas": (38, 142, "[STEP_PERCENT]")}


def _fundo() -> Image.Image:
    n = W * SS
    im = grad_radial(n, n / 2, n / 2 - 20 * SS, [(0, (14, 30, 52, 255)), (150 * SS, (7, 16, 30, 255)), (260 * SS, (2, 5, 11, 255))])
    d = ImageDraw.Draw(im)
    r = 26 * SS                                                   # malha hexagonal discreta
    for q in range(-3, 14):
        for p in range(-3, 14):
            cx = (q * 1.5) * r + 0
            cy = (p * math.sqrt(3) + (math.sqrt(3) / 2 if q % 2 else 0)) * r
            pts = [(cx + r * math.cos(math.radians(60 * i)), cy + r * math.sin(math.radians(60 * i))) for i in range(6)]
            d.line(pts + [pts[0]], fill=(90, 150, 200, 14), width=SS)
    base = reduzir_por(im)
    t = Tela()
    t.elipse(C, C, 239, contorno=(70, 90, 120, 255), esp=2)
    t.elipse(C, C, 232, contorno=(30, 44, 64, 255), esp=1.5)
    base.alpha_composite(t.pronto())
    return base


def _vidro() -> Image.Image:
    t = Tela()
    t.poly([(60, 60), (300, 20), (170, 150), (60, 210)], (255, 255, 255, 14))
    return t.pronto()


def _trilhas() -> Image.Image:
    t = Tela()
    for a0, a1, _ in ARCOS.values():
        t.arco(C, C, R_G, a0, a1, (255, 255, 255, 255), 8)
        for a in (a0, a1):
            t.elipse(C + R_G * math.sin(math.radians(a)), C - R_G * math.cos(math.radians(a)), 4, cor=(255, 255, 255, 255))
    t.arco(C, C, 190, 0, 359.9, (255, 255, 255, 70), 1)
    for k in range(72):                                           # régua interna fina
        a = math.radians(k * 5)
        r0, r1 = 192, 196 if k % 6 else 201
        t.linha([(C + r0 * math.sin(a), C - r0 * math.cos(a)), (C + r1 * math.sin(a), C - r1 * math.cos(a))], (255, 255, 255, 120 if k % 6 else 220), 1.2)
    return t.pronto()


def _colchetes() -> Image.Image:
    t = Tela()
    for sx in (-1, 1):
        for y0, dy in ((120, 1), (360, -1)):
            x = C + sx * 118
            t.linha([(x - sx * 30, y0), (x, y0), (x + sx * 14, y0 + dy * 14)], (255, 255, 255, 255), 2)
    t.linha([(190, 112), (290, 112)], (255, 255, 255, 120), 1)
    t.linha([(190, 368), (290, 368)], (255, 255, 255, 120), 1)
    return t.pronto()


def _digitos(prefixo: str, glow: bool, **kw):
    imgs, mapa = {}, {}
    colon = kw.pop("colon")
    for ch in "0123456789:":
        im = digito(ch, kw["w"] if ch != ":" else colon, kw["h"], kw["e"], kw["pad"], 0.07 if not glow else 0.0)
        if glow:
            a = im.getchannel("A")
            ga = a.filter(ImageFilter.GaussianBlur(kw["pad"] * 0.55)).point(lambda v: min(255, int(v * 1.9)))
            im = Image.new("RGBA", im.size, (255, 255, 255, 0))
            im.putalpha(ga)
        n = f"{prefixo}_{'colon' if ch == ':' else ch}"
        imgs[n] = im
        mapa[ch] = (n, im.width, im.height)
    return imgs, mapa


def assets():
    A = {"fundo": _fundo(), "vidro": _vidro(), "trilhas": _trilhas(), "colchetes": _colchetes()}
    fam = {}
    for nome, h in (("t14", 14), ("t20", 20)):
        i, m = fonte_texto(nome, h)
        A.update(i)
        fam[nome] = m
    for fnome, glow, kw in (("grande", False, GR), ("brilho", True, GR), ("peq", False, PQ), ("peqbrilho", True, PQ)):
        i, m = _digitos("gl" + fnome if glow else fnome[0:1] + "x" + fnome, glow, colon=(16 if kw is GR else 8), **kw)
        A.update(i)
        fam[fnome] = m
    return A, fam


def _arcos_xml() -> str:
    L = []
    for nome, (a0, a1, expr) in ARCOS.items():
        arco = (f'<PartDraw x="0" y="0" width="{W}" height="{W}"><Arc centerX="{C}" centerY="{C}" width="{2 * R_G}" height="{2 * R_G}" startAngle="{a0}" endAngle="{a0}">'
                '<Stroke thickness="{e}" color="[CONFIGURATION.cor.0]" cap="ROUND" />'
                f'<Transform target="endAngle" value="{a0} + clamp({expr}, 0, 100) * {(a1 - a0) / 100:g}" /></Arc></PartDraw>')
        L.append(f'    <Group name="halo_{nome}" x="0" y="0" width="{W}" height="{W}" alpha="70">' + arco.replace("{e}", "18") + "</Group>")
        L.append(arco.replace("{e}", "8"))
    return "\n".join(L)


def _arcos_prev(bat: int, pas: int):
    def f(base: Image.Image, pal) -> None:
        n = W * SS
        for halo, esp, al in ((True, 18, 70), (False, 8, 255)):
            cam = Image.new("RGBA", (n, n), (0, 0, 0, 0))
            d = ImageDraw.Draw(cam)
            for nome, v in (("bat", bat), ("pas", pas)):
                a0, a1, _ = ARCOS[nome]
                fim = a0 + v * (a1 - a0) / 100
                d.arc([(C - R_G) * SS, (C - R_G) * SS, (C + R_G) * SS, (C + R_G) * SS], a0 - 90, fim - 90, fill=pal["@cor"] + (al,), width=esp * SS)
                for a in (a0, fim):
                    cx, cy = C + R_G * math.sin(math.radians(a)), C - R_G * math.cos(math.radians(a))
                    d.ellipse([(cx - esp / 2) * SS, (cy - esp / 2) * SS, (cx + esp / 2) * SS, (cy + esp / 2) * SS], fill=pal["@cor"] + (al,))
            base.alpha_composite(reduzir_por(cam))
    return f


def cena(A, fam, ambiente=False, bat=100, pas=54, passos=3457) -> Cena:
    c = Cena(fam, A)
    if ambiente:
        c.hora("grande", 100, 170, 280, "hh:mm", "10:08", "#ffd2d2d6")
        return c
    c.img("fundo", "#ffffffff")
    c.img("vidro", "#ffffffff")
    c.img("trilhas", "@cor", alfa=95)
    c.cru(_arcos_xml(), _arcos_prev(bat, pas))
    c.img("colchetes", "@cor", alfa=210)
    c.txt("t20", 140, 86, 200, "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "SAB 28 NOV", "#ffe8f1ff")
    c.hora("brilho", 100, 170, 280, "hh:mm", "10:08", "@cor", alfa=120)
    c.hora("grande", 100, 170, 280, "hh:mm", "10:08", "#fff4faff")
    c.hora("peqbrilho", 214, 282, 80, "ss", "30", "@cor", "CENTER", alfa=110)
    c.hora("peq", 214, 282, 80, "ss", "30", "@cor", "CENTER")
    c.txt("t14", 30, 224, 62, "BAT", [], "BAT", DIM)
    c.txt("t20", 30, 242, 62, "%s", ["round([BATTERY_PERCENT])"], f"{bat}", "@cor")
    c.txt("t14", 388, 224, 62, "META", [], "META", DIM)
    c.txt("t20", 388, 242, 62, "%s%%", ["round([STEP_PERCENT])"], f"{pas}%", "@cor")
    c.txt("t20", 160, 372, 160, "%s", ["[STEP_COUNT]"], f"{passos}", "#ffe8f1ff")
    return c


def xml(A, fam) -> str:
    L = cabecalho(NOME, "DIGITAL") + ["  <BitmapFonts>"]
    for nome in ("t14", "t20"):
        L.append(xml_bitmapfont(nome, fam[nome], True))
    for nome in ("grande", "brilho", "peq", "peqbrilho"):
        L.append(xml_bitmapfont(nome, fam[nome]))
    L += ["  </BitmapFonts>", "  <UserConfigurations>", cor_config("cor", "cor_label", CORES), "  </UserConfigurations>",
          '  <Scene backgroundColor="#ff000000">', "    " + grupo("vivo", "", 0), cena(A, fam).xml("v"), "    </Group>",
          "    " + grupo("ambiente", ' alpha="0"', 255), cena(A, fam, True).xml("a"), "    </Group>", "  </Scene>", "</WatchFace>"]
    return "\n".join(L) + "\n"


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Holo", "cor_label": "Color"}
    pt = {"watch_face_name": "Holo", "cor_label": "Cor"}
    strings_opcoes(en, pt, "cor", NOMES)
    A, fam = assets()
    previas = []
    for cid, bat, p in (("ciano", 100, 54), ("magenta", 62, 83), ("lima", 17, 12), ("ambar", 88, 100)):
        previas.append(redondo(cena(A, fam, bat=bat, pas=p).previa({"@cor": rgb(dict(CORES)[cid])})))
    previas.append(redondo(cena(A, fam, True).previa({"@cor": (210, 210, 214)})))
    return finalizar(raiz, NOME, en, pt, xml(A, fam), A, previas, ["Ciano", "Magenta", "Lima", "Âmbar", "Ambiente (AOD)"], cols=5,
                     nomes_previa=["ciano", "magenta", "lima", "ambar", "ambiente"])
