"""Pruebas del núcleo: python -m unittest discover -s tests -v"""
import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from src.nucleo import *
from src.nucleo.validacion import parse_numero
from src.pdf import exportar_pdf


class TestNucleo(unittest.TestCase):
    def test_aleatorios_contra_numpy(self):
        rng = np.random.default_rng(7)
        for n in (2, 5, 10, 15):
            A = np.round(rng.uniform(-9, 9, (n, n)), 2); b = np.round(rng.uniform(-9, 9, n), 2)
            esperado = np.linalg.solve(A, b)
            for f in (resolver_gauss_jordan, resolver_por_inversa):
                r = f(A, b)
                self.assertEqual(r.estado, "unica")
                np.testing.assert_allclose(r.solucion, esperado, rtol=1e-7, atol=1e-7)

    def test_casos_especiales(self):
        self.assertEqual(resolver_gauss_jordan([[1, 1], [2, 2]], [1, 3]).estado, "inconsistente")
        r = resolver_gauss_jordan([[1, 1, 1], [2, 2, 2]], [3, 6]); self.assertEqual(r.estado, "infinita")
        np.testing.assert_allclose(np.array([[1, 1, 1], [2, 2, 2]]) @ r.solucion, [3, 6])
        self.assertTrue(resolver_por_inversa([[1, 2], [2, 4]], [1, 2]).es_error)      # singular
        self.assertTrue(resolver_por_inversa([[1, 2, 3], [4, 5, 6]], [1, 2]).es_error)  # no cuadrada
        self.assertTrue(resolver_gauss_jordan(np.zeros((2, 2)), [0, 0]).estado == "infinita")

    def test_multiplicacion_y_escalar(self):
        A = np.arange(12.).reshape(3, 4); B = np.arange(8.).reshape(4, 2)
        np.testing.assert_allclose(multiplicar_matrices(A, B).matriz, A @ B)
        self.assertTrue(multiplicar_matrices(A, A).es_error)
        np.testing.assert_allclose(operar_escalar(A, 4, True).matriz, A / 4)
        self.assertTrue(operar_escalar(A, 0, True).es_error)

    def test_combinacion(self):
        V = [[1, 0, 1], [2, 1, 0], [3, 1, -1]]
        r = analizar_combinacion_lineal(V, [4, 1, 1])
        np.testing.assert_allclose(r.solucion @ np.array(V), [4, 1, 1], atol=1e-9)
        self.assertEqual(analizar_combinacion_lineal([[1, 2], [2, 4]], [1, 0]).estado, "inconsistente")
        self.assertEqual(analizar_combinacion_lineal([[1, 2], [2, 4]], [3, 6]).estado, "infinita")

    def test_validacion(self):
        self.assertAlmostEqual(parse_numero("1/4"), 0.25); self.assertEqual(parse_numero("2,5"), 2.5)
        for malo in ("nan", "inf", "1/0", "abc", "1e99", "--1"):
            with self.assertRaises(ValueError): parse_numero(malo)

    def test_pdf_todos(self):
        rng = np.random.default_rng(3)
        A = np.round(rng.uniform(-9, 9, (15, 15)), 2); b = np.round(rng.uniform(-9, 9, 15), 2)
        reps = [resolver_gauss_jordan(A, b), resolver_por_inversa(A, b), resolver_por_inversa([[1, 2], [2, 4]], [1, 2]),
                multiplicar_matrices(A, A), operar_escalar(A, 2, False),
                analizar_combinacion_lineal(A[:6, :8], A[7, :8])]
        for r in reps:
            with tempfile.TemporaryDirectory() as d:
                ruta = os.path.join(d, "x.pdf"); exportar_pdf(r.reporte, ruta)
                self.assertTrue(open(ruta, "rb").read(5) == b"%PDF-")


if __name__ == "__main__":
    unittest.main()
