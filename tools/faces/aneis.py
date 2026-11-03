"""Watchface "Anéis": abstrata. Quatro anéis concêntricos que se enchem (hora, minuto, segundo e bateria) com pontos
luminosos nas pontas. Não há ponteiros nem números grandes: só um texto pequeno no centro (opcional).
Arte e código originais."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial
from wf.kit import C, W, cabecalho, cor_config, finalizar, hora, redondo, rgb, strings_opcoes, tint, tpl

NOME = "aneis"
PALETAS = [("aurora", "#33e1ff #8a6bff #ff5fa8 #ffd23d"), ("brasa", "#ffd23d #ff8a3d #ff4040 #ffe9c2"), ("oceano", "#7fffd4 #33b5ff #4d6bff #b0c4ff"),
           ("mata", "#d4ff6b #4be37a #1fb58a #f2ffd9"), ("mono", "#ffffff #d0d0d0 #9a9a9a #6a6a6a")]
ANEIS = [("hora", 214, 18, 0, "[HOUR_0_11_MINUTE] * 30"), ("min", 184, 14, 1, "([MINUTE] + [SECOND] / 60) * 6"),
         ("seg", 156, 9, 2, "[SECOND] * 6"), ("bat", 132, 5, 3, "clamp([BATTERY_PERCENT], 0, 100) * 3.6")]
CABECA = 56


def cabeca() -> Image.Image:
    return grad_radial(CABECA, CABECA / 2, CABECA / 2, [(0, (255, 255, 255, 255)), (7, (255, 255, 255, 255)), (11, (255, 255, 255, 150)), (28, (255, 255, 255, 0))])


def arco(r, esp, cor, expr=None, ini=0, fim=360) -> str:
    t = f'<Transform target="endAngle" value="{expr}" />' if expr else ""
    return (f'<Arc centerX="{C}" centerY="{C}" width="{2 * r}" height="{2 * r}" startAngle="{ini}" endAngle="{fim}">'
            f'<Stroke thickness="{esp}" color="{cor}" cap="ROUND" />{t}</Arc>')


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS),
                                       '    <BooleanConfiguration id="texto" displayName="texto_label" defaultValue="TRUE" />', "  </UserConfigurations>",
                                       '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a(f'    <Group name="vivo" {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    for nome, r, esp, ci, expr in ANEIS:
        cor = f"[CONFIGURATION.paleta.{ci}]"
        a(f"      <PartDraw {full}>" + arco(r, esp, "#22ffffff") + arco(r, esp, cor, expr, 0, 0) + "</PartDraw>")
    for nome, r, esp, ci, expr in ANEIS:
        cor = f"[CONFIGURATION.paleta.{ci}]"
        a(f'      <Group name="cabeca_{nome}" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="{expr}" />'
          f'<PartImage x="{C - CABECA // 2}" y="{C - r - CABECA // 2}" width="{CABECA}" height="{CABECA}" tintColor="{cor}"><Image resource="cabeca" /></PartImage></Group>')
    a('      <BooleanConfiguration id="texto"><BooleanOption id="TRUE"><Group name="texto" ' + full + '>')
    a("        " + hora(90, 190, 300, 70, "hh:mm", 56, "#ffffffff", "LIGHT", "CENTER"))
    a("        " + tpl(110, 252, 260, 28, 19, "#aaffffff", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("      </Group></BooleanOption></BooleanConfiguration>")
    a("    </Group>")
    a(f'    <Group name="ambiente" {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />')
    for nome, r, esp, ci, expr in ANEIS[:2]:
        a(f"      <PartDraw {full}>" + arco(r, 2, "#33ffffff") + "</PartDraw>")
        a(f'      <Group name="pt_{nome}" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="{expr}" />'
          f'<PartDraw x="{C - 7}" y="{C - r - 7}" width="14" height="14"><Ellipse x="0" y="0" width="14" height="14"><Fill color="#ffffffff" /></Ellipse></PartDraw></Group>')
    a("      " + hora(90, 200, 300, 70, "hh:mm", 48, "#ff9a9aa2", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A: dict, paleta: str, h: int, mi: int, s: int, bat: float = 0.76, ambiente_: bool = False, texto: bool = True) -> Image.Image:
    cores = [rgb(c) for c in paleta.split()]
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    angs = [(h % 12 + mi / 60) * 30, (mi + s / 60) * 6, s * 6, bat * 360]
    if ambiente_:
        for (nome, r, esp, ci, _), ang in zip(ANEIS[:2], angs):
            d.ellipse([C - r, C - r, C + r, C + r], outline=(80, 80, 84), width=2)
            x, y = C + r * np.sin(np.radians(ang)), C - r * np.cos(np.radians(ang))
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 255, 255))
        d.text((C, 235), f"{h:02d}:{mi:02d}", font=fonte("Light", 48), fill=(154, 154, 162), anchor="mm")
        return redondo(base)
    for (nome, r, esp, ci, _), ang in zip(ANEIS, angs):
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        dc = ImageDraw.Draw(cam)
        box = [C - r, C - r, C + r, C + r]
        dc.ellipse(box, outline=(255, 255, 255, 34), width=esp)
        dc.arc(box, -90, -90 + ang, fill=cores[ci] + (255,), width=esp)
        for a_ in (0, ang):                                   # pontas arredondadas
            x, y = C + r * np.sin(np.radians(a_)), C - r * np.cos(np.radians(a_))
            if a_ == 0 and ang < 3:
                continue
            dc.ellipse([x - esp / 2, y - esp / 2, x + esp / 2, y + esp / 2], fill=cores[ci] + (255,))
        base.alpha_composite(cam)
    for (nome, r, esp, ci, _), ang in zip(ANEIS, angs):
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        cam.paste(tint(A["cabeca"], cores[ci]), (C - CABECA // 2, C - r - CABECA // 2))
        base.alpha_composite(cam.rotate(-ang, center=(C, C), resample=Image.BICUBIC))
    d = ImageDraw.Draw(base)
    if texto:
        d.text((C, 225), f"{h:02d}:{mi:02d}", font=fonte("Light", 56), fill=(255, 255, 255), anchor="mm")
        d.text((C, 266), "SEX 31 OUT", font=fonte("Medium", 19), fill=(170, 170, 176), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Rings", "paleta_label": "Palette", "texto_label": "Center text"}
    pt = {"watch_face_name": "Anéis", "paleta_label": "Paleta", "texto_label": "Texto central"}
    strings_opcoes(en, pt, "paleta", {"aurora": ("Aurora", "Aurora"), "brasa": ("Ember", "Brasa"), "oceano": ("Ocean", "Oceano"), "mata": ("Forest", "Mata"), "mono": ("Mono", "Mono")})
    A = {"cabeca": cabeca()}
    pv = [previa(A, PALETAS[0][1], 10, 8, 32), previa(A, PALETAS[1][1], 4, 47, 12, 0.4), previa(A, PALETAS[2][1], 9, 22, 50, 0.9), previa(A, PALETAS[3][1], 1, 5, 20, 0.15),
          previa(A, PALETAS[4][1], 10, 8, 0, 0.76, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Aurora", "Brasa", "Oceano", "Mata", "Ambiente (AOD)"], cols=3, nomes_previa=["aurora", "brasa", "oceano", "mata", "ambiente"])
