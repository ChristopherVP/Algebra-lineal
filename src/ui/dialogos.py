"""Ventanas de diálogo: una sola ventana por tarea, con todas sus restricciones visibles."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import numpy as np

from .. import config
from ..nucleo import multiplicar_matrices
from ..nucleo.validacion import parse_entero, parse_numero, parse_rango
from . import tema
from .componentes import MatrixGrid, VisorReporte, crear_spin


class DialogoModal(tk.Toplevel):
    """Ventana modal centrada, con mensaje de error en línea (sin ventanas emergentes en cadena)."""

    def __init__(self, parent, titulo: str, ancho: int | None = None, alto: int | None = None, redimensionable=False):
        super().__init__(parent)
        self.padre = parent.winfo_toplevel()
        self.title(titulo)
        self.configure(background=tema.BG)
        self.transient(self.padre)
        self.resultado = None
        self.resizable(redimensionable, redimensionable)
        self.cuerpo = ttk.Frame(self, padding=14)
        self.cuerpo.pack(fill="both", expand=True)
        self.lbl_error = ttk.Label(self, text="", style="Error.TLabel", wraplength=(ancho or 420) - 30, justify="left")
        self.lbl_error.pack(fill="x", padx=14, pady=(0, 4))
        self.pie = ttk.Frame(self, padding=(14, 0, 14, 12))
        self.pie.pack(fill="x")
        self._tam = (ancho, alto)
        self.bind("<Escape>", lambda e: self.cancelar())
        self.protocol("WM_DELETE_WINDOW", self.cancelar)

    def mostrar(self):
        self.update_idletasks()
        ancho = self._tam[0] or self.winfo_reqwidth()
        alto = self._tam[1] or self.winfo_reqheight()
        x = self.padre.winfo_rootx() + max(0, (self.padre.winfo_width() - ancho) // 2)
        y = self.padre.winfo_rooty() + max(0, (self.padre.winfo_height() - alto) // 3)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.grab_set()
        self.focus_set()
        self.wait_window(self)
        return self.resultado

    def error(self, texto: str):
        self.lbl_error.configure(text=texto)

    def cancelar(self):
        self.resultado = None
        self.destroy()

    def botones_aceptar(self, texto_ok="Aceptar", comando=None):
        ttk.Button(self.pie, text="Cancelar", style="Suave.TButton", command=self.cancelar).pack(side="right", padx=(6, 0))
        ttk.Button(self.pie, text=texto_ok, style="Accion.TButton", command=comando or self.aceptar).pack(side="right")
        self.bind("<Return>", lambda e: (comando or self.aceptar)())

    def aceptar(self):  # pragma: no cover - lo redefine cada diálogo
        self.destroy()


def _fila(parent, fila, texto, widget_factory, nota=""):
    ttk.Label(parent, text=texto).grid(row=fila, column=0, sticky="w", padx=(0, 10), pady=5)
    w = widget_factory(parent)
    w.grid(row=fila, column=1, sticky="w", pady=5)
    if nota:
        ttk.Label(parent, text=nota, style="Suave.TLabel").grid(row=fila, column=2, sticky="w", padx=8)
    return w


# =============================================================================== aleatoria (matriz)
class DialogoAleatorioMatriz(DialogoModal):
    """Una sola ventana: tamaño, rango y tipo de números para una matriz aleatoria."""

    def __init__(self, parent, filas: int, columnas: int, *, bloquear_filas: bool = False,
                 etiqueta_filas="Filas", etiqueta_columnas="Columnas", titulo="Generar matriz aleatoria",
                 maximo_filas=config.MAX_FILAS, maximo_columnas=config.MAX_COLUMNAS):
        super().__init__(parent, titulo, ancho=470)
        self.max_f, self.max_c = maximo_filas, maximo_columnas
        self.et_f, self.et_c = etiqueta_filas, etiqueta_columnas
        cuerpo = self.cuerpo
        ttk.Label(cuerpo, text=titulo, style="Titulo.TLabel", font=(tema.fuente_ui(), 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        self.v_f, self.v_c = tk.StringVar(value=str(filas)), tk.StringVar(value=str(columnas))
        self.v_min, self.v_max = tk.StringVar(value="-10"), tk.StringVar(value="10")
        self.v_ent = tk.BooleanVar(value=True)
        sp_f = _fila(cuerpo, 1, f"{etiqueta_filas}:", lambda p: crear_spin(p, self.v_f, 1, maximo_filas),
                     f"1 a {maximo_filas}" + (" (fijo por compatibilidad)" if bloquear_filas else ""))
        if bloquear_filas:
            sp_f.configure(state="disabled")
        _fila(cuerpo, 2, f"{etiqueta_columnas}:", lambda p: crear_spin(p, self.v_c, 1, maximo_columnas),
              f"1 a {maximo_columnas}")
        lim = config.ALEATORIO_MAX
        _fila(cuerpo, 3, "Valor mínimo:", lambda p: ttk.Entry(p, textvariable=self.v_min, width=9, justify="center"),
              f"entre -{lim} y {lim}")
        _fila(cuerpo, 4, "Valor máximo:", lambda p: ttk.Entry(p, textvariable=self.v_max, width=9, justify="center"),
              "mayor que el mínimo")
        ttk.Checkbutton(cuerpo, text="Solo números enteros (si no, 2 decimales)", variable=self.v_ent).grid(
            row=5, column=0, columnspan=3, sticky="w", pady=6)
        self.botones_aceptar("Generar")

    def aceptar(self):
        try:
            f = parse_entero(self.v_f.get(), 1, self.max_f, self.et_f)
            c = parse_entero(self.v_c.get(), 1, self.max_c, self.et_c)
            mn, mx = parse_rango(self.v_min.get(), self.v_max.get(), config.ALEATORIO_MAX, "Rango")
        except ValueError as e:
            self.error(str(e))
            return
        self.resultado = {"filas": f, "columnas": c, "minimo": mn, "maximo": mx, "enteros": self.v_ent.get()}
        self.destroy()


def generar_aleatoria(filas, columnas, minimo, maximo, enteros) -> np.ndarray:
    if enteros:
        return np.random.randint(int(np.ceil(minimo)), int(np.floor(maximo)) + 1, size=(filas, columnas)).astype(float)
    return np.round(np.random.uniform(minimo, maximo, size=(filas, columnas)), 2)


# =============================================================================== aleatoria (vectores)
class DialogoAleatorioVectores(DialogoModal):
    def __init__(self, parent, k: int, d: int):
        super().__init__(parent, "Generar vectores aleatorios", ancho=500)
        c = self.cuerpo
        ttk.Label(c, text="Generar vectores aleatorios", style="Titulo.TLabel",
                  font=(tema.fuente_ui(), 12, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        self.v_k, self.v_d = tk.StringVar(value=str(k)), tk.StringVar(value=str(d))
        self.v_min, self.v_max = tk.StringVar(value="-10"), tk.StringVar(value="10")
        self.v_comb = tk.BooleanVar(value=False)
        _fila(c, 1, "Cantidad de vectores base:", lambda p: crear_spin(p, self.v_k, 1, config.MAX_VECTORES),
              f"1 a {config.MAX_VECTORES}")
        _fila(c, 2, "Dimensión de cada vector:", lambda p: crear_spin(p, self.v_d, 1, config.MAX_DIMENSION),
              f"1 a {config.MAX_DIMENSION}")
        lim = config.ALEATORIO_MAX
        _fila(c, 3, "Valor entero mínimo:", lambda p: ttk.Entry(p, textvariable=self.v_min, width=9, justify="center"),
              f"entre -{lim} y {lim}")
        _fila(c, 4, "Valor entero máximo:", lambda p: ttk.Entry(p, textvariable=self.v_max, width=9, justify="center"),
              "mayor que el mínimo")
        ttk.Checkbutton(c, text="Garantizar que v sea combinación lineal de los vectores base",
                        variable=self.v_comb).grid(row=5, column=0, columnspan=3, sticky="w", pady=6)
        self.botones_aceptar("Generar")

    def aceptar(self):
        try:
            k = parse_entero(self.v_k.get(), 1, config.MAX_VECTORES, "Cantidad de vectores")
            d = parse_entero(self.v_d.get(), 1, config.MAX_DIMENSION, "Dimensión")
            mn, mx = parse_rango(self.v_min.get(), self.v_max.get(), config.ALEATORIO_MAX, "Rango")
        except ValueError as e:
            self.error(str(e))
            return
        self.resultado = {"k": k, "d": d, "minimo": int(np.ceil(mn)), "maximo": int(np.floor(mx)),
                          "combinacion": self.v_comb.get()}
        if self.resultado["minimo"] >= self.resultado["maximo"]:
            self.error("Rango: debe contener al menos dos enteros distintos.")
            self.resultado = None
            return
        self.destroy()


# =============================================================================== escalar
class DialogoEscalar(DialogoModal):
    def __init__(self, parent, dividir: bool = False):
        super().__init__(parent, "Operación con escalar", ancho=400)
        c = self.cuerpo
        ttk.Label(c, text="Operar la matriz A con un escalar", style="Titulo.TLabel",
                  font=(tema.fuente_ui(), 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        self.v_op = tk.StringVar(value="div" if dividir else "mul")
        ttk.Radiobutton(c, text="Multiplicar A × k", value="mul", variable=self.v_op).grid(row=1, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(c, text="Dividir A ÷ k", value="div", variable=self.v_op).grid(row=2, column=0, columnspan=2, sticky="w")
        self.v_k = tk.StringVar(value="2")
        self.entrada = _fila(c, 3, "Escalar k:", lambda p: ttk.Entry(p, textvariable=self.v_k, width=12, justify="center"),
                             "número, decimal o fracción (1/3)")
        ttk.Label(c, text=f"Debe cumplir |k| ≤ {config.VALOR_MAX:,}".replace(",", ".") + "; para dividir, k ≠ 0.",
                  style="Suave.TLabel").grid(row=4, column=0, columnspan=3, sticky="w", pady=(4, 0))
        self.botones_aceptar("Aplicar")
        self.entrada.focus_set()
        self.entrada.select_range(0, "end")

    def aceptar(self):
        try:
            k = parse_numero(self.v_k.get())
            if self.v_op.get() == "div" and abs(k) < 1e-12:
                raise ValueError("No se puede dividir entre cero: k debe ser distinto de 0.")
        except ValueError as e:
            self.error(str(e))
            return
        self.resultado = {"k": k, "dividir": self.v_op.get() == "div"}
        self.destroy()


# =============================================================================== multiplicar por matriz
class DialogoMultiplicar(DialogoModal):
    """Define primero B compatible con A (filas fijas = columnas de A), la llena y multiplica."""

    def __init__(self, parent, A: np.ndarray, al_aplicar):
        super().__init__(parent, "Multiplicar A por una matriz B", ancho=1020, alto=760, redimensionable=True)
        self.A, self.al_aplicar = np.array(A, dtype=float), al_aplicar
        self.C: np.ndarray | None = None
        m, n = self.A.shape
        self.m, self.n = m, n
        c = self.cuerpo
        c.columnconfigure(0, weight=1)
        c.rowconfigure(2, weight=1)
        self.lbl_dim = ttk.Label(c, text="", style="Titulo.TLabel", font=(tema.fuente_ui(), 12, "bold"))
        self.lbl_dim.grid(row=0, column=0, sticky="w")
        ttk.Label(c, text=f"Para poder multiplicar, B debe tener exactamente {n} filas (las columnas de A). "
                          f"Usted elige cuántas columnas tiene B (1 a {config.MAX_COLUMNAS}).",
                  style="Suave.TLabel", wraplength=960).grid(row=1, column=0, sticky="w", pady=(0, 6))

        panel = ttk.PanedWindow(c, orient="vertical")
        panel.grid(row=2, column=0, sticky="nsew")
        arriba = ttk.Frame(panel)
        panel.add(arriba, weight=1)
        arriba.columnconfigure(0, weight=1)
        arriba.columnconfigure(1, weight=1)
        arriba.rowconfigure(0, weight=1)

        lf_a = ttk.LabelFrame(arriba, text=f"Matriz A  ({m}×{n})  — solo lectura", padding=6)
        lf_a.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        lf_a.rowconfigure(0, weight=1)
        lf_a.columnconfigure(0, weight=1)
        self.grid_a = MatrixGrid(lf_a, m, n, max_filas=config.MAX_FILAS, max_columnas=config.MAX_COLUMNAS,
                                 encabezado_col=lambda j, n: f"{j + 1}", encabezado_fila=lambda i: f"{i + 1}",
                                 editable=False, alto=150)
        self.grid_a.establecer(self.A)
        self.grid_a.grid(row=0, column=0, sticky="nsew")

        self.lf_b = ttk.LabelFrame(arriba, text="Matriz B", padding=6)
        self.lf_b.grid(row=0, column=1, sticky="nsew")
        self.lf_b.rowconfigure(1, weight=1)
        self.lf_b.columnconfigure(0, weight=1)
        ctl = ttk.Frame(self.lf_b)
        ctl.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ttk.Label(ctl, text=f"Filas: {n} (fijo)   Columnas:").pack(side="left")
        self.v_p = tk.StringVar(value=str(min(n, config.MAX_COLUMNAS)))
        crear_spin(ctl, self.v_p, 1, config.MAX_COLUMNAS, 4).pack(side="left", padx=4)
        ttk.Button(ctl, text="Aplicar tamaño", style="Suave.TButton", command=self.aplicar_tamano).pack(side="left", padx=4)
        ttk.Button(ctl, text="Aleatoria…", style="Suave.TButton", command=self.aleatoria).pack(side="left", padx=4)
        ttk.Button(ctl, text="Limpiar sel.", style="Suave.TButton", command=self.limpiar_seleccion).pack(side="left", padx=4)
        self.grid_b = MatrixGrid(self.lf_b, n, min(n, config.MAX_COLUMNAS), max_filas=config.MAX_FILAS,
                                 max_columnas=config.MAX_COLUMNAS,
                                 encabezado_col=lambda j, n: f"{j + 1}", encabezado_fila=lambda i: f"{i + 1}",
                                 on_cambio=self._b_cambio, alto=150)
        self.grid_b.grid(row=1, column=0, sticky="nsew")
        self.lbl_estado = ttk.Label(self.lf_b, text="Clic para seleccionar · Mayús+clic: rango · Supr: limpiar selección",
                                    style="Suave.TLabel")
        self.lbl_estado.grid(row=2, column=0, sticky="w", pady=(4, 0))

        self.visor = VisorReporte(panel, "Procedimiento de A · B")
        panel.add(self.visor, weight=2)

        self.btn_mult = ttk.Button(self.pie, text="Multiplicar A · B", style="Accion.TButton", command=self.multiplicar)
        self.btn_mult.pack(side="left")
        self.btn_usar = ttk.Button(self.pie, text="Usar A·B como nueva matriz A", style="Suave.TButton",
                                   command=self.usar_resultado, state="disabled")
        self.btn_usar.pack(side="left", padx=8)
        ttk.Button(self.pie, text="Cerrar", style="Suave.TButton", command=self.cancelar).pack(side="right")
        self.bind("<Return>", lambda e: None)
        self._actualizar_dim()

    def _actualizar_dim(self):
        p = self.grid_b.columnas
        self.lbl_dim.configure(text=f"A ({self.m}×{self.n})  ·  B ({self.n}×{p})  =  C ({self.m}×{p})")
        self.lf_b.configure(text=f"Matriz B  ({self.n}×{p})")

    def aplicar_tamano(self):
        try:
            p = parse_entero(self.v_p.get(), 1, config.MAX_COLUMNAS, "Columnas de B")
        except ValueError as e:
            self.error(str(e))
            return
        self.error("")
        self.grid_b.redimensionar(self.n, p)
        self._actualizar_dim()

    def aleatoria(self):
        d = DialogoAleatorioMatriz(self, self.n, self.grid_b.columnas, bloquear_filas=True,
                                   titulo="Rellenar B con valores aleatorios", maximo_columnas=config.MAX_COLUMNAS)
        r = d.mostrar()
        if r:
            self.grid_b.establecer(generar_aleatoria(self.n, r["columnas"], r["minimo"], r["maximo"], r["enteros"]))
            self.v_p.set(str(r["columnas"]))
            self._actualizar_dim()
            self.error("")

    def limpiar_seleccion(self):
        n = self.grid_b.limpiar_seleccion()
        self.lbl_estado.configure(text=f"{n} celda(s) de B puestas en 0." if n else
                                  "Primero seleccione celdas de B (clic, arrastre o Mayús+clic).")

    def _b_cambio(self):
        self.C = None
        if hasattr(self, "btn_usar"):
            self.btn_usar.state(["disabled"])

    def multiplicar(self):
        try:
            p = parse_entero(self.v_p.get(), 1, config.MAX_COLUMNAS, "Columnas de B")
            if p != self.grid_b.columnas:
                raise ValueError("Presione «Aplicar tamaño» para que B tenga el número de columnas indicado.")
            B = self.grid_b.obtener()
        except ValueError as e:
            self.error(str(e))
            return
        self.error("")
        res = multiplicar_matrices(self.A, B)
        self.visor.mostrar(res.reporte)
        if res.es_error:
            self.error(res.mensaje or "No se pudo multiplicar.")
            return
        self.C = res.matriz
        self.btn_usar.state(["!disabled"])

    def usar_resultado(self):
        if self.C is None:
            return
        if not np.all(np.isfinite(self.C)) or np.max(np.abs(self.C)) > config.RESULTADO_MAX:
            self.error(f"El resultado excede el límite permitido (±{config.RESULTADO_MAX:.0e}) para usarlo como A.")
            return
        self.al_aplicar(self.C)
        self.resultado = "aplicado"
        self.destroy()
