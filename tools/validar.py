#!/usr/bin/env python3
"""Valida o watchface.xml de um módulo e estima o uso de memória.

Uso:  python tools/validar.py cronos

O que confere (tudo offline):
  1. XML bem-formado.
  2. Cada elemento, atributo e "quem pode estar dentro de quem" contra os XSDs oficiais
     (third_party/wff-xsd/2, versão 2 do Watch Face Format).
  3. Recursos: todo `resource=`/`icon=` aponta para um PNG existente; todo `displayName=`
     existe em strings.xml (padrão e pt).
  4. Configurações: defaultValue válido, cada ListConfiguration da cena cobre todas as opções,
     Flavors apontam para opções que existem, slotId únicos (máx. 8).
  5. Fontes de dados usadas em expressões (`[SECOND]`, ...) são conhecidas.
  6. Memória estimada (4 bytes/pixel, como o avaliador oficial): ambiente <= 10 MB, interativo <= 100 MB.

Atenção: NÃO substitui o validador oficial do Google (play-validations/memory-footprint e
dwf-validator em github.com/google/watchface). Rode-o também antes de publicar.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from lxml import etree
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
XSD_DIR = RAIZ / "third_party" / "wff-xsd" / "2"
XS = "{http://www.w3.org/2001/XMLSchema}"

# Fontes de dados usadas (conferidas na tabela oficial "data sources" e no exemplo Complications).
FONTES_CONHECIDAS = {
    "SECOND", "MINUTE", "HOUR_0_11", "HOUR_1_12", "HOUR_0_23", "SECOND_MILLISECOND", "MILLISECOND",
    "DAY", "DAY_Z", "DAY_OF_WEEK_S", "DAY_OF_WEEK_F", "DAY_OF_WEEK", "MONTH_S", "MONTH_F", "MONTH", "YEAR",
    "IS_24_HOUR_MODE", "BATTERY_PERCENT", "STEP_COUNT", "STEP_GOAL", "STEP_PERCENT", "HEART_RATE",
    "WEATHER.IS_AVAILABLE", "WEATHER.IS_DAY", "WEATHER.CONDITION", "WEATHER.TEMPERATURE", "WEATHER.DAY_TEMPERATURE_HIGH", "WEATHER.DAY_TEMPERATURE_LOW", "WEATHER.CHANCE_OF_PRECIPITATION", "WEATHER.CONDITION_NAME", "WEATHER.UV_INDEX",
    "HOUR_0_11_MINUTE", "HOUR_1_12_MINUTE", "SECONDS_IN_DAY", "AMPM_STATE", "AMPM_STRING", "MINUTE_Z", "SECOND_Z", "HOUR_1_12_Z", "HOUR_0_23_Z", "DAY_OF_YEAR",
    "MOON_PHASE_POSITION", "MOON_PHASE_TYPE", "HOUR_0_23_MINUTE", "MONTH_0_11", "DAY_OF_YEAR", "DAYS_IN_MONTH", "DAY_0_30", "UNREAD_NOTIFICATION_COUNT",
    "ACCELEROMETER_ANGLE_X", "ACCELEROMETER_ANGLE_Y",
}
FUNCOES = {"clamp", "round", "floor", "ceil", "abs", "sin", "cos", "min", "max", "sqrt", "pow", "rand"}


# ------------------------------------------------------------------ esquema
class Esquema:
    def __init__(self) -> None:
        self.arqs = [etree.parse(str(p)).getroot() for p in sorted(XSD_DIR.rglob("*.xsd"))]
        self.grupos: dict[str, etree._Element] = {}
        self.grupos_attr: dict[str, etree._Element] = {}
        self.tipos: dict[str, etree._Element] = {}
        self.subst: dict[str, set[str]] = {}
        self.elementos: dict[str, list[etree._Element]] = {}
        self.attr_globais: set[str] = set()
        for r in self.arqs:
            for el in r.iter(XS + "group"):
                if el.get("name"):
                    self.grupos[el.get("name")] = el
            for el in r.iter(XS + "attributeGroup"):
                if el.get("name"):
                    self.grupos_attr[el.get("name")] = el
            for el in r.iter(XS + "complexType"):
                if el.get("name"):
                    self.tipos[el.get("name")] = el
            for el in r.iter(XS + "element"):
                if el.get("name"):
                    self.elementos.setdefault(el.get("name"), []).append(el)
                    if el.get("substitutionGroup"):
                        self.subst.setdefault(el.get("substitutionGroup"), set()).add(el.get("name"))
            for el in r:
                if el.tag == XS + "attribute" and el.get("name"):
                    self.attr_globais.add(el.get("name"))

    def _varrer(self, no, attrs: set[str], filhos: set[str], req: set[str] | None = None) -> None:
        req = self._req if req is None else req
        for c in no:
            t = c.tag
            if t == XS + "attribute":
                attrs.add(c.get("name") or c.get("ref"))
                if c.get("use") == "required":
                    req.add(c.get("name") or c.get("ref"))
            elif t == XS + "attributeGroup" and c.get("ref"):
                g = self.grupos_attr.get(c.get("ref"))
                if g is not None:
                    self._varrer(g, attrs, filhos, req)
            elif t == XS + "element":
                nome = c.get("name") or c.get("ref")
                filhos.add(nome)
                filhos.update(self.subst.get(nome, ()))
            elif t == XS + "group" and c.get("ref"):
                g = self.grupos.get(c.get("ref"))
                if g is not None:
                    self._varrer(g, attrs, filhos, req)
            elif t == XS + "extension":
                base = self.tipos.get(c.get("base"))
                if base is not None:
                    self._varrer(base, attrs, filhos, req)
                self._varrer(c, attrs, filhos, req)
            elif t in (XS + "complexType", XS + "complexContent", XS + "sequence", XS + "choice", XS + "all",
                       XS + "simpleContent"):
                self._varrer(c, attrs, filhos, req)

    def regras(self, nome: str) -> tuple[set[str], set[str], set[str]] | None:
        defs = self.elementos.get(nome)
        if not defs:
            return None
        attrs: set[str] = set()
        filhos: set[str] = set()
        reqs: list[set[str]] = []
        for d in defs:
            self._req = set()
            if d.get("type") and d.get("type") in self.tipos:
                self._varrer(self.tipos[d.get("type")], attrs, filhos)
            self._varrer(d, attrs, filhos)
            reqs.append(self._req)
        # elementos com o mesmo nome em contextos diferentes (ex.: BitmapFont): só vale o que é obrigatório em todos
        return attrs, filhos, set.intersection(*reqs)


# --------------------------------------------------------------- verificações
def checar_estrutura(raiz: etree._Element, esq: Esquema, erros: list[str]) -> None:
    cache: dict[str, tuple[set[str], set[str], set[str]] | None] = {}

    def regra(n: str):
        if n not in cache:
            cache[n] = esq.regras(n)
        return cache[n]

    def visita(no: etree._Element, pai: str | None) -> None:
        if not isinstance(no.tag, str):
            return
        r = regra(no.tag)
        if r is None:
            erros.append(f"<{no.tag}> não existe no esquema WFF v2 (linha {no.sourceline})")
            return
        attrs, filhos, req = r
        for a in req:
            if a not in no.attrib and not (a == 'ref'):
                erros.append(f"<{no.tag}> falta o atributo obrigatório '{a}' (linha {no.sourceline})")
        if no.tag in ("PartDraw", "PartImage", "PartText", "Group", "AnalogClock", "DigitalClock", "ComplicationSlot", "TimeText", "Scene"):
            for g in ("x", "y", "width", "height"):
                v = no.get(g)
                if v is not None and not re.fullmatch(r"-?\d+", v):
                    erros.append(f"<{no.tag}> {g}='{v}' precisa ser inteiro (linha {no.sourceline})")
        for a in no.attrib:
            if a not in attrs:
                erros.append(f"<{no.tag}> atributo '{a}' não é permitido (linha {no.sourceline})")
        if pai is not None:
            pr = regra(pai)
            if pr and no.tag not in pr[1]:
                erros.append(f"<{no.tag}> não pode ficar dentro de <{pai}> (linha {no.sourceline})")
        if no.tag in ("ListOption", "Compare", "Default") and not any(a.tag == "UserConfigurations" for a in no.iterancestors()):
            n_filhos = len([c for c in no if isinstance(c.tag, str)])
            if n_filhos != 1:
                erros.append(f"<{no.tag}> precisa de exatamente 1 elemento filho (tem {n_filhos}); use um <Group> (linha {no.sourceline})")
        for c in no:
            visita(c, no.tag)

    visita(raiz, None)


def strings_de(res: Path, pasta: str) -> set[str]:
    f = res / pasta / "strings.xml"
    return {e.get("name") for e in etree.parse(str(f)).getroot()} if f.exists() else set()


def checar_recursos(raiz, res: Path, erros: list[str]) -> set[str]:
    drawables = {p.stem for p in (res / "drawable-nodpi").glob("*.png")}
    for p in (res / "drawable-nodpi").glob("*.png"):
        if not re.fullmatch(r"[a-z0-9_]+", p.stem):
            erros.append(f"nome de imagem inválido para o Android: {p.name} (use só a-z, 0-9 e _)")
    usados: set[str] = set()
    for no in raiz.iter():
        if not isinstance(no.tag, str):
            continue
        for chave in ("resource", "icon"):
            v = no.get(chave)
            if v and not v.startswith("["):
                usados.add(v)
                if v not in drawables:
                    erros.append(f"recurso '{v}' ({no.tag}.{chave}) não existe em drawable-nodpi")
    for pasta in ("values", "values-pt"):
        textos = strings_de(res, pasta)
        for no in raiz.iter():
            if isinstance(no.tag, str) and no.get("displayName") and no.get("displayName") not in textos:
                erros.append(f"string '{no.get('displayName')}' falta em {pasta}/strings.xml")
    return usados


def checar_configuracoes(raiz, erros: list[str]) -> dict[str, str]:
    cfgs: dict[str, set[str]] = {}
    padroes: dict[str, str] = {}
    uc = raiz.find("UserConfigurations")
    if uc is None:
        return padroes
    for c in uc:
        if not isinstance(c.tag, str) or c.tag == "Flavors":
            continue
        cid = c.get("id")
        if c.tag == "ListConfiguration":
            ops = {o.get("id") for o in c.findall("ListOption")}
        elif c.tag == "ColorConfiguration":
            ops = {o.get("id") for o in c.findall("ColorOption")}
        else:
            ops = {"TRUE", "FALSE"}
        cfgs[cid] = ops
        padroes[cid] = c.get("defaultValue")
        if c.get("defaultValue") not in ops:
            erros.append(f"{cid}: defaultValue '{c.get('defaultValue')}' não é uma opção")
    for co in raiz.iter("ColorOption"):
        if len((co.get("colors") or "").split()) > 5:
            erros.append(f"ColorOption '{co.get('id')}' tem mais de 5 cores (limite do WFF)")
    cena = raiz.find("Scene")
    for lc in cena.iter("ListConfiguration"):
        cid = lc.get("id")
        if cid not in cfgs:
            erros.append(f"Scene usa ListConfiguration '{cid}' que não foi declarada")
            continue
        cobertas = {o.get("id") for o in lc.findall("ListOption")}
        if cobertas != cfgs[cid]:
            erros.append(f"ListConfiguration '{cid}' na cena cobre {sorted(cobertas)} mas existem {sorted(cfgs[cid])}")
    fl = uc.find("Flavors")
    slots = {s.get("slotId") for s in cena.iter("ComplicationSlot")}
    if len(list(cena.iter("ComplicationSlot"))) != len(slots):
        erros.append("slotId repetido")
    if len(slots) > 8:
        erros.append("mais de 8 ComplicationSlot")
    if fl is not None:
        ids = {f.get("id") for f in fl}
        if fl.get("defaultValue") not in ids:
            erros.append("Flavors defaultValue inválido")
        for f in fl:
            for c in f.findall("Configuration"):
                if c.get("optionId") not in cfgs.get(c.get("id"), set()):
                    erros.append(f"Flavor {f.get('id')}: {c.get('id')}={c.get('optionId')} inexistente")
            for s in f.findall("ComplicationSlot"):
                if s.get("slotId") not in slots:
                    erros.append(f"Flavor {f.get('id')}: slot {s.get('slotId')} inexistente")
    return padroes


def checar_expressoes(raiz, erros: list[str]) -> None:
    for no in raiz.iter():
        if not isinstance(no.tag, str):
            continue
        textos = list(no.attrib.values())
        if no.tag in ("Expression", "Parameter") or (no.text and no.text.strip().startswith("[")):
            textos.append(no.text or "")
        for t in textos:
            for tok in re.findall(r"\[([A-Z0-9_.]+)\]", t):
                if tok.startswith("COMPLICATION.") or tok.startswith("CONFIGURATION."):
                    continue
                if tok not in FONTES_CONHECIDAS:
                    erros.append(f"fonte de dados desconhecida: [{tok}] (linha {no.sourceline})")


# ---------------------------------------------------------------------- memória
def _alpha(no, ambiente: bool) -> float:
    base = float(no.get("alpha", 255))
    if ambiente:
        for v in no.findall("Variant"):
            if v.get("mode") == "AMBIENT" and v.get("target") == "alpha":
                return float(v.get("value"))
    return base


def memoria(raiz, res: Path, padroes: dict[str, str], ambiente: bool, so_padrao: bool) -> int:
    vistos: dict[str, int] = {}
    familias: set[str] = set()
    fontes = {bf.get("name"): [c.get("resource") for c in bf if c.tag in ("Character", "Word")]
              for bf in raiz.iter("BitmapFont") if bf.get("name")}

    def tam(nome: str) -> int:
        with Image.open(res / "drawable-nodpi" / f"{nome}.png") as im:
            return 4 * im.width * im.height

    def visita(no, oculto: bool) -> None:
        if not isinstance(no.tag, str):
            return
        if no.tag == "Variant":
            return
        oculto = oculto or (no.tag != "ListOption" and _alpha(no, ambiente) == 0)
        if not oculto and no.tag == "BitmapFont" and no.get("family"):
            familias.add(no.get("family"))
        if not oculto and no.tag in ("Image", "HourHand", "MinuteHand", "SecondHand"):
            r = no.get("resource")
            if r and not r.startswith("["):
                vistos[r] = tam(r)
        for c in no:
            if no.tag == "ListConfiguration" and so_padrao and c.get("id") != padroes.get(no.get("id")):
                continue
            visita(c, oculto)

    visita(raiz.find("Scene"), False)
    for f in familias:
        for r in fontes.get(f, []):
            vistos[r] = tam(r)
    return sum(vistos.values())


# ------------------------------------------------------------------------- main
def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    nome = sys.argv[1]
    res = RAIZ / "faces" / nome / "src" / "main" / "res"
    xml = res / "raw" / "watchface.xml"
    erros: list[str] = []
    try:
        raiz = etree.parse(str(xml)).getroot()
    except etree.XMLSyntaxError as e:
        print(f"XML inválido: {e}")
        return 1
    checar_estrutura(raiz, Esquema(), erros)
    usados = checar_recursos(raiz, res, erros)
    padroes = checar_configuracoes(raiz, erros)
    checar_expressoes(raiz, erros)
    ocios = {p.stem for p in (res / "drawable-nodpi").glob("*.png")} - usados - {"preview"}
    print(f"Validando {xml.relative_to(RAIZ)}")
    print(f"  {sum(1 for _ in raiz.iter() if isinstance(_.tag, str))} elementos, {len(usados)} recursos de imagem usados")
    for modo, amb, lim in (("ambiente", True, 10), ("interativo", False, 100)):
        pior = memoria(raiz, res, padroes, amb, False) / 1e6
        pad = memoria(raiz, res, padroes, amb, True) / 1e6
        ok = "OK" if pior <= lim else "ESTOUROU"
        print(f"  memória {modo:<10}: {pad:5.2f} MB (config. padrão) | {pior:5.2f} MB (pior caso, todas as opções) | limite {lim} MB -> {ok}")
        if pior > lim:
            erros.append(f"memória {modo} acima do limite ({pior:.1f} MB > {lim} MB)")
    if ocios:
        print(f"  aviso: PNGs não usados no XML: {sorted(ocios)}")
    if erros:
        print(f"\n{len(erros)} problema(s):")
        for e in dict.fromkeys(erros):
            print("  -", e)
        return 1
    print("  OK: estrutura, recursos, configurações e expressões consistentes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
