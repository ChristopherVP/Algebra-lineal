"""Pestaña 2: combinación lineal y dependencia lineal."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import numpy as np

from .. import config
from ..nucleo import analizar_combinacion_lineal
from ..nucleo.validacion import parse_entero
from .componentes import MatrixGrid, VisorReporte, crear_spin
from .dialogos import DialogoAleatorioVectores

K_INICIAL, D_INICIAL = 3, 3
EJEMPLO_V = [[1, 0, 1], [2, 1, 0], [3, 1, -1]]
EJEMPLO_OBJ = [4, 1, 1]


class PanelCombinacion(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._construir_controles()
        self._construir_area()
        self.reiniciar(confirmar=False)

    def _construir_controles(self):
        izq = ttk.Frame(self, padding=(8, 8, 4, 8))
        izq.grid(row=0, column=0, sticky="ns")
        lf = ttk.LabelFrame(izq, text="1 · Tamaño", padding=10)
        lf.pack(fill="x", pady=(0, 8))
        self.v_k, self.v_d = tk.StringVar(value=str(K_INICIAL)), tk.StringVar(value=str(D_INICIAL))
        ttk.Label(lf, text="Vectores base:").grid(row=0, column=0, sticky="w", pady=3)
        crear_spin(lf, self.v_k, 1, config.MAX_VECTORES).grid(row=0, column=1, padx=6)
        ttk.Label(lf, text="Dimensión:").grid(row=1, column=0, sticky="w", pady=3)
        crear_spin(lf, self.v_d, 1, config.MAX_DIMENSION).grid(row=1, column=1, padx=6)
        ttk.Label(lf, text=f"Máximo {config.MAX_VECTORES} vectores de dimensión {config.MAX_DIMENSION}",
                  style="Limites.TLabel", wraplength=190).grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 6))
        ttk.Button(lf, text="Aplicar tamaño", command=self.aplicar_tamano).grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Button(lf, text="Generar aleatorio…", command=self.aleatorio).grid(row=4, column=0, columnspan=2, sticky="ew", pady=2)

        lf2 = ttk.LabelFrame(izq, text="2 · Analizar", padding=10)
        lf2.pack(fill="x", pady=8)
        ttk.Button(lf2, text="Analizar combinación lineal", style="Accion.TButton", command=self.analizar).pack(fill="x", pady=2)

        lf3 = ttk.LabelFrame(izq, text="3 · Edición", padding=10)
        lf3.pack(fill="x", pady=8)
        ttk.Button(lf3, text="Limpiar celdas seleccionadas", command=self.limpiar_seleccion).pack(fill="x", pady=2)
        ttk.Label(lf3, text="Cada FILA de la tabla de arriba es un vector base.", style="Suave.TLabel",
                  wraplength=190).pack(anchor="w", pady=(6, 0))

    def _construir_area(self):
        der = ttk.Frame(self, padding=(4, 8, 8, 8))
        der.grid(row=0, column=1, sticky="nsew")
        der.rowconfigure(0, weight=1)
        der.columnconfigure(0, weight=1)
        panel = ttk.PanedWindow(der, orient="vertical")
        panel.grid(row=0, column=0, sticky="nsew")

        entrada = ttk.Frame(panel)
        entrada.columnconfigure(0, weight=1)
        entrada.rowconfigure(0, weight=3)
        entrada.rowconfigure(1, weight=1)
        lf1 = ttk.LabelFrame(entrada, text="Vectores base  (una fila por vector)", padding=6)
        lf1.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        lf1.rowconfigure(0, weight=1)
        lf1.columnconfigure(0, weight=1)
        self.grid_v = MatrixGrid(lf1, K_INICIAL, D_INICIAL, max_filas=config.MAX_VECTORES, max_columnas=config.MAX_DIMENSION,
                                 encabezado_col=lambda j, n: f"comp {j + 1}", encabezado_fila=lambda i: f"v{i + 1}",
                                 on_seleccion=self._seleccion, alto=130)
        self.grid_v.grid(row=0, column=0, sticky="nsew")
        lf2 = ttk.LabelFrame(entrada, text="Vector objetivo  v", padding=6)
        lf2.grid(row=1, column=0, sticky="nsew")
        lf2.rowconfigure(0, weight=1)
        lf2.columnconfigure(0, weight=1)
        self.grid_o = MatrixGrid(lf2, 1, D_INICIAL, max_filas=1, max_columnas=config.MAX_DIMENSION,
                                 encabezado_col=lambda j, n: f"comp {j + 1}", encabezado_fila=lambda i: "v",
                                 on_seleccion=self._seleccion, alto=70)
        self.grid_o.grid(row=0, column=0, sticky="nsew")
        self.estado = ttk.Label(entrada, text="", style="Suave.TLabel")
        self.estado.grid(row=2, column=0, sticky="w", pady=(4, 0))
        panel.add(entrada, weight=2)

        self.visor = VisorReporte(panel, "Resultado del análisis")
        panel.add(self.visor, weight=3)

    def _seleccion(self, origen: MatrixGrid):
        """Solo una grilla tiene selección a la vez."""
        otro = self.grid_o if origen is self.grid_v else self.grid_v
        otro.deseleccionar()

    def aviso(self, texto: str, error: bool = False):
        self.estado.configure(text=texto, style="Error.TLabel" if error else "Ok.TLabel")

    def _cargar_ejemplo(self):
        self.grid_v.redimensionar(3, 3)
        self.grid_o.redimensionar(1, 3)
        self.grid_v.establecer(np.array(EJEMPLO_V, dtype=float))
        self.grid_o.establecer(np.array([EJEMPLO_OBJ], dtype=float))
        self.v_k.set("3")
        self.v_d.set("3")

    # ------------------------------------------------------------------ acciones
    def aplicar_tamano(self):
        try:
            k = parse_entero(self.v_k.get(), 1, config.MAX_VECTORES, "Vectores base")
            d = parse_entero(self.v_d.get(), 1, config.MAX_DIMENSION, "Dimensión")
        except ValueError as e:
            self.aviso(str(e), True)
            messagebox.showerror("Tamaño no permitido", str(e), parent=self.winfo_toplevel())
            return
        self.grid_v.redimensionar(k, d)
        self.grid_o.redimensionar(1, d)
        self.visor.limpiar()
        self.aviso(f"{k} vector(es) de dimensión {d}. Se conservaron los valores que caben.")

    def aleatorio(self):
        r = DialogoAleatorioVectores(self, self.grid_v.filas, self.grid_v.columnas).mostrar()
        if not r:
            return
        k, d = r["k"], r["d"]
        V = np.random.randint(r["minimo"], r["maximo"] + 1, size=(k, d)).astype(float)
        if r["combinacion"]:
            coef = np.random.randint(-3, 4, size=k).astype(float)
            obj = coef @ V
        else:
            obj = np.random.randint(r["minimo"], r["maximo"] + 1, size=d).astype(float)
        self.grid_v.redimensionar(k, d)
        self.grid_o.redimensionar(1, d)
        self.grid_v.establecer(V)
        self.grid_o.establecer(obj.reshape(1, -1))
        self.v_k.set(str(k))
        self.v_d.set(str(d))
        self.visor.limpiar()
        self.aviso("Vectores aleatorios generados.")

    def analizar(self):
        try:
            V = self.grid_v.obtener()
            v = self.grid_o.obtener()[0]
        except ValueError as e:
            self.aviso(str(e), True)
            messagebox.showerror("Dato inválido", str(e), parent=self.winfo_toplevel())
            return
        res = analizar_combinacion_lineal(V, v)
        self.visor.mostrar(res.reporte)
        top = self.winfo_toplevel()
        if res.estado == "error":
            self.aviso(res.mensaje, True)
            messagebox.showerror("No se pudo analizar", res.mensaje, parent=top)
        elif res.estado == "inconsistente":
            self.aviso(res.mensaje, True)
            messagebox.showwarning("No es combinación lineal", res.mensaje, parent=top)
        else:
            self.aviso("Análisis completo. Puede exportarlo con «Exportar PDF».")

    def limpiar_seleccion(self):
        n = self.grid_v.limpiar_seleccion() + self.grid_o.limpiar_seleccion()
        if n == 0:
            self.aviso("Primero seleccione celdas: clic, arrastre, Mayús+clic, o clic en v#/comp # para fila/columna.", True)
        else:
            self.aviso(f"{n} celda(s) seleccionada(s) puestas en 0. El resto no cambió.")

    def reiniciar(self, confirmar: bool = True):
        self._cargar_ejemplo()
        self.visor.limpiar()
        self.aviso("")
