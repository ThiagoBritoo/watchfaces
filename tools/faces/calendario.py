"""Watchface "Calendário": o mês inteiro numa grade (dia de hoje circulado) com a hora grande no alto. A grade se monta sozinha com
expressões (quantos dias o mês tem e em que dia da semana começa), então vale para qualquer mês. Original."""
from __future__ import annotations

import calendar
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rect, rgb, textos_acento, tpl

NOME = "calendario"
PX, PY = 50, 37
CX0, CY0 = C - 3 * PX, 216
SEMANA = ["D", "S", "T", "Q", "Q", "S", "S"]
FIRST = "((([DAY_OF_WEEK] - 1) - ([DAY] - 1) % 7 + 7) % 7)"


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + hora(60, 36, 360, 100, "hh:mm", 84, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(100, 130, 280, 26, 20, ac, "%s %s", ["[MONTH_F]", "[YEAR]"], "MEDIUM"))
    for c, letra in enumerate(SEMANA):
        a("      " + tpl(CX0 + c * PX - 22, CY0 - 38, 44, 24, 16, "#ff7c8088", "%s", [f"&quot;{letra}&quot;"], "MEDIUM"))
    for i in range(42):
        col, row = i % 7, i // 7
        dn = f"({i} - {FIRST} + 1)"
        visivel = f"({dn} &gt;= 1 &amp;&amp; {dn} &lt;= [DAYS_IN_MONTH])"
        peso = 0.55 if col in (0, 6) else 1
        a(f'      <PartText x="{CX0 + col * PX - 22}" y="{CY0 + row * PY - 15}" width="44" height="30"><Transform target="alpha" value="{visivel} ? {int(255 * peso)} : 0" />'
          f'<Text align="CENTER"><Font family="SYNC_TO_DEVICE" size="20" weight="MEDIUM" color="#ffffffff"><Template><![CDATA[%s]]>'
          f'<Parameter expression="numberFormat(&quot;0&quot;, {dn})" /></Template></Font></Text></PartText>')
    idx = f"({FIRST} + [DAY] - 1)"
    a(f'      <PartDraw x="{CX0 - 21}" y="{CY0 - 16}" width="42" height="32"><Transform target="x" value="{CX0 - 21} + ({idx} % 7) * {PX}" /><Transform target="y" value="{CY0 - 16} + floor({idx} / 7) * {PY}" />'
      f'<Ellipse x="0" y="0" width="42" height="32"><Stroke thickness="3" color="{ac}" /></Ellipse></PartDraw>')
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(60, 120, 360, 110, "hh:mm", 92, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("      " + tpl(100, 220, 280, 28, 22, "#ff8e8e96", "%s %s", ["[DAY]", "[MONTH_F]"], "MEDIUM"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(acento: str, d: date, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    dr = ImageDraw.Draw(base)
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    if ambiente_:
        dr.text((C, 175), f"{h:02d}:{mi:02d}", font=fonte("Light", 92), fill=(192, 192, 200), anchor="mm")
        dr.text((C, 234), f"{d.day} {meses[d.month - 1]}", font=fonte("Medium", 22), fill=(142, 142, 150), anchor="mm")
        return redondo(base)
    dr.text((C, 86), f"{h:02d}:{mi:02d}", font=fonte("Bold", 84), fill=(255, 255, 255), anchor="mm")
    dr.text((C, 143), f"{meses[d.month - 1]} {d.year}", font=fonte("Medium", 20), fill=ac, anchor="mm")
    for c, letra in enumerate(SEMANA):
        dr.text((CX0 + c * PX, CY0 - 28), letra, font=fonte("Medium", 16), fill=(124, 128, 136), anchor="mm")
    primeiro = (calendar.monthrange(d.year, d.month)[0] + 1) % 7           # 0 = domingo
    ndias = calendar.monthrange(d.year, d.month)[1]
    for i in range(42):
        dn = i - primeiro + 1
        if 1 <= dn <= ndias:
            col, row = i % 7, i // 7
            al = 140 if col in (0, 6) else 255
            dr.text((CX0 + col * PX, CY0 + row * PY), str(dn), font=fonte("Medium", 20), fill=(255, 255, 255, al), anchor="mm")
    idx = primeiro + d.day - 1
    x, y = CX0 + (idx % 7) * PX, CY0 + (idx // 7) * PY
    dr.ellipse([x - 21, y - 16, x + 21, y + 16], outline=ac, width=3)
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Calendar", "Calendário")
    pv = [previa("#ff7a2f", date(2026, 10, 31), 10, 8), previa("#33d6ff", date(2026, 2, 14), 21, 45), previa("#ff5c93", date(2026, 7, 1), 7, 15), previa("#ff7a2f", date(2026, 10, 31), 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Out 2026", "Fev 2026", "Jul 2026", "Ambiente (AOD)"], cols=4, nomes_previa=["out", "fev", "jul", "ambiente"])
