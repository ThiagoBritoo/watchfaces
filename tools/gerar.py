#!/usr/bin/env python3
"""Gera os assets, o watchface.xml e as prévias de uma watchface.

Uso:  python tools/gerar.py cronos
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    nome = sys.argv[1]
    try:
        mod = importlib.import_module(f"faces.{nome}")
    except ModuleNotFoundError:
        print(f"Watchface desconhecida: {nome}")
        return 2
    print(mod.gerar(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
