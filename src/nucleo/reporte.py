"""Modelo de reporte: una lista de bloques que describe un procedimiento.

El mismo reporte se muestra en pantalla (texto con estilos) y se exporta a PDF,
así ambos siempre coinciden. Los algoritmos del paquete `nucleo` solo construyen
reportes; no saben nada de Tkinter ni de reportlab.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .formato import lineas_matriz


# --------------------------------------------------------------------------- bloques
@dataclass
class Titulo:
    texto: str
    nivel: int = 1  # 1 sección numerada, 2 subsección, 3 paso


@dataclass
class Parrafo:
    texto: str


@dataclass
class Ecuacion:
    lineas: list[str]


@dataclass
class Lista:
    items: list[str]


@dataclass
class Matriz:
    datos: np.ndarray
    etiqueta: str = ""
    sep: int | None = None                       # columna donde va la barra de aumentada
    resaltar: list[tuple[int, int]] = field(default_factory=list)
    decimales: int = 4


@dataclass
class Tabla:
    encabezados: list[str]
    filas: list[list[str]]
    pesos: list[float] | None = None            # anchos relativos de columnas


@dataclass
class Caja:
    tipo: str                                   # 'exito' | 'error' | 'info' | 'adv'
    titulo: str
    lineas: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- reporte
class Reporte:
    def __init__(self, titulo: str, subtitulo: str = ""):
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.meta: list[tuple[str, str]] = []   # datos de portada: (etiqueta, valor)
        self.bloques: list = []
        self._n_seccion = 0

    # -- construcción -------------------------------------------------------
    def dato(self, etiqueta: str, valor: str) -> "Reporte":
        self.meta.append((etiqueta, valor))
        return self

    def seccion(self, texto: str) -> "Reporte":
        self._n_seccion += 1
        self.bloques.append(Titulo(f"{self._n_seccion}. {texto}", 1))
        return self

    def subseccion(self, texto: str) -> "Reporte":
        self.bloques.append(Titulo(texto, 2))
        return self

    def paso(self, texto: str) -> "Reporte":
        self.bloques.append(Titulo(texto, 3))
        return self

    def parrafo(self, texto: str) -> "Reporte":
        self.bloques.append(Parrafo(texto))
        return self

    def ecuacion(self, *lineas: str) -> "Reporte":
        self.bloques.append(Ecuacion(list(lineas)))
        return self

    def lista(self, items) -> "Reporte":
        self.bloques.append(Lista([str(i) for i in items]))
        return self

    def matriz(self, datos, etiqueta: str = "", sep: int | None = None,
               resaltar=None, decimales: int = 4) -> "Reporte":
        self.bloques.append(Matriz(np.array(datos, dtype=float, ndmin=2), etiqueta, sep,
                                   list(resaltar or []), decimales))
        return self

    def tabla(self, encabezados, filas, pesos=None) -> "Reporte":
        self.bloques.append(Tabla(list(encabezados), [[str(c) for c in f] for f in filas], pesos))
        return self

    def caja(self, tipo: str, titulo: str, *lineas: str) -> "Reporte":
        self.bloques.append(Caja(tipo, titulo, list(lineas)))
        return self

    # -- salida en texto ----------------------------------------------------
    def a_segmentos(self) -> list[tuple[str, str]]:
        """Lista de (texto, etiqueta) para pintar en un widget Text."""
        seg: list[tuple[str, str]] = []
        seg.append((self.titulo.upper() + "\n", "titulo"))
        if self.subtitulo:
            seg.append((self.subtitulo + "\n", "subtitulo"))
        for etiqueta, valor in self.meta:
            seg.append((f"{etiqueta}: ", "meta_e"))
            seg.append((f"{valor}\n", "meta_v"))
        seg.append(("\n", "p"))
        for b in self.bloques:
            if isinstance(b, Titulo):
                seg.append(("\n" if b.nivel < 3 else "", "p"))
                seg.append((b.texto + "\n", f"h{b.nivel}"))
            elif isinstance(b, Parrafo):
                seg.append((b.texto + "\n", "p"))
            elif isinstance(b, Ecuacion):
                seg.append(("\n".join("   " + l for l in b.lineas) + "\n", "eq"))
            elif isinstance(b, Lista):
                seg.append(("\n".join(f"  • {i}" for i in b.items) + "\n", "p"))
            elif isinstance(b, Matriz):
                if b.etiqueta:
                    seg.append((b.etiqueta + "\n", "etiqueta"))
                seg.append(("\n".join(lineas_matriz(b.datos, b.sep, min(b.decimales, 3 if b.datos.shape[1] > 10 else 4))) + "\n", "mono"))
            elif isinstance(b, Tabla):
                seg.append((_tabla_texto(b) + "\n", "mono"))
            elif isinstance(b, Caja):
                tag = {"exito": "caja_exito", "error": "caja_error",
                       "info": "caja_info", "adv": "caja_adv"}.get(b.tipo, "caja_info")
                cuerpo = "".join(f"   {l}\n" for l in b.lineas)
                seg.append((f" {b.titulo}\n{cuerpo}", tag))
            seg.append(("", "p"))
        return seg

    def a_texto(self) -> str:
        return "".join(t for t, _ in self.a_segmentos())


def _tabla_texto(t: Tabla) -> str:
    cols = len(t.encabezados)
    anchos = [len(h) for h in t.encabezados]
    for f in t.filas:
        for j in range(cols):
            anchos[j] = max(anchos[j], len(f[j]))
    anchos = [min(a, 60) for a in anchos]

    def fila(vals):
        return " | ".join(v.ljust(anchos[j])[: max(anchos[j], 0)] if len(v) <= anchos[j] else v
                          for j, v in enumerate(vals))

    lineas = [fila(t.encabezados), "-+-".join("-" * a for a in anchos)]
    lineas += [fila(f) for f in t.filas]
    return "\n".join(lineas)
