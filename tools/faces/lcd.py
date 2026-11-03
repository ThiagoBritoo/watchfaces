"""Watchface "LCD": relógio digital de 7 segmentos com segmentos fantasma, dia da semana destacado, segundos pequenos, data e bateria. Três telas:
LCD clássico (verde-cinza), com luz azul e âmbar. Fonte de segmentos desenhada por script (original)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_linear
from wf.kit import C, W, cabecalho, finalizar, grupo, img, redondo, rgb, strings_opcoes, tint, tpl
from wf.lcd_fonte import digito

NOME = "lcd"
TELAS = [("classico", "#ffb9c7a4", "#ff1b2a1b"), ("azul", "#ff06101e", "#ff9fd8ff"), ("ambar", "#ff120a02", "#ffffb347")]
GR = dict(w=50, h=96, e=10, pad=4)
PQ = dict(w=22, h=40, e=5, pad=2)
PX, PY, PW, PH = 46, 108, 388, 262
DIAS = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]


def fundo(cor_tela: str) -> Image.Image:
    s = 3
    n = W * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([(PX - 12) * s, (PY - 12) * s, (PX + PW + 12) * s, (PY + PH + 12) * s], radius=34 * s, fill=(34, 36, 40, 255), outline=(90, 94, 102, 255), width=3 * s)
    d.rounded_rectangle([PX * s, PY * s, (PX + PW) * s, (PY + PH) * s], radius=24 * s, fill=rgb(cor_tela) + (255,))
    im = im.resize((W, W), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    yy, xx = np.mgrid[0:W, 0:W]
    dentro = (xx > PX) & (xx < PX + PW) & (yy > PY) & (yy < PY + PH) & (a[..., 3] > 0)
    luz = 1 - 0.10 * np.clip((yy - PY) / PH, 0, 1) - 0.12 * np.clip(1 - np.minimum(xx - PX, PX + PW - xx) / 30, 0, 1)
    a[..., :3] = np.where(dentro[..., None], a[..., :3] * luz[..., None], a[..., :3])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def bmfont(nome: str, mapa: dict) -> str:
    linhas = [f'      <Character name="{c}" resource="{r}" width="{w}" height="{h}" />' for c, (r, w, h) in mapa.items()]
    return f'    <BitmapFont name="{nome}">\n' + "\n".join(linhas) + "\n    </BitmapFont>"


def xml(gh: int, ph: int, gw: int) -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <BitmapFonts>", "@@FONTES@@", "  </BitmapFonts>", "  <UserConfigurations>",
                                       '    <ListConfiguration id="tela" displayName="tela_label" defaultValue="classico">' + "".join(f'<ListOption id="{k}" displayName="tela_{k}" />' for k, _, _ in TELAS)
                                       + "</ListConfiguration>", "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0) + '<ListConfiguration id="tela">')
    x0 = PX + 18
    for k, bg, fg in TELAS:
        a(f'      <ListOption id="{k}"><Group name="tela_{k}" {full}>' + img(0, 0, W, W, f"fundo_{k}")
          + f'<Group name="digitos_{k}" {full} tintColor="{fg}">'
          + f'<DigitalClock x="{x0}" y="{PY + 38}" width="300" height="{gh}"><TimeText x="0" y="0" width="300" height="{gh}" format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="START"><BitmapFont family="grande" size="{gh}" /></TimeText></DigitalClock>'
          + f'<DigitalClock x="{x0 + 296}" y="{PY + 38 + gh - ph}" width="60" height="{ph}"><TimeText x="0" y="0" width="60" height="{ph}" format="ss" hourFormat="SYNC_TO_DEVICE" align="START"><BitmapFont family="peq" size="{ph}" /></TimeText></DigitalClock>'
          + "</Group>")
        for i, nome in enumerate(DIAS):
            a(f'      <PartText x="{PX + 14 + i * 53}" y="{PY + 8}" width="50" height="24"><Transform target="alpha" value="[DAY_OF_WEEK] == {i + 1} ? 255 : 70" />'
              f'<Text align="CENTER"><Font family="SYNC_TO_DEVICE" size="16" weight="BOLD" color="{fg}"><Template><![CDATA[%s]]><Parameter expression="&quot;{nome}&quot;" /></Template></Font></Text></PartText>')
        a(tpl(PX + 18, PY + PH - 54, 190, 36, 24, fg, "%s %s", ["[DAY]", "[MONTH_S]"], "BOLD", "START"))
        a(tpl(PX + PW - 200, PY + PH - 54, 180, 36, 24, fg, "%s%%", ["round([BATTERY_PERCENT])"], "BOLD", "END"))
        a("      </Group></ListOption>")
    a("    </ListConfiguration></Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255) + f'<Group name="digitos_a" {full} tintColor="#ffd0d0d6">'
      + f'<DigitalClock x="{x0}" y="{PY + 38}" width="300" height="{gh}"><TimeText x="0" y="0" width="300" height="{gh}" format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="START"><BitmapFont family="grande" size="{gh}" /></TimeText></DigitalClock></Group></Group>')
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, tela: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    cfg = {k: (b, f) for k, b, f in TELAS}
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    x0 = PX + 18
    if ambiente_:
        cor = (208, 208, 214)
    else:
        base.alpha_composite(A[f"fundo_{tela}"])
        cor = rgb(cfg[tela][1])
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    x = x0
    for ch in f"{h:02d}:{mi:02d}":
        g = A[f"g_{'colon' if ch == ':' else ch}"]
        cam.alpha_composite(g, (x, PY + 38))
        x += g.width
    if not ambiente_:
        gh = A["g_0"].height
        x = x0 + 296
        for ch in f"{s:02d}":
            g = A[f"p_{ch}"]
            cam.alpha_composite(g, (x, PY + 38 + gh - g.height))
            x += g.width
    base.alpha_composite(tint(cam, cor))
    if not ambiente_:
        d = ImageDraw.Draw(base)
        dow = date(2026, 10, 31).isoweekday() % 7
        for i, nome in enumerate(DIAS):
            d.text((PX + 14 + i * 53 + 25, PY + 20), nome, font=fonte("Bold", 16), fill=cor + (255 if i == dow else 70,), anchor="mm")
        d.text((PX + 18, PY + PH - 36), "31 out", font=fonte("Bold", 24), fill=cor, anchor="lm")
        d.text((PX + PW - 20, PY + PH - 36), "89%", font=fonte("Bold", 24), fill=cor, anchor="rm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "LCD", "tela_label": "Screen", "tela_classico": "Classic LCD", "tela_azul": "Blue backlight", "tela_ambar": "Amber"}
    pt = {"watch_face_name": "LCD", "tela_label": "Tela", "tela_classico": "LCD clássico", "tela_azul": "Luz azul", "tela_ambar": "Âmbar"}
    A: dict[str, Image.Image] = {}
    for k, bg, fg in TELAS:
        A[f"fundo_{k}"] = fundo(bg)
    mg, mp = {}, {}
    for ch in "0123456789:":
        n = "colon" if ch == ":" else ch
        A[f"g_{n}"] = digito(ch, **GR) if ch != ":" else digito(ch, 18, GR["h"], GR["e"], GR["pad"])
        mg[ch] = (f"g_{n}", A[f"g_{n}"].width, A[f"g_{n}"].height)
    for ch in "0123456789":
        A[f"p_{ch}"] = digito(ch, **PQ)
        mp[ch] = (f"p_{ch}", A[f"p_{ch}"].width, A[f"p_{ch}"].height)
    gh, ph = A["g_0"].height, A["p_0"].height
    xm = xml(gh, ph, A["g_0"].width).replace("@@FONTES@@", bmfont("grande", mg) + "\n" + bmfont("peq", mp))
    pv = [previa(A, "classico", 10, 8, 32), previa(A, "azul", 21, 45, 7), previa(A, "ambar", 3, 12, 50), previa(A, "classico", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xm, A, pv, ["LCD clássico", "Luz azul", "Âmbar", "Ambiente (AOD)"], cols=4, nomes_previa=["classico", "azul", "ambar", "ambiente"])
