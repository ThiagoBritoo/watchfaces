"""Watchface "Ondas": ondulações que nascem no centro e se expandem até sumir (como gotas na água), com a hora fina no meio. Abstrata e calma.
Usa SECOND_MILLISECOND, então só anima suave com a tela ligada. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rgb, textos_acento, tpl

NOME = "ondas"
N = 4
MAXR = 236


def raio(k: int, ms: float) -> float:
    return (ms * 47.2 + k * MAXR / N) % MAXR


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    for k in range(N):
        r = f"(([SECOND_MILLISECOND] * 47.2 + {k * MAXR // N}) % {MAXR})"
        a(f'      <PartDraw {full}><Transform target="alpha" value="255 * pow(1 - {r} / {MAXR}, 1.6)" />'
          f'<Ellipse x="{C}" y="{C}" width="1" height="1"><Stroke thickness="3.5" color="{ac}" />'
          f'<Transform target="x" value="{C} - {r}" /><Transform target="y" value="{C} - {r}" /><Transform target="width" value="2 * {r}" /><Transform target="height" value="2 * {r}" /></Ellipse></PartDraw>')
    a("      " + hora(40, 170, 400, 120, "hh:mm", 100, "#ffffffff", "LIGHT", "CENTER"))
    a("      " + tpl(110, 276, 260, 28, 20, "#ccffffff", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw {full}><Ellipse x="{C - 60}" y="{C - 60}" width="120" height="120"><Stroke thickness="2" color="#55ffffff" /></Ellipse></PartDraw>')
    a("      " + hora(40, 170, 400, 120, "hh:mm", 86, "#ffb8b8c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(acento: str, h: int, mi: int, ms: float, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.ellipse([C - 60, C - 60, C + 60, C + 60], outline=(85, 85, 85), width=2)
        d.text((C, 230), f"{h:02d}:{mi:02d}", font=fonte("Light", 86), fill=(184, 184, 192), anchor="mm")
        return redondo(base)
    for k in range(N):
        r = raio(k, ms)
        al = int(255 * (1 - r / MAXR) ** 1.6)
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(cam).ellipse([C - r, C - r, C + r, C + r], outline=ac + (al,), width=4)
        base.alpha_composite(cam)
    d = ImageDraw.Draw(base)
    d.text((C, 228), f"{h:02d}:{mi:02d}", font=fonte("Light", 100), fill=(255, 255, 255), anchor="mm")
    d.text((C, 290), "SEX 31 OUT", font=fonte("Medium", 20), fill=(204, 204, 204), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Ripples", "Ondas")
    pv = [previa("#33d6ff", 10, 8, 3.1), previa("#ff7a2f", 10, 8, 17.0), previa("#ff5c93", 21, 45, 41.7), previa("#33d6ff", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Ciano", "Laranja", "Rosa", "Ambiente (AOD)"], cols=4, nomes_previa=["ciano", "laranja", "rosa", "ambiente"])
