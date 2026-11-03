"""Watchface "Pêndulo": um pêndulo balança (tic-tac a cada segundo) e a hora fica dentro do peso, sempre de pé.
Arte e código originais."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, redondo, rgb, textos_acento, tint, tpl

NOME = "pendulo"
PIV = (240, 30)
HASTE = 250
RAIO = 72
AMP = 24


def peso() -> Image.Image:
    t = 2 * RAIO + 8
    g = grad_radial(t, t / 2 - 22, t / 2 - 26, [(0, (255, 255, 255, 255)), (RAIO * 0.7, (214, 214, 214, 255)), (RAIO * 1.25, (120, 120, 120, 255))])
    m = Image.new("L", (t * 4, t * 4), 0)
    ImageDraw.Draw(m).ellipse([16, 16, t * 4 - 16, t * 4 - 16], fill=255)
    g.putalpha(m.resize((t, t), Image.LANCZOS))
    return g


def xml() -> str:
    full = f'x="0" y="0" width="{W}" height="{W}"'
    ac = "[CONFIGURATION.acento]"
    t = 2 * RAIO + 8
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    gx, gy, gw, gh = PIV[0] - 100, PIV[1], 200, HASTE + 2 * RAIO + 20
    cx_local = 100
    bob_y = HASTE
    def balanco(ang_expr: str | None, ambient: int) -> str:
        tr = f'<Transform target="angle" value="{ang_expr}" />' if ang_expr else ""
        contra = f'<Transform target="angle" value="-({ang_expr})" />' if ang_expr else ""
        return (f'<Group name="bal_{ambient}" x="{gx}" y="{gy}" width="{gw}" height="{gh}" pivotX="0.5" pivotY="0" {"alpha=" + chr(34) + "0" + chr(34) if ambient else ""}>{tr}'
                f'<Variant mode="AMBIENT" target="alpha" value="{255 if ambient else 0}" />'
                f'<PartDraw x="{cx_local - 1}" y="0" width="2" height="{bob_y}"><Rectangle x="0" y="0" width="2" height="{bob_y}"><Fill color="#ffb0b0b8" /></Rectangle></PartDraw>'
                f'<PartImage x="{cx_local - t // 2}" y="{bob_y - 4}" width="{t}" height="{t}" tintColor="{ac}"><Image resource="peso" /></PartImage>'
                f'<Group name="txt_{ambient}" x="{cx_local - t // 2}" y="{bob_y - 4}" width="{t}" height="{t}" pivotX="0.5" pivotY="0.5">{contra}'
                + hora(0, t // 2 - 30, t, 60, "hh", 34, "#ff101014", "BOLD", "CENTER") + hora(0, t // 2 - 2, t, 40, "mm", 30, "#cc101014", "MEDIUM", "CENTER") +
                "</Group></Group>")
    a("    " + grupo("fixo", "", 0) + f'<PartDraw {full}><Arc centerX="{PIV[0]}" centerY="{PIV[1]}" width="{2 * (HASTE + RAIO)}" height="{2 * (HASTE + RAIO)}" startAngle="{180 - AMP - 8}" endAngle="{180 + AMP + 8}"><Stroke thickness="3" color="#33ffffff" cap="ROUND" /></Arc></PartDraw>'
      + tpl(110, 440, 260, 28, 20, "#ff8e8e96", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM") + "</Group>")
    a("    " + balanco(f"{AMP} * cos([SECOND] * 3.14159)", 0))
    a("    " + balanco(None, 1))
    a(f'    <PartDraw x="{PIV[0] - 8}" y="{PIV[1] - 8}" width="16" height="16"><Ellipse x="0" y="0" width="16" height="16"><Fill color="{ac}" /></Ellipse></PartDraw>')
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    th = 0 if ambiente_ else AMP * math.cos(s * math.pi)
    r = HASTE + RAIO
    if not ambiente_:
        d.arc([PIV[0] - r, PIV[1] - r, PIV[0] + r, PIV[1] + r], 90 - AMP - 8, 90 + AMP + 8, fill=(255, 255, 255, 51), width=3)
        d.text((C, 454), "SEX 31 OUT", font=fonte("Medium", 20), fill=(142, 142, 150), anchor="mm")
    bx, by = PIV[0] + (HASTE + 4 + RAIO - 4) * math.sin(math.radians(th)), PIV[1] + (HASTE + RAIO) * math.cos(math.radians(th))
    d.line([PIV, (PIV[0] + HASTE * math.sin(math.radians(th)), PIV[1] + HASTE * math.cos(math.radians(th)))], fill=(176, 176, 184), width=2)
    bx, by = PIV[0] + (HASTE + RAIO) * math.sin(math.radians(th)), PIV[1] + (HASTE + RAIO) * math.cos(math.radians(th))
    pe = tint(A["peso"], ac if not ambiente_ else (120, 120, 126))
    base.alpha_composite(pe, (int(bx - pe.width / 2), int(by - pe.height / 2)))
    d = ImageDraw.Draw(base)
    d.text((bx, by - 14), f"{h:02d}", font=fonte("Bold", 34), fill=(16, 16, 20), anchor="mm")
    d.text((bx, by + 18), f"{mi:02d}", font=fonte("Medium", 30), fill=(40, 40, 44), anchor="mm")
    d.ellipse([PIV[0] - 8, PIV[1] - 8, PIV[0] + 8, PIV[1] + 8], fill=ac)
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Pendulum", "Pêndulo")
    A = {"peso": peso()}
    pv = [previa(A, "#f2c14e", 10, 8, 3), previa(A, "#33d6ff", 10, 8, 7), previa(A, "#ff5c93", 4, 30, 10), previa(A, "#f2c14e", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Ouro (esquerda)", "Ciano (direita)", "Rosa", "Ambiente (AOD)"], cols=4, nomes_previa=["ouro", "ciano", "rosa", "ambiente"])
