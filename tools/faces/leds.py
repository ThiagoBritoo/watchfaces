"""Watchface "LEDs": três réguas de LEDs: 24 para as horas, 60 para os minutos e 60 para os segundos, cada LED aceso até o valor atual, com a hora
em texto no meio. Estilo painel de equipamento de som. Cinco cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rgb, textos_acento, tpl

NOME = "leds"
LINHAS = [("horas", 24, 24, 118, "[HOUR_0_23] + 1"), ("minutos", 30, 60, 238, "[MINUTE] + 1"), ("segundos", 30, 60, 332, "[SECOND] + 1")]   # nome, n leds, valor máximo, y, valor atual
LW, LH = 8, 22


def pos(i: int, n: int) -> int:
    larg = 360
    return int(C - larg / 2 + (larg - LW) * i / (n - 1))


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    for nome, n, vmax, y, val in LINHAS:
        for i in range(n):
            frac = f"({i + 1} * {vmax} / {n})"
            cor = "#ffff4d4d" if (nome != "horas" and i >= n - 4) else ac
            a(f'      <PartDraw x="{pos(i, n)}" y="{y}" width="{LW}" height="{LH}"><Rectangle x="0" y="0" width="{LW}" height="{LH}"><Fill color="#33808080" /></Rectangle></PartDraw>')
            a(f'      <PartDraw x="{pos(i, n)}" y="{y}" width="{LW}" height="{LH}"><Transform target="alpha" value="({val}) &gt;= {frac} ? 255 : 0" /><Rectangle x="0" y="0" width="{LW}" height="{LH}"><Fill color="{cor}" /></Rectangle></PartDraw>')
    a("      " + hora(110, 156, 260, 70, "hh:mm", 56, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(80, 90, 120, 22, 14, "#ff8e8e96", "%s", ["&quot;HORAS&quot;"], "BOLD", "START") + tpl(80, 210, 160, 22, 14, "#ff8e8e96", "%s", ["&quot;MINUTOS&quot;"], "BOLD", "START"))
    a("      " + tpl(80, 304, 160, 22, 14, "#ff8e8e96", "%s", ["&quot;SEGUNDOS&quot;"], "BOLD", "START"))
    a("      " + tpl(110, 390, 260, 26, 18, "#ff8e8e96", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(60, 170, 360, 120, "hh:mm", 92, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 230), f"{h:02d}:{mi:02d}", font=fonte("Light", 92), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    vals = {"horas": h + 1, "minutos": mi + 1, "segundos": s + 1}
    for nome, n, vmax, y, _ in LINHAS:
        for i in range(n):
            on = vals[nome] >= (i + 1) * vmax / n
            cor = (255, 77, 77) if (nome != "horas" and i >= n - 4) else ac
            d.rectangle([pos(i, n), y, pos(i, n) + LW, y + LH], fill=cor if on else (50, 50, 50))
    d.text((C, 191), f"{h:02d}:{mi:02d}", font=fonte("Bold", 56), fill=(255, 255, 255), anchor="mm")
    for t, x, y in (("HORAS", 80, 101), ("MINUTOS", 80, 221), ("SEGUNDOS", 80, 315)):
        d.text((x, y), t, font=fonte("Bold", 14), fill=(142, 142, 150), anchor="lm")
    d.text((C, 403), "SEX 31 OUT", font=fonte("Medium", 18), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "LEDs", "LEDs")
    pv = [previa("#4be37a", 10, 8, 20), previa("#33d6ff", 21, 45, 57), previa("#ff7a2f", 3, 30, 5), previa("#4be37a", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Verde", "Ciano (azul + zona vermelha)", "Laranja", "Ambiente (AOD)"], cols=4, nomes_previa=["verde", "ciano", "laranja", "ambiente"])
