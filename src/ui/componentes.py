"""Widgets reutilizables: grilla de matriz con selección y visor de reportes con exportación a PDF."""
from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np

from .. import config
from ..nucleo.formato import fmt
from ..nucleo.reporte import Reporte
from ..nucleo.validacion import CARACTERES_NUMERICOS, parse_numero
from ..pdf import ErrorPDF, exportar_pdf, nombre_sugerido, reportlab_disponible
from . import tema


# =============================================================================== grilla
class MatrixGrid(ttk.Frame):
    """Editor de matriz con celdas validadas y selección de celdas/filas/columnas.

    Selección: clic (una celda) · arrastrar o Mayús+clic (rango) · Ctrl+clic (agregar/quitar)
               clic en el encabezado de fila/columna (toda la fila/columna) · esquina (todo) · Ctrl+A.
    Limpiar:   Supr / Retroceso con varias celdas seleccionadas, o `limpiar_seleccion()`.
    """

    def __init__(self, parent, filas: int, columnas: int, *, max_filas: int, max_columnas: int,
                 encabezado_col=None, encabezado_fila=None, columna_b: bool = False,
                 editable: bool = True, on_cambio=None, on_seleccion=None, alto: int = 200):
        super().__init__(parent)
        self.max_filas, self.max_columnas = max_filas, max_columnas
        self.encabezado_col = encabezado_col or (lambda j, n: str(j + 1))
        self.encabezado_fila = encabezado_fila or (lambda i: str(i + 1))
        self.columna_b = columna_b
        self.editable = editable
        self.on_cambio, self.on_seleccion = on_cambio, on_seleccion
        self.filas = self.columnas = 0
        self.vars: list[list[tk.StringVar]] = []
        self.entries: list[list[tk.Entry]] = []
        self._exacto: list[list[tuple[str, float] | None]] = []
        self._pos: dict[str, tuple[int, int]] = {}
        self.sel: set[tuple[int, int]] = set()
        self.invalidas: set[tuple[int, int]] = set()
        self.ancla: tuple[int, int] = (0, 0)
        self._silencio = False
        self._vcmd = (self.register(self._validar_tecla), "%P")
        self._fm = tema.fuente_mono()

        self.canvas = tk.Canvas(self, background=tema.BG_PANEL, highlightthickness=0, height=alto)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.interior = tk.Frame(self.canvas, background=tema.BG_PANEL)
        self.canvas.create_window((0, 0), window=self.interior, anchor="nw")
        self.interior.bind("<Configure>", self._al_cambiar_tamano)
        self.canvas.bind("<Configure>", self._al_cambiar_tamano)
        for w in (self.canvas, self.interior):
            w.bind("<Enter>", self._activar_rueda)
            w.bind("<Leave>", self._desactivar_rueda)
        self.redimensionar(filas, columnas)

    def _al_cambiar_tamano(self, _=None):
        """Actualiza el área desplazable y muestra las barras solo cuando hacen falta."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        ancho_int, alto_int = self.interior.winfo_reqwidth(), self.interior.winfo_reqheight()
        necesita_v = alto_int > self.canvas.winfo_height()
        necesita_h = ancho_int > self.canvas.winfo_width()
        (self.vsb.grid if necesita_v else self.vsb.grid_remove)()
        (self.hsb.grid if necesita_h else self.hsb.grid_remove)()

    # ------------------------------------------------------------------ construcción
    def _validar_tecla(self, propuesto: str) -> bool:
        return len(propuesto) <= 14 and all(ch in CARACTERES_NUMERICOS for ch in propuesto)

    def _col_visual(self, j: int) -> int:
        """Columna del grid donde va la celda j (deja un hueco antes de b)."""
        return j + 1 + (1 if self.columna_b and j == self.columnas - 1 else 0)

    def _construir(self):
        for w in self.interior.winfo_children():
            w.destroy()
        self.entries, self._pos = [], {}
        m, n = self.filas, self.columnas
        ui = tema.fuente_ui()
        esquina = tk.Label(self.interior, text="◢", bg=tema.BORDE, fg=tema.FG, width=4, cursor="hand2")
        esquina.grid(row=0, column=0, padx=1, pady=1, sticky="nsew")
        esquina.bind("<Button-1>", lambda e: self.seleccionar_todo())
        for j in range(n):
            es_b = self.columna_b and j == n - 1
            lbl = tk.Label(self.interior, text=self.encabezado_col(j, n), bg=tema.ACENTO if es_b else tema.BTN,
                           fg=tema.BG if es_b else tema.FG, font=(ui, 9, "bold"), cursor="hand2")
            lbl.grid(row=0, column=self._col_visual(j), padx=1, pady=1, sticky="nsew")
            lbl.bind("<Button-1>", lambda e, j=j: self._sel_columna(j))
        if self.columna_b and n >= 2:
            tk.Frame(self.interior, bg=tema.ACENTO, width=3).grid(row=0, column=n, rowspan=m + 1, sticky="ns", padx=2)
        for i in range(m):
            lbl = tk.Label(self.interior, text=self.encabezado_fila(i), bg=tema.BTN, fg=tema.FG,
                           font=(ui, 9, "bold"), width=5, cursor="hand2")
            lbl.grid(row=i + 1, column=0, padx=1, pady=1, sticky="nsew")
            lbl.bind("<Button-1>", lambda e, i=i: self._sel_fila(i))
            fila_e = []
            for j in range(n):
                e = tk.Entry(self.interior, textvariable=self.vars[i][j], width=9, justify="center",
                             font=(self._fm, 10), relief="flat", bd=0, highlightthickness=1,
                             highlightbackground=tema.BORDE, highlightcolor=tema.ACENTO,
                             bg=tema.ENTRY_BG, fg=tema.FG, insertbackground=tema.FG,
                             readonlybackground=tema.ENTRY_BG, disabledforeground=tema.FG,
                             validate="key", validatecommand=self._vcmd)
                if not self.editable:
                    e.configure(state="readonly")
                e.grid(row=i + 1, column=self._col_visual(j), padx=1, pady=1, ipady=3)
                self._pos[str(e)] = (i, j)
                e.bind("<Button-1>", lambda ev, i=i, j=j: self._clic(ev, i, j))
                e.bind("<B1-Motion>", self._arrastre)
                e.bind("<FocusIn>", lambda ev, i=i, j=j: self._foco(i, j))
                e.bind("<FocusOut>", lambda ev, i=i, j=j: self._normalizar(i, j))
                for tecla, (di, dj) in (("<Up>", (-1, 0)), ("<Down>", (1, 0)), ("<Return>", (1, 0)),
                                        ("<KP_Enter>", (1, 0))):
                    e.bind(tecla, lambda ev, i=i, j=j, di=di, dj=dj: self._mover(i, j, di, dj))
                e.bind("<Left>", lambda ev, i=i, j=j: self._mover_borde(ev, i, j, -1))
                e.bind("<Right>", lambda ev, i=i, j=j: self._mover_borde(ev, i, j, 1))
                e.bind("<Delete>", self._supr)
                e.bind("<BackSpace>", self._supr)
                e.bind("<Control-a>", lambda ev: self._ctrl_a())
                e.bind("<Control-A>", lambda ev: self._ctrl_a())
                fila_e.append(e)
            self.entries.append(fila_e)
        self._pintar()

    def redimensionar(self, filas: int, columnas: int) -> None:
        """Cambia el tamaño conservando los valores que caben en el nuevo tamaño."""
        if not (1 <= filas <= self.max_filas and 1 <= columnas <= self.max_columnas):
            raise ValueError(f"El tamaño debe estar entre 1×1 y {self.max_filas}×{self.max_columnas}.")
        viejo_vars, viejo_ex = self.vars, self._exacto
        self._silencio = True
        self.vars = [[tk.StringVar(value="0") for _ in range(columnas)] for _ in range(filas)]
        self._exacto = [[None] * columnas for _ in range(filas)]
        for i in range(min(filas, len(viejo_vars))):
            for j in range(min(columnas, len(viejo_vars[0]) if viejo_vars else 0)):
                self.vars[i][j].set(viejo_vars[i][j].get())
                self._exacto[i][j] = viejo_ex[i][j]
        self.filas, self.columnas = filas, columnas
        self.sel, self.invalidas = set(), set()
        for i in range(filas):
            for j in range(columnas):
                self.vars[i][j].trace_add("write", lambda *a, i=i, j=j: self._cambio(i, j))
        self._construir()
        self._silencio = False
        self._avisar_cambio()

    # ------------------------------------------------------------------ datos
    def _cambio(self, i, j):
        if self._silencio:
            return
        self.invalidas.discard((i, j))
        self._pintar_celda(i, j)
        self._avisar_cambio()

    def _avisar_cambio(self):
        if self.on_cambio and not self._silencio:
            self.on_cambio()

    def establecer(self, M) -> None:
        """Carga una matriz (conserva los decimales exactos aunque se muestren redondeados)."""
        M = np.array(M, dtype=float, ndmin=2)
        if M.shape != (self.filas, self.columnas):
            self.redimensionar(*M.shape)
        self._silencio = True
        for i in range(self.filas):
            for j in range(self.columnas):
                texto = fmt(M[i, j], 6)
                self.vars[i][j].set(texto)
                self._exacto[i][j] = (texto, float(M[i, j]))
        self.invalidas.clear()
        self._silencio = False
        self._pintar()
        self._avisar_cambio()

    def valor(self, i: int, j: int) -> float:
        texto = self.vars[i][j].get()
        ex = self._exacto[i][j]
        if ex is not None and ex[0] == texto:
            return ex[1]
        return parse_numero(texto)

    def obtener(self) -> np.ndarray:
        """Matriz numérica. Lanza ValueError indicando la celda inválida (y la marca en rojo)."""
        M = np.zeros((self.filas, self.columnas))
        malas = []
        for i in range(self.filas):
            for j in range(self.columnas):
                try:
                    M[i, j] = self.valor(i, j)
                except ValueError as e:
                    malas.append((i, j, str(e)))
        if malas:
            self.invalidas = {(i, j) for i, j, _ in malas}
            self._pintar()
            i, j, msg = malas[0]
            self.entries[i][j].focus_set()
            extra = f" (y {len(malas) - 1} celda(s) más)" if len(malas) > 1 else ""
            raise ValueError(f"Celda {self.encabezado_fila(i)}, {self.encabezado_col(j, self.columnas)}: {msg}{extra}")
        return M

    def _normalizar(self, i, j):
        try:
            self.valor(i, j)
            self.invalidas.discard((i, j))
        except ValueError:
            self.invalidas.add((i, j))
        self._pintar_celda(i, j)

    # ------------------------------------------------------------------ selección
    def _pintar_celda(self, i, j):
        if i >= self.filas or j >= self.columnas or not self.entries:
            return
        if (i, j) in self.invalidas:
            color = tema.INVALIDO
        elif (i, j) in self.sel:
            color = tema.SELECCION
        else:
            color = tema.ENTRY_BG
        e = self.entries[i][j]
        e.configure(bg=color, readonlybackground=color)

    def _pintar(self):
        for i in range(self.filas):
            for j in range(self.columnas):
                self._pintar_celda(i, j)

    def _fijar_sel(self, nueva: set):
        anteriores = self.sel
        self.sel = nueva
        for (i, j) in anteriores | nueva:
            self._pintar_celda(i, j)
        if self.on_seleccion:
            self.on_seleccion(self)

    def _rect(self, a, b):
        i0, i1 = sorted((a[0], b[0]))
        j0, j1 = sorted((a[1], b[1]))
        return {(i, j) for i in range(i0, i1 + 1) for j in range(j0, j1 + 1)}

    def _clic(self, ev, i, j):
        shift, ctrl = bool(ev.state & 0x0001), bool(ev.state & 0x0004)
        if shift:
            self._fijar_sel(self._rect(self.ancla, (i, j)))
        elif ctrl:
            nueva = set(self.sel)
            nueva ^= {(i, j)}
            self._fijar_sel(nueva)
            self.ancla = (i, j)
        else:
            self.ancla = (i, j)
            self._fijar_sel({(i, j)})

    def _arrastre(self, ev):
        w = self.winfo_containing(ev.x_root, ev.y_root)
        pos = self._pos.get(str(w)) if w is not None else None
        if pos is not None:
            nueva = self._rect(self.ancla, pos)
            if nueva != self.sel:
                self._fijar_sel(nueva)

    def _foco(self, i, j):
        if (i, j) not in self.sel:
            self.ancla = (i, j)
            self._fijar_sel({(i, j)})
        e = self.entries[i][j]
        if self.editable and len(self.sel) <= 1:
            e.after_idle(lambda: e.select_range(0, "end"))

    def _sel_fila(self, i):
        self.ancla = (i, 0)
        self._fijar_sel({(i, j) for j in range(self.columnas)})

    def _sel_columna(self, j):
        self.ancla = (0, j)
        self._fijar_sel({(i, j) for i in range(self.filas)})

    def seleccionar_todo(self):
        self._fijar_sel({(i, j) for i in range(self.filas) for j in range(self.columnas)})

    def _ctrl_a(self):
        self.seleccionar_todo()
        return "break"

    def deseleccionar(self):
        """Quita la marca de selección sin avisar al propietario (evita rebotes entre grillas)."""
        anteriores = self.sel
        self.sel = set()
        for (i, j) in anteriores:
            self._pintar_celda(i, j)

    def hay_seleccion(self) -> bool:
        return bool(self.sel)

    def descripcion_seleccion(self) -> str:
        n = len(self.sel)
        return "Ninguna celda seleccionada" if n == 0 else f"{n} celda{'s' if n != 1 else ''} seleccionada{'s' if n != 1 else ''}"

    # ------------------------------------------------------------------ edición
    def limpiar_seleccion(self) -> int:
        """Pone en 0 SOLO las celdas seleccionadas. Devuelve cuántas se limpiaron."""
        if not self.editable or not self.sel:
            return 0
        self._silencio = True
        for (i, j) in self.sel:
            self.vars[i][j].set("0")
            self._exacto[i][j] = None
            self.invalidas.discard((i, j))
        self._silencio = False
        self._pintar()
        self._avisar_cambio()
        return len(self.sel)

    def limpiar_todo(self):
        self._silencio = True
        for i in range(self.filas):
            for j in range(self.columnas):
                self.vars[i][j].set("0")
                self._exacto[i][j] = None
        self.invalidas.clear()
        self._silencio = False
        self._pintar()
        self._avisar_cambio()

    def _supr(self, ev):
        if self.editable and len(self.sel) > 1:
            self.limpiar_seleccion()
            return "break"
        return None

    def _mover(self, i, j, di, dj):
        ni, nj = i + di, j + dj
        if self.editable is False:
            return "break"
        if ni >= self.filas:
            ni, nj = 0, (j + 1) % self.columnas
        if 0 <= ni < self.filas and 0 <= nj < self.columnas:
            self._ir(ni, nj)
        return "break"

    def _mover_borde(self, ev, i, j, d):
        e = ev.widget
        if (d < 0 and e.index("insert") == 0) or (d > 0 and e.index("insert") == len(e.get())):
            if 0 <= j + d < self.columnas:
                self._ir(i, j + d)
                return "break"
        return None

    def _ir(self, i, j):
        self.ancla = (i, j)
        self._fijar_sel({(i, j)})
        self.entries[i][j].focus_set()
        self._asegurar_visible(self.entries[i][j])

    def _asegurar_visible(self, w):
        self.update_idletasks()
        try:
            bbox = self.canvas.bbox("all")
            if not bbox:
                return
            total_h, total_w = bbox[3] - bbox[1], bbox[2] - bbox[0]
            ch, cw = self.canvas.winfo_height(), self.canvas.winfo_width()
            y, x = w.winfo_y(), w.winfo_x()
            if total_h > ch:
                top = self.canvas.canvasy(0)
                if y < top:
                    self.canvas.yview_moveto(max(0, (y - 4) / total_h))
                elif y + w.winfo_height() > top + ch:
                    self.canvas.yview_moveto((y + w.winfo_height() - ch + 4) / total_h)
            if total_w > cw:
                left = self.canvas.canvasx(0)
                if x < left:
                    self.canvas.xview_moveto(max(0, (x - 4) / total_w))
                elif x + w.winfo_width() > left + cw:
                    self.canvas.xview_moveto((x + w.winfo_width() - cw + 4) / total_w)
        except tk.TclError:
            pass

    # ------------------------------------------------------------------ rueda del mouse
    def _activar_rueda(self, _):
        self.canvas.bind_all("<MouseWheel>", self._rueda)
        self.canvas.bind_all("<Shift-MouseWheel>", self._rueda_h)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-2, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(2, "units"))

    def _desactivar_rueda(self, _):
        for ev in ("<MouseWheel>", "<Shift-MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.unbind_all(ev)

    def _rueda(self, ev):
        self.canvas.yview_scroll(-1 if ev.delta > 0 else 1, "units")

    def _rueda_h(self, ev):
        self.canvas.xview_scroll(-1 if ev.delta > 0 else 1, "units")


# =============================================================================== visor
class VisorReporte(ttk.Frame):
    """Muestra un Reporte con estilos y permite exportarlo a PDF con un botón."""

    def __init__(self, parent, titulo: str = "Procedimiento y resultado"):
        super().__init__(parent)
        self.reporte: Reporte | None = None
        barra = ttk.Frame(self)
        barra.pack(fill="x", pady=(0, 4))
        ttk.Label(barra, text=titulo, style="Titulo.TLabel", font=(tema.fuente_ui(), 11, "bold")).pack(side="left")
        self.btn_pdf = ttk.Button(barra, text="Exportar PDF", style="Accion.TButton", command=self.exportar_pdf)
        self.btn_pdf.pack(side="right")
        self.btn_copiar = ttk.Button(barra, text="Copiar texto", style="Suave.TButton", command=self.copiar)
        self.btn_copiar.pack(side="right", padx=6)
        marco = ttk.Frame(self)
        marco.pack(fill="both", expand=True)
        sb = ttk.Scrollbar(marco, orient="vertical")
        mono, ui = tema.fuente_mono(), tema.fuente_ui()
        self.texto = tk.Text(marco, wrap="word", bg=tema.ENTRY_BG, fg=tema.FG, relief="flat", bd=0,
                             padx=12, pady=8, font=(ui, 10), yscrollcommand=sb.set, state="disabled",
                             insertbackground=tema.FG, selectbackground=tema.SELECCION, height=10)
        sb.config(command=self.texto.yview)
        sb.pack(side="right", fill="y")
        self.texto.pack(side="left", fill="both", expand=True)
        t = self.texto
        t.tag_configure("titulo", font=(ui, 15, "bold"), foreground=tema.ACENTO, spacing3=2)
        t.tag_configure("subtitulo", font=(ui, 11, "italic"), foreground=tema.BTN_HOVER, spacing3=4)
        t.tag_configure("meta_e", font=(ui, 9, "bold"), foreground=tema.FG_SUAVE)
        t.tag_configure("meta_v", font=(ui, 9), foreground=tema.FG_SUAVE)
        t.tag_configure("h1", font=(ui, 12, "bold"), foreground=tema.ACENTO, spacing1=6, spacing3=3, underline=False)
        t.tag_configure("h2", font=(ui, 11, "bold"), foreground=tema.BTN_HOVER, spacing1=4)
        t.tag_configure("h3", font=(ui, 10, "bold"), foreground=tema.ADV, spacing1=8)
        t.tag_configure("p", font=(ui, 10), lmargin1=4, lmargin2=4, spacing1=1)
        t.tag_configure("etiqueta", font=(ui, 9, "italic"), foreground=tema.FG_SUAVE, lmargin1=14, spacing1=4)
        t.tag_configure("mono", font=(mono, 10), lmargin1=14, lmargin2=14, wrap="none")
        t.tag_configure("eq", font=(mono, 10), foreground=tema.FG, lmargin1=14, lmargin2=14)
        for tag, (bg, fg) in {"caja_exito": ("#2F4A33", "#C9E8C0"), "caja_error": ("#5A2B31", "#F4C2C7"),
                              "caja_info": ("#2B4560", "#BFD9F2"), "caja_adv": ("#5A4A22", "#F2DFA8")}.items():
            t.tag_configure(tag, background=bg, foreground=fg, font=(ui, 10, "bold"), lmargin1=10, lmargin2=10,
                            spacing1=1, spacing3=1)
        self._vacio()

    def _vacio(self):
        self.btn_pdf.state(["disabled"])
        self.btn_copiar.state(["disabled"])
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", "\n  Aquí aparecerá el procedimiento paso a paso.\n"
                                 "  Después podrá exportarlo a PDF con el botón «Exportar PDF».", "etiqueta")
        self.texto.configure(state="disabled")

    def limpiar(self):
        self.reporte = None
        self._vacio()

    def mostrar(self, reporte: Reporte):
        self.reporte = reporte
        t = self.texto
        t.configure(state="normal")
        t.delete("1.0", "end")
        for fragmento, etiqueta in reporte.a_segmentos():
            if fragmento:
                t.insert("end", fragmento, etiqueta)
        t.configure(state="disabled")
        t.yview_moveto(0)
        self.btn_pdf.state(["!disabled"])
        self.btn_copiar.state(["!disabled"])

    def copiar(self):
        if self.reporte:
            self.clipboard_clear()
            self.clipboard_append(self.reporte.a_texto())

    def exportar_pdf(self):
        if self.reporte is None:
            messagebox.showwarning("Exportar PDF", "Primero realice una operación para generar el procedimiento.",
                                   parent=self.winfo_toplevel())
            return
        if not reportlab_disponible():
            messagebox.showerror(
                "Falta una librería",
                "Para exportar a PDF se necesita 'reportlab'.\n\nInstálela con este comando:\n\n"
                f'"{sys.executable}" -m pip install reportlab', parent=self.winfo_toplevel())
            return
        ruta = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(), defaultextension=".pdf", initialfile=nombre_sugerido(self.reporte),
            filetypes=[("Documento PDF", "*.pdf")], title="Guardar procedimiento como PDF")
        if not ruta:
            return
        try:
            exportar_pdf(self.reporte, ruta)
        except ErrorPDF as e:
            messagebox.showerror("No se pudo exportar el PDF", str(e), parent=self.winfo_toplevel())
            return
        if messagebox.askyesno("PDF guardado", f"El PDF se guardó en:\n{ruta}\n\n¿Desea abrirlo ahora?",
                               parent=self.winfo_toplevel()):
            abrir_archivo(ruta)


def abrir_archivo(ruta: str) -> None:
    try:
        if sys.platform.startswith("win"):
            os.startfile(ruta)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", ruta])
        else:
            subprocess.Popen(["xdg-open", ruta])
    except Exception:
        pass


# =============================================================================== utilidades
def crear_spin(parent, variable: tk.StringVar, minimo: int, maximo: int, ancho: int = 5, comando=None):
    """Spinbox que solo acepta dígitos y respeta [minimo, maximo]."""
    def validar(p):
        return p == "" or (p.isdigit() and len(p) <= len(str(maximo)))
    sp = ttk.Spinbox(parent, from_=minimo, to=maximo, textvariable=variable, width=ancho, justify="center",
                     validate="key", validatecommand=(parent.register(validar), "%P"), command=comando)
    return sp
