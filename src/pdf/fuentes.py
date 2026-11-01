"""Registro de fuentes Unicode (DejaVu Sans, incluida en el proyecto) para el PDF.

DejaVu permite imprimir símbolos como ← ↔ ≠ ∞ ⁻¹ ₁ · × − sin cuadritos.
Si por algún motivo no se encuentra, se usa Helvetica y se reemplazan los símbolos.
"""
from __future__ import annotations

import os

_DIR = os.path.join(os.path.dirname(__file__), "fuentes")
_ARCHIVOS = {
    "AL-Sans": "DejaVuSans.ttf",
    "AL-Sans-Bold": "DejaVuSans-Bold.ttf",
    "AL-Sans-Italic": "DejaVuSans-Oblique.ttf",
    "AL-Sans-BoldItalic": "DejaVuSans-BoldOblique.ttf",
}

NORMAL, NEGRITA, CURSIVA = "AL-Sans", "AL-Sans-Bold", "AL-Sans-Italic"
UNICODE_OK = False

_REEMPLAZOS = {
    "←": "<-", "↔": "<->", "→": "->", "≠": "!=", "≈": "~", "≤": "<=", "≥": ">=", "∞": "inf",
    "−": "-", "÷": "/", "·": "*", "×": "x", "•": "-", "Σ": "Suma", "‖": "||",
    "⁻¹": "^-1", "ᵢⱼ": "ij", "ᵢ": "i", "ⱼ": "j", "ₖ": "k", "ₙ": "n", "₁": "1", "₂": "2",
}


def registrar() -> None:
    """Registra las fuentes una sola vez; deja NORMAL/NEGRITA/CURSIVA listos."""
    global NORMAL, NEGRITA, CURSIVA, UNICODE_OK
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    if UNICODE_OK:
        return
    try:
        for nombre, archivo in _ARCHIVOS.items():
            ruta = os.path.join(_DIR, archivo)
            if nombre not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(nombre, ruta))
        pdfmetrics.registerFontFamily("AL-Sans", normal="AL-Sans", bold="AL-Sans-Bold",
                                      italic="AL-Sans-Italic", boldItalic="AL-Sans-BoldItalic")
        UNICODE_OK = True
    except Exception:
        NORMAL, NEGRITA, CURSIVA = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
        UNICODE_OK = False


def limpiar(texto: str) -> str:
    """Texto seguro para la fuente en uso (reemplaza símbolos solo si no hay Unicode)."""
    if UNICODE_OK:
        return texto
    for k, v in _REEMPLAZOS.items():
        texto = texto.replace(k, v)
    return texto.encode("latin-1", "replace").decode("latin-1")
