"""Watchface "Mondrian": arte abstrata em blocos de cor separados por linhas pretas; as linhas se movem com a hora (verticais com os
minutos, horizontais com as horas), então a composição muda o dia todo. A hora aparece em texto num bloco. Arte e código originais."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rect, rgb, strings_opcoes, tpl

NOME = "mondrian"
# cores: fundo, vermelho, amarelo, azul, preto das linhas
PALETAS = [("classico", "#f4f1e8 #d6322b #f2c230 #1f4fa3 #111111 #111111"), ("pastel", "#fff6ef #ff8fa3 #ffd37a #7fb7ff #20202a #20202a"), ("noite", "#14161c #c0392b #d6a523 #2a5db0 #f0f0f0 #f0f0f0")]
LINHA = 8


def vx(frac_min: str) -> list[str]:
    return [f"80 + {frac_min} * 2.2", f"290 - {frac_min} * 1.1"]


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    p = lambda i: f"[CONFIGURATION.paleta.{i}]"  # noqa: E731
    mn = "([MINUTE] + [SECOND] / 60)"
    hr = "[HOUR_0_11_MINUTE]"
    # linhas verticais X1, X2 e horizontais Y1, Y2 (todas variam suavemente)
    x1, x2 = f"90 + {mn} * 1.5", f"330 - {mn} * 0.9"
    y1, y2 = f"90 + {hr} * 8", f"400 - {hr} * 11"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("paleta", "paleta_label", PALETAS), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + rect(0, 0, W, W, p(0)))
    # blocos coloridos (cantos e miolo) com dimensões amarradas às linhas
    a("      " + rect(0, 0, 100, 100, p(1), 0, "Fill", 2, f'<Transform target="width" value="{x1}" /><Transform target="height" value="{y1}" />'))
    a("      " + rect(0, 0, 100, 100, p(3), 0, "Fill", 2, f'<Transform target="x" value="{x2}" /><Transform target="y" value="{y2}" /><Transform target="width" value="480 - ({x2})" /><Transform target="height" value="480 - ({y2})" />'))
    a("      " + rect(0, 0, 100, 100, p(2), 0, "Fill", 2, f'<Transform target="x" value="{x2}" /><Transform target="width" value="480 - ({x2})" /><Transform target="height" value="{y1} * 0.6" />'))
    # linhas pretas
    for expr_x in (x1, x2):
        a("      " + rect(0, 0, LINHA, W, p(4), 0, "Fill", 2, f'<Transform target="x" value="({expr_x}) - {LINHA // 2}" />'))
    for expr_y in (y1, y2):
        a("      " + rect(0, 0, W, LINHA, p(4), 0, "Fill", 2, f'<Transform target="y" value="({expr_y}) - {LINHA // 2}" />'))
    a("      " + hora(110, 196, 260, 90, "hh:mm", 76, p(5), "BOLD", "CENTER", ""))
    a("      " + tpl(150, 280, 180, 26, 18, p(5), "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "BOLD"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for expr_x in (x1, x2):
        a("      " + rect(0, 0, 2, W, "#66ffffff", 0, "Fill", 2, f'<Transform target="x" value="{expr_x}" />'))
    for expr_y in (y1, y2):
        a("      " + rect(0, 0, W, 2, "#66ffffff", 0, "Fill", 2, f'<Transform target="y" value="{expr_y}" />'))
    a("      " + hora(110, 200, 260, 90, "hh:mm", 76, "#ffc0c0c0", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(paleta: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    cs = [rgb(c) for c in paleta.split()]
    mn = mi + s / 60
    hr = (h % 12) * 1 + mi / 60
    hr = h % 12 + mi / 60
    x1, x2 = 90 + mn * 1.5, 330 - mn * 0.9
    y1, y2 = 90 + hr * 8, 400 - hr * 11
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255) if ambiente_ else cs[0] + (255,))
    d = ImageDraw.Draw(base)
    if ambiente_:
        for x in (x1, x2):
            d.line([(x, 0), (x, W)], fill=(102, 102, 102), width=2)
        for y in (y1, y2):
            d.line([(0, y), (W, y)], fill=(102, 102, 102), width=2)
        d.text((C, 245), f"{h:02d}:{mi:02d}", font=fonte("Light", 76), fill=(192, 192, 192), anchor="mm")
        return redondo(base)
    d.rectangle([0, 0, x1, y1], fill=cs[1])
    d.rectangle([x2, y2, W, W], fill=cs[3])
    d.rectangle([x2, 0, W, y1 * 0.6], fill=cs[2])
    for x in (x1, x2):
        d.rectangle([x - LINHA / 2, 0, x + LINHA / 2, W], fill=cs[4])
    for y in (y1, y2):
        d.rectangle([0, y - LINHA / 2, W, y + LINHA / 2], fill=cs[4])
    d.text((C, 241), f"{h:02d}:{mi:02d}", font=fonte("Bold", 76), fill=cs[5], anchor="mm")
    d.text((C, 293), "SEX 31", font=fonte("Bold", 18), fill=cs[5], anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Mondrian", "paleta_label": "Palette"}
    pt = {"watch_face_name": "Mondrian", "paleta_label": "Paleta"}
    strings_opcoes(en, pt, "paleta", {"classico": ("Classic", "Clássico"), "pastel": ("Pastel", "Pastel"), "noite": ("Night", "Noite")})
    pv = [previa(PALETAS[0][1], 10, 8, 20), previa(PALETAS[1][1], 3, 45, 5), previa(PALETAS[2][1], 8, 20, 40), previa(PALETAS[0][1], 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Clássico 10:08", "Pastel 03:45", "Noite 08:20", "Ambiente (AOD)"], cols=4, nomes_previa=["classico", "pastel", "noite", "ambiente"])
