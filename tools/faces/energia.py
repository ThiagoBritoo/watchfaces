"""Watchface "Energia": a bateria é a estrela: um anel grosso e o percentual enorme no centro, hora pequena em cima e aviso de carregando. O anel
fica vermelho abaixo de 20 por cento. Cinco cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rgb, textos_acento, tpl

NOME = "energia"
R = 204


def arco(cor, esp, expr=None, alpha=None):
    t = f'<Transform target="endAngle" value="{expr}" />' if expr else ""
    ta = f'<Transform target="alpha" value="{alpha}" />' if alpha else ""
    return (f'<PartDraw x="0" y="0" width="{W}" height="{W}">{ta}<Arc centerX="{C}" centerY="{C}" width="{2 * R}" height="{2 * R}" startAngle="0" endAngle="360">'
            f'<Stroke thickness="{esp}" color="{cor}" cap="ROUND" />{t}</Arc></PartDraw>')


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + arco("#22ffffff", 26))
    a("      " + arco(ac, 26, "clamp([BATTERY_PERCENT], 0, 100) * 3.6", "[BATTERY_PERCENT] &gt;= 20 ? 255 : 0"))
    a("      " + arco("#ffff4d4d", 26, "clamp([BATTERY_PERCENT], 0, 100) * 3.6", "[BATTERY_PERCENT] &lt; 20 ? 255 : 0"))
    a("      " + hora(110, 70, 260, 60, "hh:mm", 48, "#ffffffff", "MEDIUM", "CENTER"))
    a("      " + tpl(60, 130, 360, 150, 128, "#ffffffff", "%s", ["round([BATTERY_PERCENT])"], "BLACK"))
    a("      " + tpl(150, 270, 180, 34, 26, ac, "%s", ["&quot;% BATERIA&quot;"], "SEMI_BOLD"))
    a("      " + tpl(110, 318, 260, 30, 22, ac, "%s", ["&quot;CARREGANDO&quot;"], "SEMI_BOLD", "CENTER", ' alpha="0"').replace("><Text", '><Transform target="alpha" value="[BATTERY_CHARGING_STATUS] ? 255 : 0" /><Text', 1))
    a("      " + tpl(110, 352, 260, 26, 20, "#ff8e8e96", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(60, 120, 360, 110, "hh:mm", 92, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("      " + tpl(110, 240, 260, 36, 28, "#ff8e8e96", "%s%%", ["round([BATTERY_PERCENT])"], "MEDIUM"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(acento: str, h: int, mi: int, bat: int, carregando: bool = False, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento) if bat >= 20 else (255, 77, 77)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 175), f"{h:02d}:{mi:02d}", font=fonte("Light", 92), fill=(192, 192, 200), anchor="mm")
        d.text((C, 258), f"{bat}%", font=fonte("Medium", 28), fill=(142, 142, 150), anchor="mm")
        return redondo(base)
    box = [C - R, C - R, C + R, C + R]
    d.ellipse(box, outline=(34, 34, 34), width=26)
    d.arc(box, -90, -90 + bat * 3.6, fill=ac, width=26)
    d.text((C, 100), f"{h:02d}:{mi:02d}", font=fonte("Medium", 48), fill=(255, 255, 255), anchor="mm")
    d.text((C, 205), str(bat), font=fonte("Black", 128), fill=(255, 255, 255), anchor="mm")
    d.text((C, 287), "% BATERIA", font=fonte("SemiBold", 26), fill=ac, anchor="mm")
    if carregando:
        d.text((C, 335), "CARREGANDO", font=fonte("SemiBold", 22), fill=ac, anchor="mm")
    d.text((C, 365), "SEX 31 OUT", font=fonte("Medium", 20), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Energy", "Energia")
    pv = [previa("#4be37a", 10, 8, 89), previa("#33d6ff", 15, 30, 54, True), previa("#f2c14e", 21, 5, 17), previa("#4be37a", 10, 8, 89, ambiente_=True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["89%", "54% carregando", "17% (baixa, vermelho)", "Ambiente (AOD)"], cols=4, nomes_previa=["89", "54", "17", "ambiente"])
