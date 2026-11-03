"""Watchface "Céu do Dia": o fundo é o céu real do horário (madrugada, aurora, dia, entardecer, noite); sol e lua cruzam o céu num arco
sobre uma silhueta de montanhas. Hora em texto fino. Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial, grade, ruido
from wf.kit import C, W, cabecalho, colar, finalizar, grupo, hora, img, redondo, textos_acento, tpl

NOME = "ceu"
FAIXA = 1920
PIV_Y = 424
RAIO = 214
PARADAS = [(0, (5, 10, 31)), (4.5, (14, 24, 66)), (6.0, (120, 70, 110)), (7.0, (255, 140, 96)), (8.5, (120, 190, 255)), (12, (62, 160, 255)),
           (16.5, (122, 190, 255)), (18.0, (255, 150, 90)), (19.2, (150, 60, 100)), (20.5, (40, 28, 90)), (22, (12, 18, 52)), (24, (5, 10, 31))]


def faixa() -> Image.Image:
    xs = np.arange(FAIXA) / FAIXA * 24
    cols = np.array([c for _, c in PARADAS], np.float32)
    pos = [p for p, _ in PARADAS]
    base = np.stack([np.interp(xs, pos, cols[:, k]) for k in range(3)], -1)
    yy = np.linspace(0, 1, W)[:, None, None]
    topo = base[None, :, :] * (0.82 + 0.18 * (1 - yy))                      # mais escuro no alto
    horiz = np.clip((yy - 0.55) / 0.45, 0, 1) * 0.35                         # clareia perto do horizonte
    img_ = topo * (1 - horiz) + np.clip(base[None, :, :] * 1.25 + 30, 0, 255) * horiz
    img_ += np.random.default_rng(3).normal(0, 1.4, img_.shape)
    out = np.dstack([np.clip(img_, 0, 255), np.full((W, FAIXA), 255)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def estrelas() -> Image.Image:
    rng = np.random.default_rng(9)
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(70):
        x, y = rng.integers(10, W - 10), rng.integers(10, 330)
        r = float(rng.choice([1, 1, 1.5, 2]))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(rng.integers(120, 255))))
    return im


def astro(lua_: bool) -> Image.Image:
    t = 80
    if lua_:
        from wf.desenho import grad_radial as gr
        im = gr(t, 40, 40, [(0, (240, 244, 255, 255)), (22, (226, 232, 250, 255)), (26, (200, 210, 240, 90)), (39, (200, 210, 240, 0))])
        m = Image.new("L", (t * 4, t * 4), 0)
        d = ImageDraw.Draw(m)
        d.ellipse([60, 60, t * 4 - 60, t * 4 - 60], fill=255)
        d.ellipse([60 + 70, 60 - 24, t * 4 - 60 + 70, t * 4 - 60 - 24], fill=0)   # crescente
        mm = np.asarray(m.resize((t, t), Image.LANCZOS), np.float32) / 255
        a = np.asarray(im).astype(np.float32).copy()
        a[..., 3] = np.maximum(a[..., 3] * 0.35, a[..., 3] * mm)
        return Image.fromarray(a.astype(np.uint8), "RGBA")
    return grad_radial(t, 40, 40, [(0, (255, 255, 255, 255)), (20, (255, 252, 235, 255)), (26, (255, 235, 180, 180)), (39, (255, 220, 150, 0))])


def silhueta() -> Image.Image:
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rnd = np.random.default_rng(5)
    xs = np.linspace(0, W, 60)
    ys = 420 - (np.abs(np.sin(xs / 61.0 + 1)) * 34 + np.abs(np.sin(xs / 23.0)) * 12 + np.abs(np.sin(xs / 9.0 + 2)) * 5)
    pts = [(x * s, y * s) for x, y in zip(xs, ys)] + [(W * s, W * s), (0, W * s)]
    d.polygon(pts, fill=(4, 6, 12, 255))
    return im.resize((W, W), Image.LANCZOS)


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    gx, gy, gw, gh = C - 220, 0, 440, PIV_Y
    dia = "([HOUR_0_23] &gt;= 6 &amp;&amp; [HOUR_0_23] &lt; 18)"
    ang_dia = "-84 + 168 * clamp(([HOUR_0_23_MINUTE] - 6) / 12, 0, 1)"
    ang_noite = "-84 + 168 * clamp((([HOUR_0_23_MINUTE] &gt;= 18 ? [HOUR_0_23_MINUTE] - 18 : [HOUR_0_23_MINUTE] + 6)) / 12, 0, 1)"
    L = cabecalho(NOME, "DIGITAL") + ['  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("ceu", "", 0))
    a("      " + img(0, 0, FAIXA, W, "faixa", "", f'<Transform target="x" value="0 - [SECONDS_IN_DAY] / 86400 * {FAIXA - W}" />'))
    a("      " + img(0, 0, W, W, "estrelas", ' alpha="0"', '<Transform target="alpha" value="255 * clamp((([HOUR_0_23_MINUTE] &gt;= 18.5 || [HOUR_0_23_MINUTE] &lt; 5.5) ? 1 : 0), 0, 1)" />'))
    for nome, ang, cond in (("sol", ang_dia, dia), ("lua", ang_noite, f"(1 - {dia})")):
        a(f'      <Group name="{nome}" x="{gx}" y="{gy}" width="{gw}" height="{gh}" pivotX="0.5" pivotY="1"><Transform target="angle" value="{ang}" />'
          + img(gw // 2 - 40, gh - RAIO - 40, 80, 80, "astro_" + nome, "", f'<Transform target="alpha" value="{cond} ? 255 : 0" />') + "</Group>")
    a("      " + img(0, 0, W, W, "silhueta"))
    a("      " + hora(40, 240, 400, 110, "hh:mm", 92, "#ffffffff", "LIGHT", "CENTER"))
    a("      " + tpl(110, 336, 260, 28, 20, "#ccffffff", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(40, 160, 400, 120, "hh:mm", 92, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def cor_ceu(hdec: float) -> tuple[int, int, int]:
    pos = [p for p, _ in PARADAS]
    return tuple(int(np.interp(hdec, pos, [c[k] for _, c in PARADAS])) for k in range(3))


def previa(A, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    hd = h + mi / 60
    if ambiente_:
        ImageDraw.Draw(base).text((C, 220), f"{h:02d}:{mi:02d}", font=fonte("Light", 92), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    off = int(hd / 24 * (FAIXA - W))
    base.alpha_composite(A["faixa"].crop((off, 0, off + W, W)))
    if hd >= 18.5 or hd < 5.5:
        base.alpha_composite(A["estrelas"])
    dia = 6 <= hd < 18
    t = max(0, min(1, ((hd - 6) if dia else ((hd - 18) if hd >= 18 else hd + 6)) / 12))
    ang = -84 + 168 * t
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cam.paste(A["astro_sol" if dia else "astro_lua"], (C - 40, PIV_Y - RAIO - 40))
    base.alpha_composite(cam.rotate(-ang, center=(C, PIV_Y), resample=Image.BICUBIC))
    base.alpha_composite(A["silhueta"])
    d = ImageDraw.Draw(base)
    d.text((C, 295), f"{h:02d}:{mi:02d}", font=fonte("Light", 92), fill=(255, 255, 255), anchor="mm")
    d.text((C, 350), "SEX 31 OUT", font=fonte("Medium", 20), fill=(220, 224, 230), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Day Sky"}
    pt = {"watch_face_name": "Céu do Dia"}
    A = {"faixa": faixa(), "estrelas": estrelas(), "astro_sol": astro(False), "astro_lua": astro(True), "silhueta": silhueta()}
    pv = [previa(A, 6, 40), previa(A, 12, 5), previa(A, 18, 20), previa(A, 23, 15), previa(A, 12, 5, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["06:40 aurora", "12:05 dia", "18:20 entardecer", "23:15 noite", "Ambiente (AOD)"], cols=5, nomes_previa=["aurora", "dia", "tarde", "noite", "ambiente"])
