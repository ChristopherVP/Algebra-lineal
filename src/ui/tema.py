"""Colores, fuentes y estilos ttk de la aplicación (tema oscuro tipo Nord)."""
from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

BG = "#2E3440"
BG_PANEL = "#343B49"
FG = "#ECEFF4"
FG_SUAVE = "#A9B3C4"
BTN = "#5E81AC"
BTN_HOVER = "#81A1C1"
ENTRY_BG = "#3B4252"
ACENTO = "#88C0D0"
PELIGRO = "#BF616A"
PELIGRO_HOVER = "#D08770"
OK = "#A3BE8C"
ADV = "#EBCB8B"
SELECCION = "#4C6A91"
INVALIDO = "#7A3B44"
BORDE = "#4C566A"


def _primera_disponible(candidatas, por_defecto):
    disponibles = {f.lower() for f in tkfont.families()}
    for c in candidatas:
        if c.lower() in disponibles:
            return c
    return por_defecto


def fuente_ui() -> str:
    return _primera_disponible(["Segoe UI", "Helvetica Neue", "Helvetica", "DejaVu Sans"], "TkDefaultFont")


def fuente_mono() -> str:
    return _primera_disponible(["Consolas", "Cascadia Mono", "DejaVu Sans Mono", "Courier New"], "TkFixedFont")


def aplicar_tema(root: tk.Misc) -> None:
    ui = fuente_ui()
    style = ttk.Style(root)
    style.theme_use("clam")
    root.configure(background=BG)
    style.configure(".", background=BG, foreground=FG, font=(ui, 10))
    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=BG_PANEL)
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("Suave.TLabel", foreground=FG_SUAVE, font=(ui, 9))
    style.configure("Titulo.TLabel", foreground=ACENTO, font=(ui, 15, "bold"))
    style.configure("Limites.TLabel", foreground=ADV, font=(ui, 9))
    style.configure("Error.TLabel", foreground="#E8838D", font=(ui, 9, "bold"))
    style.configure("Ok.TLabel", foreground=OK, font=(ui, 9))
    style.configure("TLabelframe", background=BG, bordercolor=BORDE, borderwidth=1, relief="solid")
    style.configure("TLabelframe.Label", background=BG, foreground=ACENTO, font=(ui, 10, "bold"))
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=BTN, foreground=FG, padding=[14, 6], font=(ui, 10, "bold"))
    style.map("TNotebook.Tab", background=[("selected", ACENTO)], foreground=[("selected", BG)])
    style.configure("TButton", background=BTN, foreground=FG, borderwidth=0, padding=(10, 6), font=(ui, 10, "bold"))
    style.map("TButton", background=[("active", BTN_HOVER), ("disabled", BORDE)],
              foreground=[("disabled", FG_SUAVE)])
    style.configure("Accion.TButton", background="#5B8C5A")
    style.map("Accion.TButton", background=[("active", "#78A977"), ("disabled", BORDE)])
    style.configure("Peligro.TButton", background=PELIGRO)
    style.map("Peligro.TButton", background=[("active", PELIGRO_HOVER)])
    style.configure("Suave.TButton", background=BORDE, padding=(8, 4), font=(ui, 9, "bold"))
    style.map("Suave.TButton", background=[("active", BTN), ("disabled", BG_PANEL)])
    style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=FG, insertcolor=FG, bordercolor=BORDE)
    style.configure("TSpinbox", fieldbackground=ENTRY_BG, foreground=FG, arrowcolor=FG, bordercolor=BORDE,
                    background=BORDE, insertcolor=FG)
    style.map("TSpinbox", fieldbackground=[("!disabled", ENTRY_BG), ("disabled", BG_PANEL)],
              foreground=[("!disabled", FG), ("disabled", FG_SUAVE)])
    style.configure("TCheckbutton", background=BG, foreground=FG)
    style.map("TCheckbutton", background=[("active", BG)])
    style.configure("TRadiobutton", background=BG, foreground=FG)
    style.map("TRadiobutton", background=[("active", BG)])
    style.configure("TPanedwindow", background=BG)
    style.configure("Sash", sashthickness=6, background=BORDE)
    style.configure("Vertical.TScrollbar", background=BORDE, troughcolor=BG, arrowcolor=FG, bordercolor=BG)
    style.configure("Horizontal.TScrollbar", background=BORDE, troughcolor=BG, arrowcolor=FG, bordercolor=BG)
