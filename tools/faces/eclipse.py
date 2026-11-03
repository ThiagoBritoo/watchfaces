"""Watchface "Eclipse": a Lua atravessa o Sol ao longo de cada hora (Sol cheio no minuto 0, eclipse total no 30, Sol cheio de
novo no 60). Hora em texto fino embaixo e uma faísca na coroa marcando os segundos. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grade
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, textos_acento, tint, tpl, colar

NOME = "eclipse"
RS, RL = 112, 116                 # raio do Sol e da Lua
CY = 190                          # centro do Sol
LADO = 460                        # lado da imagem da coroa
OFF = 3.6                         # px por minuto de deslocamento da Lua


def corona() -> Image.Image:
    xx, yy = grade(LADO)
    dx, dy = xx - LADO / 2, yy - LADO / 2
    r = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)
    raios = 0.55 + 0.25 * np.sin(ang * 7 + 1.2) + 0.12 * np.sin(ang * 13 + 0.4) + 0.08 * np.sin(ang * 23)
    f = np.clip((r - RS + 6) / 150, 0, 1)
    a = np.clip((1 - f) ** 2.2 * (0.55 + raios * 0.7), 0, 1)
    a = np.where(r < RS - 2, 1.0, a) * np.clip((LADO / 2 - r) / 20, 0, 1)
    out = np.zeros((LADO, LADO, 4), np.uint8)
    out[..., :3] = 255
    out[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def lua() -> Image.Image:
    t = 2 * RL + 12
    m = Image.new("L", (t * 4, t * 4), 0)
    ImageDraw.Draw(m).ellipse([24, 24, t * 4 - 24, t * 4 - 24], fill=255)
    xx, yy = grade(t)
    dist = np.hypot(xx - t / 2, yy - t / 2) / RL
    rim = np.clip(1 - np.abs(dist - 1) * 14, 0, 1) * 70
    out = np.zeros((t, t, 4), np.uint8)
    out[..., 0] = out[..., 1] = out[..., 2] = rim.astype(np.uint8) + 4
    im = Image.fromarray(out, "RGBA")
    im.putalpha(m.resize((t, t), Image.LANCZOS))
    return im


def faisca() -> Image.Image:
    from wf.desenho import grad_radial
    return grad_radial(40, 20, 20, [(0, (255, 255, 255, 255)), (4, (255, 255, 255, 255)), (9, (255, 255, 255, 120)), (19, (255, 255, 255, 0))])


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    tl = 2 * RL + 12
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("sol", "", 0))
    a("      " + img(C - LADO // 2, CY - LADO // 2, LADO, LADO, "corona", f' tintColor="{ac}"'))
    a(f'      <Group name="faisca" x="0" y="0" width="{W}" height="{W}" pivotX="0.5" pivotY="{CY / W:.4f}"><Transform target="angle" value="[SECOND] * 6" />'
      + img(C - 20, CY - 150 - 20, 40, 40, "faisca", f' tintColor="{ac}"') + "</Group>")
    a("      " + img(C - tl // 2, CY - tl // 2, tl, tl, "lua", "", f'<Transform target="x" value="{C - tl // 2} + ([MINUTE] + [SECOND] / 60 - 30) * {OFF}" />'))
    a("      " + hora(40, 330, 400, 100, "hh:mm", 80, "#ffffffff", "LIGHT", "CENTER"))
    a("      " + tpl(110, 428, 260, 28, 20, "#ff8e8e96", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw {full}><Ellipse x="{C - RS}" y="{CY - RS}" width="{2 * RS}" height="{2 * RS}"><Stroke thickness="2" color="#99ffffff" /></Ellipse></PartDraw>')
    a("      " + img(C - tl // 2, CY - tl // 2, tl, tl, "lua", "", f'<Transform target="x" value="{C - tl // 2} + ([MINUTE] - 30) * {OFF}" />'))
    a("      " + hora(40, 340, 400, 90, "hh:mm", 72, "#ffb0b0b8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    tl = 2 * RL + 12
    off = (mi + (0 if ambiente_ else s / 60) - 30) * OFF
    if ambiente_:
        d.ellipse([C - RS, CY - RS, C + RS, CY + RS], outline=(153, 153, 153), width=2)
    else:
        colar(base, tint(A["corona"], ac), C - LADO // 2, CY - LADO // 2)
        sp = A["faisca"]
        a_ = math.radians(s * 6)
        base.alpha_composite(sp, (int(C + 150 * math.sin(a_) - 20), int(CY - 150 * math.cos(a_) - 20)))
    base.alpha_composite(A["lua"], (int(C - tl / 2 + off), int(CY - tl / 2)))
    d = ImageDraw.Draw(base)
    d.text((C, 380), f"{h:02d}:{mi:02d}", font=fonte("Light", 80 if not ambiente_ else 72), fill=(255, 255, 255) if not ambiente_ else (176, 176, 184), anchor="mm")
    if not ambiente_:
        d.text((C, 442), "SEX 31 OUT", font=fonte("Medium", 20), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Eclipse", "Eclipse")
    A = {"corona": corona(), "lua": lua(), "faisca": faisca()}
    pv = [previa(A, "#f2c14e", 10, 8, 20), previa(A, "#33d6ff", 10, 30, 0), previa(A, "#ff7a2f", 10, 52, 40), previa(A, "#f2c14e", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Minuto 8", "Minuto 30 (total)", "Minuto 52", "Ambiente (AOD)"], cols=4, nomes_previa=["m08", "m30", "m52", "ambiente"])
