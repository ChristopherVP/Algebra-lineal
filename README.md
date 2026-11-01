# Calculadora de Álgebra Lineal

Universidad Central del Ecuador · Facultad de Ingeniería y Ciencias Aplicadas

## Ejecutar
```
python -m pip install -r requirements.txt
python main.py
```

## Estructura
```
main.py                      punto de entrada (revisa dependencias)
algebra_lineal/
  config.py                  límites del programa y datos del PDF (integrantes, universidad)
  nucleo/                    matemática, sin interfaz
    eliminacion.py           motor Gauss-Jordan paso a paso
    gauss_jordan.py  inversa.py  multiplicacion.py  combinacion_lineal.py
    reporte.py               modelo de procedimiento (pantalla y PDF usan el mismo)
    validacion.py  formato.py
  pdf/                       exportación a PDF (reportlab + fuente DejaVu incluida)
  ui/                        interfaz Tkinter: app, paneles, diálogos, componentes
tests/test_nucleo.py         python -m unittest discover -s tests
```

## Límites garantizados
Matrices hasta 15×15, hasta 15 vectores de dimensión 15, valores entre ±1.000.000.
Se cambian en `algebra_lineal/config.py`.

## Edición de celdas
Clic: seleccionar · arrastrar / Mayús+clic: rango · Ctrl+clic: agregar · clic en F#/x#: fila/columna ·
«Limpiar celdas seleccionadas» o Supr: pone en 0 solo lo seleccionado · «Reiniciar todo»: vuelve al inicio.
Las celdas aceptan enteros, decimales (2.5 ó 2,5) y fracciones (1/3).
