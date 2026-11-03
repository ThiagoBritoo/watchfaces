"""Watchface "Engrenagens": três engrenagens de metal realmente engrenadas (dentes encaixados) giram juntas no ritmo do relógio; a hora fica
no cubo da maior. Reaproveita a arte das engrenagens da Cronos. Original."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import fonte
from wf.kit import C, W, cabecalho, cor_config, finalizar, grupo, hora, img, redondo, strings_opcoes, tpl

from . import cronos_assets as CA

NOME = "engrenagens"
G = [(190, 250, 118, 30), None, None]            # cx, cy, raio, dentes (as outras são calculadas)
R2, N2, R3, N3 = 64, 18, 46, 13
TH12, TH23 = 60.0, 150.0                           # direções de contato (graus, horário a partir do topo)
FUNDO = {"aco": "rc", "ouro": "noir", "bronze": "frost"}


def geometria() -> list[tuple[float, float, int, int]]:
    g1 = (190.0, 250.0, 118, 30)
    d12 = 118 + R2 - 4
    g2 = (g1[0] + d12 * math.sin(math.radians(TH12)), g1[1] - d12 * math.cos(math.radians(TH12)), R2, N2)
    d23 = R2 + R3 - 4
    g3 = (g2[0] + d23 * math.sin(math.radians(TH23)), g2[1] - d23 * math.cos(math.radians(TH23)), R3, N3)
    return [g1, g2, g3]


def fases() -> list[float]:
    """Rotações iniciais (graus) para que os dentes se encaixem. O dente 0 de engrenagem() está a 90/N graus do topo."""
    gs = geometria()
    p = [90 / g[3] for g in gs]
    pas = [360 / g[3] for g in gs]
    r1 = (TH12 - p[0]) % pas[0]
    r2 = (TH12 + 180 - p[1] - pas[1] / 2) % pas[1]
    u = ((TH23 - r2 - p[1]) % pas[1]) / pas[1]
    u3 = (u + 0.5) % 1
    r3 = (TH23 + 180 - p[2] - u3 * pas[2]) % pas[2]
    return [r1, r2, r3]


def angulos(delta: float) -> list[float]:
    gs, ph = geometria(), fases()
    a1 = ph[0] + delta
    a2 = ph[1] - delta * gs[0][3] / gs[1][3]
    a3 = ph[2] + delta * gs[0][3] / gs[2][3] * 1.0
    # G3 gira em sentido oposto a G2 (mesmo sentido de G1): delta * N1/N3 com sinal positivo
    return [a1, a2, a3]


def xml() -> str:
    gs, ph = geometria(), fases()
    full = f'x="0" y="0" width="{W}" height="{W}"'
    L = cabecalho(NOME, "DIGITAL") + ["  <UserConfigurations>", '    <ListConfiguration id="metal" displayName="metal_label" defaultValue="aco">'
                                      + "".join(f'<ListOption id="{k}" displayName="metal_{k}" />' for k in FUNDO) + "</ListConfiguration>", "  </UserConfigurations>",
                                      '  <Scene backgroundColor="#ff000000">']
    a = L.append
    delta = "(([MINUTE] * 60 + [SECOND]) * 0.6)"
    a("    " + grupo("engrenagens", "", 0) + '<ListConfiguration id="metal">')
    for k in FUNDO:
        a(f'      <ListOption id="{k}"><Group name="m_{k}" {full}>')
        for i, (cx, cy, r, n) in enumerate(gs):
            tam = 2 * r + 8
            tam += tam % 2
            sinal = "-" if i == 1 else "+"
            expr = f"{ph[i]:.3f} {sinal} {delta} * {gs[0][3] / n:.5f}"
            a(f'        <PartImage x="{round(cx - tam / 2)}" y="{round(cy - tam / 2)}" width="{tam}" height="{tam}" pivotX="0.5" pivotY="0.5">'
              f'<Image resource="eng_{k}_{i}" /><Transform target="angle" value="{expr}" /></PartImage>')
        a("      </Group></ListOption>")
    a("    </ListConfiguration>")
    a(f'      <PartDraw {full}><Ellipse x="{190 - 62}" y="{250 - 62}" width="124" height="124"><Fill color="#e6000000" /></Ellipse></PartDraw>')
    a("      " + hora(190 - 70, 250 - 34, 140, 68, "hh:mm", 50, "#ffffffff", "BOLD", "CENTER"))
    a("      " + tpl(300, 360, 150, 28, 20, "#ffa0a0a8", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM"))
    a("    </Group>")
    a("    " + grupo("ambiente", ' alpha="0"', 255))
    a(f'      <PartDraw {full}><Ellipse x="{190 - 118}" y="{250 - 118}" width="236" height="236"><Stroke thickness="2" color="#88ffffff" /></Ellipse></PartDraw>')
    a("      " + hora(190 - 70, 250 - 34, 140, 68, "hh:mm", 50, "#ffc0c0c8", "MEDIUM", "CENTER"))
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, metal: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    d = ImageDraw.Draw(base)
    gs = geometria()
    if ambiente_:
        d.ellipse([190 - 118, 250 - 118, 190 + 118, 250 + 118], outline=(136, 136, 136), width=2)
        d.text((190, 250), f"{h:02d}:{mi:02d}", font=fonte("Medium", 50), fill=(192, 192, 200), anchor="mm")
        return redondo(base)
    delta = (mi * 60 + s) * 0.6
    ph = fases()
    for i, (cx, cy, r, n) in enumerate(gs):
        ang = ph[i] + (-1 if i == 1 else 1) * delta * gs[0][3] / n
        im = A[f"eng_{metal}_{i}"]
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        cam.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))
        base.alpha_composite(cam.rotate(-ang, center=(round(cx - im.width / 2) + im.width / 2, round(cy - im.height / 2) + im.height / 2), resample=Image.BICUBIC))
    d = ImageDraw.Draw(base)
    cam2 = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(cam2).ellipse([190 - 62, 250 - 62, 190 + 62, 250 + 62], fill=(0, 0, 0, 230))
    base.alpha_composite(cam2)
    d = ImageDraw.Draw(base)
    d.text((190, 250), f"{h:02d}:{mi:02d}", font=fonte("Bold", 50), fill=(255, 255, 255), anchor="mm")
    d.text((375, 374), "SEX 31", font=fonte("Medium", 20), fill=(160, 160, 168), anchor="mm")
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en = {"watch_face_name": "Gears", "metal_label": "Metal", "metal_aco": "Steel", "metal_ouro": "Gold", "metal_bronze": "Bronze"}
    pt = {"watch_face_name": "Engrenagens", "metal_label": "Metal", "metal_aco": "Aço", "metal_ouro": "Ouro", "metal_bronze": "Bronze"}
    A = {}
    for k, tema in FUNDO.items():
        for i, (cx, cy, r, n) in enumerate(geometria()):
            A[f"eng_{k}_{i}"] = CA.engrenagem(CA.TEMAS[tema], r, n)
    pv = [previa(A, "aco", 10, 8, 20), previa(A, "ouro", 10, 8, 50), previa(A, "bronze", 4, 31, 5), previa(A, "aco", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(), A, pv, ["Aço", "Ouro", "Bronze", "Ambiente (AOD)"], cols=4, nomes_previa=["aco", "ouro", "bronze", "ambiente"])
