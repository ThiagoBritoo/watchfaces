"""Watchface "Lupa": mostrador analógico minimalista com os números 12, 3, 6 e 9 GIGANTES, cortados pela borda da tela, e ponteiros finos por cima.
Cinco cores. Original."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.desenho import SS, fonte, reduzir_por, tela, texto_centrado, polar
from wf.kit import ACENTOS_PADRAO, C, W, cabecalho, cor_config, finalizar, girar, grupo, img, redondo, rgb, textos_acento, tint, tpl

NOME = "lupa"


def numeros() -> Image.Image:
    n = W * SS
    im = tela(n)
    f = fonte("Black", 330 * SS)
    for t, (x, y) in {"12": (C, 20), "3": (452, C), "6": (C, 466), "9": (28, C)}.items():
        texto_centrado(im, t, x * SS, y * SS, f, (255, 255, 255, 255))
    return reduzir_por(im)


def mao(comp, larg, cauda):
    s = 4
    pad = 4
    w, h = int(larg) + 2 * pad, int(comp + cauda) + 2 * pad
    w += w % 2
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([w * s / 2 - larg / 2 * s, pad * s, w * s / 2 + larg / 2 * s, (pad + comp + cauda) * s], radius=larg / 2 * s, fill=(255, 255, 255, 255))
    return im.resize((w, h), Image.LANCZOS), pad + comp


def xml(med) -> str:
    ac = "[CONFIGURATION.acento]"
    full = f'x="0" y="0" width="{W}" height="{W}"'

    def m(tipo, nome, extra=""):
        w, h, py = med[nome]
        return f'<{tipo} resource="{nome}" x="{C - w // 2}" y="{round(C - py)}" width="{w}" height="{h}" pivotX="0.5" pivotY="{py / h:.6f}"{extra} />'
    L = cabecalho(NOME) + ["  <UserConfigurations>", cor_config("acento", "acento_label", ACENTOS_PADRAO), "  </UserConfigurations>", '  <Scene backgroundColor="#ff000000">']
    a = L.append
    a("    " + grupo("numeros", "", 0) + img(0, 0, W, W, "numeros", ' alpha="64"', f'<Variant mode="AMBIENT" target="alpha" value="0" />') + "</Group>")
    a("    " + grupo("data", "", 0) + tpl(190, 330, 100, 30, 22, "#ffffffff", "%s %s", ["[DAY_OF_WEEK_S]", "[DAY]"], "MEDIUM") + "</Group>")
    a(f'    <AnalogClock {full}><Variant mode="AMBIENT" target="alpha" value="0" />' + m("HourHand", "hora") + m("MinuteHand", "min") + m("SecondHand", "seg", f' tintColor="{ac}"').replace(" />", '><Sweep frequency="15" /></SecondHand>') + "</AnalogClock>")
    a(f'    <AnalogClock {full} alpha="0"><Variant mode="AMBIENT" target="alpha" value="255" />' + m("HourHand", "hora", ' tintColor="#ffd0d0d6"') + m("MinuteHand", "min", ' tintColor="#ffd0d0d6"') + "</AnalogClock>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"


def previa(A, acento: str, h: int, mi: int, s: int, ambiente_: bool = False) -> Image.Image:
    ac = rgb(acento)
    base = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    if not ambiente_:
        n = A["numeros"].copy()
        r, g, b, al = n.split()
        base.alpha_composite(Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * 64 / 255)))))
        ImageDraw.Draw(base).text((C, 345), "SEX 31", font=fonte("Medium", 22), fill=(255, 255, 255), anchor="mm")
    angs = [("hora", (h % 12) * 30 + mi * 0.5), ("min", mi * 6 + s * 0.1)] + ([] if ambiente_ else [("seg", s * 6)])
    for nome, ang in angs:
        im, py = A[nome]
        cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        cor = ac if nome == "seg" else ((208, 208, 214) if ambiente_ else (255, 255, 255))
        cam.alpha_composite(tint(im, cor), (int(C - im.width / 2), int(round(C - py))))
        base.alpha_composite(cam.rotate(-ang, center=(C, C), resample=Image.BICUBIC))
    return redondo(base)


def gerar(raiz: Path) -> dict:
    en, pt = {}, {}
    textos_acento(en, pt, "Magnifier", "Lupa")
    A = {"numeros": numeros(), "hora": mao(110, 14, 20), "min": mao(176, 9, 24), "seg": mao(214, 3, 44)}
    med = {k: (v[0].width, v[0].height, v[1]) for k, v in A.items() if isinstance(v, tuple)}
    med_k = {k: med[k] for k in med}
    imgs = {k: (v[0] if isinstance(v, tuple) else v) for k, v in A.items()}
    pv = [previa(A, "#ff7a2f", 10, 8, 20), previa(A, "#33d6ff", 3, 45, 40), previa(A, "#f2c14e", 7, 22, 5), previa(A, "#ff7a2f", 10, 8, 0, True)]
    return finalizar(raiz, NOME, en, pt, xml(med_k), imgs, pv, ["Laranja", "Ciano", "Ouro", "Ambiente (AOD)"], cols=4, nomes_previa=["laranja", "ciano", "ouro", "ambiente"])
