"""Watchface "Nível": um nível de bolha de verdade: a bolha se move quando você inclina o pulso (sensor, elemento Gyro do WFF). A hora fica no centro da mira.
Cinco cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, grad_radial, polar, reduzir_por, tela
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, textos_acento, tint, tpl, colar

NOME = "nivel"
BOLHA = 84
R = 226


def mira() -> Image.Image:
    n = W * SS
    c = n / 2
    im = tela(n)
    d = ImageDraw.Draw(im)
    for r in (R, 170, 110, 50):
        d.ellipse([c - r * SS, c - r * SS, c + r * SS, c + r * SS], outline=(255, 255, 255, 190 if r == R else 90), width=int((3 if r == R else 1.5) * SS))
    d.line([(c, 14 * SS), (c, (480 - 14) * SS)], fill=(255, 255, 255, 80), width=int(1.4 * SS))
    d.line([(14 * SS, c), ((480 - 14) * SS, c)], fill=(255, 255, 255, 80), width=int(1.4 * SS))
    for g in range(0, 360, 10):
        d.line([polar(c, c, (R - (12 if g % 90 == 0 else 7)) * SS, g), polar(c, c, R * SS, g)], fill=(255, 255, 255, 220), width=int((3 if g % 90 == 0 else 1.6) * SS))
    return reduzir_por(im)


def bolha() -> Image.Image:
    g = grad_radial(BOLHA, BOLHA * 0.38, BOLHA * 0.34, [(0, (255, 255, 255, 235)), (BOLHA * 0.22, (255, 255, 255, 120)), (BOLHA * 0.46, (255, 255, 255, 60)), (BOLHA * 0.5, (255, 255, 255, 220))])
    m = Image.new("L", (BOLHA * 4, BOLHA * 4), 0)
    ImageDraw.Draw(m).ellipse([2, 2, BOLHA * 4 - 2, BOLHA * 4 - 2], fill=255)
    a = g.getchannel("A")
    g.putalpha(Image.composite(a, Image.new("L", g.size, 0), m.resize(g.size, Image.LANCZOS)))
    return g


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + img(0, 0, W, W, "mira", f' tintColor="{ac}"'))
    a("      " + hora(110, 190, 260, 100, "hh:mm", 70, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(150, 282, 180, 26, 18, "#ffa0a0a8", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a(f'      <PartImage x="{C - BOLHA // 2}" y="{C - BOLHA // 2}" width="{BOLHA}" height="{BOLHA}" tintColor="{ac}"><Image resource="bolha" />'
      '<Gyro x="ACCELEROMETER_ANGLE_X * 2.4" y="ACCELEROMETER_ANGLE_Y * 2.4" /></PartImage>')
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw x="0" y="0" width="{W}" height="{W}"><Ellipse x="{C - R}" y="{C - R}" width="{2 * R}" height="{2 * R}"><Stroke thickness="2" color="#66ffffff" /></Ellipse></PartDraw>')
    a("      " + hora(110, 195, 260, 100, "hh:mm", 84, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, dx: float, dy: float, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.ellipse([C - R, C - R, C + R, C + R], outline=(102, 102, 102), width=2)
        d.text((C, 245), f"{h:02d}:{mi:02d}", font=fonte("Light", 84), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    base.alpha_composite(tint(A["mira"], ac))
    d = ImageDraw.Draw(base)
    d.text((C, 240), f"{h:02d}:{mi:02d}", font=fonte("Bold", 70), fill=(255, 255, 255), anchor="mm")
    d.text((C, 295), "SEX 31", font=fonte("Medium", 18), fill=(160, 160, 168), anchor="mm")
    colar(base, tint(A["bolha"], ac), int(C - BOLHA / 2 + dx), int(C - BOLHA / 2 + dy))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Level", "Nível")
    A = {"mira": mira(), "bolha": bolha()}
    pv = [previa(A, "#4be37a", 10, 8, 0, 0), previa(A, "#33d6ff", 10, 8, 70, -50), previa(A, "#ff7a2f", 10, 8, -90, 40), previa(A, "#4be37a", 10, 8, 0, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Plano", "Inclinado (direita/cima)", "Inclinado (esquerda/baixo)", "Ambiente (AOD)"], cols=4, nomes_previa=["plano", "dir", "esq", "ambiente"])
