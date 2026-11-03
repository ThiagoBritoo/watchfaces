"""Utilidades comuns às watchfaces: cores, prévia redonda, salvar módulo/PNGs/prévias, configurações de cor."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from wf.modulo import criar_modulo, nomear_grupos

W = 480
C = 240


def rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")[-6:]
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def tint(im: Image.Image, cor) -> Image.Image:
    """Multiplica o RGB da imagem (branca) pela cor, como o tintColor do relógio."""
    r, g, b, a = im.convert("RGBA").split()
    return Image.merge("RGBA", (r.point(lambda v: v * cor[0] // 255), g.point(lambda v: v * cor[1] // 255),
                                b.point(lambda v: v * cor[2] // 255), a))


def girar(img: Image.Image, centro: tuple[float, float], ang: float, canvas: int = W) -> Image.Image:
    """Gira (horário, em graus) uma camada de tamanho do canvas em torno de `centro`."""
    return img.rotate(-ang, center=centro, resample=Image.BICUBIC)


def colar(base: Image.Image, img: Image.Image, x: int, y: int) -> None:
    """alpha_composite que aceita posição negativa ou fora da tela."""
    cam = Image.new("RGBA", base.size, (0, 0, 0, 0))
    cam.paste(img, (x, y))
    base.alpha_composite(cam)


def redondo(base: Image.Image) -> Image.Image:
    mk = Image.new("L", (W * 4, W * 4), 0)
    ImageDraw.Draw(mk).ellipse([0, 0, W * 4 - 1, W * 4 - 1], fill=255)
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    out.paste(base, (0, 0), mk.resize((W, W), Image.LANCZOS))
    return out


def cor_config(id_: str, nome_label: str, opcoes: list[tuple[str, str]], padrao: str | None = None) -> str:
    """ColorConfiguration (cada opção: (id, 'cor1 cor2 ...'))."""
    ops = "\n".join(f'      <ColorOption id="{i}" displayName="{id_}_{i}" colors="{c}" />' for i, c in opcoes)
    return (f'    <ColorConfiguration id="{id_}" displayName="{nome_label}" defaultValue="{padrao or opcoes[0][0]}">\n{ops}\n'
            "    </ColorConfiguration>")


def strings_opcoes(en: dict, pt: dict, id_: str, nomes: dict[str, tuple[str, str]]) -> None:
    for k, (e, p) in nomes.items():
        en[f"{id_}_{k}"], pt[f"{id_}_{k}"] = e, p


def cabecalho(nome: str, clock: str = "ANALOG") -> list[str]:
    return ['<?xml version="1.0" encoding="utf-8"?>', f"<!-- GERADO por tools/gerar.py {nome}. Não edite à mão. -->",
            f'<WatchFace width="{W}" height="{W}" clipShape="CIRCLE">', f'  <Metadata key="CLOCK_TYPE" value="{clock}" />',
            '  <Metadata key="PREVIEW_TIME" value="10:08:32" />']


def tpl(x, y, w, h, tam, cor, fmt: str, params: list[str], peso="NORMAL", align="CENTER", extra="") -> str:
    ps = "".join(f'<Parameter expression="{p}" />' for p in params)
    return (f'<PartText x="{x}" y="{y}" width="{w}" height="{h}"{extra}><Text align="{align}" ellipsis="TRUE">'
            f'<Font family="SYNC_TO_DEVICE" size="{tam}" weight="{peso}" color="{cor}">'
            f'<Template><![CDATA[{fmt}]]>{ps}</Template></Font></Text></PartText>')


def hora(x, y, w, h, fmt: str, tam: int, cor: str, peso="BOLD", align="CENTER", extra="") -> str:
    return (f'<DigitalClock x="{x}" y="{y}" width="{w}" height="{h}"{extra}><TimeText x="0" y="0" width="{w}" height="{h}" format="{fmt}" '
            f'hourFormat="SYNC_TO_DEVICE" align="{align}"><Font family="SYNC_TO_DEVICE" size="{tam}" weight="{peso}" color="{cor}" /></TimeText></DigitalClock>')


def img(x, y, w, h, res: str, extra="", filhos="") -> str:
    return f'<PartImage x="{x}" y="{y}" width="{w}" height="{h}"{extra}><Image resource="{res}" />{filhos}</PartImage>'


def rect(x, y, w, h, cor: str, raio: float = 0, estilo: str = "Fill", esp: float = 2, filhos: str = "", extra="") -> str:
    st = f'<Fill color="{cor}" />' if estilo == "Fill" else f'<Stroke thickness="{esp}" color="{cor}" />'
    if raio:
        forma = f'<RoundRectangle x="0" y="0" width="{w}" height="{h}" cornerRadiusX="{raio}" cornerRadiusY="{raio}">{st}{filhos}</RoundRectangle>'
    else:
        forma = f'<Rectangle x="0" y="0" width="{w}" height="{h}">{st}{filhos}</Rectangle>'
    return f'<PartDraw x="{x}" y="{y}" width="{w}" height="{h}"{extra}>{forma}</PartDraw>'


def finalizar(raiz: Path, nome: str, en: dict, pt: dict, xml: str, imagens: dict[str, Image.Image], previas: list[Image.Image],
              legendas: list[str], cols: int = 3, flavors: bool = False, nomes_previa: list[str] | None = None) -> dict:
    res = criar_modulo(raiz, nome, en, pt, flavors=flavors)
    dr = res / "drawable-nodpi"
    for n, im in imagens.items():
        im.save(dr / f"{n}.png", optimize=True)
    (res / "raw" / "watchface.xml").write_text(nomear_grupos(xml), encoding="utf-8")
    pv = raiz / "previews"
    pv.mkdir(exist_ok=True)
    for i, im in enumerate(previas):
        im.save(pv / f"{nome}_{(nomes_previa or [str(i)])[i] if nomes_previa else i}.png", optimize=True)
    previas[0].resize((450, 450), Image.LANCZOS).save(dr / "preview.png", optimize=True)
    from faces.cronos_previa import folha
    folha(previas, legendas, cols=cols).save(pv / f"{nome}_folha.png", optimize=True)
    return {"xml_bytes": len(xml)}


ACENTOS_PADRAO = [("ouro", "#f2c14e"), ("laranja", "#ff7a2f"), ("ciano", "#33d6ff"), ("rosa", "#ff5c93"), ("verde", "#4be37a"), ("branco", "#f2f2f2")]
_NOMES_AC = {"ouro": ("Gold", "Ouro"), "laranja": ("Orange", "Laranja"), "ciano": ("Cyan", "Ciano"), "rosa": ("Pink", "Rosa"),
             "verde": ("Green", "Verde"), "branco": ("White", "Branco")}


def textos_acento(en: dict, pt: dict, nome_en: str, nome_pt: str, lista=None) -> None:
    en["watch_face_name"], pt["watch_face_name"] = nome_en, nome_pt
    en["acento_label"], pt["acento_label"] = "Accent color", "Cor de destaque"
    for k, _ in (lista or ACENTOS_PADRAO):
        en[f"acento_{k}"], pt[f"acento_{k}"] = _NOMES_AC.get(k, (k, k))


def moldura_ambiente(estilo: str) -> str:
    return estilo


def grupo(nome: str, extra: str = "", ambient: int | None = 0) -> str:
    v = f'<Variant mode="AMBIENT" target="alpha" value="{ambient}" />' if ambient is not None else ""
    return f'<Group name="{nome}" x="0" y="0" width="{W}" height="{W}"{extra}>{v}'
