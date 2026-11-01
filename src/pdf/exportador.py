"""Convierte un `Reporte` en un PDF con aspecto de documento formal."""
from __future__ import annotations

import os
import re
from datetime import datetime
from xml.sax.saxutils import escape

from ..config import ASIGNATURA, FACULTAD, INTEGRANTES, PROGRAMA, UNIVERSIDAD
from ..nucleo import reporte as R
from . import fuentes

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, HRFlowable, KeepTogether,
                                    PageTemplate, Paragraph, Spacer, Table, TableStyle)
    _OK = True
except ImportError:  # pragma: no cover
    _OK = False


class ErrorPDF(Exception):
    """Error al generar o guardar el PDF (el mensaje es apto para mostrar al usuario)."""


def reportlab_disponible() -> bool:
    return _OK


def nombre_sugerido(reporte: R.Reporte) -> str:
    base = f"{reporte.titulo}_{reporte.subtitulo}" if reporte.subtitulo else reporte.titulo
    base = re.sub(r"[^\w\-]+", "_", base, flags=re.UNICODE).strip("_")
    return f"{base}_{datetime.now():%Y%m%d_%H%M}.pdf"


# ------------------------------------------------------------------ paleta y medidas
if _OK:
    AZUL = colors.HexColor("#1F3A5F")
    ACENTO = colors.HexColor("#2E6F95")
    GRIS = colors.HexColor("#5B6770")
    ZEBRA = colors.HexColor("#F3F6F9")
    LINEA = colors.HexColor("#C9D3DC")
    CAJAS = {
        "exito": (colors.HexColor("#E8F5E9"), colors.HexColor("#2E7D32")),
        "error": (colors.HexColor("#FDECEA"), colors.HexColor("#C62828")),
        "info": (colors.HexColor("#E8F1FA"), colors.HexColor("#1565C0")),
        "adv": (colors.HexColor("#FFF4E0"), colors.HexColor("#E08600")),
    }
    MARGEN = 0.75 * inch
    ANCHO = letter[0] - 2 * MARGEN


class _Matriz(Flowable):
    """Matriz dibujada con corchetes, números alineados a la derecha y barra de aumentada."""

    def __init__(self, celdas, sep, resaltar, tam, ancho_col, fuente):
        super().__init__()
        self.celdas, self.sep, self.resaltar = celdas, sep, set(resaltar)
        self.tam, self.cw, self.fuente = tam, ancho_col, fuente
        self.rh = tam * 1.65
        self.pad = 7
        self.n, self.m = len(celdas[0]), len(celdas)
        self.width = self.n * self.cw + 2 * self.pad
        self.height = self.m * self.rh + 4
        self.hAlign = "CENTER"

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        c, H, pad = self.canv, self.height, self.pad
        for (i, j) in self.resaltar:
            if i < self.m and j < self.n:
                c.setFillColor(colors.HexColor("#FFF2B3"))
                c.rect(pad + j * self.cw + 1, H - 2 - (i + 1) * self.rh + 1, self.cw - 2, self.rh - 2, stroke=0, fill=1)
        c.setStrokeColor(AZUL)
        c.setLineWidth(1.2)
        for x, d in ((1, 1), (self.width - 1, -1)):
            c.line(x, 1, x, H - 1)
            c.line(x, 1, x + d * 4, 1)
            c.line(x, H - 1, x + d * 4, H - 1)
        if self.sep is not None and 0 < self.sep < self.n:
            c.setDash(2, 2)
            c.setStrokeColor(ACENTO)
            c.setLineWidth(0.9)
            xs = pad + self.sep * self.cw
            c.line(xs, 3, xs, H - 3)
            c.setDash()
        c.setFillColor(colors.black)
        c.setFont(self.fuente, self.tam)
        for i, fila in enumerate(self.celdas):
            y = H - 2 - (i + 1) * self.rh + (self.rh - self.tam) / 2 + self.tam * 0.18
            for j, txt in enumerate(fila):
                c.drawRightString(pad + (j + 1) * self.cw - 5, y, txt)


class _NumeradoCanvas(rl_canvas.Canvas if _OK else object):
    """Canvas que escribe 'Página X de Y' y el pie de página."""

    def __init__(self, *a, titulo_doc="", **k):
        super().__init__(*a, **k)
        self._paginas = []
        self.titulo_doc = titulo_doc

    def showPage(self):
        self._paginas.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._paginas)
        for estado in self._paginas:
            self.__dict__.update(estado)
            self._decorar(total)
            super().showPage()
        super().save()

    def _decorar(self, total):
        pag = self._pageNumber
        self.setStrokeColor(LINEA)
        self.setLineWidth(0.6)
        self.line(MARGEN, 0.62 * inch, letter[0] - MARGEN, 0.62 * inch)
        self.setFont(fuentes.NORMAL, 8)
        self.setFillColor(GRIS)
        self.drawString(MARGEN, 0.45 * inch, fuentes.limpiar(f"{PROGRAMA} · {UNIVERSIDAD}"))
        self.drawRightString(letter[0] - MARGEN, 0.45 * inch, f"Página {pag} de {total}")
        if pag > 1:
            self.drawString(MARGEN, letter[1] - 0.5 * inch, fuentes.limpiar(f"{ASIGNATURA} — {self.titulo_doc}"))
            self.setStrokeColor(ACENTO)
            self.setLineWidth(0.8)
            self.line(MARGEN, letter[1] - 0.56 * inch, letter[0] - MARGEN, letter[1] - 0.56 * inch)


def _estilos():
    n, b, i = fuentes.NORMAL, fuentes.NEGRITA, fuentes.CURSIVA
    base = dict(fontName=n, textColor=colors.black)
    return {
        "uni": ParagraphStyle("uni", fontName=b, fontSize=15, leading=19, alignment=TA_CENTER, textColor=AZUL),
        "fac": ParagraphStyle("fac", fontName=n, fontSize=10.5, leading=14, alignment=TA_CENTER, textColor=GRIS),
        "asig": ParagraphStyle("asig", fontName=i, fontSize=10.5, leading=14, alignment=TA_CENTER, textColor=GRIS),
        "titulo": ParagraphStyle("titulo", fontName=b, fontSize=19, leading=24, alignment=TA_CENTER, textColor=AZUL, spaceBefore=10),
        "sub": ParagraphStyle("sub", fontName=i, fontSize=11.5, leading=15, alignment=TA_CENTER, textColor=ACENTO, spaceAfter=8),
        "h1": ParagraphStyle("h1", fontName=b, fontSize=13.5, leading=17, textColor=AZUL, spaceBefore=14, spaceAfter=2, keepWithNext=1),
        "h2": ParagraphStyle("h2", fontName=b, fontSize=11.5, leading=15, textColor=ACENTO, spaceBefore=8, spaceAfter=3, keepWithNext=1),
        "h3": ParagraphStyle("h3", fontName=b, fontSize=10, leading=13, textColor=GRIS, spaceBefore=8, spaceAfter=2, keepWithNext=1),
        "p": ParagraphStyle("p", fontSize=9.5, leading=13.5, spaceAfter=4, alignment=TA_LEFT, **base),
        "eq": ParagraphStyle("eq", fontName=n, fontSize=10, leading=14.5, alignment=TA_CENTER, **{"textColor": colors.black}),
        "et": ParagraphStyle("et", fontName=i, fontSize=9, leading=12, textColor=GRIS, alignment=TA_CENTER, spaceBefore=4, spaceAfter=2, keepWithNext=1),
        "li": ParagraphStyle("li", fontSize=9.5, leading=13, leftIndent=14, bulletIndent=3, spaceAfter=1, **base),
        "td": ParagraphStyle("td", fontSize=8.5, leading=11, **base),
        "th": ParagraphStyle("th", fontName=b, fontSize=8.5, leading=11, textColor=colors.white),
        "caja_t": ParagraphStyle("caja_t", fontName=b, fontSize=10.5, leading=14),
        "caja_l": ParagraphStyle("caja_l", fontSize=9.5, leading=13.5, **base),
        "meta_e": ParagraphStyle("meta_e", fontName=b, fontSize=9, leading=12, textColor=AZUL),
        "meta_v": ParagraphStyle("meta_v", fontSize=9, leading=12, **base),
    }


def _p(texto: str, estilo) -> "Paragraph":
    return Paragraph(escape(fuentes.limpiar(texto)).replace("\n", "<br/>"), estilo)


# ------------------------------------------------------------------ bloques → flowables
def _matriz_flowables(b: R.Matriz, E):
    from ..nucleo.formato import fmt
    dec = min(b.decimales, 3 if b.datos.shape[1] > 10 else b.decimales)
    celdas = [[fmt(v, dec) for v in fila] for fila in b.datos]
    n = len(celdas[0])
    fuente = fuentes.NORMAL
    ancho_texto = lambda tam: max(stringWidth(c, fuente, tam) for f in celdas for c in f)
    disponible = ANCHO - 20
    tam, trozo = 9.5, n
    while tam >= 7.0:
        cw = ancho_texto(tam) + 10
        if n * cw <= disponible:
            break
        tam -= 0.5
    else:
        tam = 8.0
        cw = ancho_texto(tam) + 10
        trozo = max(1, int(disponible // cw))
    cw = ancho_texto(tam) + 10
    partes = []
    etiqueta = [_p(b.etiqueta, E["et"])] if b.etiqueta else []
    if trozo >= n:
        flow = _Matriz(celdas, b.sep, b.resaltar, tam, cw, fuente)
        return [KeepTogether(etiqueta + [flow, Spacer(1, 5)])]
    limites = _limites_trozos(n, trozo, b.sep)
    for ini, fin in limites:
        sub = [fila[ini:fin] for fila in celdas]
        sep = None if b.sep is None or not (ini < b.sep < fin) else b.sep - ini
        res = [(i, j - ini) for (i, j) in b.resaltar if ini <= j < fin]
        cab = f"{b.etiqueta}  —  columnas {ini + 1} a {fin}" if b.etiqueta else f"Columnas {ini + 1} a {fin}"
        partes.append(KeepTogether([_p(cab, E["et"]), _Matriz(sub, sep, res, tam, cw, fuente), Spacer(1, 5)]))
    return partes


def _limites_trozos(n: int, trozo: int, sep: int | None):
    """Rangos [ini, fin) de columnas: parejos, o cortando justo en la barra de aumentada si cabe."""
    if sep and 0 < sep < n and max(sep, n - sep) <= trozo:
        return [(0, sep), (sep, n)]
    k = -(-n // trozo)          # cantidad de trozos
    ancho = -(-n // k)          # ancho parejo
    return [(i, min(n, i + ancho)) for i in range(0, n, ancho)]


def _tabla_flowable(b: R.Tabla, E):
    pesos = b.pesos or [1] * len(b.encabezados)
    total = float(sum(pesos))
    anchos = [ANCHO * p / total for p in pesos]
    datos = [[_p(h, E["th"]) for h in b.encabezados]]
    for f in b.filas:
        datos.append([_p(c, E["td"]) for c in f])
    t = Table(datos, colWidths=anchos, repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINEA),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(datos)):
        if i % 2 == 0:
            estilo.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    t.setStyle(TableStyle(estilo))
    return [t, Spacer(1, 6)]


def _caja_flowable(b: R.Caja, E):
    fondo, borde = CAJAS.get(b.tipo, CAJAS["info"])
    est_t = ParagraphStyle("ct", parent=E["caja_t"], textColor=borde)
    contenido = [[_p(b.titulo, est_t)]] + [[_p(l, E["caja_l"])] for l in b.lineas]
    t = Table(contenido, colWidths=[ANCHO])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fondo),
        ("LINEBEFORE", (0, 0), (0, -1), 4, borde),
        ("BOX", (0, 0), (-1, -1), 0.5, borde),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, 0), 7), ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
    ]))
    return [KeepTogether([t]), Spacer(1, 8)]


def _portada(rep: R.Reporte, E):
    fl = [
        _p(UNIVERSIDAD.upper(), E["uni"]),
        _p(FACULTAD, E["fac"]),
        _p(ASIGNATURA, E["asig"]),
        Spacer(1, 4),
        HRFlowable(width="100%", thickness=2, color=AZUL, spaceBefore=2, spaceAfter=2),
        HRFlowable(width="100%", thickness=0.6, color=ACENTO, spaceBefore=0, spaceAfter=8),
        _p(rep.titulo, E["titulo"]),
    ]
    if rep.subtitulo:
        fl.append(_p(rep.subtitulo, E["sub"]))
    filas = [[_p("Integrantes", E["meta_e"]), _p("\n".join(INTEGRANTES), E["meta_v"])]]
    for etiqueta, valor in rep.meta:
        filas.append([_p(etiqueta, E["meta_e"]), _p(valor, E["meta_v"])])
    filas.append([_p("Fecha de emisión", E["meta_e"]), _p(f"{datetime.now():%d/%m/%Y  %H:%M}", E["meta_v"])])
    t = Table(filas, colWidths=[ANCHO * 0.25, ANCHO * 0.75])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), ZEBRA),
        ("GRID", (0, 0), (-1, -1), 0.4, LINEA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ]))
    fl += [Spacer(1, 6), t, Spacer(1, 6)]
    return fl


def _flowables(rep: R.Reporte):
    E = _estilos()
    fl = _portada(rep, E)
    for b in rep.bloques:
        if isinstance(b, R.Titulo):
            fl.append(_p(b.texto, E[f"h{b.nivel}"]))
            if b.nivel == 1:
                fl.append(HRFlowable(width="100%", thickness=0.8, color=ACENTO, spaceBefore=0, spaceAfter=5))
        elif isinstance(b, R.Parrafo):
            fl.append(_p(b.texto, E["p"]))
        elif isinstance(b, R.Ecuacion):
            fl.append(KeepTogether([_p("\n".join(b.lineas), E["eq"]), Spacer(1, 5)]) if len(b.lineas) < 10
                      else _p("\n".join(b.lineas), E["eq"]))
        elif isinstance(b, R.Lista):
            for item in b.items:
                fl.append(Paragraph(escape(fuentes.limpiar(item)), E["li"], bulletText="•"))
            fl.append(Spacer(1, 3))
        elif isinstance(b, R.Matriz):
            fl += _matriz_flowables(b, E)
        elif isinstance(b, R.Tabla):
            fl += _tabla_flowable(b, E)
        elif isinstance(b, R.Caja):
            fl += _caja_flowable(b, E)
    return fl


def exportar_pdf(reporte: R.Reporte, ruta: str) -> str:
    """Genera el PDF en `ruta`. Lanza ErrorPDF con un mensaje claro si algo falla."""
    if not _OK:
        raise ErrorPDF("Falta la librería 'reportlab'. Instálela con:  python -m pip install reportlab")
    if not reporte.bloques:
        raise ErrorPDF("No hay ningún procedimiento para exportar. Realice primero una operación.")
    fuentes.registrar()
    carpeta = os.path.dirname(os.path.abspath(ruta))
    if not os.path.isdir(carpeta):
        raise ErrorPDF(f"La carpeta de destino no existe:\n{carpeta}")
    try:
        doc = BaseDocTemplate(
            ruta, pagesize=letter, leftMargin=MARGEN, rightMargin=MARGEN,
            topMargin=0.8 * inch, bottomMargin=0.85 * inch,
            title=f"{reporte.titulo} - {reporte.subtitulo}".strip(" -"), author=", ".join(INTEGRANTES),
            subject=ASIGNATURA, creator=PROGRAMA,
        )
        doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(
            MARGEN, 0.85 * inch, ANCHO, letter[1] - 0.8 * inch - 0.85 * inch, id="f",
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)])])
        titulo_doc = reporte.titulo + (f" — {reporte.subtitulo}" if reporte.subtitulo else "")
        doc.build(_flowables(reporte), canvasmaker=lambda *a, **k: _NumeradoCanvas(*a, titulo_doc=titulo_doc, **k))
    except PermissionError:
        raise ErrorPDF("No se pudo escribir el archivo: está abierto en otro programa o no tiene permiso.\n"
                       "Cierre el PDF si lo tiene abierto, o elija otra carpeta/nombre.") from None
    except OSError as e:
        raise ErrorPDF(f"No se pudo guardar el archivo:\n{e}") from None
    except Exception as e:  # error interno de reportlab
        raise ErrorPDF(f"Error al construir el PDF: {type(e).__name__}: {e}") from e
    return ruta
