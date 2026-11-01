"""Formato numérico y de texto para matrices, ecuaciones y operaciones."""
from __future__ import annotations

import numpy as np

from ..config import DECIMALES


def fmt(x, decimales: int = DECIMALES) -> str:
    """Número legible: sin notación científica salvo extremos, sin ceros sobrantes."""
    x = float(x)
    if np.isnan(x):
        return "NaN"
    if np.isinf(x):
        return "∞" if x > 0 else "-∞"
    if x == 0:
        return "0"
    if abs(x) >= 1e9 or abs(x) < 10 ** -(decimales + 2):
        return f"{x:.3e}"
    texto = f"{x:.{decimales}f}".rstrip("0").rstrip(".")
    if texto in ("", "-", "-0"):
        return f"{x:.2e}"  # distinto de cero pero menor que la precisión mostrada
    return texto


def fmt_par(x, decimales: int = DECIMALES) -> str:
    """Número entre paréntesis si es negativo (útil dentro de operaciones)."""
    s = fmt(x, decimales)
    return f"({s})" if s.startswith("-") else s


def termino(coef: float, var: str, primero: bool, decimales: int = DECIMALES) -> str:
    """Término 'coef·var' con signo, para armar ecuaciones lineales."""
    signo = "-" if coef < 0 else "+"
    mag = abs(coef)
    cuerpo = var if np.isclose(mag, 1.0) else f"{fmt(mag, decimales)}·{var}"
    if primero:
        return f"-{cuerpo}" if coef < 0 else cuerpo
    return f" {signo} {cuerpo}"


def ecuacion_lineal(coefs, nombres, rhs, decimales: int = DECIMALES) -> str:
    """Ej.: '2·x1 - x2 + 3·x3 = 5'."""
    partes: list[str] = []
    for c, v in zip(coefs, nombres):
        if abs(c) < 1e-12:
            continue
        partes.append(termino(float(c), v, not partes, decimales))
    lado_izq = "".join(partes) if partes else "0"
    return f"{lado_izq} = {fmt(rhs, decimales)}"


def combinacion_texto(coefs, nombres, decimales: int = DECIMALES) -> str:
    """Ej.: '2·v1 - 3·v2' (omite coeficientes nulos)."""
    return ecuacion_lineal(coefs, nombres, 0.0, decimales).rsplit(" = ", 1)[0]


def lineas_matriz(M, sep: int | None = None, decimales: int = DECIMALES) -> list[str]:
    """Matriz como líneas de texto monoespaciado con corchetes; 'sep' = columna donde va '|'."""
    M = np.atleast_2d(np.asarray(M, dtype=float))
    celdas = [[fmt(v, decimales) for v in fila] for fila in M]
    ancho = max((len(c) for fila in celdas for c in fila), default=1)
    lineas = []
    for fila in celdas:
        partes = []
        for j, c in enumerate(fila):
            if sep is not None and j == sep:
                partes.append("|")
            partes.append(c.rjust(ancho))
        lineas.append("[ " + "  ".join(partes) + " ]")
    return lineas


def texto_matriz(M, sep: int | None = None, decimales: int = DECIMALES) -> str:
    return "\n".join(lineas_matriz(M, sep, decimales))


def agrupar(lineas: list[str], por_fila: int = 3, umbral: int = 6) -> list[str]:
    """Si hay muchas líneas cortas (ej. la solución de 15 incógnitas), las junta de a `por_fila`."""
    if len(lineas) <= umbral:
        return list(lineas)
    return ["      ".join(lineas[i:i + por_fila]) for i in range(0, len(lineas), por_fila)]
