"""Watchface "Deslizante": hora e minuto são duas réguas de números que deslizam; o número do meio fica grande e
aceso, os vizinhos encolhem e somem. A régua dos minutos anda a cada segundo, a das horas a cada minuto.
Inspirada em relógios de "tempo deslizante". Arte e código originais."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial
from wf.kit import C, W, cabecalho, cor_config, finalizar, img, redondo, rect, rgb, strings_opcoes, tint

NOME = "deslizante"
ACENTOS = [("ciano", "#2ee6ff"), ("laranja", "#ff8a3d"), ("verde", "#4be37a"), ("rosa", "#ff5c93"), ("violeta", "#a98bff"), ("branco", "#f2f4f8")]
HORAS = dict(y=178, h=70, sp=82, ks=range(-3, 4), base=34, mod="12")
MINUTOS = dict(y=262, h=70, sp=68, ks=range(-4, 5), base=28, mod="60")
CY = {"horas": 213, "minutos": 297}
BX = 64                                   # largura de cada caixa de texto


def _dist(k: int, frac: str) -> str:
    return f"abs({k} - {frac})"


def linha(cfg: dict, frac: str, expr_valor, nome: str) -> list[str]:
    out = []
    for k in cfg["ks"]:
        d = _dist(k, frac)
        x0 = C - BX // 2
        out.append(
            f'<PartText x="{x0}" y="{cfg["y"]}" width="{BX}" height="{cfg["h"]}" pivotX="0.5" pivotY="0.5">'
            f'<Transform target="x" value="{x0} + ({k} - {frac}) * {cfg["sp"]}" />'
            f'<Transform target="alpha" value="255 * clamp(1.1 - 0.34 * {d}, 0, 1)" />'
            f'<Transform target="scaleX" value="0.78 + 0.95 * clamp(1 - {d}, 0, 1)" />'
            f'<Transform target="scaleY" value="0.78 + 0.95 * clamp(1 - {d}, 0, 1)" />'
            f'<Text align="CENTER"><Font family="SYNC_TO_DEVICE" size="{cfg["base"]}" weight="BOLD" color="[CONFIGURATION.acento]">'
            f'<Template><![CDATA[%s]]><Parameter expression="numberFormat(&quot;00&quot;, {expr_valor(k)})" /></Template></Font></Text></PartText>')
    return out


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    ac = "[CONFIGURATION.acento]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS), "  </UserConfigurations>",
                                       '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a(f'    <Group name="deslizante" {full}><Variant mode="AMBIENT" target="alpha" value="0" />')
    a("      " + img(C - 110, 150, 220, 200, "brilho", f' tintColor="{ac}" alpha="150"'))
    a(f'      <PartText x="{C - 40}" y="118" width="80" height="34"><Text align="CENTER"><Font family="SYNC_TO_DEVICE" size="22" weight="SEMI_BOLD" color="#ffa8aeb8">'
      '<Template><![CDATA[%s]]><Parameter expression="[AMPM_STRING]" /></Template></Font></Text></PartText>')
    for t in linha(HORAS, "([MINUTE] / 60)", lambda k: f"(([HOUR_1_12] - 1 + {k} + 12) % 12) + 1", "h"):
        a("      " + t)
    for t in linha(MINUTOS, "([SECOND] / 60)", lambda k: f"([MINUTE] + {k} + 60) % 60", "m"):
        a("      " + t)
    a('      <PartText x="90" y="360" width="300" height="38"><Text align="CENTER"><Font family="SYNC_TO_DEVICE" size="26" weight="SEMI_BOLD" color="#ffffffff">'
      '<Upper><Template><![CDATA[%s %s %s]]><Parameter expression="[MONTH_S]" /><Parameter expression="[DAY]" /><Parameter expression="[DAY_OF_WEEK_S]" /></Template></Upper></Font></Text></PartText>')
    a("      " + rect(C - 100, 402, 200, 3, ac, 1.5))
    a("    </Group>")
    a(f'    <Group name="ambiente" {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />')
    a(f'      <DigitalClock x="40" y="160" width="400" height="130"><TimeText x="0" y="0" width="400" height="130" format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER">'
      '<Font family="SYNC_TO_DEVICE" size="92" weight="LIGHT" color="#ffc8c8ce" /></TimeText></DigitalClock>')
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def brilho() -> Image.Image:
    g = grad_radial(220, 110, 100, [(0, (255, 255, 255, 120)), (70, (255, 255, 255, 40)), (110, (255, 255, 255, 0))])
    return g


def _linha_previa(base, cfg, frac, valor, cor, cy):
    d = ImageDraw.Draw(base)
    for k in cfg["ks"]:
        dist = abs(k - frac)
        alpha = max(0.0, min(1.0, 1.1 - 0.34 * dist))
        esc = 0.78 + 0.95 * max(0.0, min(1.0, 1 - dist))
        x = C + (k - frac) * cfg["sp"]
        tam = int(round(cfg["base"] * esc))
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(cam).text((x, cy), f"{valor(k):02d}", font=fonte("Bold", tam), fill=cor + (int(255 * alpha),), anchor="mm")
        base.alpha_composite(cam)


def previa(acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (4, 8, 14, 255) if not ambiente_ else (0, 0, 0, 255))
    ac = rgb(acento)
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 225), f"{h:02d}:{mi:02d}", font=fonte("Light", 92), fill=(200, 200, 206), anchor="mm")
        return redondo(base)
    g = tint(brilho(), ac)
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    cam.paste(g, (C - 110, 150))
    r, gg, b, al = cam.split()
    base.alpha_composite(Image.merge("RGBA", (r, gg, b, al.point(lambda v: int(v * 150 / 255)))))
    d = ImageDraw.Draw(base)
    d.text((C, 135), "PM" if h >= 12 else "AM", font=fonte("SemiBold", 22), fill=(168, 174, 184), anchor="mm")
    h12 = (h - 1) % 12 + 1
    _linha_previa(base, HORAS, mi / 60, lambda k: (h12 - 1 + k + 12) % 12 + 1, ac, CY["horas"])
    _linha_previa(base, MINUTOS, s / 60, lambda k: (mi + k + 60) % 60, ac, CY["minutos"])
    d = ImageDraw.Draw(base)
    d.text((C, 379), "OUT 31 SEX", font=fonte("SemiBold", 26), fill=(255, 255, 255), anchor="mm")
    d.rounded_rectangle([C - 100, 402, C + 100, 405], radius=1, fill=ac)
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Sliding", "acento_label": "Accent color"}
    pt = {"watch_face_name": "Deslizante", "acento_label": "Cor de destaque"}
    strings_opcoes(en, pt, "acento", {"ciano": ("Cyan", "Ciano"), "laranja": ("Orange", "Laranja"), "verde": ("Green", "Verde"),
                                       "rosa": ("Pink", "Rosa"), "violeta": ("Violet", "Violeta"), "branco": ("White", "Branco")})
    A = {"brilho": brilho()}
    pv = [previa("#2ee6ff", 13, 37, 0), previa("#ff8a3d", 9, 5, 30), previa("#a98bff", 22, 59, 45), previa("#2ee6ff", 13, 37, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Ciano", "Laranja (meio do minuto)", "Violeta (virando a hora)", "Ambiente (AOD)"], cols=4,
                     nomes_previa=["ciano", "laranja", "violeta", "ambiente"])
