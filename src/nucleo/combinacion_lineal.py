"""Combinación lineal, dependencia e independencia lineal de vectores."""
from __future__ import annotations

import numpy as np

from ..config import MAX_DIMENSION, MAX_VECTORES
from .eliminacion import gauss_jordan, tolerancia
from .formato import combinacion_texto, ecuacion_lineal, fmt, fmt_par, lineas_matriz
from .reporte import Reporte
from .resultado import Resultado


def _vec(v) -> str:
    return "(" + ", ".join(fmt(x) for x in v) + ")"


def analizar_combinacion_lineal(vectores, objetivo) -> Resultado:
    """¿Es `objetivo` combinación lineal de `vectores` (uno por fila)? Además: dependencia/independencia."""
    rep = Reporte("Combinación lineal", "Análisis de combinación y dependencia lineal")
    try:
        V = np.array(vectores, dtype=float, ndmin=2)
        v = np.asarray(objetivo, dtype=float).reshape(-1)
        k, d = V.shape
        if k > MAX_VECTORES or d > MAX_DIMENSION:
            raise ValueError(f"El máximo garantizado es {MAX_VECTORES} vectores de dimensión {MAX_DIMENSION}.")
        if v.shape[0] != d:
            raise ValueError("El vector objetivo debe tener la misma dimensión que los vectores base.")
        if not (np.all(np.isfinite(V)) and np.all(np.isfinite(v))):
            raise ValueError("Hay valores no finitos (NaN o infinito).")
    except ValueError as e:
        rep.caja("error", "Datos inválidos", str(e))
        return Resultado(rep, "error", mensaje=str(e))

    nv = [f"v{i + 1}" for i in range(k)]
    nc = [f"c{i + 1}" for i in range(k)]
    rep.dato("Vectores base", f"{k} vectores en R^{d}")
    rep.dato("Objetivo", f"v = {_vec(v)}")

    # 1. datos
    rep.seccion("Datos del problema")
    rep.lista([f"{nv[i]} = {_vec(V[i])}" for i in range(k)])
    rep.parrafo(f"Vector objetivo:  v = {_vec(v)}")

    # 2. planteamiento
    rep.seccion("Planteamiento")
    rep.parrafo("Se buscan escalares c₁, c₂, …, cₖ tales que:")
    rep.ecuacion(" + ".join(f"{nc[i]}·{nv[i]}" for i in range(k)) + " = v")
    rep.ecuacion(" + ".join(f"{nc[i]}·{_vec(V[i])}" for i in range(k)) + f" = {_vec(v)}")
    rep.parrafo("Igualando componente a componente se obtiene el sistema A·c = v, donde las columnas de A son los vectores base:")
    A = V.T
    rep.ecuacion(*[ecuacion_lineal(A[i], nc, v[i]) for i in range(d)])
    aug = np.column_stack([A, v])
    rep.matriz(A, f"A  ({d}×{k})  — columnas = vectores base")
    rep.matriz(aug, "Matriz aumentada [A | v]", sep=k)

    # 3. eliminación
    rep.seccion("Eliminación de Gauss-Jordan")
    el = gauss_jordan(aug, k, rep, sep=k)
    R = el.M
    tol = tolerancia(R)
    rep.seccion("Matriz escalonada reducida")
    rep.matriz(R, "[R | d]", sep=k, resaltar=el.pivotes)

    # 4. consistencia
    rango_A = el.rango
    filas_incons = [i for i in range(d) if np.all(np.abs(R[i, :k]) <= tol) and abs(R[i, k]) > tol]
    consistente = not filas_incons
    rango_aug = rango_A + (0 if consistente else 1)
    rep.seccion("Análisis de consistencia")
    rep.tabla(["Concepto", "Valor"], [
        ["rango(A)", str(rango_A)], ["rango([A | v])", str(rango_aug)],
        ["Cantidad de vectores base", str(k)], ["Dimensión del espacio", str(d)],
    ], [3, 1])

    coef = None
    if not consistente:
        rep.parrafo("Filas contradictorias (0 = c con c ≠ 0):")
        rep.lista([f"Fila {i + 1}:  0 = {fmt(R[i, k])}" for i in filas_incons])
        rep.parrafo("rango(A) < rango([A | v]): el sistema no tiene solución.")
    else:
        rep.parrafo("rango(A) = rango([A | v]): el sistema es compatible, existen escalares que cumplen la igualdad.")
        coef = np.zeros(k)
        for fila, col in el.pivotes:
            coef[col] = R[fila, k]

    # 5. solución / combinación
    rep.seccion("Coeficientes de la combinación")
    unica = consistente and rango_A == k
    if consistente:
        if unica:
            rep.parrafo("Solución única; los coeficientes se leen directamente de la matriz reducida:")
            rep.lista([f"{nc[i]} = {fmt(coef[i])}" for i in range(k)])
        else:
            basicas = [c for _, c in el.pivotes]
            rep.parrafo(f"Hay {k - rango_A} variable(s) libre(s): {', '.join(nc[j] for j in el.libres)}. "
                        "Solución general (cada básica en función de las libres):")
            ecs = []
            for fila, col in el.pivotes:
                expr = fmt(R[fila, k])
                for j in el.libres:
                    c = -R[fila, j]
                    if abs(c) > tol:
                        expr += (" - " if c < 0 else " + ") + (nc[j] if abs(abs(c) - 1) < 1e-12 else f"{fmt(abs(c))}·{nc[j]}")
                ecs.append((col, f"{nc[col]} = {expr}"))
            ecs += [(j, f"{nc[j]} = {nc[j]}   (libre)") for j in el.libres]
            rep.ecuacion(*[t for _, t in sorted(ecs)])
            rep.parrafo("Combinación particular (libres = 0):")
            rep.lista([f"{nc[i]} = {fmt(coef[i])}" for i in range(k)])
    else:
        rep.parrafo("No existen coeficientes: v no pertenece al espacio generado por los vectores base.")

    # 6. verificación
    ok_verif = None
    if consistente:
        rep.seccion("Verificación")
        comp = coef[:, None] * V
        rep.parrafo("Cada vector base multiplicado por su coeficiente:")
        rep.lista([f"{nc[i]}·{nv[i]} = {fmt_par(coef[i])}·{_vec(V[i])} = {_vec(comp[i])}" for i in range(k)])
        suma = comp.sum(axis=0)
        rep.parrafo("Suma componente por componente:")
        filas = []
        for j in range(d):
            terms = " + ".join(fmt_par(comp[i, j]) for i in range(k))
            filas.append([f"Componente {j + 1}", terms, fmt(suma[j], 6), fmt(v[j], 6),
                          "Correcto" if abs(suma[j] - v[j]) <= 1e-8 * max(1, abs(v[j])) else "Error"])
        rep.tabla(["Componente", "Suma de términos", "Resultado", "v", "Estado"], filas, [2, 5, 2, 2, 1.6])
        ok_verif = bool(np.allclose(suma, v, atol=1e-8, rtol=1e-8))

    # 7. dependencia lineal
    rep.seccion("Dependencia e independencia lineal de los vectores base")
    independientes = rango_A == k
    rep.parrafo(f"El rango de la matriz de vectores base es {rango_A} y hay {k} vectores. "
                "Los vectores son independientes si y solo si no hay variables libres (rango = cantidad de vectores).")
    if independientes:
        rep.caja("exito", "Linealmente INDEPENDIENTES",
                 "rango = número de vectores: la única forma de obtener el vector cero es con todos los coeficientes en 0.")
        if k == d:
            det = float(np.linalg.det(V))
            rep.parrafo(f"Como hay {k} vectores en R^{d}, además det = {fmt(det, 6)} ≠ 0 y forman una base de R^{d}.")
    else:
        rep.caja("adv", "Linealmente DEPENDIENTES",
                 f"rango ({rango_A}) < número de vectores ({k}): hay {k - rango_A} vector(es) redundante(s).")
        rep.parrafo("Relaciones de dependencia (combinaciones no triviales que dan el vector cero), "
                    "obtenidas del sistema homogéneo con la misma reducción:")
        relaciones = []
        for j in el.libres:
            c = np.zeros(k)
            c[j] = 1.0
            for fila, col in el.pivotes:
                c[col] = -R[fila, j]
            expr = combinacion_texto(c, nv)
            residuo = float(np.linalg.norm(c @ V))
            relaciones.append(f"{expr} = 0      (‖Σ cᵢ·vᵢ‖ = {residuo:.1e})")
        rep.ecuacion(*relaciones)

    rep.parrafo(f"Los vectores generan un subespacio de dimensión {rango_A} de R^{d}"
                + (" (todo el espacio)." if rango_A == d else " (subespacio propio)."))

    # 8. conclusión
    rep.seccion("Conclusión")
    if consistente:
        eq = " + ".join(f"({fmt(coef[i])})·{_vec(V[i])}" for i in range(k))
        lineas = [f"v ES combinación lineal de {{{', '.join(nv)}}}.",
                  ", ".join(f"{nc[i]} = {fmt(coef[i])}" for i in range(k)),
                  f"{eq} = {_vec(v)}"]
        if not unica:
            lineas.append("Como los vectores son dependientes, existen infinitas formas de escribir v.")
        else:
            lineas.append("Como los vectores son independientes, esta es la única combinación.")
        rep.caja("exito" if ok_verif else "adv", "El vector es combinación lineal", *lineas)
        return Resultado(rep, "unica" if unica else "infinita", solucion=coef)
    msg = "v NO es combinación lineal de los vectores base (no pertenece a su espacio generado)."
    rep.caja("error", "No es combinación lineal", msg)
    return Resultado(rep, "inconsistente", mensaje=msg)
