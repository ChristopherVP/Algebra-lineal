"""Resultado común devuelto por todos los algoritmos."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .reporte import Reporte


@dataclass
class Resultado:
    reporte: Reporte
    estado: str                      # 'unica' | 'infinita' | 'inconsistente' | 'error' | 'ok'
    solucion: np.ndarray | None = None
    matriz: np.ndarray | None = None  # resultado matricial (inversa, producto, ...)
    mensaje: str | None = None        # texto breve para avisar al usuario (advertencia o error)

    @property
    def es_error(self) -> bool:
        return self.estado == "error"

    @property
    def requiere_aviso(self) -> bool:
        return self.estado in ("error", "inconsistente")
