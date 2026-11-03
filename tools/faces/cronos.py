"""Orquestra a geração da watchface Cronos: PNGs, XML, recursos Android e prévias."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw

from . import cronos_assets as A_
from .cronos_assets import C, TEMAS
from .cronos_previa import folha, previa
from wf.modulo import nomear_grupos
from .cronos_xml import ACENTOS, ESTILOS, MEDIDAS, PAD_SOMBRA, SEG, Medidas, gerar_xml

NOME = "cronos"
PACOTE = "br.com.thiagobritoo.watchfaces.cronos"


@dataclass
class Ativos:
    fundo: dict[str, Image.Image] = field(default_factory=dict)
    ambiente: dict[str, Image.Image] = field(default_factory=dict)
    gear: dict[tuple[str, str], Image.Image] = field(default_factory=dict)
    agulha: tuple[Image.Image, float] | None = None
    tampa: dict[str, Image.Image] = field(default_factory=dict)
    maos: dict[str, tuple[Image.Image, float]] = field(default_factory=dict)
    vidro: Image.Image | None = None


def construir() -> Ativos:
    a = Ativos()
    for tid, t in TEMAS.items():
        print(f"  tema {tid}: mostrador, ambiente, engrenagem, tampa")
        a.fundo[tid] = A_.mostrador(t)
        a.ambiente[tid] = A_.mostrador_ambiente(t)
        for pos, (_, _, raio, dentes) in A_.ENGRENAGENS.items():
            a.gear[(tid, pos)] = A_.engrenagem(t, raio, dentes)
        a.tampa[tid] = A_.tampa_central(t)
    ref = TEMAS["rc"]
    for est in ESTILOS:
        for nome in ("hora", "min"):
            comp, cauda, larg = MEDIDAS[nome][est]
            for tid, t in TEMAS.items():
                a.maos[f"{nome}_{est}_{tid}"] = A_.ponteiro(t, est, comp, cauda, larg)
            im, py = a.maos[f"{nome}_{est}_rc"]
            a.maos[f"{nome}_sombra_{est}"] = A_.ponteiro_sombra(im, py, PAD_SOMBRA)
            a.maos[f"{nome}_contorno_{est}"] = A_.ponteiro_contorno(ref, est, comp, cauda, larg)
    seg, py = A_.ponteiro_segundos(*SEG)
    a.maos["seg"] = (seg, py)
    a.maos["seg_sombra"] = A_.ponteiro_sombra(seg, py, PAD_SOMBRA)
    a.agulha = A_.agulha()
    a.vidro = A_.vidro()
    return a


def _icone_estilo(a: Ativos, est: str) -> Image.Image:
    base = Image.new("RGBA", (192, 192), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    d.ellipse([2, 2, 189, 189], fill=(22, 22, 26, 255), outline=(150, 150, 158, 255), width=3)
    im, py = a.maos[f"min_{est}_rc"]
    k = 0.62
    im2 = im.resize((max(1, int(im.width * k)), int(im.height * k)), Image.LANCZOS)
    g = Image.new("RGBA", (384, 384), (0, 0, 0, 0))
    g.alpha_composite(im2, (192 - im2.width // 2, int(192 - py * k)))
    g = g.rotate(-35, center=(192, 192), resample=Image.BICUBIC).crop((96, 96, 288, 288))
    base.alpha_composite(g)
    return base


def gerar(raiz: Path) -> dict:
    """Escreve tudo em faces/cronos/ e previews/. Retorna estatísticas."""
    mod = raiz / "faces" / NOME / "src" / "main"
    dr = mod / "res" / "drawable-nodpi"
    for p in (dr, mod / "res" / "raw", mod / "res" / "xml", mod / "res" / "values", mod / "res" / "values-pt",
              raiz / "previews"):
        p.mkdir(parents=True, exist_ok=True)
    print("Gerando assets (leva ~1 min)...")
    a = construir()
    med = Medidas()

    def salvar(nome: str, im: Image.Image) -> None:
        im.save(dr / f"{nome}.png", optimize=True)

    for tid in TEMAS:
        salvar(f"fundo_{tid}", a.fundo[tid])
        salvar(f"ambiente_{tid}", a.ambiente[tid])
        for pos in A_.ENGRENAGENS:
            salvar(f"engrenagem_{tid}_{pos}", a.gear[(tid, pos)])
        salvar(f"tampa_{tid}", a.tampa[tid])
    salvar("vidro", a.vidro)
    salvar("agulha", a.agulha[0])
    med.mao("agulha", a.agulha[0].width, a.agulha[0].height, a.agulha[1])
    for nome, (im, py) in a.maos.items():
        salvar(nome, im)
        med.mao(nome, im.width, im.height, py)
    xml = gerar_xml(med)
    (mod / "res" / "raw" / "watchface.xml").write_text(nomear_grupos(xml), encoding="utf-8")

    # prévias (simulação) + ícones do editor
    print("Renderizando prévias...")
    pv = {tid: previa(a, tid, "bastao" if tid in ("frost", "romano") else "espada", 10, 8, 32, {"rc": 0, "frost": 1, "noir": 2, "romano": 2, "neon": 6}[tid]) for tid in TEMAS}
    for tid, im in pv.items():
        im.save(raiz / "previews" / f"cronos_{tid}.png", optimize=True)
        salvar(f"icone_tema_{tid}", im.resize((192, 192), Image.LANCZOS))
    pv["rc"].resize((450, 450), Image.LANCZOS).save(dr / "preview.png", optimize=True)
    amb = previa(a, "rc", "espada", 10, 8, 32, ambiente=True)
    amb.save(raiz / "previews" / "cronos_ambiente.png", optimize=True)
    for est in ESTILOS:
        salvar(f"icone_estilo_{est}", _icone_estilo(a, est))
    extra = [previa(a, "noir", "bastao", 7, 42, 10, 3), previa(a, "frost", "espada", 3, 15, 50, 4),
             previa(a, "rc", "bastao", 1, 55, 20, 5)]
    folha([pv["rc"], pv["frost"], pv["noir"], pv["romano"], pv["neon"], amb] + extra, ["Preto e vermelho", "Frost (branco/bronze/azul)", "Noir (preto/dourado)", "Romanos (branco/dourado)", "Neon (grafite/ciano)", "Ambiente (AOD)",
          "Noir + bastão + laranja", "Frost + espada + verde", "RC + bastão + roxo"], cols=4).save(
        raiz / "previews" / "cronos_folha.png", optimize=True)
    return {"xml_bytes": len(xml)}
