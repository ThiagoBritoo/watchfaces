"""Watchface "Terminal": uma tela de linha de comando com a hora em horas:minutos:segundos, barras de bateria e passos e um cursor que pisca
(a cada segundo). Três cores de texto. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rect, rgb, strings_opcoes, tpl

NOME = "terminal"
CORES = [("verde", "#4dff88"), ("ambar", "#ffb938"), ("branco", "#e8eaee"), ("ciano", "#4de1ff")]
X0 = 74


def xml() -> str:
    cor = "[CONFIGURATION.cor]"
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("cor", "cor_label", CORES), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append

    def linha(y, texto, alpha=255, tam=22, peso="MEDIUM"):
        return tpl(X0, y, 330, 30, tam, cor, "%s", [f"&quot;{texto}&quot;"], peso, "START")
    a("    " + grupo("vivo", "", 0))
    a("      " + linha(64, "$ date +%T"))
    a("      " + hora(X0, 94, 340, 80, "hh:mm:ss", 64, cor, "BOLD", "START"))
    a("      " + tpl(X0, 176, 330, 28, 20, "#ff7d8590", "%s, %s %s", ["[DAY_OF_WEEK_F]", "[DAY]", "[MONTH_F]"], "MEDIUM", "START"))
    a("      " + linha(218, "$ battery"))
    a("      " + rect(X0, 250, 240, 14, "#33808080", 3) + rect(X0, 250, 240, 14, cor, 3, "Fill", 2, '<Transform target="width" value="240 * clamp([BATTERY_PERCENT], 0, 100) / 100" />'))
    a("      " + tpl(X0 + 250, 244, 90, 26, 20, cor, "%s%%", ["round([BATTERY_PERCENT])"], "MEDIUM", "START"))
    a("      " + linha(282, "$ steps"))
    a("      " + rect(X0, 314, 240, 14, "#33808080", 3) + rect(X0, 314, 240, 14, cor, 3, "Fill", 2, '<Transform target="width" value="240 * clamp([STEP_PERCENT], 0, 100) / 100" />'))
    a("      " + tpl(X0 + 250, 308, 90, 26, 20, cor, "%s", ["[STEP_COUNT]"], "MEDIUM", "START"))
    a("      " + linha(352, "$ "))
    a("      " + rect(X0 + 36, 354, 14, 24, cor, 2, "Fill", 2, '<Transform target="alpha" value="[SECOND] % 2 == 0 ? 255 : 0" />'))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + tpl(X0, 130, 330, 30, 22, "#ff8e8e96", "%s", ["&quot;$ date +%R&quot;"], "MEDIUM", "START"))
    a("      " + hora(X0, 164, 340, 90, "hh:mm", 72, "#ffc0c0c8", "LIGHT", "START"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(cor: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    c = rgb(cor)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((X0, 145), "$ date +%R", font=fonte("Medium", 22), fill=(142, 142, 150), anchor="lm")
        d.text((X0, 209), f"{h:02d}:{mi:02d}", font=fonte("Light", 72), fill=(192, 192, 200), anchor="lm")
        return redondo(base)
    d.text((X0, 79), "$ date +%T", font=fonte("Medium", 22), fill=c, anchor="lm")
    d.text((X0, 134), f"{h:02d}:{mi:02d}:{s:02d}", font=fonte("Bold", 64), fill=c, anchor="lm")
    d.text((X0, 190), "sexta-feira, 31 outubro", font=fonte("Medium", 20), fill=(125, 133, 144), anchor="lm")
    d.text((X0, 233), "$ battery", font=fonte("Medium", 22), fill=c, anchor="lm")
    for y, f, txt in ((250, 0.89, "89%"), (314, 0.62, "6234")):
        d.rectangle([X0, y, X0 + 240, y + 14], fill=(51, 51, 51))
        d.rectangle([X0, y, X0 + 240 * f, y + 14], fill=c)
        d.text((X0 + 250, y + 7), txt, font=fonte("Medium", 20), fill=c, anchor="lm")
    d.text((X0, 297), "$ steps", font=fonte("Medium", 22), fill=c, anchor="lm")
    d.text((X0, 367), "$ ", font=fonte("Medium", 22), fill=c, anchor="lm")
    if s % 2 == 0:
        d.rectangle([X0 + 36, 354, X0 + 50, 378], fill=c)
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Terminal", "cor_label": "Text color"}
    pt = {"watch_face_name": "Terminal", "cor_label": "Cor do texto"}
    strings_opcoes(en, pt, "cor", {"verde": ("Green", "Verde"), "ambar": ("Amber", "Âmbar"), "branco": ("White", "Branco"), "ciano": ("Cyan", "Ciano")})
    pv = [previa("#4dff88", 10, 8, 32), previa("#ffb938", 21, 45, 7), previa("#4de1ff", 3, 12, 50), previa("#4dff88", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), {}, pv, ["Verde", "Âmbar", "Ciano", "Ambiente (AOD)"], cols=4, nomes_previa=["verde", "ambar", "ciano", "ambiente"])
