"""Watchface "Régua": minimalista/abstrata. Dois anéis de escala (minutos e segundos) giram sob uma cápsula fixa,
que mostra o minuto e o segundo de agora; a hora fica gigante no centro. Sem ponteiros.
Inspirada em relógios de "escala rotativa". Arte e código originais."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, polar, reduzir_por, tela, texto_centrado
from wf.kit import C, W, cabecalho, cor_config, finalizar, girar, hora, img, redondo, rgb, rect, strings_opcoes, tint

NOME = "regua"
PILULA = (284, 212, 184, 56)       # x, y, largura, altura
ACENTOS = [("branco", "#ffffff"), ("laranja", "#ff8a3d"), ("ciano", "#33d6ff"), ("verde", "#6bff9c"), ("rosa", "#ff5c93")]


def anel(r_rot: float, r_tick0: float, r_tick1: float, tam_fonte: float, tick_menor: bool) -> Image.Image:
    n = W * SS
    c = n / 2
    im = tela(n)
    d = ImageDraw.Draw(im)
    f = fonte("Medium", tam_fonte * SS)
    for m in range(60):
        a = m * 6
        maior = m % 5 == 0
        if not maior and not tick_menor:
            continue
        d.line([polar(c, c, (r_tick0 if maior else r_tick0 + (r_tick1 - r_tick0) * 0.45) * SS, a), polar(c, c, r_tick1 * SS, a)],
               fill=(255, 255, 255, 255 if maior else 120), width=int((3.2 if maior else 1.8) * SS))
        if maior:
            x, y = polar(c, c, r_rot * SS, a)
            texto_centrado(im, f"{m:02d}", x, y, f, (255, 255, 255, 235), rot=-a + (180 if 90 < a < 270 else 0))
    return reduzir_por(im)


def xml() -> str:
    x, y, w, h = PILULA
    ac = "[CONFIGURATION.acento]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS), "  </UserConfigurations>",
                                       '  <Scene backgroundColor="#ff000000">']
    a = L.append
    full = f'x="0" y="0" width="{W}" height="{W}"'
    a(f'    <Group name="anéis" {full}><Variant mode="AMBIENT" target="alpha" value="0" />'.replace("anéis", "aneis"))
    a("      " + img(0, 0, W, W, "anel_min", ' pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="90 - ([MINUTE] + [SECOND] / 60) * 6" />'))
    a("      " + img(0, 0, W, W, "anel_seg", ' pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="90 - [SECOND] * 6" />'))
    a("    </Group>")
    a(f'    <Group name="vivo" {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a("      " + hora(70, 150, 240, 180, "hh", 168, "#ffffffff", "BOLD", "CENTER"))
    a("      " + rect(x, y, w, h, "#ff000000", h // 2))
    a("      " + rect(x, y, w, h, ac, h // 2, "Stroke", 3.5))
    a("      " + hora(x + 14, y + 4, 78, h - 8, "mm", 42, "#ffffffff", "BOLD", "CENTER"))
    a("      " + hora(x + 104, y + 8, 66, h - 16, "ss", 30, ac, "MEDIUM", "CENTER"))
    a("    </Group>")
    a(f'    <Group name="ambiente" {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />')
    a("      " + hora(40, 110, 400, 150, "hh", 130, "#ffd0d0d6", "LIGHT", "CENTER"))
    a("      " + hora(40, 235, 400, 150, "mm", 130, "#ff8e8e94", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A: dict, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    ac = rgb(acento)
    if ambiente_:
        d.text((C, 185), f"{h:02d}", font=fonte("Light", 130), fill=(208, 208, 214), anchor="mm")
        d.text((C, 310), f"{mi:02d}", font=fonte("Light", 130), fill=(142, 142, 148), anchor="mm")
    else:
        base.alpha_composite(girar(A["anel_min"], (C, C), 90 - (mi + s / 60) * 6))
        base.alpha_composite(girar(A["anel_seg"], (C, C), 90 - s * 6))
        d = ImageDraw.Draw(base)
        d.text((190, 240), f"{h:02d}", font=fonte("Bold", 168), fill=(255, 255, 255), anchor="mm")
        x, y, w, hh = PILULA
        d.rounded_rectangle([x, y, x + w, y + hh], radius=hh // 2, fill=(0, 0, 0), outline=ac, width=4)
        d.text((x + 53, y + hh / 2), f"{mi:02d}", font=fonte("Bold", 42), fill=(255, 255, 255), anchor="mm")
        d.text((x + 137, y + hh / 2 + 1), f"{s:02d}", font=fonte("Medium", 30), fill=ac, anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Ruler", "acento_label": "Accent color"}
    pt = {"watch_face_name": "Régua", "acento_label": "Cor de destaque"}
    strings_opcoes(en, pt, "acento", {"branco": ("White", "Branco"), "laranja": ("Orange", "Laranja"), "ciano": ("Cyan", "Ciano"),
                                       "verde": ("Green", "Verde"), "rosa": ("Pink", "Rosa")})
    A = {"anel_min": anel(196, 212, 230, 22, True), "anel_seg": anel(128, 146, 160, 18, False)}
    pv = [previa(A, "#ffffff", 12, 45, 0), previa(A, "#ff8a3d", 3, 17, 38), previa(A, "#33d6ff", 9, 5, 21), previa(A, "#ffffff", 12, 45, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Branco", "Laranja", "Ciano", "Ambiente (AOD)"], cols=4,
                     nomes_previa=["branco", "laranja", "ciano", "ambiente"])
