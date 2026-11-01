"""Resolución de sistemas lineales A·x = b por Gauss-Jordan."""
from __future__ import annotations

import numpy as np

from ..config import MAX_COLUMNAS, MAX_FILAS
from .eliminacion import gauss_jordan, tolerancia
from .formato import ecuacion_lineal, fmt, fmt_par, termino, agrupar
from .reporte import Reporte
from .resultado import Resultado


def _verificar_dimensiones(A, b):
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float).reshape(-1)
    if A.ndim != 2 or A.size == 0:
        raise ValueError("La matriz A no está definida.")
    m, n = A.shape
    if m > MAX_FILAS or n > MAX_COLUMNAS:
        raise ValueError(f"El tamaño máximo garantizado es {MAX_FILAS}×{MAX_COLUMNAS} (A es {m}×{n}).")
    if b.shape[0] != m:
        raise ValueError("El vector b debe tener tantas entradas como filas tiene A.")
    if not (np.all(np.isfinite(A)) and np.all(np.isfinite(b))):
        raise ValueError("La matriz contiene valores no finitos (NaN o infinito).")
    return A, b


def tabla_verificacion(rep: Reporte, A, x, b, titulo: str = "Verificación A·x = b"):
    """Sustituye x en cada ecuación y compara con b."""
    m, n = A.shape
    filas = []
    todo_ok = True
    for i in range(m):
        lhs = float(A[i] @ x)
        dif = abs(lhs - b[i])
        ok = dif <= 1e-8 * max(1.0, abs(b[i]), float(np.max(np.abs(A[i] * x))) if n else 1.0)
        todo_ok &= ok
        filas.append([f"Ecuación {i + 1}", fmt(lhs, 6), fmt(b[i], 6), f"{dif:.2e}", "Correcto" if ok else "Error"])
    rep.paso(titulo)
    rep.tabla(["Ecuación", "A·x (lado izq.)", "b (lado der.)", "|Diferencia|", "Estado"], filas, [2, 3, 3, 2.5, 2])
    if n <= 5 and m <= 6:
        rep.parrafo("Sustitución detallada:")
        rep.lista([
            " + ".join(f"({fmt(A[i, j])})·({fmt(x[j])})" for j in range(n)) + f" = {fmt(float(A[i] @ x), 6)}"
            for i in range(m)
        ])
    return todo_ok


def resolver_gauss_jordan(A, b) -> Resultado:
    rep = Reporte("Resolución de sistema lineal", "Método de Gauss-Jordan")
    try:
        A, b = _verificar_dimensiones(A, b)
    except ValueError as e:
        rep.caja("error", "No se puede resolver", str(e))
        return Resultado(rep, "error", mensaje=str(e))

    m, n = A.shape
    nombres = [f"x{j + 1}" for j in range(n)]
    rep.dato("Método", "Gauss-Jordan")
    rep.dato("Sistema", f"{m} ecuaciones con {n} incógnitas")

    rep.seccion("Planteamiento del sistema")
    rep.parrafo("Sistema de ecuaciones original:")
    rep.ecuacion(*[ecuacion_lineal(A[i], nombres, b[i]) for i in range(m)])
    aug = np.column_stack([A, b])
    rep.parrafo("Matriz aumentada [A | b]:")
    rep.matriz(aug, "[A | b]", sep=n)

    rep.seccion("Eliminación de Gauss-Jordan")
    if m <= 6:
        rep.parrafo("Se muestra la matriz después de cada operación elemental entre filas.")
    else:
        rep.parrafo("Por el tamaño del sistema, se listan las operaciones de cada paso y se muestra la matriz "
                    "resultante al terminar cada pivote.")
    el = gauss_jordan(aug, n, rep, sep=n)
    R = el.M
    tol = tolerancia(R)

    rep.seccion("Matriz escalonada reducida")
    rep.matriz(R, "[R | d]", sep=n, resaltar=el.pivotes)

    rep.seccion("Análisis de consistencia (Rouché-Frobenius)")
    rango_A = el.rango
    filas_incons = [i for i in range(m) if np.all(np.abs(R[i, :n]) <= tol) and abs(R[i, n]) > tol]
    rango_aug = rango_A + (1 if filas_incons else 0)
    rep.tabla(["Concepto", "Valor"], [
        ["rango(A)", str(rango_A)],
        ["rango([A | b])", str(rango_aug)],
        ["Número de incógnitas n", str(n)],
    ], [3, 1])

    # ---- inconsistente
    if filas_incons:
        rep.parrafo("Filas de la forma 0 = c con c ≠ 0 encontradas en la matriz reducida:")
        rep.lista([f"Fila {i + 1}:  0 = {fmt(R[i, n])}" for i in filas_incons])
        msg = "El sistema es INCONSISTENTE: rango(A) < rango([A | b]), no tiene solución."
        rep.caja("error", "Sistema inconsistente", msg,
                 "Alguna ecuación se contradice con las demás (0 no puede ser igual a un número distinto de 0).")
        return Resultado(rep, "inconsistente", mensaje=msg)

    # ---- solución única
    solucion = np.zeros(n)
    for fila, col in el.pivotes:
        solucion[col] = R[fila, n]

    if rango_A == n:
        rep.parrafo("rango(A) = rango([A | b]) = n  →  el sistema es compatible determinado (solución única).")
        rep.seccion("Solución")
        rep.parrafo("Leyendo la matriz reducida, cada fila representa xᵢ = dᵢ:")
        rep.lista([f"{nombres[j]} = {fmt(solucion[j])}" for j in range(n)])
        ok = tabla_verificacion(rep, A, solucion, b)
        rep.seccion("Conclusión")
        lineas = agrupar([f"{nombres[j]} = {fmt(solucion[j])}" for j in range(n)])
        if ok:
            rep.caja("exito", "Solución única", *lineas, "La verificación en las ecuaciones originales es correcta.")
        else:
            rep.caja("adv", "Solución única (con diferencias numéricas)", *lineas,
                     "Alguna verificación presenta diferencias; el sistema puede estar mal condicionado.")
        return Resultado(rep, "unica", solucion=solucion)

    # ---- infinitas soluciones
    libres = el.libres
    basicas = [c for _, c in el.pivotes]
    rep.parrafo(f"rango(A) = rango([A | b]) = {rango_A} < n = {n}  →  sistema compatible indeterminado "
                f"({n - rango_A} variable(s) libre(s)): infinitas soluciones.")
    rep.seccion("Solución paramétrica")
    rep.parrafo("Variables básicas (con pivote): " + ", ".join(nombres[c] for c in basicas))
    rep.parrafo("Variables libres (parámetros):   " + ", ".join(nombres[c] for c in libres))
    ecs = []
    for fila, col in el.pivotes:
        expr = fmt(R[fila, n])
        for j in libres:
            c = -R[fila, j]
            if abs(c) > tol:
                expr += termino(c, nombres[j], False)
        ecs.append(f"{nombres[col]} = {expr}")
    ecs += [f"{nombres[j]} = {nombres[j]}   (libre)" for j in libres]
    rep.ecuacion(*sorted(ecs, key=lambda s: int(s.split(" ")[0][1:])))
    rep.parrafo("Solución particular (haciendo 0 todas las variables libres):")
    rep.lista([f"{nombres[j]} = {fmt(solucion[j])}" for j in range(n)])
    ok = tabla_verificacion(rep, A, solucion, b, "Verificación de la solución particular")
    rep.seccion("Conclusión")
    rep.caja("info" if ok else "adv", "Infinitas soluciones",
             f"El sistema tiene {n - rango_A} grado(s) de libertad.",
             "Solución general en la sección 5. Una solución particular:",
             *agrupar([f"{nombres[j]} = {fmt(solucion[j])}" for j in range(n)]))
    return Resultado(rep, "infinita", solucion=solucion)
