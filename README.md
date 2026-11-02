# Linear Algebra Calculator

> Desktop application in **Python + Tkinter** that solves linear systems, computes matrix inverses and products, and analyzes linear combinations and dependence — showing **every step** of the procedure and exporting it to a formal **PDF**.

**Universidad Central del Ecuador** · Faculty of Engineering and Applied Sciences · Course: Linear Algebra

Spanish version: [README.es.md](README.es.md)

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Requirements](#project-requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Guaranteed Limits](#guaranteed-limits)
7. [Input Rules](#input-rules)
8. [Cell Editing](#cell-editing)
9. [PDF Export](#pdf-export)
10. [Project Structure](#project-structure)
11. [Architecture](#architecture)
12. [Configuration](#configuration)
13. [Testing](#testing)
14. [Authors](#authors)

---

## Overview

The Linear Algebra Calculator is an educational tool. Instead of only giving a final answer, it documents the full procedure (row operations, pivots, substitutions, verification) so students can follow and check each step. The same procedure model is rendered on screen and in the exported PDF, so both always match.

The application has two tabs:

- **Systems and Matrices** — solve `A·x = b`, invert matrices, multiply matrices, scale matrices.
- **Linear Combination** — decide whether a vector is a linear combination of a set of vectors, and whether that set is linearly dependent or independent.

## Features

### Tab 1 · Systems and Matrices

| Feature | Description |
|---|---|
| **Gauss-Jordan elimination** | Solves `A·x = b` step by step, reducing the augmented matrix to reduced row echelon form. Detects **unique solution**, **infinitely many solutions** (free variables) and **inconsistent** systems. Includes an `A·x = b` verification table. |
| **Inverse matrix method** | Solves `x = A⁻¹·b`. Computes `A⁻¹` by applying Gauss-Jordan to `[A | I]`. Reports an error for non-square or singular matrices. |
| **Multiply / divide by scalar** | Computes `A × k` or `A ÷ k` (division by zero is rejected). |
| **Multiply by matrix B** | Computes `A · B`. B is defined in a dialog with its rows fixed to the columns of A so dimensions are always compatible. Incompatible sizes are rejected. |
| **Use result as new A** | The product `A·B` (and scalar results) can replace the current matrix A (values capped at ±10¹²). |
| **Random matrix generator** | Choose size, integer range, and integers-only or 2-decimal numbers. |

### Tab 2 · Linear Combination

| Feature | Description |
|---|---|
| **Linear combination test** | Checks whether a target vector `v` is a linear combination of the base vectors and, if so, gives the coefficients. Distinguishes unique, infinite and no-solution cases. |
| **Dependence / independence** | Determines whether the set of base vectors is linearly dependent or independent. |
| **Random vector generator** | Generates base vectors and a target vector; optionally **guarantees** that `v` is a linear combination of the base vectors. |
| **Built-in example** | Loads with a ready example (`v₁=(1,0,1)`, `v₂=(2,1,0)`, `v₃=(3,1,−1)`, `v=(4,1,1)`). |

### General

- **Step-by-step procedure** — matrix shown after each row operation for systems up to 6 rows; after each pivot for larger ones.
- **Fractions, decimals and integers** accepted in every cell (`3`, `2.5`, `2,5`, `1/3`).
- **Export to PDF** — formal document with university header, authors, matrices drawn with brackets and augmented-matrix bar, highlighted pivots, and colored result boxes.
- **Copy as text** — copies the procedure to the clipboard as plain text.
- **Inline validation** — invalid cells are highlighted in red; dialogs show errors inline (no chained pop-ups).
- **Reset all** — returns both tabs to the initial state (with confirmation).
- **Responsive grid** — scrollable matrix editor with mouse wheel, keyboard navigation and automatic scrollbars.
- **Missing-dependency detection** — on startup, `main.py` checks for Tkinter, NumPy and ReportLab and shows the exact `pip install` command if something is missing.

## Project Requirements

### Software requirements

| Requirement | Version | Notes |
|---|---|---|
| **Python** | **3.10 or newer** (developed and tested with 3.11) | Uses `X \| None` type syntax and built-in generics. |
| **Tkinter** | Bundled with Python | On Linux install `python3-tk`. Python from python.org includes it on Windows/macOS. |
| **NumPy** | `>= 1.24` | Numerical arrays and linear algebra. |
| **ReportLab** | `>= 4.0` | PDF generation. |
| **DejaVu Sans fonts** | Included in `src/pdf/fuentes` | Unicode symbols in PDF (`←`, `≠`, `∞`, `⁻¹`, `₁`, …). Falls back to Helvetica with symbol replacement if missing. |

Python dependencies are listed in `requirements.txt`:

```
numpy>=1.24
reportlab>=4.0
```

### Hardware / environment requirements

- Any computer able to run Python 3.10+ with a graphical desktop (Windows, macOS or Linux).
- Minimum window size: **1000 × 680**; default **1240 × 820** (centered on start).
- A desktop environment is required (Tkinter is a GUI toolkit); it will not run on a headless server.

### Functional requirements

1. Solve linear systems `A·x = b` by **Gauss-Jordan**, showing every step.
2. Solve linear systems using the **inverse matrix** (`x = A⁻¹·b`).
3. Classify systems as unique / infinite / inconsistent and report free variables.
4. Multiply or divide a matrix by a scalar.
5. Multiply two matrices with dimension compatibility checks.
6. Determine whether a vector is a **linear combination** of given vectors.
7. Determine **linear dependence / independence** of a set of vectors.
8. Accept integers, decimals (`.` or `,`) and fractions as input.
9. Generate random matrices and vectors within user-defined ranges.
10. Export any procedure to **PDF** and copy it as text.
11. Validate all inputs with clear messages (in Spanish).

### Non-functional requirements

- **Correctness** — results are tested against NumPy for random systems up to 15×15.
- **Separation of concerns** — math core has no GUI or PDF dependencies.
- **Single source of truth** — one report model drives both screen and PDF.
- **Configurable limits** — all size/value limits live in `src/config.py`.
- **Robustness** — numerical tolerance scaled to the matrix magnitude (`1e-10 · max(1, max|M|)`); inputs such as `nan`, `inf`, `1/0` or out-of-range values are rejected.

## Installation

```bash
# 1. Get the project
git clone <repository-url>
cd Algebra-lineal

# 2. (Optional) create a virtual environment
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate

# 3. Install dependencies
python -m pip install -r requirements.txt
```

On Debian/Ubuntu, if Tkinter is missing:

```bash
sudo apt install python3-tk
```

## Usage

```bash
python main.py
```

### Solving a system

1. In **Systems and Matrices**, set the number of equations (rows) and unknowns (columns) and click **Apply size**.
2. Fill in the coefficient matrix `A` and the constants column `b`.
3. Click **Gauss-Jordan** or **Inverse matrix (x = A⁻¹·b)**.
4. Read the procedure in the right panel. Click **Export PDF** or **Copy text** if needed.

### Matrix operations

- **Multiply / divide by scalar…** — choose `A × k` or `A ÷ k` and the value of `k`.
- **Multiply by matrix B…** — define B (rows are fixed to the columns of A), fill it (or generate it randomly) and multiply. Optionally use `A·B` as the new A.

### Linear combination

1. In **Linear Combination**, set the number of base vectors and their dimension, then **Apply size**.
2. Enter the base vectors (one per row) and the target vector `v`.
3. Click **Analyze linear combination** to see whether `v` is a combination, the coefficients, and whether the vectors are dependent or independent.

## Guaranteed Limits

| Item | Limit |
|---|---|
| Matrix size | up to **15 × 15** |
| Base vectors | up to **15** |
| Vector dimension | up to **15** |
| Cell value | between **−1,000,000** and **1,000,000** |
| Random number range | between **−1,000** and **1,000** |
| Result replacing A | up to **10¹²** in absolute value |
| Displayed decimals | **4** |

All limits can be changed in `src/config.py`.

## Input Rules

- Accepted: integers (`3`), decimals (`2.5` or `2,5`), fractions (`1/3`), scientific notation (`1e3`). An empty cell is `0`.
- Rejected: `nan`, `inf`, division by zero (`1/0`), text, malformed signs (`--1`) and values beyond the limit.
- Size fields accept digits only and respect their minimum and maximum.

## Cell Editing

| Action | Effect |
|---|---|
| Click | Select a cell |
| Drag / Shift + click | Select a range |
| Ctrl + click | Add a cell to the selection |
| Click on row header (`F#`) / column header (`x#`) | Select the whole row / column |
| Ctrl + A / **Select all** | Select every cell |
| Arrow keys | Move between cells |
| `Del` / **Clear selected cells** | Set only the selected cells to 0 |
| **Reset all** | Clear everything and return to the initial state |

## PDF Export

Every result can be saved as a formal PDF (Letter size) that contains:

- University, faculty, course, program name and authors.
- Numbered sections and subsections with the full procedure.
- Matrices drawn with brackets, an augmented-matrix separator and highlighted pivots.
- Tables (e.g., verification of `A·x = b`).
- Colored boxes: success (green), error (red), information (blue), warning (orange).
- Automatically suggested file name: `<title>_<subtitle>_YYYYMMDD_HHMM.pdf`.

## Project Structure

```
Algebra-lineal/
├── main.py                         Entry point (checks dependencies)
├── requirements.txt                Python dependencies
├── README.md / README.es.md        Documentation (EN / ES)
├── src/
│   ├── config.py                   Limits and PDF data (university, authors)
│   ├── nucleo/                     Math core — no GUI
│   │   ├── eliminacion.py          Step-by-step Gauss-Jordan engine
│   │   ├── gauss_jordan.py         Solve A·x = b by Gauss-Jordan
│   │   ├── inversa.py              Inverse and solve by x = A⁻¹·b
│   │   ├── multiplicacion.py       A·B and scalar multiply/divide
│   │   ├── combinacion_lineal.py   Linear combination / dependence
│   │   ├── reporte.py              Report model (screen + PDF)
│   │   ├── resultado.py            Common result type
│   │   ├── validacion.py           Input parsing and validation
│   │   └── formato.py              Number and equation formatting
│   ├── pdf/
│   │   ├── exportador.py           Report → PDF (ReportLab)
│   │   ├── fuentes.py              Unicode font registration
│   │   └── fuentes/                DejaVu Sans fonts (4 variants)
│   └── ui/                         Tkinter interface
│       ├── app.py                  Main window
│       ├── panel_sistemas.py       Tab 1: systems and matrices
│       ├── panel_combinacion.py    Tab 2: linear combination
│       ├── componentes.py          MatrixGrid, report viewer, helpers
│       ├── dialogos.py             Modal dialogs (random, scalar, multiply)
│       └── tema.py                 Theme and styles
└── tests/
    └── test_nucleo.py              Unit tests
```

## Architecture

The project is split in three independent layers:

1. **Core (`nucleo`)** — pure math. Each algorithm returns a `Resultado` containing a `Reporte` (the procedure), a status (`unica`, `infinita`, `inconsistente`, `error`, `ok`), and the numerical result (`solucion` or `matriz`). It knows nothing about Tkinter or ReportLab.
2. **Report model (`reporte`)** — a list of typed blocks: `Titulo`, `Parrafo`, `Ecuacion`, `Lista`, `Matriz`, `Tabla`, `Caja`. It can be rendered as styled text on screen, as plain text (clipboard) or as PDF.
3. **Presentation (`ui`, `pdf`)** — Tkinter widgets display the report; the exporter converts the same report into a PDF.

Gauss-Jordan elimination is implemented once (`eliminacion.py`) and shared by the system solver, the inverse and the linear-combination analysis.

## Configuration

Edit `src/config.py` to change:

- `MAX_FILAS`, `MAX_COLUMNAS`, `MAX_VECTORES`, `MAX_DIMENSION` — size limits.
- `VALOR_MAX`, `ALEATORIO_MAX`, `RESULTADO_MAX` — value limits.
- `DECIMALES` — displayed decimals.
- `UNIVERSIDAD`, `FACULTAD`, `ASIGNATURA`, `PROGRAMA`, `INTEGRANTES` — data printed on the PDF.

Spinners, warnings and validations update automatically.

## Testing

```bash
python -m unittest discover -s tests -v
```

The tests cover:

- Random systems (2×2 up to 15×15) solved by Gauss-Jordan and by inverse, compared against `numpy.linalg.solve`.
- Special cases: inconsistent, infinite-solution, singular and non-square matrices.
- Matrix and scalar multiplication, including dimension and zero-division errors.
- Linear combination (unique, inconsistent, infinite).
- Input validation (`1/4`, `2,5`, and rejection of `nan`, `inf`, `1/0`, `abc`, `1e99`, `--1`).
- PDF generation for every kind of report (valid `%PDF-` output).

## Author
- Christopher Josué Villón Peralta

Universidad Central del Ecuador · Faculty of Engineering and Applied Sciences · Linear Algebra
