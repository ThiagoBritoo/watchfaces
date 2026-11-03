#!/usr/bin/env python3
"""Monta a pasta "recomendado": os APKs que você realmente precisa instalar.

Uma coleção (faces/colecao_*) já contém várias watchfaces (lista em MEMBROS.txt); então as versões individuais dessas faces ficam de fora.
Uso: python tools/montar_pacote.py <pasta_com_os_apks> <pasta_de_saida>
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    entrada, saida = Path(sys.argv[1]), Path(sys.argv[2])
    membros: set[str] = set()
    for f in (RAIZ / "faces").glob("colecao_*/MEMBROS.txt"):
        membros |= {l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip()}
    saida.mkdir(parents=True, exist_ok=True)
    n = 0
    for apk in sorted(entrada.rglob("*-debug.apk")):
        nome = apk.name.removesuffix("-debug.apk")
        if nome in membros:
            continue
        shutil.copy(apk, saida / apk.name)
        n += 1
    print(f"{n} APKs em {saida} ({len(membros)} faces vieram dentro de coleções)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
