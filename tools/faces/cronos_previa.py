"""Renderiza prévias da Cronos sem precisar do relógio.

É uma SIMULAÇÃO em Python com os mesmos PNGs que vão no APK: serve para conferir o desenho,
posição e proporção. O brilho/animação reais só aparecem no relógio (ou no emulador).
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from wf.desenho import fonte, polar

from .cronos_assets import C, ENGRENAGENS, GAUGES, R_GAUGE, TEMAS, TEXTOS, W, fase_engrenagens
from .cronos_xml import ACENTOS


def _girar(layer_size: int, img: Image.Image, pivo_y: float, ang: float) -> Image.Image:
    """Cola `img` com o pivô no centro e gira `ang` graus (horário) em volta dele."""
    g = Image.new("RGBA", (layer_size * 2, layer_size * 2), (0, 0, 0, 0))
    g.alpha_composite(img, (int(layer_size - img.width / 2), int(round(layer_size - pivo_y))))
    g = g.rotate(-ang, center=(layer_size, layer_size), resample=Image.BICUBIC)
    return g.crop((layer_size // 2, layer_size // 2, layer_size // 2 + layer_size, layer_size // 2 + layer_size))


def _complicacoes(img: Image.Image, A, acento: tuple[int, int, int], t) -> None:
    """Simula o que o relógio desenha nos slots: agulhas nos dois mostradores e texto nos quatro campos."""
    ag, py = A.agulha
    cor = Image.new("RGBA", ag.size, (*acento, 255))
    r, g, b, a = ag.split()
    tint = Image.merge("RGBA", (r.point(lambda v: v * acento[0] // 255), g.point(lambda v: v * acento[1] // 255),
                                b.point(lambda v: v * acento[2] // 255), a))
    for (nome, (cx, cy)), norm in zip(GAUGES.items(), (0.76, 0.62)):
        ang = -135 + norm * 270
        g_ = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        g_.alpha_composite(tint, (int(cx - ag.width / 2), int(round(cy - py))))
        img.alpha_composite(g_.rotate(-ang, center=(cx, cy), resample=Image.BICUBIC))
    d = ImageDraw.Draw(img)
    dados = {"te": ("LON", "9:08"), "td": ("STEPS", "5500"), "be": ("SOL", "18:49"), "bd": ("NOTIF", "3")}
    for nome, (cx, cy) in TEXTOS.items():
        titulo, valor = dados[nome]
        d.text((cx, cy - 13), titulo, font=fonte("Medium", 13), fill=(*acento, 255), anchor="mm")
        d.text((cx, cy + 9), valor, font=fonte("SemiBold", 24), fill=(*t.texto, 255), anchor="mm")


def previa(A, tema_id: str, estilo: str, h: int, m: int, s: int, acento_idx: int = 0,
           ambiente: bool = False) -> Image.Image:
    """A = Ativos (ver cronos.py). Retorna RGBA 480x480 recortado em círculo."""
    t = TEMAS[tema_id]
    tela_ = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    ang_h = (h % 12) * 30 + m * 0.5 + s / 120
    ang_m = m * 6 + s * 0.1
    ang_s = s * 6
    if ambiente:
        tela_.alpha_composite(A.ambiente[tema_id])
        d = ImageDraw.Draw(tela_)
        cor = tuple(int(v * 0.5) for v in t.texto)
        d.text((C, 352), "SEX 31", font=fonte("Medium", 17), fill=(*cor, 255), anchor="mm")
        for nome, ang in (("hora", ang_h), ("min", ang_m)):
            im, py = A.maos[f"{nome}_contorno_{estilo}"]
            tela_.alpha_composite(_girar(W, im, py, ang))
    else:
        tela_.alpha_composite(A.fundo[tema_id])
        fases = fase_engrenagens()
        for pos, (gx, gy, raio, dentes) in ENGRENAGENS.items():
            gear = A.gear[(tema_id, pos)]
            ang = s * 6 + fases[pos] if pos == "meio" else fases[pos] - s * 6 * ENGRENAGENS["meio"][3] / dentes
            g = Image.new("RGBA", (W, W), (0, 0, 0, 0))
            g.alpha_composite(gear, (gx - gear.width // 2, gy - gear.height // 2))
            tela_.alpha_composite(g.rotate(-ang, center=(gx, gy), resample=Image.BICUBIC))
        d = ImageDraw.Draw(tela_)
        d.text((C, 352), "SEX 31", font=fonte("Medium", 17), fill=(*t.texto, 255), anchor="mm")
        _complicacoes(tela_, A, tuple(int(ACENTOS[acento_idx][i:i + 2], 16) for i in (1, 3, 5)), t)
        for nome, ang in (("hora", ang_h), ("min", ang_m)):
            sh, py = A.maos[f"{nome}_sombra_{estilo}"]
            tela_.alpha_composite(_girar(W, sh, py, ang))
        for nome, ang in (("hora", ang_h), ("min", ang_m)):
            im, py = A.maos[f"{nome}_{estilo}_{tema_id}"]
            tela_.alpha_composite(_girar(W, im, py, ang))
        sh, py = A.maos["seg_sombra"]
        tela_.alpha_composite(_girar(W, sh, py, ang_s))
        im, py = A.maos["seg"]
        cor = tuple(int(ACENTOS[acento_idx][i:i + 2], 16) for i in (1, 3, 5))
        r, g_, b, a = im.split()
        r = r.point(lambda v, c=cor[0]: v * c // 255)
        g_ = g_.point(lambda v, c=cor[1]: v * c // 255)
        b = b.point(lambda v, c=cor[2]: v * c // 255)
        tela_.alpha_composite(_girar(W, Image.merge("RGBA", (r, g_, b, a)), py, ang_s))
        tela_.alpha_composite(A.tampa[tema_id], (C - 24, C - 24))
        tela_.alpha_composite(A.vidro)
    mascara = Image.new("L", (W * 4, W * 4), 0)
    ImageDraw.Draw(mascara).ellipse([0, 0, W * 4 - 1, W * 4 - 1], fill=255)
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    out.paste(tela_, (0, 0), mascara.resize((W, W), Image.LANCZOS))
    return out


def folha(imagens: list[Image.Image], legendas: list[str], cols: int = 4) -> Image.Image:
    esp, topo = 16, 34
    linhas = (len(imagens) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (W + esp) + esp, linhas * (W + topo + esp) + esp), (28, 28, 32))
    d = ImageDraw.Draw(sheet)
    for i, (im, leg) in enumerate(zip(imagens, legendas)):
        x = esp + (i % cols) * (W + esp)
        y = esp + (i // cols) * (W + topo + esp)
        sheet.paste(im, (x, y + topo), im)
        d.text((x + W // 2, y + 14), leg, font=fonte("Medium", 18), fill=(210, 210, 215), anchor="mm")
    return sheet
