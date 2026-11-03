"""Watchface "Sistema Solar": um sol no centro, um planeta que dá a volta na órbita das horas, outro na dos minutos e uma lua que orbita o planeta dos
minutos a cada minuto (os segundos). Sem ponteiros. Quatro paletas de mundos. Original."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial, polar
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, strings_opcoes, tint, tpl, colar

NOME = "solar"
MUNDOS = [("terra", "#3d8bff #ff6b4a #e8eefc"), ("gelo", "#8fd3ff #c79bff #ffffff"), ("fogo", "#ff9d3d #ff4a6b #ffe6c2"), ("jade", "#4be3a0 #ffd23d #eafff4")]
RH, RM, RL = 96, 168, 34
PH, PM, PL = 46, 34, 14


def esfera(t: int) -> Image.Image:
    g = grad_radial(t, t * 0.38, t * 0.34, [(0, (255, 255, 255, 255)), (t * 0.3, (222, 222, 228, 255)), (t * 0.62, (84, 86, 98, 255)), (t * 0.9, (60, 62, 72, 255))])
    m = Image.new("L", (t * 4, t * 4), 0)
    ImageDraw.Draw(m).ellipse([4, 4, t * 4 - 4, t * 4 - 4], fill=255)
    g.putalpha(m.resize((t, t), Image.LANCZOS))
    return g


def sol() -> Image.Image:
    t = 120
    return grad_radial(t, t / 2, t / 2, [(0, (255, 255, 255, 255)), (22, (255, 246, 214, 255)), (30, (255, 214, 120, 190)), (60, (255, 190, 90, 0))])


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    p = lambda i: f"[CONFIGURATION.mundo.{i}]"  # noqa: E731
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("mundo", "mundo_label", MUNDOS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    for r in (RH, RM):
        a(f'      <PartDraw {full}><Ellipse x="{C - r}" y="{C - r}" width="{2 * r}" height="{2 * r}"><Stroke thickness="1.5" color="#33ffffff" /></Ellipse></PartDraw>')
    a("      " + img(C - 60, C - 60, 120, 120, "sol"))
    a(f'      <Group name="ph" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="[HOUR_0_11_MINUTE] * 30" />'
      + img(C - PH // 2, C - RH - PH // 2, PH, PH, "esfera_g", f' tintColor="{p(0)}"') + "</Group>")
    gw = 2 * RL + PM + 20
    a(f'      <Group name="pm" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="([MINUTE] + [SECOND] / 60) * 6" />'
      + img(C - PM // 2, C - RM - PM // 2, PM, PM, "esfera_m", f' tintColor="{p(1)}"')
      + f'<Group name="orb_lua" x="{C - gw // 2}" y="{C - RM - gw // 2}" width="{gw}" height="{gw}" pivotX="0.5" pivotY="0.5"><Transform target="angle" value="[SECOND] * 6" />'
      + f'<PartDraw x="0" y="0" width="{gw}" height="{gw}"><Ellipse x="{gw // 2 - RL}" y="{gw // 2 - RL}" width="{2 * RL}" height="{2 * RL}"><Stroke thickness="1" color="#33ffffff" /></Ellipse></PartDraw>'
      + img(gw // 2 - PL // 2, gw // 2 - RL - PL // 2, PL, PL, "esfera_p", f' tintColor="{p(2)}"') + "</Group></Group>")
    a("      " + hora(130, 388 - 12, 220, 50, "hh:mm", 34, "#ffffffff", "MEDIUM", "CENTER"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for r in (RH, RM):
        a(f'      <PartDraw {full}><Ellipse x="{C - r}" y="{C - r}" width="{2 * r}" height="{2 * r}"><Stroke thickness="1.5" color="#44ffffff" /></Ellipse></PartDraw>')
    for nome, r, d_, expr in (("h", RH, PH, "[HOUR_0_11_MINUTE] * 30"), ("m", RM, PM, "([MINUTE] + [SECOND] / 60) * 6")):
        a(f'      <Group name="a_{nome}" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="{expr}" />'
          f'<PartDraw x="{C - d_ // 4}" y="{C - r - d_ // 4}" width="{d_ // 2}" height="{d_ // 2}"><Ellipse x="0" y="0" width="{d_ // 2}" height="{d_ // 2}"><Fill color="#ffffffff" /></Ellipse></PartDraw></Group>')
    a("      " + hora(130, 388 - 12, 220, 50, "hh:mm", 34, "#ffb0b0b8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, mundo: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    cs = [rgb(c) for c in mundo.split()]
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    ah, am = (h % 12 + mi / 60) * 30, (mi + s / 60) * 6
    for r in (RH, RM):
        d.ellipse([C - r, C - r, C + r, C + r], outline=(255, 255, 255, 70) if not ambiente_ else (110, 110, 110), width=2)
    if not ambiente_:
        colar(base, A["sol"], C - 60, C - 60)
    for r, ang, t, cor, key in ((RH, ah, PH, cs[0], "esfera_g"), (RM, am, PM, cs[1], "esfera_m")):
        x, y = polar(C, C, r, ang)
        if ambiente_:
            d = ImageDraw.Draw(base)
            d.ellipse([x - t / 4, y - t / 4, x + t / 4, y + t / 4], fill=(255, 255, 255))
        else:
            base.alpha_composite(tint(A[key], cor), (int(x - t / 2), int(y - t / 2)))
    if not ambiente_:
        px, py = polar(C, C, RM, am)
        d = ImageDraw.Draw(base)
        d.ellipse([px - RL, py - RL, px + RL, py + RL], outline=(255, 255, 255, 51), width=1)
        lx, ly = polar(px, py, RL, s * 6)
        base.alpha_composite(tint(A["esfera_p"], cs[2]), (int(lx - PL / 2), int(ly - PL / 2)))
    d = ImageDraw.Draw(base)
    d.text((C, 392), f"{h:02d}:{mi:02d}", font=fonte("Medium" if not ambiente_ else "Light", 34), fill=(255, 255, 255) if not ambiente_ else (176, 176, 184), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Solar System", "mundo_label": "Worlds"}
    pt = {"watch_face_name": "Sistema Solar", "mundo_label": "Mundos"}
    strings_opcoes(en, pt, "mundo", {"terra": ("Earth", "Terra"), "gelo": ("Ice", "Gelo"), "fogo": ("Fire", "Fogo"), "jade": ("Jade", "Jade")})
    A = {"sol": sol(), "esfera_g": esfera(PH), "esfera_m": esfera(PM), "esfera_p": esfera(PL)}
    pv = [previa(A, MUNDOS[0][1], 10, 8, 20), previa(A, MUNDOS[1][1], 4, 47, 50), previa(A, MUNDOS[2][1], 8, 20, 5), previa(A, MUNDOS[3][1], 1, 55, 35), previa(A, MUNDOS[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Terra", "Gelo", "Fogo", "Jade", "Ambiente (AOD)"], cols=5, nomes_previa=["terra", "gelo", "fogo", "jade", "ambiente"])
