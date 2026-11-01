"""Ventana principal."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .. import config
from . import tema
from .panel_combinacion import PanelCombinacion
from .panel_sistemas import PanelSistemas


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(config.PROGRAMA)
        self.minsize(1000, 680)
        ancho, alto = 1240, 820
        x = max(0, (self.winfo_screenwidth() - ancho) // 2)
        y = max(0, (self.winfo_screenheight() - alto) // 3)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        tema.aplicar_tema(self)

        barra = ttk.Frame(self, padding=(14, 10, 14, 0))
        barra.pack(fill="x")
        ttk.Label(barra, text=config.PROGRAMA, style="Titulo.TLabel").pack(side="left")
        ttk.Button(barra, text="Reiniciar todo", style="Peligro.TButton", command=self.reiniciar_todo).pack(side="right")
        ttk.Label(self, text=config.texto_limites(), style="Limites.TLabel", padding=(14, 2, 14, 4)).pack(fill="x")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.panel_sistemas = PanelSistemas(self.notebook)
        self.panel_combinacion = PanelCombinacion(self.notebook)
        self.notebook.add(self.panel_sistemas, text="  Sistemas y Matrices  ")
        self.notebook.add(self.panel_combinacion, text="  Combinación Lineal  ")

    def reiniciar_todo(self, confirmar: bool = True):
        if confirmar and not messagebox.askyesno(
                "Reiniciar todo",
                "Se borrarán TODOS los datos y resultados de ambas pestañas y se volverá al estado inicial.\n\n"
                "Si solo desea vaciar algunas celdas, use «Limpiar celdas seleccionadas».\n\n¿Continuar?", parent=self):
            return
        self.panel_sistemas.reiniciar()
        self.panel_combinacion.reiniciar()
        self.notebook.select(self.panel_sistemas)
