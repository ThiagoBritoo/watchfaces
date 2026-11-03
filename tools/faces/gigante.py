"""Watchface "Gigante": tipografia como arte. Hora e minuto em números enormes, um sobre o outro, e um anel fino de segundos.
Arte e código originais."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rgb, textos_acento

NOME = "gigante"


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO),
                                       '    <BooleanConfiguration id="segundos" displayName="segundos_label" defaultValue="TRUE" />', "  </UserConfigurations>",
                                       '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + hora(0, 6, W, 250, "hh", 270, ac, "BLACK", "CENTER"))
    a("      " + hora(0, 222, W, 250, "mm", 270, "#ffffffff", "BLACK", "CENTER"))
    a('      <BooleanConfiguration id="segundos"><BooleanOption id="TRUE"><Group name="seg" ' + full + '>'
      f'<PartDraw {full}><Arc centerX="{C}" centerY="{C}" width="470" height="470" startAngle="0" endAngle="0"><Stroke thickness="5" color="{ac}" cap="ROUND" />'
      '<Transform target="endAngle" value="[SECOND] * 6" /></Arc></PartDraw></Group></BooleanOption></BooleanConfiguration>')
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(0, 40, W, 200, "hh", 190, "#ff9a9aa2", "LIGHT", "CENTER"))
    a("      " + hora(0, 220, W, 200, "mm", 190, "#ff6a6a72", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 140), f"{h:02d}", font=fonte("Light", 190), fill=(154, 154, 162), anchor="mm")
        d.text((C, 325), f"{mi:02d}", font=fonte("Light", 190), fill=(106, 106, 114), anchor="mm")
        return redondo(base)
    d.text((C, 130), f"{h:02d}", font=fonte("Black", 270), fill=ac, anchor="mm")
    d.text((C, 345), f"{mi:02d}", font=fonte("Black", 270), fill=(255, 255, 255), anchor="mm")
    d.arc([5, 5, W - 5, W - 5], -90, -90 + s * 6, fill=ac, width=5)
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {"segundos_label": "Seconds ring"}, {"segundos_label": "Anel dos segundos"}
    textos_acento(en, pt, "Giant", "Gigante")
    pv = [previa("#f2c14e", 10, 8, 20), previa("#ff7a2f", 21, 45, 40), previa("#33d6ff", 3, 12, 5), previa("#f2c14e", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Ouro", "Laranja", "Ciano", "Ambiente (AOD)"], cols=4, nomes_previa=["ouro", "laranja", "ciano", "ambiente"])
