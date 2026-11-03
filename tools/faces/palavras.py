"""Watchface "Palavras": a hora por extenso em português ("SÃO DEZ HORAS E VINTE E CINCO"). As palavras da hora atual acendem e as demais ficam
apagadas; quatro pontinhos mostram os minutos entre os múltiplos de 5. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, redondo, rect, rgb, strings_opcoes

NOME = "palavras"
CORES = [("branco", "#ffffff"), ("laranja", "#ff8a3d"), ("ciano", "#33d6ff"), ("verde", "#6bff9c"), ("rosa", "#ff5c93")]
M5 = "floor([MINUTE] / 5)"
H = "[HOUR_1_12]"
# (palavra, expressão booleana de quando acende, x do centro, y, largura)
def _linhas():
    L = []
    def linha(y, itens):
        n = len(itens)
        xs = {1: [C], 2: [C - 60, C + 60], 3: [C - 108, C, C + 108], 4: [C - 138, C - 62, C + 22, C + 118]}[n]
        for (pal, cond), x in zip(itens, xs):
            L.append((pal, cond, x, y))
    linha(58, [("É", f"{H} == 1"), ("SÃO", f"{H} != 1")])
    linha(98, [("UMA", f"{H} == 1"), ("DUAS", f"{H} == 2"), ("TRÊS", f"{H} == 3")])
    linha(130, [("QUATRO", f"{H} == 4"), ("CINCO", f"{H} == 5"), ("SEIS", f"{H} == 6")])
    linha(162, [("SETE", f"{H} == 7"), ("OITO", f"{H} == 8"), ("NOVE", f"{H} == 9")])
    linha(194, [("DEZ", f"{H} == 10"), ("ONZE", f"{H} == 11"), ("DOZE", f"{H} == 12")])
    linha(236, [("HORA", f"{H} == 1"), ("HORAS", f"{H} != 1")])
    linha(282, [("E", f"{M5} &gt;= 1"), ("CINCO", f"{M5} == 1"), ("DEZ", f"{M5} == 2"), ("QUINZE", f"{M5} == 3")])
    linha(314, [("VINTE", f"({M5} == 4 || {M5} == 5)"), ("E", f"({M5} == 5 || {M5} == 7 || {M5} == 9 || {M5} == 11)"), ("CINCO", f"({M5} == 5 || {M5} == 7 || {M5} == 9 || {M5} == 11)")])
    linha(344, [("TRINTA", f"({M5} == 6 || {M5} == 7)"), ("QUARENTA", f"({M5} == 8 || {M5} == 9)")])
    linha(372, [("CINQUENTA", f"({M5} &gt;= 10)")])
    linha(400, [("EM PONTO", f"{M5} == 0")])
    return L


def _py(h: int, mi: int) -> set[tuple[str, int]]:
    """Conjunto de (palavra, y) acesos, para a prévia."""
    h12 = (h - 1) % 12 + 1
    m5 = mi // 5
    ativo = set()
    for pal, cond, x, y in _linhas():
        c = (cond.replace("&gt;=", ">=").replace("{H}", "").replace("[HOUR_1_12]", str(h12)).replace("floor([MINUTE] / 5)", str(m5)).replace("||", " or ").replace("&&", " and "))
        if eval(c):
            ativo.add((pal, y, x))
    return ativo


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    cor = "[CONFIGURATION.cor]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("cor", "cor_label", CORES), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append

    def palavra(pal, cond, x, y, apagado) -> str:
        return (f'<PartText x="{x - 60}" y="{y - 16}" width="120" height="32"><Transform target="alpha" value="{cond} ? 255 : {apagado}" />'
                f'<Text align="CENTER"><Font family="SYNC_TO_DEVICE" size="25" weight="BOLD" color="{cor}"><Template><![CDATA[%s]]><Parameter expression="&quot;{pal}&quot;" /></Template></Font></Text></PartText>')
    a("    " + grupo("vivo", "", 0))
    for pal, cond, x, y in _linhas():
        a("      " + palavra(pal, cond, x, y, 46))
    for k in range(4):
        a("      " + rect(C - 42 + k * 28 - 5, 428, 10, 10, cor, 5, "Fill", 2, f'<Transform target="alpha" value="[MINUTE] % 5 &gt; {k} ? 255 : 46" />'))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    for pal, cond, x, y in _linhas():
        a("      " + palavra(pal, cond, x, y, 0).replace('color="[CONFIGURATION.cor]"', 'color="#ffc0c0c8"'))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(cor: str, h: int, mi: int, ambiente_: bool = False) -> Image.Image:
    c = rgb(cor)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    ativos = _py(h, mi)
    for pal, cond, x, y in _linhas():
        on = (pal, y, x) in ativos
        if ambiente_:
            if on:
                d.text((x, y), pal, font=fonte("Bold", 25), fill=(192, 192, 200, 255), anchor="mm")
        else:
            d.text((x, y), pal, font=fonte("Bold", 25), fill=c + (255 if on else 46,), anchor="mm")
    if not ambiente_:
        for k in range(4):
            on = mi % 5 > k
            d.ellipse([C - 42 + k * 28 - 5, 428, C - 42 + k * 28 + 5, 438], fill=c + (255 if on else 46,))
    base.alpha_composite(cam)
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Words", "cor_label": "Color"}
    pt = {"watch_face_name": "Palavras", "cor_label": "Cor"}
    strings_opcoes(en, pt, "cor", {"branco": ("White", "Branco"), "laranja": ("Orange", "Laranja"), "ciano": ("Cyan", "Ciano"), "verde": ("Green", "Verde"), "rosa": ("Pink", "Rosa")})
    pv = [previa("#ffffff", 10, 28), previa("#ff8a3d", 1, 0), previa("#33d6ff", 7, 47), previa("#6bff9c", 12, 55), previa("#ffffff", 10, 28, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["10:28", "01:00 (uma hora)", "07:47", "12:55", "Ambiente (AOD)"], cols=5, nomes_previa=["dez28", "uma", "sete47", "doze55", "ambiente"])
