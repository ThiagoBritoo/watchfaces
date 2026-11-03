"""Watchface "Chomp": uma bolinha de boca aberta percorre o anel comendo os pontos (os pontos dos minutos já passados somem) e a boca abre e fecha a
cada segundo; a hora fica no centro. Personagem original. Seis cores."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte, polar
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, textos_acento, tint, tpl, colar

NOME = "chomp"
R = 208
SP = 46


def sprite(boca: float) -> Image.Image:
    s = 4
    t = SP + 8
    im = Image.new("RGBA", (t * s, t * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = t * s / 2
    r = SP / 2 * s
    d.pieslice([c - r, c - r, c + r, c + r], boca / 2, 360 - boca / 2, fill=(255, 255, 255, 255))     # boca para a direita (0 graus)
    d.ellipse([c + 2 * s, c - 14 * s, c + 9 * s, c - 7 * s], fill=(20, 20, 24, 255))
    return im.resize((t, t), Image.LANCZOS)


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    t = SP + 8
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    for j in range(60):
        x, y = polar(C, C, R, j * 6)
        tam = 14 if j % 5 == 0 else 8
        a(f'      <PartDraw x="{round(x - tam / 2)}" y="{round(y - tam / 2)}" width="{tam}" height="{tam}"><Transform target="alpha" value="[MINUTE] &lt; {j} ? 255 : 0" />'
          f'<Ellipse x="0" y="0" width="{tam}" height="{tam}"><Fill color="#ffffffff" /></Ellipse></PartDraw>')
    a(f'      <Group name="comilao" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="([MINUTE] + [SECOND] / 60) * 6" />'
      + img(C - t // 2, C - R - t // 2, t, t, "aberto", f' tintColor="{ac}"', '<Transform target="alpha" value="[SECOND] % 2 == 0 ? 255 : 0" />')
      + img(C - t // 2, C - R - t // 2, t, t, "fechado", f' tintColor="{ac}"', '<Transform target="alpha" value="[SECOND] % 2 == 1 ? 255 : 0" />') + "</Group>")
    a("      " + hora(60, 150, 360, 140, "hh:mm", 100, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(130, 270, 220, 28, 20, "#ffa0a0a8", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for j in range(0, 60, 5):
        x, y = polar(C, C, R, j * 6)
        a(f'      <PartDraw x="{round(x - 5)}" y="{round(y - 5)}" width="10" height="10"><Transform target="alpha" value="[MINUTE] &lt; {j} ? 255 : 0" />'
          f'<Ellipse x="0" y="0" width="10" height="10"><Fill color="#ffb0b0b8" /></Ellipse></PartDraw>')
    a(f'      <Group name="comilao_a" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="[MINUTE] * 6" />' + img(C - t // 2, C - R - t // 2, t, t, "fechado", ' tintColor="#ffd0d0d6"') + "</Group>")
    a("      " + hora(60, 160, 360, 140, "hh:mm", 92, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    for j in range(60):
        if ambiente_ and j % 5:
            continue
        if mi < j:
            x, y = polar(C, C, R, j * 6)
            tam = (14 if j % 5 == 0 else 8) if not ambiente_ else 10
            d.ellipse([x - tam / 2, y - tam / 2, x + tam / 2, y + tam / 2], fill=(255, 255, 255) if not ambiente_ else (176, 176, 184))
    ang = (mi + (0 if ambiente_ else s / 60)) * 6
    sp = tint(A["fechado" if (ambiente_ or s % 2) else "aberto"], (208, 208, 214) if ambiente_ else ac)
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cam.alpha_composite(sp, (C - sp.width // 2, C - R - sp.height // 2))
    base.alpha_composite(cam.rotate(-ang, center=(C, C), resample=Image.BICUBIC))
    d = ImageDraw.Draw(base)
    d.text((C, 225), f"{h:02d}:{mi:02d}", font=fonte("Bold" if not ambiente_ else "Light", 100 if not ambiente_ else 92), fill=(255, 255, 255) if not ambiente_ else (192, 192, 200), anchor="mm")
    if not ambiente_:
        d.text((C, 284), "SEX 31 OUT", font=fonte("Medium", 20), fill=(160, 160, 168), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Chomp", "Chomp")
    A = {"aberto": sprite(70), "fechado": sprite(6)}
    pv = [previa(A, "#f2c14e", 10, 8, 2), previa(A, "#33d6ff", 10, 31, 3), previa(A, "#ff5c93", 7, 52, 20), previa(A, "#f2c14e", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Boca aberta", "Boca fechada", "Rosa 07:52", "Ambiente (AOD)"], cols=4, nomes_previa=["aberta", "fechada", "rosa", "ambiente"])
