"""Resolución de A·x = b mediante la matriz inversa: x = A⁻¹·b."""
from __future__ import annotations

import numpy as np

from .eliminacion import gauss_jordan, tolerancia
from .formato import fmt, agrupar
from .gauss_jordan import _verificar_dimensiones, tabla_verificacion
from .reporte import Reporte
from .resultado import Resultado


def calcular_inversa(A, rep: Reporte | None = None):
    """Inversa por Gauss-Jordan sobre [A | I]. Devuelve (inversa|None, Eliminacion)."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    rep = rep if rep is not None else Reporte("")
    aug = np.column_stack([A, np.eye(n)])
    el = gauss_jordan(aug, n, rep, sep=n, detalle=(n <= 4))
    if el.rango < n:
        return None, el
    return el.M[:, n:], el


def resolver_por_inversa(A, b) -> Resultado:
    rep = Reporte("Resolución de sistema lineal", "Método de la matriz inversa")
    try:
        A, b = _verificar_dimensiones(A, b)
    except ValueError as e:
        rep.caja("error", "No se puede resolver", str(e))
        return Resultado(rep, "error", mensaje=str(e))

    m, n = A.shape
    rep.dato("Método", "Matriz inversa  x = A⁻¹·b")
    rep.dato("Sistema", f"{m} ecuaciones con {n} incógnitas")

    rep.seccion("Planteamiento")
    rep.parrafo("El sistema se escribe en forma matricial A·x = b. Si A es invertible, entonces x = A⁻¹·b.")
    rep.matriz(A, "Matriz de coeficientes A")
    rep.matriz(b.reshape(-1, 1), "Vector de términos independientes b")

    # --- condición necesaria: cuadrada
    if m != n:
        msg = (f"La matriz A es de {m}×{n}: no es cuadrada, por lo tanto no tiene inversa. "
               f"El método de la inversa solo aplica a sistemas con igual número de ecuaciones e incógnitas.")
        rep.seccion("Verificación de la condición")
        rep.caja("error", "Método no aplicable", msg, "Use el método de Gauss-Jordan para este sistema.")
        return Resultado(rep, "error", mensaje=msg)

    det = float(np.linalg.det(A))
    rep.seccion("Condición de invertibilidad")
    rep.parrafo(f"A es cuadrada de {n}×{n}. Determinante calculado: det(A) = {fmt(det, 6)}.")

    rep.seccion("Cálculo de A⁻¹ por Gauss-Jordan sobre [A | I]")
    rep.parrafo("Se reduce la matriz aumentada [A | I]; si A es invertible, el bloque izquierdo se convierte en I "
                "y el derecho en A⁻¹.")
    rep.matriz(np.column_stack([A, np.eye(n)]), "[A | I]", sep=n)
    inv, el = calcular_inversa(A, rep)

    if inv is None:
        msg = (f"La matriz A es SINGULAR: rango(A) = {el.rango} < {n}. No existe A⁻¹ "
               f"(det(A) ≈ {fmt(det, 6)}).")
        rep.seccion("Resultado de la reducción")
        rep.matriz(el.M, "Forma escalonada reducida de [A | I]", sep=n, resaltar=el.pivotes)
        rep.caja("error", "La matriz no es invertible", msg,
                 "Sin matriz inversa no se puede aplicar x = A⁻¹·b.",
                 "Use el método de Gauss-Jordan: permite saber si hay infinitas soluciones o ninguna.")
        return Resultado(rep, "error", mensaje=msg)

    rep.seccion("Matriz inversa")
    rep.matriz(inv, "A⁻¹ (bloque derecho de la matriz reducida)")
    err = float(np.max(np.abs(A @ inv - np.eye(n))))
    rep.parrafo(f"Comprobación A·A⁻¹ = I: error máximo = {err:.2e}.")
    rep.matriz(A @ inv, "A · A⁻¹")

    rep.seccion("Solución  x = A⁻¹·b")
    x = inv @ b
    nombres = [f"x{j + 1}" for j in range(n)]
    filas = []
    for i in range(n):
        expr = " + ".join(f"({fmt(inv[i, j])})·({fmt(b[j])})" for j in range(n)) if n <= 6 else "Σ (A⁻¹)ᵢⱼ·bⱼ"
        filas.append([nombres[i], expr, fmt(x[i])])
    rep.tabla(["Incógnita", "Cálculo (fila i de A⁻¹ por b)", "Valor"], filas, [1.2, 6, 2])
    ok = tabla_verificacion(rep, A, x, b)
    rep.seccion("Conclusión")
    lineas = agrupar([f"{nombres[j]} = {fmt(x[j])}" for j in range(n)])
    if ok:
        rep.caja("exito", "Solución única", *lineas, "La verificación en las ecuaciones originales es correcta.")
    else:
        rep.caja("adv", "Solución única (con diferencias numéricas)", *lineas,
                 "La matriz está mal condicionada; las diferencias numéricas son mayores de lo habitual.")
    return Resultado(rep, "unica", solucion=x, matriz=inv)
