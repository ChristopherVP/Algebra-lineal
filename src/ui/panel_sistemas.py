"""Pestaña 1: sistemas de ecuaciones y operaciones con matrices."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import numpy as np

from .. import config
from ..nucleo import (multiplicar_matrices, operar_escalar, resolver_gauss_jordan, resolver_por_inversa)
from ..nucleo.validacion import parse_entero
from . import tema
from .componentes import MatrixGrid, VisorReporte, crear_spin
from .dialogos import DialogoAleatorioMatriz, DialogoEscalar, DialogoMultiplicar, generar_aleatoria

DIM_INICIAL = 3


class PanelSistemas(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._construir_controles()
        self._construir_area()
        self.reiniciar(confirmar=False)

    # ------------------------------------------------------------------ interfaz
    def _construir_controles(self):
        izq = ttk.Frame(self, padding=(8, 8, 4, 8))
        izq.grid(row=0, column=0, sticky="ns")

        lf = ttk.LabelFrame(izq, text="1 · Tamaño de la matriz", padding=10)
        lf.pack(fill="x", pady=(0, 8))
        self.v_filas, self.v_cols = tk.StringVar(value=str(DIM_INICIAL)), tk.StringVar(value=str(DIM_INICIAL))
        ttk.Label(lf, text="Ecuaciones (filas):").grid(row=0, column=0, sticky="w", pady=3)
        crear_spin(lf, self.v_filas, 1, config.MAX_FILAS).grid(row=0, column=1, padx=6)
        ttk.Label(lf, text="Incógnitas (columnas):").grid(row=1, column=0, sticky="w", pady=3)
        crear_spin(lf, self.v_cols, 1, config.MAX_COLUMNAS).grid(row=1, column=1, padx=6)
        ttk.Label(lf, text=f"Máximo {config.MAX_FILAS}×{config.MAX_COLUMNAS}", style="Limites.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(2, 6))
        ttk.Button(lf, text="Aplicar tamaño", command=self.aplicar_tamano).grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Button(lf, text="Generar aleatoria…", command=self.aleatoria).grid(row=4, column=0, columnspan=2, sticky="ew", pady=2)

        lf2 = ttk.LabelFrame(izq, text="2 · Resolver el sistema", padding=10)
        lf2.pack(fill="x", pady=8)
        ttk.Button(lf2, text="Gauss-Jordan", style="Accion.TButton",
                   command=lambda: self.resolver(resolver_gauss_jordan)).pack(fill="x", pady=2)
        ttk.Button(lf2, text="Matriz inversa  (x = A⁻¹·b)", style="Accion.TButton",
                   command=lambda: self.resolver(resolver_por_inversa)).pack(fill="x", pady=2)

        lf3 = ttk.LabelFrame(izq, text="3 · Operaciones con A", padding=10)
        lf3.pack(fill="x", pady=8)
        ttk.Button(lf3, text="Multiplicar / dividir por escalar…", command=self.escalar).pack(fill="x", pady=2)
        ttk.Button(lf3, text="Multiplicar por matriz B…", command=self.multiplicar_matriz).pack(fill="x", pady=2)

        lf4 = ttk.LabelFrame(izq, text="4 · Edición", padding=10)
        lf4.pack(fill="x", pady=8)
        ttk.Button(lf4, text="Limpiar celdas seleccionadas", command=self.limpiar_seleccion).pack(fill="x", pady=2)
        ttk.Button(lf4, text="Seleccionar todo", style="Suave.TButton",
                   command=lambda: self.grid.seleccionar_todo()).pack(fill="x", pady=2)

    def _construir_area(self):
        der = ttk.Frame(self, padding=(4, 8, 8, 8))
        der.grid(row=0, column=1, sticky="nsew")
        der.rowconfigure(0, weight=1)
        der.columnconfigure(0, weight=1)
        panel = ttk.PanedWindow(der, orient="vertical")
        panel.grid(row=0, column=0, sticky="nsew")

        lf = ttk.LabelFrame(panel, text="Matriz aumentada [A | b]   (edite escribiendo en las celdas)", padding=8)
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)
        self.grid = MatrixGrid(lf, DIM_INICIAL, DIM_INICIAL + 1, max_filas=config.MAX_FILAS,
                               max_columnas=config.MAX_COLUMNAS + 1, columna_b=True,
                               encabezado_col=lambda j, n: f"x{j + 1}" if j < n - 1 else "b",
                               encabezado_fila=lambda i: f"F{i + 1}", alto=190)
        self.grid.grid(row=0, column=0, sticky="nsew")
        self.estado = ttk.Label(lf, text="", style="Suave.TLabel")
        self.estado.grid(row=1, column=0, sticky="w", pady=(6, 0))
        panel.add(lf, weight=1)

        self.visor = VisorReporte(panel)
        panel.add(self.visor, weight=2)

    def aviso(self, texto: str, error: bool = False):
        self.estado.configure(text=texto, style="Error.TLabel" if error else "Ok.TLabel")

    # ------------------------------------------------------------------ datos
    def _leer(self) -> tuple[np.ndarray, np.ndarray] | None:
        try:
            M = self.grid.obtener()
        except ValueError as e:
            self.aviso(str(e), True)
            messagebox.showerror("Dato inválido", str(e), parent=self.winfo_toplevel())
            return None
        return M[:, :-1], M[:, -1]

    def _poner(self, A: np.ndarray, b: np.ndarray | None = None):
        if b is None:
            b = self.grid.obtener()[:, -1] if self.grid.filas == A.shape[0] else np.zeros(A.shape[0])
        self.grid.establecer(np.column_stack([A, b]))
        self.v_filas.set(str(A.shape[0]))
        self.v_cols.set(str(A.shape[1]))

    # ------------------------------------------------------------------ acciones
    def aplicar_tamano(self):
        try:
            m = parse_entero(self.v_filas.get(), 1, config.MAX_FILAS, "Ecuaciones (filas)")
            n = parse_entero(self.v_cols.get(), 1, config.MAX_COLUMNAS, "Incógnitas (columnas)")
        except ValueError as e:
            self.aviso(str(e), True)
            messagebox.showerror("Tamaño no permitido", str(e), parent=self.winfo_toplevel())
            return
        self.grid.redimensionar(m, n + 1)
        self.visor.limpiar()
        self.aviso(f"Matriz de {m}×{n} lista. Se conservaron los valores que caben en el nuevo tamaño.")

    def aleatoria(self):
        d = DialogoAleatorioMatriz(self, self.grid.filas, self.grid.columnas - 1, etiqueta_filas="Ecuaciones (filas)",
                                   etiqueta_columnas="Incógnitas (columnas)", titulo="Generar sistema aleatorio")
        r = d.mostrar()
        if not r:
            return
        M = generar_aleatoria(r["filas"], r["columnas"] + 1, r["minimo"], r["maximo"], r["enteros"])
        self.grid.establecer(M)
        self.v_filas.set(str(r["filas"]))
        self.v_cols.set(str(r["columnas"]))
        self.visor.limpiar()
        self.aviso(f"Sistema aleatorio de {r['filas']}×{r['columnas']} generado.")

    def resolver(self, metodo):
        datos = self._leer()
        if datos is None:
            return
        A, b = datos
        res = metodo(A, b)
        self.visor.mostrar(res.reporte)
        top = self.winfo_toplevel()
        if res.estado == "error":
            self.aviso(res.mensaje or "Error", True)
            messagebox.showerror("No se pudo resolver", res.mensaje, parent=top)
        elif res.estado == "inconsistente":
            self.aviso(res.mensaje or "Sistema inconsistente", True)
            messagebox.showwarning("Sistema sin solución", res.mensaje, parent=top)
        else:
            self.aviso("Resuelto. Puede exportar el procedimiento con «Exportar PDF».")

    def escalar(self):
        datos = self._leer()
        if datos is None:
            return
        A, b = datos
        r = DialogoEscalar(self).mostrar()
        if not r:
            return
        res = operar_escalar(A, r["k"], r["dividir"])
        self.visor.mostrar(res.reporte)
        if res.es_error:
            self.aviso(res.mensaje, True)
            messagebox.showerror("Operación no permitida", res.mensaje, parent=self.winfo_toplevel())
            return
        self._poner(res.matriz, b)
        self.aviso("Matriz A actualizada con el resultado (el vector b no cambia).")

    def multiplicar_matriz(self):
        datos = self._leer()
        if datos is None:
            return
        A, b = datos

        def aplicar(C: np.ndarray):
            self._poner(C, b)
            self.visor.limpiar()
            self.aviso(f"A fue reemplazada por A·B ({C.shape[0]}×{C.shape[1]}). El vector b se conservó.")

        DialogoMultiplicar(self, A, aplicar).mostrar()

    def limpiar_seleccion(self):
        if not self.grid.hay_seleccion():
            self.aviso("Primero seleccione celdas: clic, arrastre, Mayús+clic, o clic en F#/x# para fila/columna.", True)
            return
        n = self.grid.limpiar_seleccion()
        self.aviso(f"{n} celda(s) seleccionada(s) puestas en 0. El resto de la matriz no cambió.")

    def reiniciar(self, confirmar: bool = True):
        self.v_filas.set(str(DIM_INICIAL))
        self.v_cols.set(str(DIM_INICIAL))
        self.grid.redimensionar(DIM_INICIAL, DIM_INICIAL + 1)
        self.grid.limpiar_todo()
        self.visor.limpiar()
        self.aviso("")
