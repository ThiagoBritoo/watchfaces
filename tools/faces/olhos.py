"""Watchface "Olhos": dois olhos grandes e simpáticos. A pupila do olho esquerdo olha na direção da hora e a do direito na direção dos minutos (como
ponteiros). A hora aparece embaixo em texto. Abstrata e divertida. Cinco cores de íris. Original."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial
from wf.kit import C, W, cabecalho, colar, cor_config, finalizar, grupo, hora, img, redondo, rgb, strings_opcoes, tint, tpl

NOME = "olhos"
IRIS = [("azul", "#4aa8ff"), ("verde", "#4be37a"), ("ambar", "#ffb347"), ("rosa", "#ff7ac8"), ("cinza", "#c4cad6")]
OX = (C - 86, C + 86)
OY = 190
RO = 78                       # raio do olho
RI = 40                       # raio da íris
PUP = 24                      # raio da pupila
ALC = 30                      # alcance do movimento do olhar


def olho() -> Image.Image:
    t = 2 * RO + 12
    g = grad_radial(t, t / 2 - 10, t / 2 - 14, [(0, (255, 255, 255, 255)), (RO * 0.7, (246, 246, 250, 255)), (RO * 1.05, (200, 204, 214, 255))])
    m = Image.new("L", (t * 4, t * 4), 0)
    ImageDraw.Draw(m).ellipse([24, 24, t * 4 - 24, t * 4 - 24], fill=255)
    g.putalpha(m.resize((t, t), Image.LANCZOS))
    ImageDraw.Draw(g).ellipse([t / 2 - RO, t / 2 - RO, t / 2 + RO, t / 2 + RO], outline=(60, 62, 72, 255), width=3)
    return g


def iris() -> Image.Image:
    t = 2 * RI + 4
    g = grad_radial(t, t / 2, t / 2, [(0, (255, 255, 255, 255)), (RI * 0.55, (222, 222, 222, 255)), (RI * 0.95, (150, 150, 150, 255)), (RI, (110, 110, 110, 255))])
    m = Image.new("L", (t * 4, t * 4), 0)
    ImageDraw.Draw(m).ellipse([8, 8, t * 4 - 8, t * 4 - 8], fill=255)
    g.putalpha(m.resize((t, t), Image.LANCZOS))
    return g


def pupila() -> Image.Image:
    t = 2 * PUP + 4
    im = Image.new("RGBA", (t * 4, t * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([8, 8, t * 4 - 8, t * 4 - 8], fill=(10, 10, 14, 255))
    d.ellipse([t * 4 * 0.52, t * 4 * 0.18, t * 4 * 0.78, t * 4 * 0.42], fill=(255, 255, 255, 235))
    return im.resize((t, t), Image.LANCZOS)


def xml() -> str:
    p = "[CONFIGURATION.iris]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("iris", "iris_label", IRIS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    t, ti, tp = 2 * RO + 12, 2 * RI + 4, 2 * PUP + 4
    a("    " + grupo("vivo", "", 0))
    for k, cx in enumerate(OX):
        ang = "[HOUR_0_11_MINUTE] * 30" if k == 0 else "([MINUTE] + [SECOND] / 60) * 6"
        a("      " + img(cx - t // 2, OY - t // 2, t, t, "olho"))
        # a íris e a pupila se deslocam na direção do ponteiro (x = sin, y = -cos)
        a("      " + img(cx - ti // 2, OY - ti // 2, ti, ti, "iris", f' tintColor="{p}"', f'<Transform target="x" value="{cx - ti // 2} + {ALC} * sin(({ang}) * 0.0174533)" /><Transform target="y" value="{OY - ti // 2} - {ALC} * cos(({ang}) * 0.0174533)" />'))
        a("      " + img(cx - tp // 2, OY - tp // 2, tp, tp, "pupila", "", f'<Transform target="x" value="{cx - tp // 2} + {ALC + 4} * sin(({ang}) * 0.0174533)" /><Transform target="y" value="{OY - tp // 2} - {ALC + 4} * cos(({ang}) * 0.0174533)" />'))
    a("      " + hora(60, 300, 360, 100, "hh:mm", 84, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(110, 392, 260, 28, 20, "#ff8e8e96", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for cx in OX:
        a(f'      <PartDraw x="0" y="0" width="{W}" height="{W}"><Ellipse x="{cx - RO}" y="{OY - RO}" width="{2 * RO}" height="{2 * RO}"><Stroke thickness="2" color="#88ffffff" /></Ellipse></PartDraw>')
    for k, cx in enumerate(OX):
        ang = "[HOUR_0_11_MINUTE] * 30" if k == 0 else "[MINUTE] * 6"
        a(f'      <PartDraw x="{cx - 14}" y="{OY - 14}" width="28" height="28"><Transform target="x" value="{cx - 14} + {ALC + 4} * sin(({ang}) * 0.0174533)" /><Transform target="y" value="{OY - 14} - {ALC + 4} * cos(({ang}) * 0.0174533)" />'
          f'<Ellipse x="0" y="0" width="28" height="28"><Fill color="#ffffffff" /></Ellipse></PartDraw>')
    a("      " + hora(60, 300, 360, 100, "hh:mm", 76, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, iris_hex: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ic = rgb(iris_hex)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    angs = ((h % 12 + mi / 60) * 30, (mi + (0 if ambiente_ else s / 60)) * 6)
    t = 2 * RO + 12
    for cx, ang in zip(OX, angs):
        dx, dy = math.sin(math.radians(ang)), -math.cos(math.radians(ang))
        if ambiente_:
            d.ellipse([cx - RO, OY - RO, cx + RO, OY + RO], outline=(136, 136, 136), width=2)
            x, y = cx + (ALC + 4) * dx, OY + (ALC + 4) * dy
            d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(255, 255, 255))
            continue
        base.alpha_composite(A["olho"], (cx - t // 2, OY - t // 2))
        colar(base, tint(A["iris"], ic), int(cx + ALC * dx - A["iris"].width / 2), int(OY + ALC * dy - A["iris"].height / 2))
        colar(base, A["pupila"], int(cx + (ALC + 4) * dx - A["pupila"].width / 2), int(OY + (ALC + 4) * dy - A["pupila"].height / 2))
    d = ImageDraw.Draw(base)
    d.text((C, 350), f"{h:02d}:{mi:02d}", font=fonte("Bold" if not ambiente_ else "Light", 84 if not ambiente_ else 76), fill=(255, 255, 255) if not ambiente_ else (192, 192, 200), anchor="mm")
    if not ambiente_:
        d.text((C, 406), "SEX 31 OUT", font=fonte("Medium", 20), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Eyes", "iris_label": "Eye color"}
    pt = {"watch_face_name": "Olhos", "iris_label": "Cor dos olhos"}
    strings_opcoes(en, pt, "iris", {"azul": ("Blue", "Azul"), "verde": ("Green", "Verde"), "ambar": ("Amber", "Âmbar"), "rosa": ("Pink", "Rosa"), "cinza": ("Gray", "Cinza")})
    A = {"olho": olho(), "iris": iris(), "pupila": pupila()}
    pv = [previa(A, "#4aa8ff", 10, 8, 20), previa(A, "#4be37a", 3, 45, 40), previa(A, "#ffb347", 7, 22, 5), previa(A, "#4aa8ff", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["10:08", "03:45", "07:22", "Ambiente (AOD)"], cols=4, nomes_previa=["h1008", "h0345", "h0722", "ambiente"])
