"""Watchface "Morse": a hora em código Morse. São 4 linhas (dezena e unidade da hora, dezena e unidade dos minutos), cada uma com 5 símbolos (ponto ou
traço). Um pequeno número cinza ao lado de cada linha ajuda a conferir. Nem parece relógio. Cinco cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, redondo, rect, rgb, textos_acento, tpl

NOME = "morse"
LINHAS = [("floor([HOUR_0_23] / 10)", 116), ("[HOUR_0_23] % 10", 176), ("floor([MINUTE] / 10)", 270), ("[MINUTE] % 10", 330)]
MORSE = {0: "-----", 1: ".----", 2: "..---", 3: "...--", 4: "....-", 5: ".....", 6: "-....", 7: "--...", 8: "---..", 9: "----."}
X0, DX = 118, 56
D = 22


def e_ponto(n: str, j: int) -> str:
    return f"(({n} &gt;= 1 &amp;&amp; {n} &lt;= 5 &amp;&amp; {j} &lt; {n}) || ({n} &gt;= 6 &amp;&amp; {j} &gt;= {n} - 5))"


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    for val, y in LINHAS:
        for j in range(5):
            x = X0 + j * DX
            dot = e_ponto(val, j)
            a(f'      <PartDraw x="{x}" y="{y}" width="{D}" height="{D}"><Transform target="alpha" value="{dot} ? 255 : 0" /><Ellipse x="0" y="0" width="{D}" height="{D}"><Fill color="{ac}" /></Ellipse></PartDraw>')
            a(f'      <PartDraw x="{x - 12}" y="{y}" width="{D + 24}" height="{D}"><Transform target="alpha" value="{dot} ? 0 : 255" /><RoundRectangle x="0" y="0" width="{D + 24}" height="{D}" cornerRadiusX="{D // 2}" cornerRadiusY="{D // 2}"><Fill color="{ac}" /></RoundRectangle></PartDraw>')
        a("      " + tpl(X0 + 5 * DX + 4, y - 4, 50, 30, 22, "#ff6e727c", "%s", [f"numberFormat(&quot;0&quot;, {val})"], "MEDIUM", "START"))
    a("      " + rect(C - 90, 236, 180, 2, "#44ffffff", 0))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for val, y in LINHAS:
        for j in range(5):
            x = X0 + j * DX
            dot = e_ponto(val, j)
            a(f'      <PartDraw x="{x + 4}" y="{y + 4}" width="{D - 8}" height="{D - 8}"><Transform target="alpha" value="{dot} ? 255 : 0" /><Ellipse x="0" y="0" width="{D - 8}" height="{D - 8}"><Fill color="#ffc0c0c8" /></Ellipse></PartDraw>')
            a(f'      <PartDraw x="{x - 8}" y="{y + 4}" width="{D + 16}" height="{D - 8}"><Transform target="alpha" value="{dot} ? 0 : 255" /><RoundRectangle x="0" y="0" width="{D + 16}" height="{D - 8}" cornerRadiusX="7" cornerRadiusY="7"><Fill color="#ffc0c0c8" /></RoundRectangle></PartDraw>')
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(acento: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento) if not ambiente_ else (192, 192, 200)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    vals = [h // 10, h % 10, mi // 10, mi % 10]
    for v, (_, y) in zip(vals, LINHAS):
        for j, simb in enumerate(MORSE[v]):
            x = X0 + j * DX
            if simb == ".":
                d.ellipse([x, y, x + D, y + D], fill=ac)
            else:
                d.rounded_rectangle([x - 12, y, x + D + 12, y + D], radius=D // 2, fill=ac)
        if not ambiente_:
            d.text((X0 + 5 * DX + 4, y + 11), str(v), font=fonte("Medium", 22), fill=(110, 114, 124), anchor="lm")
    if not ambiente_:
        d.rectangle([C - 90, 236, C + 90, 238], fill=(68, 68, 68))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Morse", "Morse")
    pv = [previa("#4be37a", 10, 8), previa("#33d6ff", 21, 45), previa("#ff7a2f", 3, 12), previa("#4be37a", 10, 8, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["10:08", "21:45", "03:12", "Ambiente (AOD)"], cols=4, nomes_previa=["h1008", "h2145", "h0312", "ambiente"])
