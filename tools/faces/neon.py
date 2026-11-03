"""Watchface "Neon": dígitos de tubo de neon com brilho, um tubo sublinhado e um anel de neon em volta, sobre fundo preto. Cinco cores de neon. Fonte de tubos desenhada por script (original)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
import numpy as np

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, img, redondo, rgb, strings_opcoes, tint, tpl
from wf.neon_fonte import digito

NOME = "neon"
CORES = [("rosa", "#ff3ea5"), ("ciano", "#26e6ff"), ("amarelo", "#ffe14a"), ("verde", "#45ff8a"), ("laranja", "#ff7a2f")]
GR = dict(w=54, h=100, esp=7, pad=14)
PQ = dict(w=14, h=26, esp=3, pad=6)


def anel() -> Image.Image:
    s = 3
    n = W * s
    im = Image.new("L", (n, n), 0)
    ImageDraw.Draw(im).ellipse([C * s - 218 * s, C * s - 218 * s, C * s + 218 * s, C * s + 218 * s], outline=255, width=5 * s)
    im = im.resize((W, W), Image.LANCZOS)
    g1 = im.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.8))
    g2 = im.filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.9))
    a = np.maximum(np.maximum(np.asarray(im, np.float32), np.asarray(g1, np.float32) * 0.6), np.asarray(g2, np.float32))
    out = np.zeros((W, W, 4), np.uint8)
    out[..., :3] = 255
    out[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def bmfont(nome, mapa):
    return f'    <BitmapFont name="{nome}">\n' + "\n".join(f'      <Character name="{c}" resource="{r}" width="{w}" height="{h}" />' for c, (r, w, h) in mapa.items()) + "\n    </BitmapFont>"


def xml(gh: int, gw: int, ph: int) -> str:
    cor = "[CONFIGURATION.cor]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <BitmapFonts>", "@@FONTES@@", "  </BitmapFonts>", "  <UserConfigurations>", cor_config("cor", "cor_label", CORES), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", f' tintColor="{cor}"', 0))
    a("      " + img(0, 0, W, W, "anel"))
    a(f'      <DigitalClock x="{C - 170}" y="{C - gh // 2 - 30}" width="340" height="{gh}"><TimeText x="0" y="0" width="340" height="{gh}" format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER"><BitmapFont family="grande" size="{gh}" /></TimeText></DigitalClock>')
    a(f'      <PartText x="{C - 100}" y="{C + gh // 2 - 8}" width="200" height="{ph + 4}"><Text align="CENTER"><BitmapFont family="peq" size="{ph}"><Template><![CDATA[%s:%s]]>'
      '<Parameter expression="numberFormat(&quot;00&quot;, [MONTH])" /><Parameter expression="numberFormat(&quot;00&quot;, [DAY])" /></Template></BitmapFont></Text></PartText>')
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255) + f'<Group name="amb_txt" {full} tintColor="{cor}">'
      f'<DigitalClock x="{C - 170}" y="{C - gh // 2 - 14}" width="340" height="{gh}"><TimeText x="0" y="0" width="340" height="{gh}" format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER"><BitmapFont family="grande" size="{gh}" /></TimeText></DigitalClock></Group></Group>')
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, cor: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    c = rgb(cor)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    gh = A["g_0"].height
    if not ambiente_:
        cam.alpha_composite(A["anel"])
    tot = sum(A[f"g_{'colon' if ch == ':' else ch}"].width for ch in f"{h:02d}:{mi:02d}")
    x = C - tot // 2
    y = C - gh // 2 - (14 if ambiente_ else 30)
    for ch in f"{h:02d}:{mi:02d}":
        g = A[f"g_{'colon' if ch == ':' else ch}"]
        cam.alpha_composite(g, (x, y))
        x += g.width
    if not ambiente_:
        txt = "10:31"
        tot = sum(A[f"p_{'colon' if ch == ':' else ch}"].width for ch in txt)
        x = C - tot // 2
        for ch in txt:
            g = A[f"p_{'colon' if ch == ':' else ch}"]
            cam.alpha_composite(g, (x, C + gh // 2 - 8))
            x += g.width
    base.alpha_composite(tint(cam, c))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Neon", "cor_label": "Neon color"}
    pt = {"watch_face_name": "Neon", "cor_label": "Cor do neon"}
    strings_opcoes(en, pt, "cor", {"rosa": ("Pink", "Rosa"), "ciano": ("Cyan", "Ciano"), "amarelo": ("Yellow", "Amarelo"), "verde": ("Green", "Verde"), "laranja": ("Orange", "Laranja")})
    A = {"anel": anel()}
    mg, mp = {}, {}
    for ch in "0123456789:":
        n = "colon" if ch == ":" else ch
        A[f"g_{n}"] = digito(ch, **GR) if ch != ":" else digito(ch, 14, GR["h"], GR["esp"], GR["pad"])
        mg[ch] = (f"g_{n}", A[f"g_{n}"].width, A[f"g_{n}"].height)
        A[f"p_{n}"] = digito(ch, **PQ) if ch != ":" else digito(ch, 6, PQ["h"], PQ["esp"], PQ["pad"])
        mp[ch] = (f"p_{n}", A[f"p_{n}"].width, A[f"p_{n}"].height)
    xm = xml(A["g_0"].height, A["g_0"].width, A["p_0"].height).replace("@@FONTES@@", bmfont("grande", mg) + "\n" + bmfont("peq", mp))
    pv = [previa(A, "#ff3ea5", 10, 8), previa(A, "#26e6ff", 21, 45), previa(A, "#ffe14a", 3, 12), previa(A, "#ff3ea5", 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xm, A, pv, ["Rosa", "Ciano", "Amarelo", "Ambiente (AOD)"], cols=4, nomes_previa=["rosa", "ciano", "amarelo", "ambiente"])
