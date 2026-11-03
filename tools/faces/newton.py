"""Watchface "Newton": o pêndulo de Newton, cinco bolas penduradas com os dígitos da hora (H H : M M). A cada segundo a bola da esquerda ou da
direita balança. Cinco cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte, grad_radial
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, rect, rgb, textos_acento, tint, tpl, colar

NOME = "newton"
D = 68
PASSO = 70
BAR_Y = 92
FIO = 120
SW = 22                                     # amplitude do balanço (graus)


def bola() -> Image.Image:
    t = D + 8
    g = grad_radial(t, t / 2 - 14, t / 2 - 16, [(0, (255, 255, 255, 255)), (D * 0.5, (206, 208, 214, 255)), (D * 0.82, (116, 118, 126, 255))])
    m = Image.new("L", (t * 4, t * 4), 0)
    ImageDraw.Draw(m).ellipse([16, 16, t * 4 - 16, t * 4 - 16], fill=255)
    g.putalpha(m.resize((t, t), Image.LANCZOS))
    return g


DIG = ["floor([HOUR_0_23] / 10)", "[HOUR_0_23] % 10", None, "floor([MINUTE] / 10)", "[MINUTE] % 10"]


def xml() -> str:
    ac = "[CONFIGURATION.acento]"
    t = D + 8
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("vivo", "", 0))
    a("      " + rect(C - 2 * PASSO - 50, BAR_Y - 8, 4 * PASSO + 100, 10, "#ffb4b8c0", 5))
    for i in range(5):
        cx = C + (i - 2) * PASSO
        gx, gy, gw, gh = cx - 40, BAR_Y, 80, FIO + t + 4
        if i == 0:
            ang = "[SECOND] % 2 == 0 ? " + str(SW) + " : 0"
        elif i == 4:
            ang = "[SECOND] % 2 == 1 ? -" + str(SW) + " : 0"
        else:
            ang = None
        tr = f'<Transform target="angle" value="{ang}" />' if ang else ""
        contra = f'<Transform target="angle" value="-({ang})" />' if ang else ""
        txt = ""
        if DIG[i]:
            txt = tpl(0, t // 2 - 22, t, 44, 36, "#ff15161a", "%s", [f"numberFormat(&quot;0&quot;, {DIG[i]})"], "BOLD")
        else:
            txt = tpl(0, t // 2 - 22, t, 44, 36, "#ff15161a", "%s", ["&quot;:&quot;"], "BOLD")
        a(f'      <Group name="bola{i}" x="{gx}" y="{gy}" width="{gw}" height="{gh}" pivotX="0.5" pivotY="0">{tr}'
          f'<PartDraw x="39" y="0" width="2" height="{FIO}"><Rectangle x="0" y="0" width="2" height="{FIO}"><Fill color="#ff9a9ea6" /></Rectangle></PartDraw>'
          + img(40 - t // 2, FIO - 4, t, t, "bola", f' tintColor="{ac}"')
          + f'<Group name="dig{i}" x="{40 - t // 2}" y="{FIO - 4}" width="{t}" height="{t}" pivotX="0.5" pivotY="0.5">{contra}{txt}</Group></Group>')
    a("      " + tpl(110, 392, 260, 28, 20, "#ff8e8e96", "%s %s %s", ["[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a("      " + hora(40, 160, 400, 140, "hh:mm", 110, "#ffc0c0c8", "LIGHT", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    import math
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    if ambiente_:
        d.text((C, 232), f"{h:02d}:{mi:02d}", font=fonte("Light", 110), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    t = D + 8
    d.rounded_rectangle([C - 2 * PASSO - 50, BAR_Y - 8, C + 2 * PASSO + 50, BAR_Y + 2], radius=5, fill=(180, 184, 192))
    vals = [h // 10, h % 10, ":", mi // 10, mi % 10]
    bola_t = tint(A["bola"], ac)
    for i in range(5):
        cx = C + (i - 2) * PASSO
        ang = 0
        if i == 0 and s % 2 == 0:
            ang = SW
        if i == 4 and s % 2 == 1:
            ang = -SW
        r = math.radians(ang)
        bx, by = cx - (FIO + t / 2 - 4) * math.sin(r), BAR_Y + (FIO + t / 2 - 4) * math.cos(r)
        d.line([(cx, BAR_Y), (cx - FIO * math.sin(r), BAR_Y + FIO * math.cos(r))], fill=(154, 158, 166), width=2)
        base.alpha_composite(bola_t, (int(bx - t / 2), int(by - t / 2)))
        d = ImageDraw.Draw(base)
        d.text((bx, by), str(vals[i]), font=fonte("Bold", 36), fill=(21, 22, 26), anchor="mm")
    d.text((C, 406), "SEX 31 OUT", font=fonte("Medium", 20), fill=(142, 142, 150), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Newton", "Newton")
    A = {"bola": bola()}
    pv = [previa(A, "#f2c14e", 10, 8, 20), previa(A, "#33d6ff", 21, 45, 7), previa(A, "#ff5c93", 3, 12, 30), previa(A, "#f2c14e", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Segundo par (esquerda)", "Segundo ímpar (direita)", "Rosa", "Ambiente (AOD)"], cols=4, nomes_previa=["par", "impar", "rosa", "ambiente"])
