"""Watchface "Ponto": o mais minimalista possível. Um único ponto percorre um círculo fino marcando os minutos, um traço curto marca a hora e a
hora digital fica bem pequena no centro. Seis cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte, polar
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rgb, textos_acento, tpl

NOME = "ponto"
R = 206


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a(f'      <PartDraw {full}><Ellipse x="{C - R}" y="{C - R}" width="{2 * R}" height="{2 * R}"><Stroke thickness="1.5" color="#33ffffff" /></Ellipse></PartDraw>')
    a(f'      <Group name="min" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="([MINUTE] + [SECOND] / 60) * 6" />'
      f'<PartDraw x="{C - 11}" y="{C - R - 11}" width="22" height="22"><Ellipse x="0" y="0" width="22" height="22"><Fill color="{ac}" /></Ellipse></PartDraw></Group>')
    a(f'      <Group name="hora" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="[HOUR_0_11_MINUTE] * 30" />'
      f'<PartDraw x="{C - 2}" y="{C - 160}" width="4" height="34"><Rectangle x="0" y="0" width="4" height="34"><Fill color="#ffffffff" /></Rectangle></PartDraw></Group>')
    a("      " + hora(130, 206, 220, 60, "hh:mm", 44, "#ffffffff", "LIGHT", "CENTER"))
    a("      " + tpl(150, 258, 180, 24, 16, "#ff8e8e96", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw {full}><Ellipse x="{C - R}" y="{C - R}" width="{2 * R}" height="{2 * R}"><Stroke thickness="1.5" color="#44ffffff" /></Ellipse></PartDraw>')
    a(f'      <Group name="min_a" {full} pivotX="0.5" pivotY="0.5"><Transform target="angle" value="[MINUTE] * 6" />'
      f'<PartDraw x="{C - 9}" y="{C - R - 9}" width="18" height="18"><Ellipse x="0" y="0" width="18" height="18"><Fill color="#ffffffff" /></Ellipse></PartDraw></Group>')
    a("      " + hora(130, 210, 220, 60, "hh:mm", 44, "#ffb0b0b8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    d.ellipse([C - R, C - R, C + R, C + R], outline=(255, 255, 255, 51) if not ambiente_ else (68, 68, 68), width=2)
    x, y = polar(C, C, R, (mi + (0 if ambiente_ else s / 60)) * 6)
    d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(255, 255, 255) if ambiente_ else ac)
    if not ambiente_:
        a = (h % 12 + mi / 60) * 30
        d.line([polar(C, C, 160, a), polar(C, C, 126, a)], fill=(255, 255, 255), width=4)
    d.text((C, 236), f"{h:02d}:{mi:02d}", font=fonte("Light", 44), fill=(255, 255, 255) if not ambiente_ else (176, 176, 184), anchor="mm")
    if not ambiente_:
        d.text((C, 270), "SEX 31", font=fonte("Medium", 16), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Dot", "Ponto")
    pv = [previa("#f2c14e", 10, 8, 20), previa("#33d6ff", 3, 45, 40), previa("#ff5c93", 7, 22, 5), previa("#f2c14e", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Ouro", "Ciano", "Rosa", "Ambiente (AOD)"], cols=4, nomes_previa=["ouro", "ciano", "rosa", "ambiente"])
