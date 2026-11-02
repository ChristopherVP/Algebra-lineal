# 🧮 Linear Algebra Calculator

**A step-by-step linear algebra calculator for solving systems, inverting matrices and analyzing linear combinations — with every procedure exportable to a formal PDF.**

The Linear Algebra Calculator is a desktop application (Python + Tkinter) created for a **Linear Algebra** course at the Universidad Central del Ecuador. Instead of giving only a final answer, it **documents the whole procedure** — row operations, pivots, consistency analysis, substitutions and verification — so a student can follow the method, compare it with their own work and hand in a clean report. The same procedure is shown on screen and exported to **PDF**, so both always match.

> All results are computed with floating-point arithmetic and displayed with up to **4 decimals**; sizes up to **15 × 15** are guaranteed.

---

## Table of Contents

1. [Features at a Glance](#-features-at-a-glance)
2. [Project Requirements](#-project-requirements)
3. [Installation](#-installation)
4. [Running the Application](#-running-the-application)
5. [How to Use It (Step by Step)](#-how-to-use-it-step-by-step)
6. [Worked Example](#-worked-example)
7. [The Mathematics Behind It](#-the-mathematics-behind-it)
8. [Guaranteed Limits and Input Rules](#-guaranteed-limits-and-input-rules)
9. [Cell Editing and Shortcuts](#-cell-editing-and-shortcuts)
10. [PDF Export](#-pdf-export)
11. [Project Structure](#-project-structure)
12. [Architecture and Design Notes](#-architecture-and-design-notes)
13. [Configuration](#-configuration)
14. [Testing](#-testing)
15. [Assumptions and Limitations](#-assumptions-and-limitations)
16. [Troubleshooting](#-troubleshooting)
17. [Author and Context](#-author-and-context)

---

## ✨ Features at a Glance

- **Gauss-Jordan elimination, step by step** — shows the matrix after every elementary row operation (`F2 ← F2 + 3·F1`, `F1 ↔ F3`) for systems up to 6 rows, and after each pivot for larger ones.
- **Complete classification of a system** — unique solution, infinitely many solutions (with free variables and parametric solution) or inconsistent, with a **Rouché-Frobenius** rank analysis and an `A·x = b` verification table.
- **Inverse matrix method** — computes `A⁻¹` by applying Gauss-Jordan to `[A | I]` and solves `x = A⁻¹·b`; detects non-square and singular matrices.
- **Matrix operations** — product `A · B` with dimension checks, and multiplication / division by a scalar.
- **Linear combination analysis** — decides whether a vector `v` is a linear combination of a set of vectors, gives the coefficients and verifies the result.
- **Linear dependence / independence** of the base vectors.
- **Random generators** for matrices and vectors, with optional **guaranteed linear combination**.
- **Flexible input** — integers, decimals (`2.5` or `2,5`), fractions (`1/3`) and scientific notation in every cell.
- **Formal PDF export** with university header, bracketed matrices, highlighted pivots and colored result boxes — plus **copy as text**.
- **Comfortable matrix editor** — range selection, row/column selection, keyboard navigation, selective clearing and live validation.
- **Startup dependency check** that prints the exact `pip install` command if something is missing.

---

## 📋 Project Requirements

### Functional requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Solve `A·x = b` by **Gauss-Jordan**, showing every elementary row operation. |
| FR-02 | Solve `A·x = b` by the **inverse matrix** (`x = A⁻¹·b`), computing `A⁻¹` on `[A \| I]`. |
| FR-03 | Classify every system as unique / infinite / inconsistent, reporting rank, free variables and the parametric solution. |
| FR-04 | Reject the inverse method for non-square or singular matrices with an explanatory message. |
| FR-05 | Multiply or divide a matrix by a scalar (division by zero rejected). |
| FR-06 | Multiply two matrices `A · B`, checking dimension compatibility. |
| FR-07 | Allow the result of an operation (`A·B`, scalar result) to replace the current matrix `A`. |
| FR-08 | Determine whether a vector is a **linear combination** of given vectors and return the coefficients. |
| FR-09 | Determine **linear dependence / independence** of a set of vectors. |
| FR-10 | Accept integers, decimals (`.` or `,`), fractions and scientific notation; an empty cell is `0`. |
| FR-11 | Generate random matrices and vectors in a user-defined range (integers or 2 decimals). |
| FR-12 | Export every procedure to **PDF** and copy it as plain text. |
| FR-13 | Validate every input and explain errors clearly (invalid cells marked in red). |
| FR-14 | Provide a **Reset all** action (with confirmation) and selective clearing of cells. |

### Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | **Correctness**: results are tested against NumPy on random systems from 2×2 up to 15×15. |
| NFR-02 | **Separation of concerns**: the math core has no GUI or PDF dependencies. |
| NFR-03 | **Single source of truth**: one report model drives both the screen and the PDF. |
| NFR-04 | **Configurable limits**: all size and value limits live in `src/config.py`. |
| NFR-05 | **Numerical robustness**: tolerance scaled to the matrix magnitude (`1e-10 · max(1, max|M|)`); `nan`, `inf`, `1/0` and out-of-range values are rejected. |
| NFR-06 | **Offline desktop app**: no server, no internet, standard-library GUI toolkit (Tkinter). |
| NFR-07 | **Unicode-safe PDFs**: bundled DejaVu Sans fonts so symbols (`←`, `↔`, `≠`, `∞`, `⁻¹`, `₁`) print correctly. |
| NFR-08 | **Language**: interface, procedures and messages are in **Spanish**. |

### Software requirements

| Requirement | Details |
|-------------|---------|
| **Python** | **3.10 or newer** (developed and tested on CPython 3.11). Uses `X \| None` type syntax and built-in generics. |
| **Tkinter** | Bundled with the official Python installers for Windows/macOS. On Debian/Ubuntu: `sudo apt install python3-tk`. |
| **NumPy** | `>= 1.24` — numerical arrays and linear algebra. |
| **ReportLab** | `>= 4.0` — PDF generation. |
| **DejaVu Sans fonts** | Included in `src/pdf/fuentes/`. If missing, the PDF falls back to Helvetica and replaces symbols. |
| **OS** | Windows, macOS or Linux with a graphical desktop. |
| **Display** | Minimum window size 1000 × 680; default 1240 × 820 (centered on start). |

### Python dependencies (`requirements.txt`)

```text
numpy>=1.24
reportlab>=4.0
```

### Hardware / environment

- Any computer able to run Python 3.10+ with a graphical desktop session.
- Tkinter is a GUI toolkit: the app does **not** run on a headless server.

---

## 🔧 Installation

```bash
# 1. Get the project
git clone <repository-url>
cd Algebra-lineal

# 2. (Recommended) create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
python -m pip install -r requirements.txt
```

On Debian/Ubuntu, if Tkinter is missing:

```bash
sudo apt install python3-tk
```

---

## ▶️ Running the Application

```bash
python main.py
```

Run it from the project root. On startup `main.py` checks Tkinter, NumPy and ReportLab; if something is missing it shows a dialog (or prints a message) with the exact command to install it. The main window opens centered at 1240 × 820.

---

## 🧭 How to Use It (Step by Step)

### Tab 1 · Systems and Matrices

1. Set the number of **equations (rows)** and **unknowns (columns)** and click **Apply size**. Existing values that still fit are kept.
2. Fill in the coefficient matrix `A` and the constants column `b` (the last column). Fractions such as `1/3` are accepted.
3. Choose a method:
   - **Gauss-Jordan** — full elimination with classification of the system.
   - **Inverse matrix (x = A⁻¹·b)** — computes `A⁻¹` first, then the solution.
4. Read the procedure in the right panel. Use **Export PDF** or **Copy text** at the top of the panel.
5. Optional operations on `A`:
   - **Multiply / divide by scalar…** — pick `A × k` or `A ÷ k`.
   - **Multiply by matrix B…** — define B (rows fixed to the columns of A), fill or randomize it, multiply, and optionally keep `A·B` as the new `A`.
6. **Generate random…** fills the matrix with random integers or 2-decimal numbers in a range you choose.

### Tab 2 · Linear Combination

1. Set the number of **base vectors** and their **dimension**, then **Apply size**. *Each row of the table is one base vector.*
2. Enter the base vectors and the target vector `v`. The tab starts with a ready example.
3. Click **Analyze linear combination**. The report tells you whether `v` is a combination, gives the coefficients, verifies the result and finally states whether the base vectors are **linearly dependent or independent**.
4. **Generate random…** can optionally guarantee that `v` is a combination of the base vectors.

### Global actions

- **Reset all** (top right) clears both tabs after confirmation.
- **Clear selected cells** / `Del` sets only the selected cells to 0.

---

## 📝 Worked Example

Solve:

```text
 2x₁ +  x₂ −  x₃ =   8
−3x₁ −  x₂ + 2x₃ = −11
−2x₁ +  x₂ + 2x₃ =  −3
```

Enter `A = [[2, 1, −1], [−3, −1, 2], [−2, 1, 2]]` and `b = [8, −11, −3]`, then click **Gauss-Jordan**. The report contains:

1. **System setup** — original equations and augmented matrix `[A | b]`.
2. **Gauss-Jordan elimination** — for each pivot, every operation and the resulting matrix, for example:

```text
Step 1: pivot in column 1
F1 ← F1 ÷ 2
F2 ← F2 + 3·F1
F3 ← F3 + 2·F1
```

3. **Reduced row echelon form** `[R | d]`:

```text
[  1   0   0  |   2 ]
[  0   1   0  |   3 ]
[  0   0   1  |  -1 ]
```

4. **Consistency analysis (Rouché-Frobenius)** — `rank(A)` vs. `rank([A|b])` vs. number of unknowns.
5. **Solution and verification table** — `x₁ = 2`, `x₂ = 3`, `x₃ = −1`, substituted into each equation.

The procedure text itself is written in Spanish.

---

## 📐 The Mathematics Behind It

### Gauss-Jordan elimination (`nucleo/eliminacion.py`)

The augmented matrix is reduced to **reduced row echelon form (RREF)** using three elementary operations: swap rows (`Fi ↔ Fj`), scale a row (`Fi ← Fi ÷ p`) and add a multiple of a row to another (`Fi ← Fi ± k·Fj`). For each column the engine looks for a pivot, swaps it into place if needed, normalizes it to 1 and clears the rest of the column. Values smaller than the tolerance are set to exactly 0 to avoid floating-point noise. The same engine serves the system solver, the inverse and the linear-combination analysis.

### Classification of a system

With `R` the RREF of `[A | b]`:

| Condition | Conclusion |
|-----------|------------|
| `rank(A) < rank([A \| b])` | **Inconsistent** — no solution (a row `0 = c`, `c ≠ 0`). |
| `rank(A) = rank([A \| b]) = n` | **Unique solution**. |
| `rank(A) = rank([A \| b]) < n` | **Infinitely many solutions**; `n − rank(A)` free variables and a parametric solution. |

### Inverse matrix

Gauss-Jordan is applied to `[A | I]`. If `A` reduces to `I`, the right block is `A⁻¹` and `x = A⁻¹·b`. If `A` is not square, or a pivot is missing (singular), the app explains why the inverse does not exist.

### Matrix operations

- **Product:** `(A·B)ᵢⱼ = Σₖ aᵢₖ·bₖⱼ`; requires `columns(A) = rows(B)`, and the procedure shows each entry.
- **Scalar:** `k·A` or `A ÷ k` entry by entry (`k ≠ 0` for division).

### Linear combination and dependence

`v` is a linear combination of `v₁, …, vₖ` if the system `c₁v₁ + … + cₖvₖ = v` has a solution. The vectors are placed as the columns of a coefficient matrix and the system is solved with Gauss-Jordan. The base vectors are **linearly independent** if the homogeneous system `c₁v₁ + … + cₖvₖ = 0` has only the trivial solution (rank = number of vectors), and **dependent** otherwise.

---

## 📏 Guaranteed Limits and Input Rules

| Item | Limit |
|---|---|
| Matrix size | up to **15 × 15** |
| Base vectors | up to **15** |
| Vector dimension | up to **15** |
| Cell value | between **−1,000,000** and **1,000,000** |
| Random number range | between **−1,000** and **1,000** |
| Result replacing `A` | up to **10¹²** in absolute value |
| Displayed decimals | **4** |

**Accepted input:** integers (`3`), decimals (`2.5` or `2,5`), fractions (`1/3`), scientific notation (`1e3`). An empty cell is `0`.
**Rejected input:** `nan`, `inf`, division by zero (`1/0`), text, malformed signs (`--1`) and values beyond the limits.
Size fields accept digits only and respect their minimum and maximum. All limits can be changed in `src/config.py`.

---

## ⌨️ Cell Editing and Shortcuts

| Action | Effect |
|---|---|
| Click | Select a cell |
| Drag / Shift + click | Select a range |
| Ctrl + click | Add a cell to the selection |
| Click on row header (`F#`) / column header (`x#`) | Select the whole row / column |
| Ctrl + A / **Select all** | Select every cell |
| Arrow keys | Move between cells |
| Mouse wheel (Shift + wheel) | Scroll vertically (horizontally) |
| `Del` / **Clear selected cells** | Set only the selected cells to 0 |
| **Reset all** | Clear everything and return to the initial state |

Invalid cells are highlighted in red and the error message names the offending cell.

---

## 📄 PDF Export

Every result can be saved as a formal **Letter-size** PDF containing:

- University, faculty, course, program name and authors.
- Numbered sections and subsections with the full procedure.
- Matrices drawn with brackets, an augmented-matrix separator and highlighted pivots.
- Tables (e.g., verification of `A·x = b`).
- Colored boxes: success (green), error (red), information (blue), warning (orange).
- Page footers (“Página n de total”) and PDF metadata (title, author).
- A suggested file name: `<title>_<subtitle>_YYYYMMDD_HHMM.pdf`.

After saving, the app offers to open the file. The **Copy text** button copies the same procedure as plain text.

---

## 🧱 Project Structure

```text
Algebra-lineal/
├── main.py                         # Entry point (checks dependencies)
├── requirements.txt                # numpy, reportlab
├── README.md / README.es.md        # Documentation (EN / ES)
├── src/
│   ├── config.py                   # Limits and PDF data (university, authors)
│   ├── nucleo/                     # Math core — no GUI
│   │   ├── eliminacion.py          # Step-by-step Gauss-Jordan engine
│   │   ├── gauss_jordan.py         # Solve A·x = b by Gauss-Jordan
│   │   ├── inversa.py              # Inverse and solve by x = A⁻¹·b
│   │   ├── multiplicacion.py       # A·B and scalar multiply/divide
│   │   ├── combinacion_lineal.py   # Linear combination / dependence
│   │   ├── reporte.py              # Report model (screen + PDF)
│   │   ├── resultado.py            # Common result type
│   │   ├── validacion.py           # Input parsing and validation
│   │   └── formato.py              # Number and equation formatting
│   ├── pdf/
│   │   ├── exportador.py           # Report → PDF (ReportLab)
│   │   ├── fuentes.py              # Unicode font registration
│   │   └── fuentes/                # DejaVu Sans fonts (4 variants)
│   └── ui/                         # Tkinter interface
│       ├── app.py                  # Main window
│       ├── panel_sistemas.py       # Tab 1: systems and matrices
│       ├── panel_combinacion.py    # Tab 2: linear combination
│       ├── componentes.py          # MatrixGrid, report viewer, helpers
│       ├── dialogos.py             # Modal dialogs (random, scalar, multiply)
│       └── tema.py                 # Theme and styles
└── tests/
    └── test_nucleo.py              # Unit tests
```

---

## 🏗 Architecture and Design Notes

```text
 user input ──► nucleo (math) ──► Resultado ──► Reporte ──┬──► Tkinter viewer
                                                          ├──► clipboard (text)
                                                          └──► PDF (ReportLab)
```

- **Core (`nucleo`)** — pure math. Each algorithm returns a `Resultado` holding a `Reporte` (the procedure), a status (`unica`, `infinita`, `inconsistente`, `error`, `ok`) and the numerical result (`solucion` or `matriz`). It knows nothing about Tkinter or ReportLab.
- **Report model (`reporte`)** — a list of typed blocks (`Titulo`, `Parrafo`, `Ecuacion`, `Lista`, `Matriz`, `Tabla`, `Caja`) rendered as styled on-screen text, plain text or PDF, so all outputs always match.
- **Presentation (`ui`, `pdf`)** — Tkinter widgets display the report; the exporter converts the same report into a PDF.
- **Shared elimination engine** — Gauss-Jordan is written once (`eliminacion.py`) and reused by the system solver, the inverse and the linear-combination analysis.
- **Centralized configuration** — `config.py` feeds the spinners, warnings and validations, so changing a limit updates the whole program.
- **Single-window dialogs** — each task uses one modal dialog with inline error messages instead of chained pop-ups.

---

## ⚙️ Configuration

Edit `src/config.py` to change:

- `MAX_FILAS`, `MAX_COLUMNAS`, `MAX_VECTORES`, `MAX_DIMENSION` — size limits.
- `VALOR_MAX`, `ALEATORIO_MAX`, `RESULTADO_MAX` — value limits.
- `DECIMALES` — displayed decimals.
- `UNIVERSIDAD`, `FACULTAD`, `ASIGNATURA`, `PROGRAMA`, `INTEGRANTES` — data printed on the PDF.

---

## 🧪 Testing

```bash
python -m unittest discover -s tests -v
```

| Test | What it checks |
|------|----------------|
| `test_aleatorios_contra_numpy` | Random systems (2×2, 5×5, 10×10, 15×15) solved by Gauss-Jordan **and** by inverse match `numpy.linalg.solve`. |
| `test_casos_especiales` | Inconsistent, infinite-solution, singular and non-square cases. |
| `test_multiplicacion_y_escalar` | `A·B` against NumPy, dimension mismatch and division by zero errors. |
| `test_combinacion` | Linear combination: unique, inconsistent and infinite cases. |
| `test_validacion` | Parsing of `1/4` and `2,5`; rejection of `nan`, `inf`, `1/0`, `abc`, `1e99`, `--1`. |
| `test_pdf_todos` | A valid `%PDF-` file is produced for every kind of report, including 15×15 cases. |

---

## ⚠️ Assumptions and Limitations

This is an **educational tool**.

- It works with **floating-point arithmetic**, not exact rational arithmetic; results are shown with up to 4 decimals and tiny values are cleaned using a tolerance. Ill-conditioned matrices may show rounding effects.
- Sizes are guaranteed up to **15 × 15**; larger sizes are not offered by the interface.
- Determinants, eigenvalues, LU/QR decompositions and other topics are **not** included.
- The interface, the procedures and the PDF text are in **Spanish**.
- Requires a graphical desktop; there is no command-line or web version.

---

## 🛠 Troubleshooting

| Problem | Solution |
|---------|----------|
| “Este Python no incluye Tkinter” on startup | Install Python from python.org, or on Linux `sudo apt install python3-tk`. |
| “Faltan librerías” dialog | Run the `pip install` command shown in the dialog, or `python -m pip install -r requirements.txt`. |
| `ModuleNotFoundError: src` | Run the app from the project root: `python main.py`. |
| PDF shows `<-`, `!=` or `inf` instead of symbols | The bundled DejaVu fonts were not found; check that `src/pdf/fuentes/` is intact. |
| Cell turns red | The value is invalid (text, `nan`, `1/0`, or beyond ±1,000,000); correct it and try again. |
| “No se pudo exportar el PDF” | The target file is open in another program or the folder is read-only; close it or choose another location. |

---

## 👤 Author and Context

- **Author:** Christopher Josué Villón Peralta
- **Context:** university project for the **Linear Algebra** course — Universidad Central del Ecuador, Faculty of Engineering and Applied Sciences.
- **License:** *not specified yet* — add a `LICENSE` file (e.g., MIT) if you want others to reuse the code.

---

*This software is for educational purposes.*
