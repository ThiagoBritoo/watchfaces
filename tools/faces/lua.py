"""Watchface "Lua": uma lua grande no centro mostrando a fase real do dia (8 fases, MOON_PHASE_TYPE), com estrelas e a hora embaixo. Original."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial
from wf.kit import C, W, cabecalho, colar, finalizar, grupo, hora, img, redondo, tpl

NOME = "lua"
R = 118
T = 2 * R + 40
CY = 200
NOMES = ["Nova", "Crescente", "Quarto crescente", "Gibosa crescente", "Cheia", "Gibosa minguante", "Quarto minguante", "Minguante"]


def fase(f: int) -> Image.Image:
    xx, yy = np.meshgrid(np.arange(T, dtype=np.float32), np.arange(T, dtype=np.float32))
    X, Y = (xx + 0.5 - T / 2) / R, (yy + 0.5 - T / 2) / R
    dentro = np.clip((1 - np.hypot(X, Y)) * R / 1.4, 0, 1)
    z = np.sqrt(np.clip(1 - X ** 2 - Y ** 2, 0, 1))
    ang = f * math.pi / 4
    lx, lz = -math.sin(ang), -math.cos(ang)
    ilum = np.clip((X * lx + z * lz) * 3.2, 0, 1)
    rng = np.random.default_rng(2)
    ruido = np.zeros((T, T), np.float32)
    for esc in (30, 14, 6):
        r = rng.random((T // esc + 2, T // esc + 2)).astype(np.float32)
        ruido += np.asarray(Image.fromarray((r * 255).astype(np.uint8)).resize((T, T), Image.BICUBIC), np.float32) / 255 * (esc / 30)
    ruido /= ruido.max()
    base = 205 + 40 * (ruido - 0.5)
    cor = 24 + (base - 24) * ilum
    out = np.zeros((T, T, 4), np.uint8)
    out[..., 0] = np.clip(cor * 0.98, 0, 255)
    out[..., 1] = np.clip(cor * 0.99, 0, 255)
    out[..., 2] = np.clip(cor, 0, 255)
    out[..., 3] = (dentro * 255).astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    halo = grad_radial(T, T / 2, T / 2, [(R * 0.95, (190, 205, 255, 80)), (R * 1.18, (190, 205, 255, 0))])
    cam = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    cam.alpha_composite(halo)
    cam.alpha_composite(im)
    ImageDraw.Draw(cam).ellipse([T / 2 - R, T / 2 - R, T / 2 + R, T / 2 + R], outline=(150, 165, 210, 90), width=2)
    return cam


def estrelas() -> Image.Image:
    rng = np.random.default_rng(14)
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(90):
        x, y = rng.integers(12, W - 12), rng.integers(12, W - 12)
        if (x - C) ** 2 + (y - C) ** 2 > 226 ** 2 or (x - C) ** 2 + (y - CY) ** 2 < 150 ** 2:
            continue
        r = float(rng.choice([0.8, 1.0, 1.4, 1.8]))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(rng.integers(90, 230))))
    return im


def xml() -> str:
    L = cabecalho(NOME, "DIGITAL") + ['  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + img(0, 0, W, W, "estrelas"))
    for f in range(8):
        a("      " + img(C - T // 2, CY - T // 2, T, T, f"fase_{f}", "", f'<Transform target="alpha" value="[MOON_PHASE_TYPE] == {f} ? 255 : 0" />'))
    a("      " + hora(60, 330, 360, 90, "hh:mm", 76, "#ffffffff", "LIGHT", "CENTER"))
    a("      " + tpl(110, 412, 260, 26, 18, "#ff9aa6c8", "%s", ["[MOON_PHASE_TYPE_STRING]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for f in range(8):
        a("      " + img(C - T // 2, CY - T // 2, T, T, f"fase_{f}", ' alpha="150"', f'<Transform target="alpha" value="[MOON_PHASE_TYPE] == {f} ? 150 : 0" />'))
    a("      " + hora(60, 336, 360, 90, "hh:mm", 70, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, f: int, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    if not ambiente_:
        base.alpha_composite(A["estrelas"])
    m = A[f"fase_{f}"].copy()
    if ambiente_:
        r, g, b, al = m.split()
        m = Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * 150 / 255))))
    colar(base, m, C - T // 2, CY - T // 2)
    d = ImageDraw.Draw(base)
    d.text((C, 375), f"{h:02d}:{mi:02d}", font=fonte("Light", 76 if not ambiente_ else 70), fill=(255, 255, 255) if not ambiente_ else (184, 184, 192), anchor="mm")
    if not ambiente_:
        d.text((C, 425), NOMES[f].lower(), font=fonte("Medium", 18), fill=(154, 166, 200), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Moon"}
    pt = {"watch_face_name": "Lua"}
    A = {f"fase_{f}": fase(f) for f in range(8)}
    A["estrelas"] = estrelas()
    pv = [previa(A, f, 22, 14) for f in (0, 2, 4, 6)] + [previa(A, 3, 22, 14), previa(A, 4, 22, 14, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Nova (0)", "Quarto crescente (2)", "Cheia (4)", "Quarto minguante (6)", "Gibosa crescente (3)", "Ambiente (AOD)"], cols=3,
                     nomes_previa=["nova", "q_cresc", "cheia", "q_ming", "gibosa", "ambiente"])
