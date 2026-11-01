"""Eliminación de Gauss-Jordan paso a paso (motor compartido por varios métodos)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .formato import fmt, fmt_par
from .reporte import Reporte


@dataclass
class Eliminacion:
    M: np.ndarray                      # matriz final (forma escalonada reducida)
    pivotes: list[tuple[int, int]]     # (fila, columna) de cada pivote
    libres: list[int]                  # columnas de coeficientes sin pivote

    @property
    def rango(self) -> int:
        return len(self.pivotes)


def tolerancia(M: np.ndarray) -> float:
    escala = float(np.max(np.abs(M))) if M.size else 1.0
    return 1e-10 * max(1.0, escala)


def gauss_jordan(M, n_coef: int, rep: Reporte, *, sep: int | None = None,
                 detalle: bool | None = None) -> Eliminacion:
    """Reduce M a su forma escalonada reducida por filas, documentando cada paso en `rep`.

    n_coef  : cuántas columnas (desde la izquierda) se usan para buscar pivotes.
    sep     : posición de la barra de matriz aumentada (solo visual).
    detalle : True muestra la matriz tras CADA operación; False solo tras cada pivote.
              Por defecto True si hay 6 filas o menos.
    """
    M = np.array(M, dtype=float, copy=True)
    m = M.shape[0]
    if detalle is None:
        detalle = m <= 6
    tol = tolerancia(M)
    pivotes: list[tuple[int, int]] = []
    libres: list[int] = []
    fila = 0
    paso = 0

    for col in range(n_coef):
        if fila >= m:
            libres.append(col)
            continue
        candidatos = [i for i in range(fila, m) if abs(M[i, col]) > tol]
        if not candidatos:
            libres.append(col)
            rep.paso(f"Columna {col + 1}: sin pivote")
            rep.parrafo(f"Todas las entradas desde la fila {fila + 1} hacia abajo son 0 en la columna {col + 1}; "
                        f"esa columna no tiene pivote (variable libre).")
            continue

        paso += 1
        p = candidatos[0]
        rep.paso(f"Paso {paso}: pivote en la columna {col + 1}")
        operaciones: list[str] = []

        def registrar(texto: str, resaltar):
            if detalle:
                rep.matriz(M, texto, sep, resaltar)
            else:
                operaciones.append(texto)

        if p != fila:
            M[[fila, p]] = M[[p, fila]]
            registrar(f"F{fila + 1} ↔ F{p + 1}   (el pivote debe quedar en la fila {fila + 1})", [(fila, col)])
        piv = M[fila, col]
        if abs(piv - 1.0) > 1e-12:
            M[fila] = M[fila] / piv
            M[fila, col] = 1.0
            registrar(f"F{fila + 1} ← F{fila + 1} ÷ {fmt_par(piv)}", [(fila, col)])
        for i in range(m):
            if i == fila:
                continue
            f = M[i, col]
            if abs(f) <= tol:
                M[i, col] = 0.0
                continue
            M[i] = M[i] - f * M[fila]
            M[i, col] = 0.0
            mag = abs(f)
            coef = "" if abs(mag - 1.0) < 1e-12 else f"{fmt(mag)}·"
            signo = "−" if f > 0 else "+"
            texto = f"F{i + 1} ← F{i + 1} {signo} {coef}F{fila + 1}"
            registrar(texto, [(fila, col)])
        M[np.abs(M) < tol] = 0.0

        if not detalle:
            rep.lista(operaciones)
            rep.matriz(M, f"Matriz tras el paso {paso}", sep, [(fila, col)])
        pivotes.append((fila, col))
        fila += 1

    M[np.abs(M) < tol] = 0.0
    return Eliminacion(M, pivotes, libres)
