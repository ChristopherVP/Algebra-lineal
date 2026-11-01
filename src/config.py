"""Configuración central: límites garantizados y datos del documento PDF.

Todos los límites de la interfaz salen de aquí; cambiarlos en este archivo
actualiza restricciones, avisos y validaciones del programa completo.
"""

# --- Límites de tamaño (el programa funciona sin problema hasta estos valores) ---
MAX_FILAS = 15          # ecuaciones / filas de una matriz
MAX_COLUMNAS = 15       # incógnitas / columnas de una matriz
MAX_VECTORES = 15       # cantidad de vectores base
MAX_DIMENSION = 15      # componentes de cada vector

# --- Límites de valores ---
VALOR_MAX = 1_000_000          # |valor| máximo de una celda ingresada
ALEATORIO_MAX = 1_000          # |valor| máximo del rango de números aleatorios
RESULTADO_MAX = 1e12           # |valor| máximo permitido al reemplazar A por un resultado

# --- Presentación numérica ---
DECIMALES = 4

# --- Datos del documento PDF ---
UNIVERSIDAD = "Universidad Central del Ecuador"
FACULTAD = "Facultad de Ingeniería y Ciencias Aplicadas"
ASIGNATURA = "Álgebra Lineal"
PROGRAMA = "Calculadora de Álgebra Lineal"
INTEGRANTES = []


def texto_limites() -> str:
    """Texto del anuncio de límites que se muestra al usuario."""
    return (
        f"Límites garantizados: matrices hasta {MAX_FILAS}×{MAX_COLUMNAS} · "
        f"hasta {MAX_VECTORES} vectores de dimensión {MAX_DIMENSION} · "
        f"valores entre −{VALOR_MAX:,} y {VALOR_MAX:,}".replace(",", ".")
    )
