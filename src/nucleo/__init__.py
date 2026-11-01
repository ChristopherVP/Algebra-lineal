"""Núcleo matemático: algoritmos que devuelven un `Resultado` con su `Reporte`."""
from .combinacion_lineal import analizar_combinacion_lineal
from .gauss_jordan import resolver_gauss_jordan
from .inversa import resolver_por_inversa
from .multiplicacion import multiplicar_matrices, operar_escalar
from .reporte import Reporte
from .resultado import Resultado

__all__ = [
    "analizar_combinacion_lineal", "resolver_gauss_jordan", "resolver_por_inversa",
    "multiplicar_matrices", "operar_escalar", "Reporte", "Resultado",
]
