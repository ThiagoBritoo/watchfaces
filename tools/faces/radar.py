"""Watchface "Radar": tela de radar de fósforo; a varredura gira uma volta por minuto (um passo a cada segundo) e dois alvos
marcam a hora e o minuto. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, grad_radial, grade, polar, reduzir_por, tela, texto_centrado
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rgb, strings_opcoes, tint, tpl

NOME = "radar"
FOSFOROS = [("verde", "#33ff77"), ("ambar", "#ffb000"), ("ciano", "#33e0ff"), ("branco", "#e8f0e8")]
RH, RM = 96, 170
ALVO = 56


def grade_radar() -> Image.Image:
    n = W * SS
    c = n / 2
    im = tela(n)
    d = ImageDraw.Draw(im)
    for r in (60, 120, 180, 230):
        d.ellipse([c - r * SS, c - r * SS, c + r * SS, c + r * SS], outline=(255, 255, 255, 120 if r != 230 else 230), width=int((1.6 if r != 230 else 3) * SS))
    for g in range(0, 360, 30):
        d.line([polar(c, c, 0, g), polar(c, c, 230 * SS, g)], fill=(255, 255, 255, 70), width=int(1.2 * SS))
    for m in range(60):
        a = m * 6
        d.line([polar(c, c, (216 if m % 5 == 0 else 222) * SS, a), polar(c, c, 230 * SS, a)], fill=(255, 255, 255, 220), width=int((2.6 if m % 5 == 0 else 1.4) * SS))
    f = fonte("Medium", 16 * SS)
    for g in range(0, 360, 90):
        x, y = polar(c, c, 202 * SS, g)
        texto_centrado(im, {0: "N", 90: "L", 180: "S", 270: "O"}[g], x, y, f, (255, 255, 255, 230))
    return reduzir_por(im)


def varredura() -> Image.Image:
    xx, yy = grade(W)
    dx, dy = xx + 0.5 - C, yy + 0.5 - C
    r = np.hypot(dx, dy)
    th = (np.degrees(np.arctan2(dx, -dy)) % 360)        # 0 = 12h, horário
    atras = (360 - th) % 360                              # graus "atrás" da linha da varredura (que fica em 0)
    a = np.clip(1 - atras / 95.0, 0, 1) ** 2.2 * 0.9
    a = np.where(r < 232, a, 0)
    linha = np.clip(1 - np.minimum(th, 360 - th) / 1.4, 0, 1)
    a = np.maximum(a, np.where(r < 232, linha, 0))
    out = np.zeros((W, W, 4), np.uint8)
    out[..., :3] = 255
    out[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def alvo() -> Image.Image:
    return grad_radial(ALVO, ALVO / 2, ALVO / 2, [(0, (255, 255, 255, 255)), (6, (255, 255, 255, 255)), (10, (255, 255, 255, 110)), (ALVO / 2, (255, 255, 255, 0))])


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    fo = "[CONFIGURATION.fosforo]"
    L = cabecalho(NOME) + ["  <UserConfigurations>", cor_config("fosforo", "fosforo_label", FOSFOROS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("tela", f' tintColor="{fo}"', 0))
    a("      " + img(0, 0, W, W, "grade"))
    a("      " + img(0, 0, W, W, "varredura", ' pivotX="0.5" pivotY="0.5"', '<Transform target="angle" value="[SECOND] * 6" />'))
    for nome, r, expr, esc in (("h", RH, "[HOUR_0_11_MINUTE] * 30", 1.0), ("m", RM, "([MINUTE] + [SECOND] / 60) * 6", 0.7)):
        tam = int(ALVO * esc)
        a(f'      <Group name="alvo_{nome}" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="{expr}" />'
          + img(C - tam // 2, C - r - tam // 2, tam, tam, "alvo") + "</Group>")
    a("      " + hora(130, 196, 220, 70, "hh:mm", 54, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(140, 254, 200, 26, 18, "#ccffffff", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", f' alpha="0" tintColor="{fo}"', 255))
    a("      " + img(0, 0, W, W, "grade", ' alpha="90"'))
    a("      " + hora(130, 200, 220, 70, "hh:mm", 54, "#ffc0c0c0", "MEDIUM", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, cor: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c = rgb(cor)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    if ambiente_:
        g = A["grade"].copy()
        r_, g_, b_, a_ = g.split()
        cam.alpha_composite(Image.merge("RGBA", (r_, g_, b_, a_.point(lambda v: int(v * 90 / 255)))))
        ImageDraw.Draw(cam).text((C, 235), f"{h:02d}:{mi:02d}", font=fonte("Medium", 54), fill=(192, 192, 192, 255), anchor="mm")
    else:
        cam.alpha_composite(A["grade"])
        cam.alpha_composite(A["varredura"].rotate(-s * 6, center=(C, C), resample=Image.BICUBIC))
        for r, ang, esc in ((RH, (h % 12 + mi / 60) * 30, 1.0), (RM, (mi + s / 60) * 6, 0.7)):
            t = A["alvo"].resize((int(ALVO * esc),) * 2, Image.LANCZOS)
            x, y = polar(C, C, r, ang)
            cam.alpha_composite(t, (int(x - t.width / 2), int(y - t.height / 2)))
        dd = ImageDraw.Draw(cam)
        dd.text((C, 231), f"{h:02d}:{mi:02d}", font=fonte("Bold", 54), fill=(255, 255, 255, 255), anchor="mm")
        dd.text((C, 266), "SEX 31", font=fonte("Medium", 18), fill=(255, 255, 255, 200), anchor="mm")
    base.alpha_composite(tint(cam, c))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Radar", "fosforo_label": "Phosphor"}
    pt = {"watch_face_name": "Radar", "fosforo_label": "Fósforo"}
    strings_opcoes(en, pt, "fosforo", {"verde": ("Green", "Verde"), "ambar": ("Amber", "Âmbar"), "ciano": ("Cyan", "Ciano"), "branco": ("White", "Branco")})
    A = {"grade": grade_radar(), "varredura": varredura(), "alvo": alvo()}
    pv = [previa(A, "#33ff77", 10, 8, 20), previa(A, "#ffb000", 4, 47, 50), previa(A, "#33e0ff", 8, 20, 5), previa(A, "#33ff77", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Verde", "Âmbar", "Ciano", "Ambiente (AOD)"], cols=4, nomes_previa=["verde", "ambar", "ciano", "ambiente"])
