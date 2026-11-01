"""Punto de entrada: python main.py"""
import sys


def _verificar_dependencias() -> list[str]:
    faltan = []
    for modulo, paquete in (("numpy", "numpy"), ("reportlab", "reportlab")):
        try:
            __import__(modulo)
        except ImportError:
            faltan.append(paquete)
    return faltan


def main() -> int:
    faltan = _verificar_dependencias()
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print("Este Python no incluye Tkinter. Instale una versión de Python con Tkinter (python.org) "
              "o el paquete python3-tk.")
        return 1
    if faltan:
        comando = f'"{sys.executable}" -m pip install ' + " ".join(faltan)
        mensaje = ("Faltan librerías para ejecutar el programa:\n  " + ", ".join(faltan) +
                   f"\n\nInstálelas con este comando:\n\n{comando}")
        try:
            import tkinter as tk
            from tkinter import messagebox
            raiz = tk.Tk()
            raiz.withdraw()
            messagebox.showerror("Faltan librerías", mensaje)
        except Exception:
            print(mensaje)
        return 1
    from src.ui.app import App
    App().mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
