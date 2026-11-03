"""Watchface "Tático": painel LCD digital estilo equipamento de campo. Moldura segmentada, duas placas chanfradas
(bateria + data / meta de passos com barra de 10 segmentos), hora em 7 segmentos com segmentos fantasma, segundos
pequenos e uma pílula com passos. Onze cores. Arte 100% original, gerada por script."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import SS
from wf.hud import (DIA_PREVIA, Cena, Tela, digitos_lcd, fonte_texto, painel_chanfrado, redondo, sombra_interna, unir,
                    xml_bitmapfont)
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, rgb, strings_opcoes

NOME = "tatico"
CORES = [("areia", "#ffd3c8ad"), ("branco", "#fff2f2f2"), ("verde", "#ff17b324"), ("azul", "#ff3a86c9"), ("vermelho", "#fffb2323"),
         ("cinza", "#ff8a93a6"), ("amarelo", "#ffe0e01a"), ("petroleo", "#ff0a7ea0"), ("ciano", "#ff1ae9f7"), ("laranja", "#ffe08a0a"), ("roxo", "#ffb00ab8")]
NOMES = {"areia": ("Sand", "Areia"), "branco": ("White", "Branco"), "verde": ("Green", "Verde"), "azul": ("Blue", "Azul"), "vermelho": ("Red", "Vermelho"),
         "cinza": ("Slate", "Cinza"), "amarelo": ("Yellow", "Amarelo"), "petroleo": ("Teal", "Petróleo"), "ciano": ("Cyan", "Ciano"),
         "laranja": ("Orange", "Laranja"), "roxo": ("Purple", "Roxo")}
ESC = "#ff17140c"        # texto escuro sobre as placas
GR = dict(w=44, h=76, e=10, pad=3)
PQ = dict(w=20, h=34, e=5, pad=2)
L_PAINEL = [(96, 124), (260, 124), (222, 200), (74, 200), (74, 150)]
R_PAINEL = [(270, 124), (380, 124), (410, 160), (410, 200), (232, 200)]
MOLDURA = [(52, 226), (70, 210), (410, 210), (428, 226), (428, 314), (410, 330), (70, 330), (52, 314)]
PILULA = [(140, 362), (156, 346), (324, 346), (340, 362), (324, 378), (156, 378)]
SEGS_X = [246 + i * 13 for i in range(10)]


def _placa_fundo() -> Image.Image:
    """Chapa escura do relógio: disco, bisel com ranhuras e as caixas escuras atrás da hora e da pílula."""
    t = Tela()
    t.elipse(C, C, 240, cor=(9, 9, 10, 255))
    t.elipse(C, C, 237, contorno=(46, 47, 50, 255), esp=2)
    t.elipse(C, C, 210, contorno=(30, 31, 33, 255), esp=2)
    for k in range(120):
        a = math.radians(k * 3)
        r0, r1 = 213, 218 if k % 5 else 222
        t.linha([(C + r0 * math.sin(a), C - r0 * math.cos(a)), (C + r1 * math.sin(a), C - r1 * math.cos(a))], (58, 60, 64, 255), 1.0)
    t.poly(MOLDURA, (16, 16, 17, 255))
    t.poly(PILULA, (16, 16, 17, 255))
    return sombra_interna(t.pronto(), 5, 0.5, 2)


def _bezel() -> Image.Image:
    t = Tela()
    # arcos grossos segmentados (cor do usuário)
    padrao = [(8, 38), (44, 58), (64, 76), (84, 96), (104, 116), (124, 150), (156, 176), (184, 196), (204, 216), (224, 236), (244, 262),
              (270, 290), (296, 306), (312, 330), (336, 350), (356, 370)]
    for a0, a1 in padrao:
        t.arco(C, C, 229, a0, a1, (255, 255, 255, 255), 6)
    t.arco(C, C, 221, 0, 360, (255, 255, 255, 70), 1.2)
    for k in range(60):                      # tracinhos finos internos
        a = math.radians(k * 6)
        r0, r1 = 203, 208 if k % 5 else 207
        t.linha([(C + r0 * math.sin(a), C - r0 * math.cos(a)), (C + r1 * math.sin(a), C - r1 * math.cos(a))], (255, 255, 255, 120 if k % 5 else 230), 1.4)
    return t.pronto()


def _tracos() -> Image.Image:
    t = Tela()
    for y, x0, x1 in ((92, 122, 358), (398, 100, 380)):
        x = x0
        while x < x1:
            t.linha([(x, y), (min(x + 12, x1), y)], (255, 255, 255, 255), 2)
            x += 17
    for cx in (176, 304):                    # dois "x" de mira ao lado do rótulo
        t.linha([(cx - 5, 66), (cx + 5, 76)], (255, 255, 255, 255), 2)
        t.linha([(cx - 5, 76), (cx + 5, 66)], (255, 255, 255, 255), 2)
    return t.pronto()


def _contorno(pts, esp=3, dupla=True) -> Image.Image:
    t = Tela()
    t.contorno(pts, (255, 255, 255, 255), esp)
    if dupla:                                # segundo filete, mais fino e apagado, por dentro
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        ins = [(cx + (x - cx) * 0.965, cy + (y - cy) * 0.93) for x, y in pts]
        t.contorno(ins, (255, 255, 255, 90), 1)
    return t.pronto()


def _icones() -> dict[str, Image.Image]:
    """Ícones pequenos: bateria e sino (sobre as placas, escuros) e tênis (sobre a pílula, na cor)."""
    t = Tela()
    for (x, y) in ((92, 152),):   # bateria vertical
        t.retangulo(x, y, x + 9, y + 17, (255, 255, 255, 255), 1.5)
        t.retangulo(x + 3, y - 2, x + 6, y, (255, 255, 255, 255))
        t.retangulo(x + 2, y + 3, x + 7, y + 15, (0, 0, 0, 0), 0.5)
        t.d.rectangle([(x + 2) * SS, (y + 3) * SS, (x + 7) * SS, (y + 15) * SS], fill=(0, 0, 0, 0))
        t.d.rectangle([(x + 2) * SS, (y + 3) * SS, (x + 7) * SS, (y + 15) * SS], fill=(255, 255, 255, 255))
        t.d.rectangle([(x + 2) * SS, (y + 3) * SS, (x + 7) * SS, (y + 6) * SS], fill=(0, 0, 0, 0))
    for (cx, cy) in ((100, 138), (292, 138)):  # sino
        t.poly([(cx - 8, cy + 6), (cx - 5, cy + 6), (cx - 5, cy - 3), (cx, cy - 8), (cx + 5, cy - 3), (cx + 5, cy + 6), (cx + 8, cy + 6),
                (cx + 8, cy + 8), (cx - 8, cy + 8)], (255, 255, 255, 255))
        t.elipse(cx, cy + 11, 2.2, cor=(255, 255, 255, 255))
    escuro = t.pronto()
    s = Tela()
    s.poly([(168, 369), (168, 357), (175, 355), (177, 360), (184, 361), (192, 366), (200, 368), (200, 369)], (255, 255, 255, 255))
    s.poly([(166, 370), (202, 370), (202, 373), (166, 373)], (255, 255, 255, 255))
    s.linha([(180, 362), (184, 365)], (0, 0, 0, 255), 1.2)
    s.linha([(184, 359), (188, 364)], (0, 0, 0, 255), 1.2)
    return {"icones_escuro": escuro, "icone_tenis": s.pronto()}


def _segmentos(passo_pct: bool = True) -> Image.Image:
    t = Tela()
    for x in SEGS_X:
        t.retangulo(x, 178, x + 10, 190, (255, 255, 255, 255), 1)
    return t.pronto()


def assets() -> tuple[dict, dict]:
    A: dict[str, Image.Image] = {"fundo": _placa_fundo(), "bezel": _bezel(), "tracos": _tracos(), "moldura": _contorno(MOLDURA),
                                 "pilula": _contorno(PILULA, 2, False)}
    A["paineis"] = painel_chanfrado(L_PAINEL + [], 250, 200, 3, 4, 3)
    A["painel_dir"] = painel_chanfrado(R_PAINEL, 250, 200, 3, 4, 5)
    pe = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    pe.alpha_composite(A["paineis"])
    pe.alpha_composite(A["painel_dir"])
    A["paineis"] = pe
    del A["painel_dir"]
    A.update(_icones())
    fontes_img, fam = {}, {}
    for nome, h in (("t14", 14), ("t20", 20)):
        i, m = fonte_texto(nome, h)
        fontes_img.update(i)
        fam[nome] = m
    i, m = digitos_lcd("g", **GR, colon=18)
    fontes_img.update(i)
    fam["grande"] = m
    i, m = digitos_lcd("p", **PQ, colon=8)
    fontes_img.update(i)
    fam["peq"] = m
    A.update(fontes_img)
    return A, fam


def _barra_xml() -> str:
    L = []
    for k, x in enumerate(SEGS_X):
        lim = (k + 1) * 10
        L.append(f'<Group name="meta_{k}" x="{x}" y="178" width="10" height="12"><PartDraw x="0" y="0" width="10" height="12">'
                 f'<Rectangle x="0" y="0" width="10" height="12"><Fill color="{ESC}" /></Rectangle></PartDraw>'
                 f'<Transform target="alpha" value="[STEP_PERCENT] &gt;= {lim - 5} ? 255 : 50" /></Group>')
    return "\n".join("    " + s for s in L)


def _barra_prev(pct: int):
    def f(base: Image.Image, pal) -> None:
        d = ImageDraw.Draw(base)
        for k, x in enumerate(SEGS_X):
            a = 255 if pct >= (k + 1) * 10 - 5 else 50
            d.rectangle([x, 178, x + 9, 189], fill=rgb(ESC) + (a,))
    return f


def cena(A: dict, fam: dict, ambiente: bool = False, bat: int = 100, passos: int = 3457, pct: int = 54) -> Cena:
    c = Cena(fam, A)
    if ambiente:
        c.img("moldura", "#ff5a5a60")
        c.hora("grande", 99, 229, 232, "hh:mm", "10:08", "#ffd2d2d6")
        return c
    c.img("fundo", "#ffffffff")
    c.img("bezel", "@cor")
    c.img("tracos", "@cor")
    c.txt("t14", 150, 62, 180, "LOC-6", [], "LOC-6", "@cor")
    c.img("paineis", "@cor")
    c.img("icones_escuro", ESC)
    c.txt("t14", 114, 131, 120, "%s", ['[DAY_OF_WEEK_S]'], "SAB", ESC, "START")
    c.txt("t14", 108, 153, 100, "%s%%", ["round([BATTERY_PERCENT])"], f"{bat}%", ESC, "START")
    c.txt("t14", 86, 178, 160, "%s %s", ["[DAY]", "[MONTH_S]"], "28 NOV", ESC, "START")
    c.txt("t14", 306, 131, 90, "%s", ["&quot;META&quot;"], "META", ESC, "START")
    c.txt("t14", 280, 153, 120, "%s%%", ["round([STEP_PERCENT])"], f"{pct}%", ESC, "START")
    c.cru(_barra_xml(), _barra_prev(pct))
    c.img("moldura", "@cor")
    c.hora("grande", 99, 229, 232, "hh:mm", "10:08", "@cor")
    c.hora("peq", 329, 269, 56, "ss", "30", "@cor")
    c.img("pilula", "@cor")
    c.img("icone_tenis", "@cor")
    c.txt("t20", 200, 349, 120, "%s", ["[STEP_COUNT]"], f"{passos}", "@cor", "START")
    return c


def xml(A: dict, fam: dict) -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <BitmapFonts>"]
    for nome in ("t14", "t20"):
        L.append(xml_bitmapfont(nome, fam[nome], True))
    for nome in ("grande", "peq"):
        L.append(xml_bitmapfont(nome, fam[nome]))
    L += ["  </BitmapFonts>", "  <UserConfigurations>", cor_config("cor", "cor_label", [(k, v) for k, v in CORES]), "  </UserConfigurations>",
          '  <Scene backgroundColor="#ff000000">', "    " + grupo("vivo", "", 0), cena(A, fam).xml("v"), "    </Group>",
          "    " + grupo("ambiente", ' alpha="0"', 255), cena(A, fam, True).xml("a"), "    </Group>", "  </Scene>", "</WatchFace>"]
    return "\n".join(L) + "\n"


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Tactical", "cor_label": "Color"}
    pt = {"watch_face_name": "Tático", "cor_label": "Cor"}
    strings_opcoes(en, pt, "cor", NOMES)
    A, fam = assets()
    previas = []
    for cid, bat, p in (("areia", 100, 54), ("ciano", 62, 83), ("laranja", 17, 12), ("verde", 88, 100)):
        pal = {"@cor": rgb(dict(CORES)[cid])}
        previas.append(redondo(cena(A, fam, bat=bat, pct=p).previa(pal)))
    previas.append(redondo(cena(A, fam, True).previa({"@cor": (210, 210, 214)})))
    return finalizar(raiz, NOME, en, pt, xml(A, fam), A, previas, ["Areia", "Ciano", "Laranja", "Verde", "Ambiente (AOD)"], cols=5,
                     nomes_previa=["areia", "ciano", "laranja", "verde", "ambiente"])
