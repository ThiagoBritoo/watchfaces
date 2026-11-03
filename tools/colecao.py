"""Junta várias watchfaces com a MESMA configuração de cor ("acento") em um único pacote: uma "coleção".

No relógio você instala um APK só e escolhe o mostrador em Personalizar > Estilo (cada estilo é uma das watchfaces originais, com ícone).
Como funciona: cada watchface vira um <Group> dentro de uma <ListOption> da configuração "estilo". Recursos (PNGs, fontes bitmap) ganham o
prefixo do nome da face para não colidirem. Só entram faces sem complicações e com exatamente a configuração `acento` padrão (ou nenhuma).
"""
from __future__ import annotations

import copy
import shutil
from pathlib import Path

from lxml import etree
from PIL import Image

from wf.modulo import criar_modulo

ACENTO_PADRAO = "ouro #f2c14e|laranja #ff7a2f|ciano #33d6ff|rosa #ff5c93|verde #4be37a|branco #f2f2f2"


def _res(raiz: Path, nome: str) -> Path:
    return raiz / "faces" / nome / "src" / "main" / "res"


def _assinatura_acento(root: etree._Element) -> str | None:
    uc = root.find("UserConfigurations")
    if uc is None:
        return None
    cfgs = [c for c in uc if isinstance(c.tag, str)]
    if len(cfgs) != 1 or cfgs[0].tag != "ColorConfiguration" or cfgs[0].get("id") != "acento":
        raise ValueError("configuração não é só 'acento'")
    return "|".join(f'{o.get("id")} {o.get("colors")}' for o in cfgs[0])


def _prefixar(no: etree._Element, pref: str) -> None:
    for e in no.iter():
        if not isinstance(e.tag, str):
            continue
        r = e.get("resource")
        if r and not r.startswith("["):
            e.set("resource", f"{pref}_{r}")
        if e.tag == "BitmapFont":
            for atr in ("name", "family"):
                if e.get(atr):
                    e.set(atr, f"{pref}_{e.get(atr)}")


def _nome(raiz: Path, face: str, pasta: str) -> str:
    t = etree.parse(str(_res(raiz, face) / pasta / "strings.xml")).getroot()
    return next(s.text for s in t if s.get("name") == "watch_face_name")


def _strings(raiz: Path, face: str, pasta: str) -> dict[str, str]:
    t = etree.parse(str(_res(raiz, face) / pasta / "strings.xml")).getroot()
    return {s.get("name"): s.text for s in t}


def montar(raiz: Path, modulo: str, membros: list[str], nome_en: str, nome_pt: str) -> dict:
    sigs: set[str | None] = set()
    raizes: dict[str, etree._Element] = {}
    for m in membros:
        r = etree.parse(str(_res(raiz, m) / "raw" / "watchface.xml")).getroot()
        if r.find(".//ComplicationSlot") is not None:
            raise ValueError(f"{m}: tem complicações; não entra em coleção")
        sigs.add(_assinatura_acento(r))
        raizes[m] = r
    sigs.discard(None)
    if len(sigs) > 1:
        raise ValueError("membros com configurações de cor diferentes")

    en = {"watch_face_name": nome_en, "estilo_label": "Style"}
    pt = {"watch_face_name": nome_pt, "estilo_label": "Estilo"}
    primeiro_com_acento = next((m for m in membros if raizes[m].find("UserConfigurations") is not None), None)
    if primeiro_com_acento:
        for k, v in _strings(raiz, primeiro_com_acento, "values").items():
            if k.startswith("acento_"):
                en[k] = v
        for k, v in _strings(raiz, primeiro_com_acento, "values-pt").items():
            if k.startswith("acento_"):
                pt[k] = v
    for m in membros:
        en[f"estilo_{m}"] = _nome(raiz, m, "values")
        pt[f"estilo_{m}"] = _nome(raiz, m, "values-pt")
    res = criar_modulo(raiz, modulo, en, pt, flavors=False)
    dr = res / "drawable-nodpi"
    for velho in dr.glob("*.png"):
        velho.unlink()

    wf = etree.Element("WatchFace", width="480", height="480", clipShape="CIRCLE")
    etree.SubElement(wf, "Metadata", key="CLOCK_TYPE", value="DIGITAL")
    etree.SubElement(wf, "Metadata", key="PREVIEW_TIME", value="10:08:32")
    fontes = etree.Element("BitmapFonts")
    for m in membros:
        bf = raizes[m].find("BitmapFonts")
        if bf is not None:
            for f in bf:
                c = copy.deepcopy(f)
                _prefixar(c, m)
                fontes.append(c)
    if len(fontes):
        wf.append(fontes)
    uc = etree.SubElement(wf, "UserConfigurations")
    if primeiro_com_acento:
        uc.append(copy.deepcopy(raizes[primeiro_com_acento].find("UserConfigurations")[0]))
    est = etree.SubElement(uc, "ListConfiguration", id="estilo", displayName="estilo_label", defaultValue=membros[0], icon=f"icone_{membros[0]}")
    for m in membros:
        etree.SubElement(est, "ListOption", id=m, displayName=f"estilo_{m}", icon=f"icone_{m}")
    cena = etree.SubElement(wf, "Scene", backgroundColor="#ff000000")
    lc = etree.SubElement(cena, "ListConfiguration", id="estilo")
    for m in membros:
        lo = etree.SubElement(lc, "ListOption", id=m)
        g = etree.SubElement(lo, "Group", name=f"face_{m}", x="0", y="0", width="480", height="480")
        r = raizes[m]
        sc = r.find("Scene")
        bg = sc.get("backgroundColor", "#ff000000")
        if bg.lower() != "#ff000000":
            pd = etree.SubElement(g, "PartDraw", x="0", y="0", width="480", height="480")
            rc = etree.SubElement(pd, "Rectangle", x="0", y="0", width="480", height="480")
            etree.SubElement(rc, "Fill", color=bg)
        for filho in sc:
            c = copy.deepcopy(filho)
            g.append(c)
        _prefixar(g, m)
        # imagens da face (menos a prévia) com prefixo
        for png in _res(raiz, m).joinpath("drawable-nodpi").glob("*.png"):
            if png.stem == "preview" or png.stem.startswith("icone_"):
                continue
            shutil.copy(png, dr / f"{m}_{png.name}")
        # ícone do editor = primeira prévia da face
        prev = sorted((raiz / "previews").glob(f"{m}_*.png"))
        prev = [p for p in prev if "folha" not in p.name and "ambiente" not in p.name]
        Image.open(prev[0]).convert("RGBA").resize((192, 192), Image.LANCZOS).save(dr / f"icone_{m}.png", optimize=True)
    xml = etree.tostring(wf, pretty_print=True, xml_declaration=True, encoding="utf-8").decode("utf-8")
    xml = xml.replace("<WatchFace ", "<!-- GERADO por tools/gerar.py " + modulo + ". Não edite à mão. -->\n<WatchFace ", 1) if False else xml
    (res / "raw" / "watchface.xml").write_text(xml, encoding="utf-8")
    Image.open(dr / f"icone_{membros[0]}.png").resize((450, 450), Image.LANCZOS).save(dr / "preview.png", optimize=True)
    (raiz / "faces" / modulo / "MEMBROS.txt").write_text("\n".join(membros) + "\n", encoding="utf-8")

    # folha de contatos com os ícones
    cols = 7
    linhas = (len(membros) + cols - 1) // cols
    folha = Image.new("RGB", (cols * 140, linhas * 140), (28, 28, 32))
    for i, m in enumerate(membros):
        ic = Image.open(dr / f"icone_{m}.png").convert("RGBA").resize((132, 132), Image.LANCZOS)
        folha.paste(ic, ((i % cols) * 140 + 4, (i // cols) * 140 + 4), ic)
    (raiz / "previews").mkdir(exist_ok=True)
    folha.save(raiz / "previews" / f"{modulo}_folha.png", optimize=True)
    return {"membros": len(membros), "xml_bytes": len(xml)}
