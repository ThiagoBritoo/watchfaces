"""Watchface "Fragmento": abstrata. Você só enxerga um pedaço de dois mostradores gigantes (horas e minutos) que giram
por baixo da tela; uma linha laranja inclinada marca o instante. Não há ponteiros nem círculo à vista.
Inspirada em mostradores "recortados". Arte e código originais."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, fonte_serifa, polar, reduzir_por, tela, texto_centrado
from wf.kit import C, W, cabecalho, colar, cor_config, finalizar, girar, hora, img, redondo, rect, rgb, strings_opcoes, tpl

NOME = "fragmento"
CY = 500                          # centro (fora da tela) dos dois mostradores
RH, RM = 700, 540                 # lado das imagens das horas e dos minutos
ACENTOS = [("laranja", "#ff6a1a"), ("vermelho", "#ff3b3b"), ("ciano", "#33d6ff"), ("ouro", "#f2c14e"), ("branco", "#ffffff")]


def anel_horas() -> Image.Image:
    n = RH * SS
    c = n / 2
    im = tela(n)
    d = ImageDraw.Draw(im)
    fs = fonte_serifa(44 * SS)
    for k in range(72):
        a = k * 5
        hr = k % 6 == 0
        d.line([polar(c, c, 322 * SS, a), polar(c, c, (346 if hr else 334) * SS, a)], fill=(255, 255, 255, 255 if hr else 150), width=int((4 if hr else 2.4) * SS))
    for k in range(12):
        a = k * 30
        x, y = polar(c, c, 292 * SS, a)
        texto_centrado(im, "12" if k == 0 else str(k), x, y, fs, (255, 255, 255, 255), rot=-a)
    return reduzir_por(im)


def anel_min() -> Image.Image:
    n = RM * SS
    c = n / 2
    im = tela(n)
    d = ImageDraw.Draw(im)
    f = fonte("Medium", 21 * SS)
    for m in range(60):
        a = m * 6
        mj = m % 5 == 0
        d.line([polar(c, c, (234 if mj else 240) * SS, a), polar(c, c, 252 * SS, a)], fill=(255, 255, 255, 235 if mj else 120), width=int((3 if mj else 1.6) * SS))
        if mj:
            x, y = polar(c, c, 212 * SS, a)
            texto_centrado(im, f"{m:02d}", x, y, f, (255, 255, 255, 215), rot=-a)
    return reduzir_por(im)


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS), "  </UserConfigurations>",
                                       '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a(f'    <Group name="mostradores" {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a("      " + img(C - RH // 2, CY - RH // 2, RH, RH, "anel_horas", ' pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="-[HOUR_0_11_MINUTE] * 30" />'))
    a("      " + img(C - RM // 2, CY - RM // 2, RM, RM, "anel_min", ' pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="-([MINUTE] + [SECOND] / 60) * 6" />'))
    a("      " + rect(C - 1.5, 118, 3, 230, ac, 0, "Fill", 2, "", ' angle="-9" pivotX="0.5" pivotY="0.5"'))
    a("      " + tpl(110, 392, 260, 30, 22, "#ff9a9aa2", "%s", ["[DAY_OF_WEEK_F]"], "MEDIUM"))
    a("      " + tpl(110, 418, 260, 36, 28, "#ffffffff", "%s %s", ["[DAY]", "[MONTH_F]"], "SEMI_BOLD"))
    a("    </Group>")
    a(f'    <Group name="ambiente" {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />')
    a("      " + hora(40, 150, 400, 100, "hh:mm", 96, "#ffd0d0d6", "LIGHT", "CENTER"))
    a("      " + rect(C - 20, 270, 40, 3, ac, 1.5))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A: dict, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    ac = rgb(acento)
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 200), f"{h:02d}:{mi:02d}", font=fonte("Light", 96), fill=(208, 208, 214), anchor="mm")
        d.rounded_rectangle([C - 20, 270, C + 20, 273], radius=1, fill=ac)
    else:
        for nome, lado, ang in (("anel_horas", RH, -((h % 12) + mi / 60) * 30), ("anel_min", RM, -(mi + s / 60) * 6)):
            im = A[nome].rotate(-ang, resample=Image.BICUBIC)
            colar(base, im, C - lado // 2, CY - lado // 2)
        lin = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(lin).rectangle([C - 2, 118, C + 1, 348], fill=ac + (255,))
        base.alpha_composite(lin.rotate(9, center=(C, 233), resample=Image.BICUBIC))
        d = ImageDraw.Draw(base)
        d.text((C, 407), "SEXTA-FEIRA", font=fonte("Medium", 22), fill=(154, 154, 162), anchor="mm")
        d.text((C, 436), "31 outubro", font=fonte("SemiBold", 28), fill=(255, 255, 255), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Fragment", "acento_label": "Accent color"}
    pt = {"watch_face_name": "Fragmento", "acento_label": "Cor da linha"}
    strings_opcoes(en, pt, "acento", {"laranja": ("Orange", "Laranja"), "vermelho": ("Red", "Vermelho"), "ciano": ("Cyan", "Ciano"),
                                       "ouro": ("Gold", "Ouro"), "branco": ("White", "Branco")})
    A = {"anel_horas": anel_horas(), "anel_min": anel_min()}
    pv = [previa(A, "#ff6a1a", 11, 52, 20), previa(A, "#33d6ff", 3, 17, 40), previa(A, "#f2c14e", 7, 30, 5), previa(A, "#ff6a1a", 11, 52, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Laranja", "Ciano", "Ouro", "Ambiente (AOD)"], cols=4, nomes_previa=["laranja", "ciano", "ouro", "ambiente"])
