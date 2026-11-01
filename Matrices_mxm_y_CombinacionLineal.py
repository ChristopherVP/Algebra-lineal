#Integrantes:Gabriela Chacón, Marlon Cruz, Miryam Miranda, Atik Tontaquimba, Christopher Villón
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import numpy as np
import re
import traceback
import random
import json

# IMPORTS PARA LA FUNCIONALIDAD PDF
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.colors import black
    from reportlab.lib.units import inch
    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False

def format_number(num, decimals=4):
    """Formatea números evitando notación científica y limitando decimales."""
    if abs(num) > 1e6 or (abs(num) < 1e-4 and num != 0):
        # Para números muy grandes o muy pequeños, usar notación científica más legible
        return f"{num:.{decimals}g}"
    else:
        # Para números normales, formato decimal fijo
        formatted = f"{num:.{decimals}f}".rstrip('0').rstrip('.')
        return formatted if formatted else "0"

def format_matrix_display(matrix):
    """Formatea una matriz para mostrar sin notación científica."""
    if matrix.ndim == 1:
        return "[" + ", ".join([format_number(x, 3) for x in matrix]) + "]"
    else:
        rows = []
        for row in matrix:
            formatted_row = "[" + ", ".join([f"{format_number(x, 3):>8}" for x in row]) + "]"
            rows.append(formatted_row)
        return "\n".join(rows)

class CollapsiblePane(ttk.Frame):
    def __init__(self, parent, text="", style_prefix=""):
        super().__init__(parent, padding=5)
        self.columnconfigure(0, weight=1)
        self.text = text
        style = ttk.Style()
        style.configure(f"{style_prefix}.TButton", font=('Helvetica', 10, 'bold'))
        self._button = ttk.Button(self, text=f"+ {self.text}", command=self.toggle, style=f"{style_prefix}.TButton")
        self._button.grid(row=0, column=0, sticky='ew')
        self.frame = ttk.Frame(self)
        self.frame.grid(row=1, column=0, sticky='ew')
        self.frame.grid_remove() 
        self._is_collapsed = True
    
    def toggle(self):
        if self._is_collapsed:
            self.frame.grid()
            self._button.configure(text=f"- {self.text}")
            self._is_collapsed = False
        else:
            self.frame.grid_remove()
            self._button.configure(text=f"+ {self.text}")
            self._is_collapsed = True

class SistemaEcuaciones:
    def __init__(self):
        self.A = None
        self.b = None
        self.variables = []
        self.solucion = None
        self.procedimiento = []
    
    def configurar_dimensiones(self, n_vars, m_eqs):
        if not (n_vars > 0 and m_eqs > 0): 
            raise ValueError("Las dimensiones deben ser números enteros positivos.")
        self.variables = [f'x{i+1}' for i in range(n_vars)]
        self.A = np.zeros((m_eqs, n_vars))
        self.b = np.zeros(m_eqs)
    
    def generar_matriz_aleatoria(self, n_vars, m_eqs, min_val, max_val):
        self.configurar_dimensiones(n_vars, m_eqs)
        self.A = np.random.uniform(min_val, max_val, size=(m_eqs, n_vars))
        self.b = np.random.uniform(min_val, max_val, size=m_eqs)
        self.A = np.round(self.A, 2)
        self.b = np.round(self.b, 2)
    
    def resolver_gauss_jordan(self):
        if self.A is None or self.b is None: 
            raise ValueError("El sistema no ha sido inicializado.")
        
        self.procedimiento = []
        A_aug = np.column_stack([self.A.astype(np.float64), self.b.astype(np.float64)])
        m, n = A_aug.shape  # m = filas (ecuaciones), n = columnas (incluyendo b)
        num_vars = n - 1    # número de variables (columnas sin contar b)
        
        self.procedimiento.append("--- MATRIZ AUMENTADA INICIAL ---")
        self.procedimiento.append(f"Sistema: {m} ecuaciones con {num_vars} incógnitas")
        self.procedimiento.append(format_matrix_display(A_aug))
        
        # Fase de eliminación hacia adelante
        pivote_col = 0
        filas_con_pivote = []
        
        for fila_actual in range(m):
            if pivote_col >= num_vars:
                break
                
            # Buscar un pivote no cero en la columna actual
            fila_pivote = None
            for i in range(fila_actual, m):
                if not np.isclose(A_aug[i, pivote_col], 0, atol=1e-12):
                    fila_pivote = i
                    break
            
            if fila_pivote is None:
                # No hay pivote en esta columna, pasar a la siguiente
                self.procedimiento.append(f"\n--- No hay pivote válido en columna {pivote_col+1}, saltando ---")
                pivote_col += 1
                continue
            
            # Intercambiar filas si es necesario
            if fila_pivote != fila_actual:
                A_aug[[fila_actual, fila_pivote]] = A_aug[[fila_pivote, fila_actual]]
                self.procedimiento.append(f"\n--- INTERCAMBIO F{fila_actual+1} <-> F{fila_pivote+1} ---")
                self.procedimiento.append(format_matrix_display(A_aug))
            
            # Normalizar la fila del pivote
            factor_pivote = A_aug[fila_actual, pivote_col]
            if not np.isclose(factor_pivote, 1, atol=1e-12):
                A_aug[fila_actual] = A_aug[fila_actual] / factor_pivote
                self.procedimiento.append(f"\n--- F{fila_actual+1} = F{fila_actual+1} / {format_number(factor_pivote, 4)} ---")
                self.procedimiento.append(format_matrix_display(A_aug))
            
            # Eliminar elementos arriba y abajo del pivote
            for i in range(m):
                if i != fila_actual:
                    factor = A_aug[i, pivote_col]
                    if not np.isclose(factor, 0, atol=1e-12):
                        A_aug[i] = A_aug[i] - factor * A_aug[fila_actual]
                        self.procedimiento.append(f"\n--- F{i+1} = F{i+1} - ({format_number(factor, 4)}) * F{fila_actual+1} ---")
                        self.procedimiento.append(format_matrix_display(A_aug))
            
            filas_con_pivote.append((fila_actual, pivote_col))
            pivote_col += 1
        
        # Verificar inconsistencias
        self.procedimiento.append("\n--- ANÁLISIS DE CONSISTENCIA ---")
        inconsistente = False
        
        for i in range(m):
            fila_ceros = np.all(np.isclose(A_aug[i, :-1], 0, atol=1e-12))
            if fila_ceros and not np.isclose(A_aug[i, -1], 0, atol=1e-12):
                self.procedimiento.append(f"Fila {i+1}: 0 = {format_number(A_aug[i, -1], 4)} (INCONSISTENCIA)")
                inconsistente = True
        
        if inconsistente:
            self.procedimiento.append("\n✗ SISTEMA INCONSISTENTE: No tiene solución")
            raise np.linalg.LinAlgError("El sistema no tiene solución (es inconsistente).")
        
        # Analizar el tipo de solución
        rango_A = len(filas_con_pivote)  # número de filas con pivotes
        self.procedimiento.append(f"\nRango de la matriz de coeficientes: {rango_A}")
        self.procedimiento.append(f"Número de variables: {num_vars}")
        
        self.procedimiento.append("\n--- MATRIZ ESCALONADA REDUCIDA FINAL ---")
        self.procedimiento.append(format_matrix_display(A_aug))
        
        if rango_A == num_vars:
            # Solución única
            self.procedimiento.append("\n✓ SOLUCIÓN ÚNICA")
            self.solucion = np.zeros(num_vars)
            
            for fila, col in filas_con_pivote:
                self.solucion[col] = A_aug[fila, -1]
                
            self.procedimiento.append("\n--- EXTRACCIÓN DE LA SOLUCIÓN ---")
            for i, valor in enumerate(self.solucion):
                self.procedimiento.append(f"x{i+1} = {format_number(valor, 4)}")
                
        elif rango_A < num_vars:
            # Infinitas soluciones
            self.procedimiento.append("\n∞ INFINITAS SOLUCIONES")
            variables_libres = num_vars - rango_A
            self.procedimiento.append(f"Variables libres: {variables_libres}")
            
            # Identificar variables básicas y libres
            variables_basicas = set(col for _, col in filas_con_pivote)
            variables_libres_indices = [i for i in range(num_vars) if i not in variables_basicas]
            
            self.procedimiento.append(f"\nVariables básicas: {[f'x{i+1}' for i in sorted(variables_basicas)]}")
            self.procedimiento.append(f"Variables libres: {[f'x{i+1}' for i in variables_libres_indices]}")
            
            # Expresar variables básicas en términos de las libres
            self.procedimiento.append("\n--- SOLUCIÓN PARAMÉTRICA ---")
            
            for fila, col_pivote in filas_con_pivote:
                terminos = []
                termino_independiente = A_aug[fila, -1]
                
                ecuacion = f"x{col_pivote+1} = {format_number(termino_independiente, 4)}"
                
                for j in variables_libres_indices:
                    coef = -A_aug[fila, j]  # Negativo porque pasamos al otro lado
                    if not np.isclose(coef, 0, atol=1e-12):
                        if coef > 0:
                            ecuacion += f" + {format_number(coef, 4)}*x{j+1}"
                        else:
                            ecuacion += f" - {format_number(abs(coef), 4)}*x{j+1}"
                
                self.procedimiento.append(ecuacion)
            
            for i in variables_libres_indices:
                self.procedimiento.append(f"x{i+1} = x{i+1} (variable libre)")
            
            # Para compatibilidad, crear una solución particular (variables libres = 0)
            self.solucion = np.zeros(num_vars)
            for fila, col in filas_con_pivote:
                self.solucion[col] = A_aug[fila, -1]
                
            self.procedimiento.append(f"\n--- SOLUCIÓN PARTICULAR (variables libres = 0) ---")
            for i, valor in enumerate(self.solucion):
                self.procedimiento.append(f"x{i+1} = {format_number(valor, 4)}")
        
        # Verificación de la solución
        if hasattr(self, 'solucion') and self.solucion is not None:
            self.procedimiento.append("\n--- VERIFICACIÓN DE UNA SOLUCIÓN ---")
            self.procedimiento.append("Sustituyendo en las ecuaciones originales:")
            
            for i in range(min(self.A.shape[0], len(self.solucion))):
                resultado_ecuacion = 0
                terminos = []
                for j in range(min(self.A.shape[1], len(self.solucion))):
                    producto = self.A[i, j] * self.solucion[j]
                    resultado_ecuacion += producto
                    if not np.isclose(self.A[i, j], 0, atol=1e-12):
                        terminos.append(f"({format_number(self.A[i, j], 3)})×({format_number(self.solucion[j], 3)})")
                
                if terminos:
                    ecuacion_str = " + ".join(terminos).replace("+ -", "- ")
                    self.procedimiento.append(f"Ecuación {i+1}: {ecuacion_str} = {format_number(resultado_ecuacion, 3)}")
                else:
                    self.procedimiento.append(f"Ecuación {i+1}: 0 = {format_number(resultado_ecuacion, 3)}")
                    
                self.procedimiento.append(f"  Valor esperado b[{i+1}] = {format_number(self.b[i], 3)}")
                
                if np.isclose(resultado_ecuacion, self.b[i], atol=1e-10):
                    self.procedimiento.append(f"  ✓ Verificación correcta")
                else:
                    self.procedimiento.append(f"  ✗ Error en verificación")
        
        return "\n".join(self.procedimiento), self.solucion
    
    def generar_procedimiento_multiplicacion(self, matriz_a, matriz_b):
        """
        Genera una cadena de texto explicando el cálculo de la multiplicación de dos matrices.
        """
        procedimiento = ["\n--- PROCEDIMIENTO DE MULTIPLICACIÓN (A * B) ---"]
        m_a, n_a = matriz_a.shape
        m_b, n_b = matriz_b.shape
        
        # Iterar sobre cada celda de la matriz resultante
        for i in range(m_a):  # Filas de A
            for j in range(n_b):  # Columnas de B
                # Fila i de A y Columna j de B
                fila_a = matriz_a[i, :]
                col_b = matriz_b[:, j]
                
                # Construir la cadena de la operación
                terminos = [f"({format_number(fila_a[k], 2)} * {format_number(col_b[k], 2)})" for k in range(n_a)]
                calculo_str = " + ".join(terminos)
                
                # Calcular el resultado del elemento
                resultado_elemento = np.dot(fila_a, col_b)
                
                procedimiento.append(f"Elemento C({i+1},{j+1}) = {calculo_str} = {format_number(resultado_elemento, 4)}")
        
        procedimiento.append("\nDonde C es la nueva Matriz A.")
        return "\n".join(procedimiento)

    def analizar_dependencia_independencia(self, vectores_base):
        """
        Analiza si un conjunto de vectores es linealmente dependiente o independiente.
        Retorna información detallada sobre el análisis.
        """
        procedimiento = []
        
        # Convertir a numpy array si no lo es
        if not isinstance(vectores_base, np.ndarray):
            vectores_base = np.array(vectores_base)
        
        if vectores_base.ndim == 1:
            vectores_base = vectores_base.reshape(1, -1)
        
        num_vectores, dimension = vectores_base.shape
        
        procedimiento.append("=== ANÁLISIS DE DEPENDENCIA/INDEPENDENCIA LINEAL ===")
        procedimiento.append(f"Conjunto de {num_vectores} vectores en R^{dimension}")
        procedimiento.append(f"Matriz de vectores B:")
        procedimiento.append(format_matrix_display(vectores_base))
        
        # Calcular el rango de la matriz
        rango = np.linalg.matrix_rank(vectores_base)
        procedimiento.append(f"\nRango de la matriz: {rango}")
        procedimiento.append(f"Número de vectores: {num_vectores}")
        procedimiento.append(f"Dimensión del espacio: {dimension}")
        
        # Determinar dependencia/independencia
        procedimiento.append("\n--- CRITERIOS DE ANÁLISIS ---")
        
        if rango == num_vectores:
            procedimiento.append("✓ VECTORES LINEALMENTE INDEPENDIENTES")
            procedimiento.append("  Razón: El rango es igual al número de vectores")
            if num_vectores <= dimension:
                procedimiento.append("  Los vectores no se pueden expresar como combinación lineal de los otros")
                if num_vectores == dimension:
                    procedimiento.append("  Además, forman una BASE para R^" + str(dimension))
                    procedimiento.append("  Cualquier vector en R^" + str(dimension) + " puede expresarse como combinación lineal de estos vectores")
            else:
                procedimiento.append("  NOTA: Hay más vectores que la dimensión del espacio")
                procedimiento.append("  Esto debería ser imposible para vectores independientes")
        else:
            procedimiento.append("✗ VECTORES LINEALMENTE DEPENDIENTES")
            procedimiento.append(f"  Razón: El rango ({rango}) es menor que el número de vectores ({num_vectores})")
            redundantes = num_vectores - rango
            procedimiento.append(f"  Hay {redundantes} vector(es) redundante(s)")
            procedimiento.append("  Al menos uno de los vectores puede expresarse como combinación lineal de los otros")
        
        # Análisis del determinante (solo para matrices cuadradas)
        if num_vectores == dimension:
            try:
                det = np.linalg.det(vectores_base)
                procedimiento.append(f"\n--- ANÁLISIS DEL DETERMINANTE ---")
                procedimiento.append(f"Determinante: {format_number(det, 6)}")
                if abs(det) < 1e-10:
                    procedimiento.append("✗ Determinante ≈ 0: Confirma dependencia lineal")
                    procedimiento.append("  La matriz es singular (no invertible)")
                else:
                    procedimiento.append("✓ Determinante ≠ 0: Confirma independencia lineal")
                    procedimiento.append("  La matriz es invertible")
                    procedimiento.append("  Los vectores forman una base para R^" + str(dimension))
            except np.linalg.LinAlgError:
                procedimiento.append("No se pudo calcular el determinante")
        
        # Encontrar relaciones de dependencia si existen
        if rango < num_vectores:
            procedimiento.append("\n--- BÚSQUEDA DE RELACIONES DE DEPENDENCIA ---")
            procedimiento.append("Resolviendo el sistema homogéneo B^T * c = 0:")
            
            # Transponer para que cada fila sea un vector
            B_T = vectores_base.T
            
            try:
                # Encontrar el espacio nulo (kernel)
                # Usamos SVD para encontrar vectores en el espacio nulo
                U, s, Vt = np.linalg.svd(B_T)
                
                # Los vectores en el espacio nulo corresponden a valores singulares muy pequeños
                tolerance = 1e-10
                null_space_dim = np.sum(s < tolerance)
                
                if null_space_dim > 0:
                    # Extraer vectores del espacio nulo
                    null_vectors = Vt[-null_space_dim:, :]
                    
                    procedimiento.append(f"Dimensión del espacio nulo: {null_space_dim}")
                    procedimiento.append("Vectores del espacio nulo (coeficientes de dependencia):")
                    
                    for i, null_vec in enumerate(null_vectors):
                        # Aquí se corrigió un error de sintaxis en el código original con end=""
                        relacion_str = f"Relación {i+1}: "
                        terminos = []
                        for j, coef in enumerate(null_vec):
                            if abs(coef) > tolerance:
                                if coef > 0 and terminos:
                                    terminos.append(f" + {format_number(coef, 4)}*v{j+1}")
                                else:
                                    terminos.append(f"{format_number(coef, 4)}*v{j+1}")
                        
                        if terminos:
                            ecuacion = "".join(terminos) + " = 0"
                            procedimiento.append(relacion_str + ecuacion)
                        
                        # Verificar la relación
                        verificacion = np.dot(vectores_base.T, null_vec)
                        procedimiento.append(f"  Verificación: ||B^T * c|| = {format_number(np.linalg.norm(verificacion), 6)}")
                
            except Exception as e:
                procedimiento.append(f"Error al calcular relaciones de dependencia: {e}")
        
        # Información sobre el espacio generado
        procedimiento.append(f"\n--- ESPACIO GENERADO ---")
        procedimiento.append(f"Los vectores generan un subespacio de dimensión {rango} en R^{dimension}")
        if rango == dimension:
            procedimiento.append(f"El subespacio generado ES TODO R^{dimension}")
        else:
            procedimiento.append(f"El subespacio generado es un subespacio PROPIO de R^{dimension}")
        # Recomendaciones
        if rango < num_vectores:
            procedimiento.append(f"\n--- RECOMENDACIONES ---")
            procedimiento.append(f"• Se pueden eliminar {num_vectores - rango} vector(es) para obtener un conjunto independiente")
            procedimiento.append("• Los primeros vectores linealmente independientes formarían una base del subespacio")
        
        if rango < dimension:
            procedimiento.append(f"• Se necesitan {dimension - rango} vector(es) adicional(es) independiente(s) para formar una base de R^{dimension}")
        
        return "\n".join(procedimiento), rango, num_vectores

    def analizar_combinacion_lineal(self, vectores_base_str, vector_obj_str):
        procedimiento = []
        try:
            vectores_base = np.array(json.loads(vectores_base_str.replace('\n', '')))
            vector_objetivo = np.array(json.loads(vector_obj_str))
            if vectores_base.ndim == 1: vectores_base = vectores_base.reshape(1, -1)
            if vectores_base.ndim != 2: raise ValueError("Los vectores base deben formar una matriz 2D.")
            if vector_objetivo.ndim != 1: raise ValueError("El vector objetivo debe ser un array 1D.")
            if vectores_base.shape[1] != len(vector_objetivo): raise ValueError("La dimensión de los vectores base no coincide con la del vector objetivo.")
        except Exception as e: raise SyntaxError(f"Error en el formato de entrada: {e}. Use listas de Python, ej: [[1,2],[3,4]] y [5,6].")
        
        # ANÁLISIS DE DEPENDENCIA/INDEPENDENCIA LINEAL
        analisis_dep, rango, num_vectores = self.analizar_dependencia_independencia(vectores_base)
        procedimiento.append(analisis_dep)
        
        procedimiento.append("\n" + "="*70)
        procedimiento.append("=== ANÁLISIS DE COMBINACIÓN LINEAL ===")
        procedimiento.append(f"Vectores base B:\n{format_matrix_display(vectores_base)}")
        procedimiento.append(f"Vector objetivo v: {format_matrix_display(vector_objetivo)}")
        
        # Mostrar la ecuación con escalares
        num_vectores = vectores_base.shape[0]
        dimension = vectores_base.shape[1]
        
        procedimiento.append("\n--- PLANTEAMIENTO DEL PROBLEMA ---")
        procedimiento.append("Se busca encontrar escalares c1, c2, c3, ... tales que:")
        
        # Mostrar la combinación lineal paso a paso
        ecuacion_str = ""
        for i in range(num_vectores):
            if i > 0:
                ecuacion_str += " + "
            # Convertir a lista simple de Python para evitar tipos numpy
            vector_simple = [float(x) for x in vectores_base[i]]
            ecuacion_str += f"c{i+1}*{vector_simple}"
        # Convertir vector objetivo también
        vector_obj_simple = [float(x) for x in vector_objetivo]
        ecuacion_str += f" = {vector_obj_simple}"
        procedimiento.append(ecuacion_str)
        
        # Expandir la multiplicación escalar por vector - CORREGIDO
        procedimiento.append("\n--- EXPANDIENDO LA MULTIPLICACIÓN ESCALAR POR VECTOR ---")
        for i in range(num_vectores):
            vector_expandido = []
            vector_simple = [float(x) for x in vectores_base[i]]  # Convertir a float simple
            for j in range(dimension):
                valor = vector_simple[j]
                if valor == 1:
                    vector_expandido.append(f"c{i+1}")
                elif valor == -1:
                    vector_expandido.append(f"-c{i+1}")
                elif valor == 0:
                    vector_expandido.append("0")
                elif valor == int(valor):  # Si es entero, mostrarlo como entero
                    vector_expandido.append(f"c{i+1}*{int(valor)}")
                else:
                    vector_expandido.append(f"c{i+1}*{format_number(valor, 3)}")
            procedimiento.append(f"c{i+1}*{vector_simple} = [{', '.join(vector_expandido)}]")
        
        # Mostrar la suma de vectores componente por componente
        procedimiento.append("\n--- SUMANDO COMPONENTE POR COMPONENTE ---")
        for j in range(dimension):
            suma_componentes = []
            for i in range(num_vectores):
                coef = float(vectores_base[i][j])  # Convertir a float simple
                if coef == 1:
                    suma_componentes.append(f"c{i+1}")
                elif coef == -1:
                    suma_componentes.append(f"-c{i+1}")
                elif coef == 0:
                    continue
                elif coef == int(coef):  # Si es entero, mostrarlo como entero
                    suma_componentes.append(f"{int(coef)}*c{i+1}")
                else:
                    suma_componentes.append(f"{format_number(coef, 3)}*c{i+1}")
            
            if suma_componentes:
                ecuacion_comp = " + ".join(suma_componentes).replace("+ -", "- ")
                procedimiento.append(f"Componente {j+1}: {ecuacion_comp} = {float(vector_objetivo[j])}")
            else:
                procedimiento.append(f"Componente {j+1}: 0 = {float(vector_objetivo[j])}")
        
        # Formar el sistema de ecuaciones matricial
        procedimiento.append("\n--- SISTEMA DE ECUACIONES LINEALES RESULTANTE ---")
        A = vectores_base.T  # Transponer para que cada columna sea un vector base
        b = vector_objetivo
        
        procedimiento.append("El sistema matricial es A*c = b, donde:")
        # Convertir a arrays simples de Python
        A_simple = [[float(A[i][j]) for j in range(A.shape[1])] for i in range(A.shape[0])]
        b_simple = [float(x) for x in b]
        procedimiento.append(f"A = {A_simple}")
        procedimiento.append(f"c = [c1, c2, c3, ...]^T")
        procedimiento.append(f"b = {b_simple}")
        
        # Análisis de la matriz aumentada para verificar consistencia
        A_aumentada = np.column_stack([A, b])
        rango_A = np.linalg.matrix_rank(A)
        rango_A_aumentada = np.linalg.matrix_rank(A_aumentada)
        
        procedimiento.append(f"\n--- ANÁLISIS DE CONSISTENCIA ---")
        procedimiento.append(f"Rango de A: {rango_A}")
        procedimiento.append(f"Rango de [A|b]: {rango_A_aumentada}")
        
        if rango_A != rango_A_aumentada:
            procedimiento.append("✗ SISTEMA INCONSISTENTE: rango(A) ≠ rango([A|b])")
            procedimiento.append("CONCLUSIÓN: El vector NO ES una combinación lineal de los vectores base.")
            procedimiento.append("El vector objetivo no pertenece al espacio generado por los vectores base.")
            return "\n".join(procedimiento)
        else:
            procedimiento.append("✓ SISTEMA CONSISTENTE: rango(A) = rango([A|b])")
            if rango_A == num_vectores:
                procedimiento.append("✓ SOLUCIÓN ÚNICA: El sistema tiene exactamente una solución.")
            else:
                procedimiento.append("∞ INFINITAS SOLUCIONES: El sistema tiene múltiples soluciones.")
                procedimiento.append(f"Grados de libertad: {num_vectores - rango_A}")
        
        try:
            A_num = A.astype(float)
            b_num = b.astype(float)
            
            # Aplicar Gauss-Jordan paso a paso
            procedimiento.append("\n--- RESOLVIENDO POR MÉTODO DE GAUSS-JORDAN ---")
            
            # Crear matriz aumentada
            A_aug = np.column_stack([A_num, b_num])
            m, n = A_aug.shape
            
            procedimiento.append("Matriz aumentada inicial [A|b]:")
            # Convertir matriz aumentada a formato simple
            matriz_aug_simple = [[float(A_aug[i][j]) for j in range(A_aug.shape[1])] for i in range(A_aug.shape[0])]
            for i, fila in enumerate(matriz_aug_simple):
                fila_str = "  [" + ", ".join([f"{format_number(x, 3):>8}" for x in fila]) + "]"
                procedimiento.append(fila_str)
            
            # Aplicar eliminación de Gauss-Jordan
            pivote = 0
            for i in range(m):
                if pivote >= n - 1:
                    break
                    
                # Buscar pivote no cero
                if np.isclose(A_aug[i, pivote], 0):
                    fila_pivote = i
                    for j in range(i + 1, m):
                        if not np.isclose(A_aug[j, pivote], 0):
                            fila_pivote = j
                            break
                            
                    if fila_pivote != i:
                        A_aug[[i, fila_pivote]] = A_aug[[fila_pivote, i]]
                        procedimiento.append(f"\nIntercambio F{i+1} <-> F{fila_pivote+1}:")
                        matriz_aug_simple = [[float(A_aug[i][j]) for j in range(A_aug.shape[1])] for i in range(A_aug.shape[0])]
                        for k, fila in enumerate(matriz_aug_simple):
                            fila_str = "  [" + ", ".join([f"{format_number(x, 3):>8}" for x in fila]) + "]"
                            procedimiento.append(fila_str)
                
                if np.isclose(A_aug[i, pivote], 0):
                    procedimiento.append(f"\nNo hay pivote válido en columna {pivote+1}, continuando...")
                    pivote += 1
                    continue
                
                # Normalizar fila del pivote
                factor = float(A_aug[i, pivote])  # Convertir a float simple
                if not np.isclose(factor, 1):
                    A_aug[i] = A_aug[i] / factor
                    procedimiento.append(f"\nF{i+1} = F{i+1} / {format_number(factor, 3)}:")
                    matriz_aug_simple = [[float(A_aug[i][j]) for j in range(A_aug.shape[1])] for i in range(A_aug.shape[0])]
                    for k, fila in enumerate(matriz_aug_simple):
                        fila_str = "  [" + ", ".join([f"{format_number(x, 3):>8}" for x in fila]) + "]"
                        procedimiento.append(fila_str)
                
                # Eliminar otras filas
                for j in range(m):
                    if i != j and not np.isclose(A_aug[j, pivote], 0):
                        factor = float(A_aug[j, pivote])  # Convertir a float simple
                        A_aug[j] = A_aug[j] - factor * A_aug[i]
                        procedimiento.append(f"\nF{j+1} = F{j+1} - ({format_number(factor, 3)}) * F{i+1}:")
                        matriz_aug_simple = [[float(A_aug[i][j]) for j in range(A_aug.shape[1])] for i in range(A_aug.shape[0])]
                        for k, fila in enumerate(matriz_aug_simple):
                            fila_str = "  [" + ", ".join([f"{format_number(x, 3):>8}" for x in fila]) + "]"
                            procedimiento.append(fila_str)
                
                pivote += 1
            
            # Verificar consistencia
            for i in range(m):
                fila_ceros = np.all(np.isclose(A_aug[i, :-1], 0))
                if fila_ceros and not np.isclose(A_aug[i, -1], 0):
                    procedimiento.append(f"\n¡INCONSISTENCIA DETECTADA!")
                    procedimiento.append(f"La fila {i+1} indica 0 = {format_number(float(A_aug[i, -1]), 3)}, lo cual es imposible.")
                    procedimiento.append("CONCLUSIÓN: El vector NO ES una combinación lineal de los vectores base.")
                    return "\n".join(procedimiento)
            
            procedimiento.append("\n--- MATRIZ ESCALONADA REDUCIDA FINAL ---")
            matriz_final_simple = [[float(A_aug[i][j]) for j in range(A_aug.shape[1])] for i in range(A_aug.shape[0])]
            for i, fila in enumerate(matriz_final_simple):
                fila_str = "  [" + ", ".join([f"{format_number(x, 3):>8}" for x in fila]) + "]"
                procedimiento.append(fila_str)
            
            # Extraer solución
            solucion = A_aug[:num_vectores, -1]  # Tomar solo las primeras num_vectores filas para los coeficientes
            
            procedimiento.append("\n--- EXTRACCIÓN DE LA SOLUCIÓN ---")
            procedimiento.append("De la matriz escalonada reducida, leemos los coeficientes:")
            coeficientes_texto = []
            for i in range(min(len(solucion), num_vectores)):
                coef_valor = format_number(float(solucion[i]), 4)
                procedimiento.append(f"c{i+1} = {coef_valor}")
                coeficientes_texto.append(f"c{i+1} = {coef_valor}")
            
            # Verificación de la solución - MEJORADA
            procedimiento.append("\n--- VERIFICACIÓN DETALLADA DE LA SOLUCIÓN ---")
            procedimiento.append("Sustituyendo los coeficientes encontrados en la combinación lineal:")
            
            # Mostrar cada paso de la verificación
            verificacion = np.zeros(dimension)
            terminos_por_componente = [[] for _ in range(dimension)]
            
            for i in range(num_vectores):
                if i < len(solucion):
                    coef = float(solucion[i])
                    vector = vectores_base[i]
                    vector_simple = [float(x) for x in vector]
                    procedimiento.append(f"\nVector {i+1} multiplicado por c{i+1} = {format_number(coef, 4)}:")
                    resultado_parcial = coef * vector
                    resultado_simple = [float(x) for x in resultado_parcial]
                    procedimiento.append(f"  {format_number(coef, 4)} * {vector_simple} = {[format_number(x, 4) for x in resultado_simple]}")
                    
                    verificacion += resultado_parcial
                    
                    # Guardar términos para mostrar la suma por componente
                    for j in range(dimension):
                        if resultado_parcial[j] != 0:
                            terminos_por_componente[j].append(format_number(float(resultado_parcial[j]), 4))
            
            # Mostrar la suma por componentes
            procedimiento.append(f"\n--- SUMA COMPONENTE POR COMPONENTE ---")
            for j in range(dimension):
                if terminos_por_componente[j]:
                    suma_str = " + ".join(terminos_por_componente[j]).replace("+ -", "- ")
                    procedimiento.append(f"Componente {j+1}: {suma_str} = {format_number(float(verificacion[j]), 4)}")
                else:
                    procedimiento.append(f"Componente {j+1}: 0 = {format_number(float(verificacion[j]), 4)}")
            
            verificacion_simple = [format_number(float(x), 4) for x in verificacion]
            vector_obj_simple = [format_number(float(x), 4) for x in vector_objetivo]
            procedimiento.append(f"\nResultado de la combinación lineal: {verificacion_simple}")
            procedimiento.append(f"Vector objetivo original:           {vector_obj_simple}")
            
            # Verificación final
            if np.allclose(verificacion, vector_objetivo, atol=1e-10):
                procedimiento.append("\n✓ VERIFICACIÓN EXITOSA: Los valores coinciden perfectamente.")
                
                # CONCLUSIÓN MEJORADA CON LOS COEFICIENTES
                procedimiento.append("\n" + "="*50)
                procedimiento.append("CONCLUSIÓN FINAL:")
                procedimiento.append("✓ El vector ES una combinación lineal de los vectores base.")
                procedimiento.append(f"✓ SOLUCIÓN ENCONTRADA: {', '.join(coeficientes_texto)}")
                
                # Mostrar la ecuación final
                ecuacion_final = ""
                for i in range(num_vectores):
                    if i > 0:
                        if float(solucion[i]) >= 0:
                            ecuacion_final += " + "
                        else:
                            ecuacion_final += " "
                    vector_simple = [float(x) for x in vectores_base[i]]
                    ecuacion_final += f"({format_number(float(solucion[i]), 4)})*{vector_simple}"
                procedimiento.append(f"\nLa ecuación final es:")
                procedimiento.append(f"{ecuacion_final} = {vector_obj_simple}")
                
                # Análisis adicional basado en la dependencia/independencia
                if rango == num_vectores:
                    procedimiento.append("\n✓ Como los vectores base son linealmente independientes,")
                    procedimiento.append("  esta es la ÚNICA forma de expresar el vector objetivo.")
                else:
                    procedimiento.append(f"\n⚠ Como los vectores base son linealmente dependientes,")
                    procedimiento.append("  existen MÚLTIPLES formas de expresar el vector objetivo.")
                    procedimiento.append(f"  El sistema tiene {num_vectores - rango} grado(s) de libertad.")
                
            else:
                error = np.linalg.norm(verificacion - vector_objetivo)
                procedimiento.append(f"\n✗ Error en la verificación: {format_number(error, 6)}")
                procedimiento.append("CONCLUSIÓN: El vector NO ES una combinación lineal exacta.")
            
            # Información adicional sobre dependencia lineal
            procedimiento.append(f"\n--- RESUMEN DEL ANÁLISIS ---")
            procedimiento.append(f"• Rango de la matriz de vectores base: {rango}")
            procedimiento.append(f"• Número de vectores base: {num_vectores}")
            procedimiento.append(f"• Dimensión del espacio: {dimension}")
            
            if rango < num_vectores:
                procedimiento.append("• ADVERTENCIA: Los vectores base son linealmente dependientes.")
                procedimiento.append(f"• Se podrían eliminar {num_vectores - rango} vector(es) redundante(s).")
            else:
                procedimiento.append("• Los vectores base son linealmente independientes.")
                
            if rango == dimension:
                procedimiento.append(f"• Los vectores base GENERAN todo el espacio R^{dimension}.")
                procedimiento.append("• Cualquier vector en este espacio puede expresarse como combinación lineal.")
            else:
                procedimiento.append(f"• Los vectores base generan un SUBESPACIO de dimensión {rango}.")
                procedimiento.append("• Solo vectores en este subespacio pueden expresarse como combinación lineal.")
                
        except (ValueError, TypeError):
            procedimiento.append("\n--- ANÁLISIS SIMBÓLICO ---")
            procedimiento.append("La entrada contiene variables (letras). El sistema debe resolverse algebraicamente.")
            procedimiento.append("Sistema planteado (A*c = b):")
            for i in range(A.shape[0]):
                ecuacion = " + ".join([f"({A[i, j]})*c{j+1}" for j in range(A.shape[1])]) + f" = {b[i]}"
                procedimiento.append(f"  Ecuación {i+1}: {ecuacion}")
            procedimiento.append("\nEste programa no resuelve sistemas simbólicos algebraicamente, solo los plantea.")
        
        return "\n".join(procedimiento)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora de Álgebra Lineal")
        self.geometry("1050x800")
        self.sistema = SistemaEcuaciones()
        self.setup_styles()
        top_frame = ttk.Frame(self, style="App.TFrame")
        top_frame.pack(side="top", fill="x", padx=10, pady=(10, 0))
        reset_button = ttk.Button(top_frame, text="Limpiar y Reiniciar Todo", command=self.reset_interface, style="Reset.TButton")
        reset_button.pack(side="right")
        self.notebook = ttk.Notebook(self, style="TNotebook")
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)
        self.tab1 = ttk.Frame(self.notebook, style="App.TFrame")
        self.tab2 = ttk.Frame(self.notebook, style="App.TFrame")
        self.notebook.add(self.tab1, text='Sistema de Ecuaciones y Matrices')
        self.notebook.add(self.tab2, text='Combinación Lineal')
        self.setup_tab1()
        self.setup_tab2()
    def setup_styles(self):
        BG_COLOR = "#2E3440"; FG_COLOR = "#ECEFF4"; BTN_COLOR = "#5E81AC"; BTN_HOVER = "#81A1C1"
        ENTRY_BG = "#3B4252"; ACCENT_COLOR = "#88C0D0"; RESET_BTN_COLOR = "#D08770"; RESET_HOVER_COLOR = "#BF616A"
        style = ttk.Style(self); style.theme_use("clam")
        self.configure(background=BG_COLOR)
        style.configure("App.TFrame", background=BG_COLOR)
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_COLOR, foreground=FG_COLOR, padding=[10, 5], font=('Helvetica', 10, 'bold'))
        style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], foreground=[("selected", BG_COLOR)])
        style.configure("TLabelFrame", background=BG_COLOR, foreground=FG_COLOR, borderwidth=1, relief="solid")
        style.configure("TLabelFrame.Label", foreground=ACCENT_COLOR, background=BG_COLOR, font=('Helvetica', 11, 'bold'))
        style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=('Helvetica', 10))
        style.configure("TButton", background=BTN_COLOR, foreground=FG_COLOR, borderwidth=0, font=('Helvetica', 10, 'bold'), padding=8)
        style.map("TButton", background=[('active', BTN_HOVER)])
        style.configure("Reset.TButton", background=RESET_BTN_COLOR, foreground=FG_COLOR)
        style.map("Reset.TButton", background=[('active', RESET_HOVER_COLOR)])
        style.configure("Small.TButton", padding=5, font=('Helvetica', 8))
        style.configure("Collapsible.TButton", background=BG_COLOR, foreground=ACCENT_COLOR)
        style.map("Collapsible.TButton", background=[('active', ENTRY_BG)])
        style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=FG_COLOR, borderwidth=1, insertbackground=FG_COLOR)
        style.configure("Treeview", background=ENTRY_BG, foreground=FG_COLOR, fieldbackground=ENTRY_BG, rowheight=25)
        style.configure("Treeview.Heading", background=BTN_COLOR, foreground=FG_COLOR, font=('Helvetica', 10, 'bold'))
        style.map("Treeview.Heading", background=[('active', BTN_HOVER)])
        ttk.Style().configure("Accent.TButton", background="#BF616A", foreground="#ECEFF4")
        ttk.Style().map("Accent.TButton", background=[('active', "#D08770")])
    def setup_tab1(self):
        main_pane = ttk.PanedWindow(self.tab1, orient=tk.HORIZONTAL); main_pane.pack(fill="both", expand=True)
        left_frame = ttk.Frame(main_pane, style="App.TFrame"); main_pane.add(left_frame, weight=1)
        right_frame = ttk.Frame(main_pane, style="App.TFrame"); main_pane.add(right_frame, weight=2)
        controles_lf = ttk.LabelFrame(left_frame, text="Controles", padding=10); controles_lf.pack(padx=10, pady=5, fill="both", expand=True)
        definir_frame = ttk.LabelFrame(controles_lf, text="Definir Matriz", padding=10); definir_frame.pack(fill="x", pady=5)
        ttk.Label(definir_frame, text="Incógnitas (Col):").grid(row=0, column=0, padx=5, pady=5)
        self.n_vars_entry = ttk.Entry(definir_frame, width=5); self.n_vars_entry.grid(row=0, column=1, padx=5, pady=5); self.n_vars_entry.insert(0, "3")
        ttk.Label(definir_frame, text="Ecuaciones (Filas):").grid(row=0, column=2, padx=5, pady=5)
        self.m_eqs_entry = ttk.Entry(definir_frame, width=5); self.m_eqs_entry.grid(row=0, column=3, padx=5, pady=5); self.m_eqs_entry.insert(0, "3")
        ttk.Button(definir_frame, text="Crear/Reiniciar", command=self.crear_matriz).grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(definir_frame, text="Generar Aleatoria", command=self.generar_aleatoria).grid(row=1, column=2, columnspan=2, pady=10)
        resolver_frame = ttk.LabelFrame(controles_lf, text="Resolver Sistema", padding=10); resolver_frame.pack(fill="x", pady=15)
        ttk.Button(resolver_frame, text="Resolver (Gauss-Jordan)", command=self.resolver_sistema).pack(fill="x", pady=5)
        ttk.Button(resolver_frame, text="Resolver por Inversa", command=self.resolver_inversa).pack(fill="x", pady=5)
        operaciones_frame = ttk.LabelFrame(controles_lf, text="Operaciones con Matriz A", padding=10); operaciones_frame.pack(fill="x", pady=15)
        ttk.Button(operaciones_frame, text="Multiplicar por Escalar", command=self.multiplicar_escalar).pack(fill="x", pady=5)
        ttk.Button(operaciones_frame, text="Dividir por Escalar", command=self.dividir_escalar).pack(fill="x", pady=5)
        ttk.Button(operaciones_frame, text="Multiplicar por Matriz", command=self.multiplicar_matriz).pack(fill="x", pady=5)
        matriz_pane = CollapsiblePane(right_frame, text="Editor de Matriz (Doble Clic para Editar)", style_prefix="Collapsible"); matriz_pane.pack(padx=10, pady=5, fill="both", expand=True)
        tree_frame = ttk.Frame(matriz_pane.frame); tree_frame.pack(fill="both", expand=True, pady=5)
        self.tree = ttk.Treeview(tree_frame, show="headings")
        vsb_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview); vsb_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb_y.set, xscrollcommand=vsb_x.set)
        vsb_y.pack(side='right', fill='y'); vsb_x.pack(side='bottom', fill='x'); self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.editar_celda)
        resultado_pane = CollapsiblePane(right_frame, text="Procedimiento y Solución", style_prefix="Collapsible"); resultado_pane.pack(padx=10, pady=5, fill="both", expand=True)
        text_frame_1 = ttk.Frame(resultado_pane.frame); text_frame_1.pack(fill="both", expand=True, pady=5)
        
        # BOTÓN EXPORTAR PDF PARA TAB 1
        export_frame_1 = ttk.Frame(text_frame_1, style="App.TFrame")
        export_frame_1.pack(fill='x', pady=(0, 5))
        pdf_button_1 = ttk.Button(export_frame_1, text="Exportar a PDF", command=self.exportar_procedimiento_pdf, style="Small.TButton")
        pdf_button_1.pack(side='right')

        proc_scrollbar = ttk.Scrollbar(text_frame_1, orient="vertical")
        self.procedimiento_text = tk.Text(text_frame_1, wrap=tk.WORD, background="#3B4252", foreground="#ECEFF4", relief="flat", borderwidth=1, font=('Consolas', 10), yscrollcommand=proc_scrollbar.set)
        proc_scrollbar.config(command=self.procedimiento_text.yview)
        proc_scrollbar.pack(side="right", fill="y"); self.procedimiento_text.pack(side="left", fill="both", expand=True)
        self.crear_matriz(); matriz_pane.toggle(); resultado_pane.toggle()
    def setup_tab2(self):
        entrada_pane = CollapsiblePane(self.tab2, "Definir Vectores", style_prefix="Collapsible"); entrada_pane.pack(fill="x", expand=False, padx=10, pady=10)
        action_frame = ttk.Frame(entrada_pane.frame, style="App.TFrame"); action_frame.pack(fill="x", pady=(5, 10))
        ttk.Button(action_frame, text="Analizar Combinación Lineal", command=self.analizar_combinacion, style="Accent.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="Generar Problema Aleatorio", command=self.generar_combinacion_lineal_aleatoria).pack(side="left", padx=5)
        base_frame = ttk.LabelFrame(entrada_pane.frame, text="Vectores Base B", padding=10); base_frame.pack(fill="both", pady=5, padx=5, expand=True)
        ttk.Label(base_frame, text="Ingrese los vectores como una lista de listas (ej: [[1,2],[3,4]])").pack(anchor="w")
        self.vectores_base_entry = tk.Text(base_frame, height=5, width=60, background="#3B4252", foreground="#ECEFF4", font=('Consolas', 10)); self.vectores_base_entry.pack(fill="both", expand=True, pady=(5,0))
        self.vectores_base_entry.insert("1.0", "[[1, 0, 1], [2, 1, 0], [3, 1, -1]]")
        obj_frame = ttk.LabelFrame(entrada_pane.frame, text="Vector Objetivo v", padding=10); obj_frame.pack(fill="x", pady=5, padx=5)
        ttk.Label(obj_frame, text="Ingrese el vector como una lista (ej: [5,6])").pack(anchor="w")
        self.vector_obj_entry = ttk.Entry(obj_frame, width=60, font=('Consolas', 10)); self.vector_obj_entry.pack(fill="x", expand=True, pady=(5,0))
        self.vector_obj_entry.insert(0, "[4, 1, 1]")
        analisis_pane = CollapsiblePane(self.tab2, "Resultado del Análisis", style_prefix="Collapsible"); analisis_pane.pack(fill="both", expand=True, padx=10, pady=10)
        text_frame_2 = ttk.Frame(analisis_pane.frame); text_frame_2.pack(fill="both", expand=True, pady=5)
        
        # BOTÓN EXPORTAR PDF PARA TAB 2
        export_frame_2 = ttk.Frame(text_frame_2, style="App.TFrame")
        export_frame_2.pack(fill='x', pady=(0, 5))
        pdf_button_2 = ttk.Button(export_frame_2, text="Exportar a PDF", command=self.exportar_analisis_pdf, style="Small.TButton")
        pdf_button_2.pack(side='right')

        analisis_scrollbar = ttk.Scrollbar(text_frame_2, orient="vertical")
        self.analisis_text = tk.Text(text_frame_2, wrap=tk.WORD, background="#3B4252", foreground="#ECEFF4", relief="flat", borderwidth=1, font=('Consolas', 10), yscrollcommand=analisis_scrollbar.set)
        analisis_scrollbar.config(command=self.analisis_text.yview)
        analisis_scrollbar.pack(side="right", fill="y"); self.analisis_text.pack(side="left", fill="both", expand=True)
        entrada_pane.toggle(); analisis_pane.toggle()
    
    # EXPORTAR PDF
    def exportar_a_pdf(self, contenido, titulo_documento):
        """Función genérica para guardar contenido de texto en un archivo PDF con un encabezado personalizado."""
        if not REPORTLAB_DISPONIBLE:
            messagebox.showerror("Librería Faltante", "La librería 'reportlab' es necesaria para exportar a PDF.\n\nInstálala con: pip install reportlab")
            return
        
        contenido = contenido.strip()
        if not contenido:
            messagebox.showwarning("Exportar PDF", "No hay contenido para exportar.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Documentos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
            title="Guardar resultado como...",
            initialfile=f"{titulo_documento.replace(' ', '_')}.pdf"
        )

        if not filepath:
            return  # El usuario canceló el diálogo

        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter,
                                    rightMargin=inch, leftMargin=inch,
                                    topMargin=inch, bottomMargin=inch)
            
            styles = getSampleStyleSheet()
            
            universidad_style = ParagraphStyle(
                'Universidad',
                parent=styles['h1'],
                alignment=TA_CENTER,
                fontSize=16,
                leading=20
            )

            facultad_style = ParagraphStyle(
                'Facultad',
                parent=styles['h2'],
                alignment=TA_CENTER,
                fontSize=12,
                leading=16
            )

            integrantes_style = ParagraphStyle(
                'Integrantes',
                parent=styles['Normal'],
                alignment=TA_LEFT,
                fontSize=10,
                spaceBefore=24,
                leading=14
            )

            mono_style = ParagraphStyle(
                'Mono',
                parent=styles['Normal'],
                fontName='Courier',
                fontSize=9,
                leading=12,
                textColor=black,
                alignment=TA_LEFT,
            )
            
            titulo_style = styles['h3']
            titulo_style.alignment = TA_LEFT
            titulo_style.spaceBefore = 24

            # Convertir el contenido de texto plano a un formato que reportlab entienda (HTML-like)
            contenido_html = contenido.replace('\n', '<br/>').replace(' ', ' ')

            # Construir el documento con el nuevo encabezado
            flowables = [
                Paragraph("Universidad Central del Ecuador", universidad_style),
                Paragraph("Facultad de Ingeniería y Ciencias Aplicadas", facultad_style),
                Paragraph("Integrantes: Gabriela Chacón, Marlon Cruz, Miryam Miranda, Atik Tontaquimba, Christopher Villón", integrantes_style),
                Spacer(1, 0.2 * inch),
                Paragraph(titulo_documento.replace('_', ' '), titulo_style),
                Spacer(1, 0.1 * inch),
                Paragraph(contenido_html, mono_style)
            ]

            doc.build(flowables)
            messagebox.showinfo("Exportación Exitosa", f"El archivo ha sido guardado en:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Error al Exportar", f"No se pudo guardar el archivo PDF.\nError: {e}")
            traceback.print_exc()

    def exportar_procedimiento_pdf(self):
        """Extrae el texto del panel de procedimiento y lo envía a la función de exportación."""
        contenido = self.procedimiento_text.get("1.0", tk.END)
        self.exportar_a_pdf(contenido, "Procedimiento y Solución del Sistema")

    def exportar_analisis_pdf(self):
        """Extrae el texto del panel de análisis y lo envía a la función de exportación."""
        contenido = self.analisis_text.get("1.0", tk.END)
        self.exportar_a_pdf(contenido, "Análisis de Combinación Lineal")
    # ---------------------------------------------
    
    def reset_interface(self):
        if not messagebox.askyesno("Confirmar Reinicio", "Esto borrará todos los datos y restablecerá la interfaz. ¿Está seguro?"): return
        self.n_vars_entry.delete(0, tk.END); self.n_vars_entry.insert(0, "3")
        self.m_eqs_entry.delete(0, tk.END); self.m_eqs_entry.insert(0, "3")
        self.crear_matriz()
        self.procedimiento_text.delete("1.0", tk.END)
        self.vectores_base_entry.delete("1.0", tk.END)
        self.vectores_base_entry.insert("1.0", "[[1, 0, 1], [2, 1, 0], [3, 1, -1]]")
        self.vector_obj_entry.delete(0, tk.END); self.vector_obj_entry.insert(0, "[4, 1, 1]")
        self.analisis_text.delete("1.0", tk.END)
        self.notebook.select(self.tab1)
        messagebox.showinfo("Reinicio Completo", "La interfaz ha sido restablecida.")
    def crear_matriz(self):
        try:
            n_vars = int(self.n_vars_entry.get()); m_eqs = int(self.m_eqs_entry.get())
            if n_vars > 50 or m_eqs > 50:
                if not messagebox.askokcancel("Advertencia", f"Está creando una matriz de {m_eqs}x{n_vars}. Esto puede afectar el rendimiento. ¿Continuar?"): return
            self.sistema.configurar_dimensiones(n_vars, m_eqs); self.actualizar_treeview(); self.procedimiento_text.delete("1.0", tk.END)
        except (ValueError, TypeError): messagebox.showerror("Error de Entrada", "Ingrese números enteros positivos para las dimensiones.")
        except Exception as e: messagebox.showerror("Error Inesperado", f"Error: {e}"); traceback.print_exc()
    def generar_aleatoria(self):
        try:
            n_vars, m_eqs = int(self.n_vars_entry.get()), int(self.m_eqs_entry.get())
            min_val = simpledialog.askfloat("Rango Aleatorio", "Valor mínimo:", initialvalue=-10)
            if min_val is None: return
            max_val = simpledialog.askfloat("Rango Aleatorio", "Valor máximo:", initialvalue=10)
            if max_val is None: return
            if min_val >= max_val: messagebox.showerror("Error", "El mínimo debe ser menor que el máximo."); return
            self.sistema.generar_matriz_aleatoria(n_vars, m_eqs, min_val, max_val); self.actualizar_treeview(); self.procedimiento_text.delete("1.0", tk.END)
        except (ValueError, TypeError): messagebox.showerror("Error de Entrada", "Ingrese números enteros válidos.")
        except Exception as e: messagebox.showerror("Error Inesperado", f"Error: {e}"); traceback.print_exc()
    def actualizar_treeview(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        if self.sistema.A is None: return
        m_eqs, n_vars = self.sistema.A.shape
        cols = [f"x{i+1}" for i in range(n_vars)] + ["b"]
        self.tree["columns"] = cols
        for col in cols: self.tree.heading(col, text=col); self.tree.column(col, width=80, anchor='center')
        for i in range(m_eqs):
            fila_valores = list(self.sistema.A[i]) + ([self.sistema.b[i]] if self.sistema.b is not None and i < len(self.sistema.b) else [0])
            self.tree.insert("", "end", iid=i, values=[format_number(val, 4) for val in fila_valores])
    def editar_celda(self, event):
        item_id = self.tree.identify_row(event.y); column_id = self.tree.identify_column(event.x)
        if not item_id or not column_id: return
        row, col = int(item_id), int(column_id.replace('#', '')) - 1
        x, y, width, height = self.tree.bbox(item_id, column_id)
        valor_actual = self.tree.item(item_id, "values")[col]
        entry_popup = ttk.Entry(self.tree, style="TEntry"); entry_popup.place(x=x, y=y, width=width, height=height)
        entry_popup.insert(0, valor_actual); entry_popup.focus(); entry_popup.select_range(0, 'end')
        entry_popup.bind("<FocusOut>", lambda e: self.guardar_valor(entry_popup, row, col))
        entry_popup.bind("<Return>", lambda e: self.guardar_valor(entry_popup, row, col))
    def guardar_valor(self, entry, row, col):
        try:
            nuevo_valor = float(entry.get() or 0.0)
            n_vars = self.sistema.A.shape[1]
            if col < n_vars: self.sistema.A[row, col] = nuevo_valor
            else: self.sistema.b[row] = nuevo_valor
            self.actualizar_treeview()
        except ValueError: messagebox.showerror("Entrada Inválida", f"'{entry.get()}' no es un número.")
        except Exception as e: messagebox.showerror("Error", f"Error: {e}"); traceback.print_exc()
        finally: entry.destroy()
    def _ejecutar_resolucion(self, metodo_resolucion):
        try:
            procedimiento, solucion = metodo_resolucion()
            self.procedimiento_text.delete("1.0", tk.END); self.procedimiento_text.insert("1.0", procedimiento)
            sol_texto = "\n\n--- SOLUCIÓN FINAL ---"
            if isinstance(solucion, np.ndarray):
                sol_texto += "\n" + "\n".join([f"{var} = {format_number(val, 4)}" for var, val in zip(self.sistema.variables, solucion)])
            self.procedimiento_text.insert(tk.END, sol_texto)
        except (np.linalg.LinAlgError, ValueError) as e:
            messagebox.showerror("Error en la Resolución", str(e))
            self.procedimiento_text.delete("1.0", tk.END); self.procedimiento_text.insert("1.0", f"Error:\n{e}")
        except Exception as e: messagebox.showerror("Error", f"Error: {e}"); traceback.print_exc()
    def resolver_sistema(self): self._ejecutar_resolucion(self.sistema.resolver_gauss_jordan)
    def resolver_inversa(self): self._ejecutar_resolucion(self.sistema.resolver_por_inversa)
    def multiplicar_escalar(self):
        escalar = simpledialog.askfloat("Multiplicar", "Ingrese el escalar:", initialvalue=2.0)
        if escalar is not None and self.sistema.A is not None:
            self.sistema.A = self.sistema.A * escalar
            self.actualizar_treeview()
            self.procedimiento_text.delete("1.0", tk.END)
            self.procedimiento_text.insert("1.0", f"--- Matriz A multiplicada por {format_number(escalar, 3)} ---\n")
    def dividir_escalar(self):
        escalar = simpledialog.askfloat("Dividir", "Ingrese el escalar:", initialvalue=2.0)
        if escalar is not None:
            if np.isclose(escalar, 0): messagebox.showerror("Error", "No se puede dividir por cero."); return
            if self.sistema.A is not None:
                self.sistema.A = self.sistema.A / escalar
                self.actualizar_treeview()
                self.procedimiento_text.delete("1.0", tk.END)
                self.procedimiento_text.insert("1.0", f"--- Matriz A dividida por {format_number(escalar, 3)} ---\n")

    def multiplicar_matriz(self):
        if self.sistema.A is None: return
        m, n = self.sistema.A.shape
        prompt = f"Ingrese la matriz B (en formato de lista de listas, ej: [[1,2],[3,4]]) para multiplicar por A.\nLa matriz A actual es de {m}x{n}, por lo que B debe tener {n} filas."
        matriz_str = simpledialog.askstring("Multiplicar por Matriz", prompt, initialvalue="[]")
        if matriz_str:
            try:
                matriz_b = np.array(json.loads(matriz_str))
                if matriz_b.ndim != 2 or matriz_b.shape[0] != n:
                    raise ValueError(f"La matriz B debe ser 2D y tener {n} filas para poder multiplicar.")
                
                matriz_a_original = self.sistema.A.copy()
                procedimiento_mult = self.sistema.generar_procedimiento_multiplicacion(matriz_a_original, matriz_b)
                
                matriz_resultado = np.dot(matriz_a_original, matriz_b)
                new_m, new_n = matriz_resultado.shape
                
                self.sistema.configurar_dimensiones(new_n, new_m)
                self.sistema.A = matriz_resultado
                
                self.n_vars_entry.delete(0, tk.END); self.n_vars_entry.insert(0, str(new_n))
                self.m_eqs_entry.delete(0, tk.END); self.m_eqs_entry.insert(0, str(new_m))
                self.actualizar_treeview()
                
                self.procedimiento_text.delete("1.0", tk.END)
                info_texto = (f"--- Matriz A multiplicada por B ---\n"
                              f"Matriz B ingresada:\n{format_matrix_display(matriz_b)}\n\n"
                              f"{procedimiento_mult}\n\n"
                              f"Resultado Final (nueva Matriz A):\n{format_matrix_display(self.sistema.A)}\n\n"
                              f"AVISO: El sistema ha cambiado. La matriz A se ha actualizado y el vector 'b' se ha reiniciado a ceros.")
                self.procedimiento_text.insert("1.0", info_texto)

            except (json.JSONDecodeError, ValueError) as e: messagebox.showerror("Error de Formato o Dimensión", str(e))
            except Exception as e: messagebox.showerror("Error Inesperado", f"Error: {e}"); traceback.print_exc()

    def analizar_combinacion(self):
        self.analisis_text.delete("1.0", tk.END)
        try:
            base_str, obj_str = self.vectores_base_entry.get("1.0", tk.END), self.vector_obj_entry.get()
            if not base_str.strip() or not obj_str.strip(): raise ValueError("Las entradas no pueden estar vacías.")
            resultado = self.sistema.analizar_combinacion_lineal(base_str, obj_str)
            self.analisis_text.insert("1.0", resultado)
        except (SyntaxError, ValueError, json.JSONDecodeError) as e:
            messagebox.showerror("Error de Entrada", str(e)); self.analisis_text.insert("1.0", f"Error: {e}")
        except Exception as e: messagebox.showerror("Error", f"Error: {e}"); traceback.print_exc()
    def generar_combinacion_lineal_aleatoria(self):
        try:
            num_vectores = simpledialog.askinteger("Generación Aleatoria", "Cantidad de vectores base:", initialvalue=3, minvalue=1)
            if num_vectores is None: return
            dimension = simpledialog.askinteger("Generación Aleatoria", "Dimensión de cada vector:", initialvalue=3, minvalue=1)
            if dimension is None: return
            min_val = simpledialog.askinteger("Generación Aleatoria", "Valor entero MÍNIMO del rango:", initialvalue=-10)
            if min_val is None: return
            max_val = simpledialog.askinteger("Generación Aleatoria", "Valor entero MÁXIMO del rango:", initialvalue=10)
            if max_val is None: return
            if min_val >= max_val: messagebox.showerror("Error de Rango", "El valor mínimo debe ser menor que el máximo."); return
            vectores_base = [[random.randint(min_val, max_val) for _ in range(dimension)] for _ in range(num_vectores)]
            vector_objetivo = [random.randint(min_val, max_val) for _ in range(dimension)]
            base_str = json.dumps(vectores_base)
            obj_str = json.dumps(vector_objetivo)
            self.vectores_base_entry.delete("1.0", tk.END); self.vectores_base_entry.insert("1.0", base_str)
            self.vector_obj_entry.delete(0, tk.END); self.vector_obj_entry.insert(0, obj_str)
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error al generar los vectores: {e}"); traceback.print_exc()

if __name__ == "__main__":
    app = App()
    app.mainloop()