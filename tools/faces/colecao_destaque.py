"""Coleção Destaque: 28 watchfaces em UM APK. Escolha o estilo em Personalizar > Estilo e a cor de destaque em Personalizar > Cor de destaque.
Entram só as faces sem complicações e com a configuração de cor `acento` padrão (ou nenhuma)."""
from __future__ import annotations

from pathlib import Path

from colecao import montar

NOME = "colecao_destaque"
MEMBROS = ["ampulheta", "binario", "bussola", "calendario", "cartesiano", "ceu", "chomp", "eclipse", "energia", "espectro", "espiral", "horizonte", "leds", "lua",
           "lupa", "morse", "newton", "nivel", "odometro", "ondas", "pendulo", "pixel", "ponto", "pulsar", "resistor", "velocimetro", "vinil", "vintequatro"]


def gerar(raiz: Path) -> dict:
    return montar(raiz, NOME, MEMBROS, "Highlight Collection", "Coleção Destaque")
