"""Validación y conversión de entradas del usuario (con mensajes claros en español)."""
from __future__ import annotations

import re

import numpy as np

from ..config import VALOR_MAX

_NUM = r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?"
_RE_NUM = re.compile(rf"^{_NUM}$")
_RE_FRAC = re.compile(rf"^({_NUM})\s*/\s*({_NUM})$")

# Caracteres que puede contener una celda numérica (para filtrar el teclado)
CARACTERES_NUMERICOS = set("0123456789+-−.,/eE ")


def parse_numero(texto: str, limite: float = VALOR_MAX) -> float:
    """Convierte '3', '-2,5', '1/3', '1e3' en float. Vacío = 0.

    Rechaza NaN, infinito, divisiones entre cero y valores fuera de ±limite.
    """
    t = (texto or "").strip().replace(",", ".").replace("−", "-")
    if t in ("", "+", "-"):
        if t == "":
            return 0.0
        raise ValueError(f"'{texto}' no es un número válido.")
    m = _RE_FRAC.match(t)
    if m:
        den = float(m.group(2))
        if den == 0:
            raise ValueError(f"'{texto}': división entre cero.")
        valor = float(m.group(1)) / den
    elif _RE_NUM.match(t):
        valor = float(t)
    else:
        raise ValueError(f"'{texto}' no es un número válido (use 3, -2.5 o 1/3).")
    if not np.isfinite(valor):
        raise ValueError(f"'{texto}' no es un número finito.")
    if abs(valor) > limite:
        raise ValueError(f"'{texto}' excede el límite permitido (±{limite:,.0f}).".replace(",", "."))
    return valor


def parse_entero(texto: str, minimo: int, maximo: int, nombre: str) -> int:
    t = (texto or "").strip()
    if not re.fullmatch(r"\d+", t):
        raise ValueError(f"{nombre}: ingrese un número entero entre {minimo} y {maximo}.")
    valor = int(t)
    if not (minimo <= valor <= maximo):
        raise ValueError(f"{nombre}: debe estar entre {minimo} y {maximo} (ingresó {valor}).")
    return valor


def parse_rango(min_txt: str, max_txt: str, limite: float, nombre: str = "Rango") -> tuple[float, float]:
    """Valida un rango [mínimo, máximo] con mínimo < máximo y |valores| <= limite."""
    try:
        minimo = parse_numero(min_txt, limite)
        maximo = parse_numero(max_txt, limite)
    except ValueError as e:
        raise ValueError(f"{nombre}: {e}") from None
    if minimo >= maximo:
        raise ValueError(f"{nombre}: el mínimo ({minimo:g}) debe ser menor que el máximo ({maximo:g}).")
    return minimo, maximo
