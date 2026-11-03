"""Watchface "Rádio": mostrador de rádio antigo. A agulha de sintonia percorre a escala de 88 a 108 MHz conforme os minutos (0 a 59); a hora vai grande
na janela e a data embaixo. Quatro madeiras/cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, grad_linear, reduzir_por, tela, texto_centrado
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rect, rgb, strings_opcoes, tint, tpl, colar

NOME = "radio"
ESC = (56, 168, 424)                      # x inicial, y da régua, x final
VIDROS = [("ambar", "#ffcf6b #2a1606 #ff4d2e"), ("verde", "#9dffb8 #08200f #ff4d2e"), ("azul", "#a8d8ff #08142a #ffd24d"), ("creme", "#fff3d6 #2a2118 #d6402b")]


def escala() -> Image.Image:
    n = W * SS
    im = tela(n)
    d = ImageDraw.Draw(im)
    x0, y, x1 = ESC
    f = fonte("SemiBold", 17 * SS)
    for k in range(0, 41):
        x = x0 + (x1 - x0) * k / 40
        mj = k % 4 == 0
        d.line([(x * SS, (y - (18 if mj else 9)) * SS), (x * SS, (y + 2) * SS)], fill=(255, 255, 255, 255 if mj else 170), width=int((2.6 if mj else 1.4) * SS))
        if mj:
            texto_centrado(im, str(88 + k // 2), x * SS, (y - 34) * SS, f, (255, 255, 255, 255))
    d.line([(x0 * SS, (y + 2) * SS), (x1 * SS, (y + 2) * SS)], fill=(255, 255, 255, 220), width=int(2 * SS))
    texto_centrado(im, "FM  MHz", C * SS, (y + 28) * SS, fonte("Medium", 14 * SS), (255, 255, 255, 200), espaco=2 * SS)
    return reduzir_por(im)


def agulha() -> Image.Image:
    return Image.new("RGBA", (6, 74), (255, 255, 255, 255))


def xml() -> str:
    p = lambda i: f"[CONFIGURATION.vidro.{i}]"  # noqa: E731
    x0, y, x1 = ESC
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("vidro", "vidro_label", VIDROS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + rect(24, 120, 432, 252, p(1), 40))
    a("      " + rect(24, 120, 432, 252, "#ff8a6a3c", 40, "Stroke", 4))
    a("      " + img(0, 0, W, W, "escala", f' tintColor="{p(0)}"'))
    a("      " + hora(80, 190, 320, 90, "hh:mm", 72, p(0), "BOLD", "CENTER"))
    a(f'      <PartDraw x="{x0 - 2}" y="{y - 40}" width="6" height="74"><Transform target="x" value="{x0 - 2} + ({x1 - x0}) * [MINUTE] / 60" />'
      f'<Rectangle x="0" y="0" width="6" height="74"><Fill color="{p(2)}" /></Rectangle></PartDraw>')
    a("      " + tpl(130, 332, 220, 26, 18, p(0), "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw x="0" y="0" width="{W}" height="{W}"><Rectangle x="{x0}" y="{y + 2}" width="{x1 - x0}" height="2"><Fill color="#66ffffff" /></Rectangle></PartDraw>')
    a(f'      <PartDraw x="{x0 - 1}" y="{y - 30}" width="4" height="60"><Transform target="x" value="{x0 - 1} + ({x1 - x0}) * [MINUTE] / 60" /><Rectangle x="0" y="0" width="4" height="60"><Fill color="#ffffffff" /></Rectangle></PartDraw>')
    a("      " + hora(80, 200, 320, 90, "hh:mm", 72, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, vidro: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c0, c1, c2 = (rgb(c) for c in vidro.split())
    x0, y, x1 = ESC
    x = x0 - 2 + (x1 - x0) * mi / 60
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.rectangle([x0, y + 2, x1, y + 4], fill=(102, 102, 102))
        d.rectangle([x, y - 30, x + 4, y + 30], fill=(255, 255, 255))
        d.text((C, 245), f"{h:02d}:{mi:02d}", font=fonte("Light", 72), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    d.rounded_rectangle([24, 120, 456, 372], radius=40, fill=c1, outline=(138, 106, 60), width=4)
    base.alpha_composite(tint(A["escala"], c0))
    d = ImageDraw.Draw(base)
    d.text((C, 235), f"{h:02d}:{mi:02d}", font=fonte("Bold", 72), fill=c0, anchor="mm")
    d.rectangle([x, y - 40, x + 6, y + 34], fill=c2)
    d.text((C, 345), "SEX 31 OUT", font=fonte("Medium", 18), fill=c0, anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Radio", "vidro_label": "Dial glass"}
    pt = {"watch_face_name": "Rádio", "vidro_label": "Vidro do mostrador"}
    strings_opcoes(en, pt, "vidro", {"ambar": ("Amber", "Âmbar"), "verde": ("Green", "Verde"), "azul": ("Blue", "Azul"), "creme": ("Cream", "Creme")})
    A = {"escala": escala()}
    pv = [previa(A, VIDROS[0][1], 10, 8, 0), previa(A, VIDROS[1][1], 3, 45, 0), previa(A, VIDROS[2][1], 7, 30, 0), previa(A, VIDROS[3][1], 21, 52, 0), previa(A, VIDROS[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Âmbar", "Verde", "Azul", "Creme", "Ambiente (AOD)"], cols=5, nomes_previa=["ambar", "verde", "azul", "creme", "ambiente"])
