"""Watchface "Binário": a hora em BCD (decimal codificado em binário): seis colunas de pontos (hora, minuto, segundo; dezena e unidade),
cada ponto aceso vale 8, 4, 2 ou 1. Não parece um relógio. Arte e código originais."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, redondo, rgb, textos_acento, tpl

NOME = "binario"
COLS = [("ht", "floor([HOUR_0_23] / 10)", 2), ("hu", "[HOUR_0_23] % 10", 4), ("mt", "floor([MINUTE] / 10)", 3), ("mu", "[MINUTE] % 10", 4),
        ("st", "floor([SECOND] / 10)", 3), ("su", "[SECOND] % 10", 4)]
PAS_X, PAS_Y, D = 58, 54, 32
X0 = C - (5 * PAS_X) // 2
Y0 = 150


def pos(c: int, r: int) -> tuple[int, int]:
    return X0 + c * PAS_X - D // 2, Y0 + r * PAS_Y - D // 2


def ponto(c: int, r: int, cor: str, expr: str | None, alpha_base: int | None = None) -> str:
    x, y = pos(c, r)
    t = f'<Transform target="alpha" value="{expr}" />' if expr else ""
    al = f' alpha="{alpha_base}"' if alpha_base is not None else ""
    return f'<PartDraw x="{x}" y="{y}" width="{D}" height="{D}"{al}><Ellipse x="0" y="0" width="{D}" height="{D}"><Fill color="{cor}" />{t}</Ellipse></PartDraw>'


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    for c, (nome, val, nbits) in enumerate(COLS):
        for r in range(4 - nbits, 4):
            bit = 3 - r
            a("      " + ponto(c, r, "#33808080", None))
            a("      " + ponto(c, r, ac, f"255 * (floor(({val}) / {2 ** bit}) % 2)"))
    for c, (nome, val, nbits) in enumerate(COLS):
        x, _ = pos(c, 0)
        a("      " + tpl(x - 12, Y0 + 3 * PAS_Y + 26, D + 24, 30, 22, "#ff8e8e96", "%s", [f'numberFormat(&quot;0&quot;, floor({val}))'], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for c, (nome, val, nbits) in enumerate(COLS[:4]):
        for r in range(4 - nbits, 4):
            bit = 3 - r
            a("      " + ponto(c, r, "#ffffffff", f"255 * (floor(({val}) / {2 ** bit}) % 2)").replace(f'width="{D}" height="{D}"', f'width="{D - 8}" height="{D - 8}"').replace(f'<Ellipse x="0" y="0" width="{D}" height="{D}">', f'<Ellipse x="0" y="0" width="{D - 8}" height="{D - 8}">'))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    vals = [h // 10, h % 10, mi // 10, mi % 10, s // 10, s % 10]
    n = 4 if ambiente_ else 6
    for c in range(n):
        nome, _, nbits = COLS[c]
        for r in range(4 - nbits, 4):
            x, y = pos(c, r)
            on = (vals[c] >> (3 - r)) & 1
            if ambiente_:
                if on:
                    d.ellipse([x + 4, y + 4, x + D - 4, y + D - 4], fill=(255, 255, 255))
            else:
                d.ellipse([x, y, x + D, y + D], fill=ac if on else (51, 51, 51))
        if not ambiente_:
            x, _ = pos(c, 0)
            d.text((x + D / 2, Y0 + 3 * PAS_Y + 40), str(vals[c]), font=fonte("Medium", 22), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Binary", "Binário")
    pv = [previa("#33d6ff", 10, 8, 32), previa("#ff7a2f", 21, 45, 59), previa("#4be37a", 7, 17, 6), previa("#f2f2f2", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Ciano", "Laranja", "Verde", "Ambiente (AOD)"], cols=4, nomes_previa=["ciano", "laranja", "verde", "ambiente"])
