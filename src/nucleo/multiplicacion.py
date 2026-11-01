"""Operaciones sobre la matriz A: producto A·B y multiplicación/división por escalar."""
from __future__ import annotations

import numpy as np

from ..config import MAX_COLUMNAS, MAX_FILAS, RESULTADO_MAX
from .formato import fmt, fmt_par
from .reporte import Reporte
from .resultado import Resultado


def compatibles(A, B) -> bool:
    return np.asarray(A).shape[1] == np.asarray(B).shape[0]


def multiplicar_matrices(A, B) -> Resultado:
    rep = Reporte("Multiplicación de matrices", "Producto C = A · B")
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    m, n = A.shape
    nb, p = B.shape
    rep.dato("Operación", "C = A · B")
    rep.dato("Dimensiones", f"A es {m}×{n},  B es {nb}×{p}")

    rep.seccion("Compatibilidad")
    if n != nb:
        msg = (f"No se pueden multiplicar: A tiene {n} columnas y B tiene {nb} filas. "
               f"Para A·B el número de columnas de A debe ser igual al número de filas de B.")
        rep.caja("error", "Matrices incompatibles", msg)
        return Resultado(rep, "error", mensaje=msg)
    if max(m, n, nb, p) > max(MAX_FILAS, MAX_COLUMNAS):
        msg = f"El tamaño máximo garantizado es {MAX_FILAS}×{MAX_COLUMNAS}."
        rep.caja("error", "Tamaño excedido", msg)
        return Resultado(rep, "error", mensaje=msg)
    rep.parrafo(f"columnas de A = {n} = filas de B  →  el producto está definido y C será de {m}×{p}.")

    rep.seccion("Matrices")
    rep.matriz(A, f"A  ({m}×{n})")
    rep.matriz(B, f"B  ({nb}×{p})")

    rep.seccion("Procedimiento")
    rep.parrafo("Cada elemento se obtiene multiplicando la fila i de A por la columna j de B "
                "y sumando los productos:   cᵢⱼ = aᵢ₁·b₁ⱼ + aᵢ₂·b₂ⱼ + … + aᵢₙ·bₙⱼ")
    C = A @ B
    filas = []
    for i in range(m):
        for j in range(p):
            calculo = " + ".join(f"{fmt_par(A[i, k])}·{fmt_par(B[k, j])}" for k in range(n))
            filas.append([f"c({i + 1},{j + 1})", calculo, fmt(C[i, j], 6)])
    rep.tabla(["Elemento", "Cálculo", "Resultado"], filas, [1.3, 7, 1.7])

    rep.seccion("Resultado")
    rep.matriz(C, f"C = A · B   ({m}×{p})")
    rep.caja("exito", "Producto calculado", f"C es una matriz de {m}×{p}.")
    return Resultado(rep, "ok", matriz=C)


def operar_escalar(A, k: float, dividir: bool) -> Resultado:
    A = np.asarray(A, dtype=float)
    m, n = A.shape
    simbolo = "÷" if dividir else "×"
    rep = Reporte("Operación con escalar", f"Matriz A {simbolo} {fmt(k)}")
    rep.dato("Operación", f"A {simbolo} {fmt_par(k)}")
    if dividir and abs(k) < 1e-12:
        msg = "No se puede dividir entre cero."
        rep.caja("error", "Operación inválida", msg)
        return Resultado(rep, "error", mensaje=msg)
    R = A / k if dividir else A * k
    if not np.all(np.isfinite(R)) or np.max(np.abs(R)) > RESULTADO_MAX:
        msg = f"El resultado excede el límite permitido (±{RESULTADO_MAX:.0e})."
        rep.caja("error", "Resultado fuera de límite", msg)
        return Resultado(rep, "error", mensaje=msg)
    rep.seccion("Matriz original")
    rep.matriz(A, f"A  ({m}×{n})")
    rep.seccion("Procedimiento")
    rep.parrafo(f"Cada elemento de A se {'divide entre' if dividir else 'multiplica por'} {fmt_par(k)}.")
    if m * n <= 100:
        rep.tabla(["Elemento", "Cálculo", "Resultado"],
                  [[f"a({i + 1},{j + 1})", f"{fmt_par(A[i, j])} {simbolo} {fmt_par(k)}", fmt(R[i, j], 6)]
                   for i in range(m) for j in range(n)], [1.5, 5, 2])
    rep.seccion("Resultado")
    rep.matriz(R, f"A {simbolo} {fmt_par(k)}")
    rep.caja("exito", "Operación realizada", "La matriz A fue actualizada con este resultado.")
    return Resultado(rep, "ok", matriz=R)
