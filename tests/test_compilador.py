import unittest
from pathlib import Path

from compilador.analisador_lexico import AnalisadorLexico, ErroLexico
from compilador.analisador_sintatico import AnalisadorSintatico, ErroSintatico

EXEMPLOS = Path(__file__).resolve().parent.parent / "exemplos"


def compilar(codigo):
    tokens = AnalisadorLexico(codigo).tokenizar()
    AnalisadorSintatico(tokens).analisar()
    return tokens


class TestLexico(unittest.TestCase):
    def test_palavras_reservadas_e_identificadores(self):
        tipos = [t.tipo for t in AnalisadorLexico("program x1_a if").tokenizar()]
        self.assertEqual(tipos, ["program", "IDENT", "if", "EOF"])

    def test_operadores_duplos(self):
        tipos = [t.tipo for t in AnalisadorLexico("== != >= <= = < >").tokenizar()]
        self.assertEqual(tipos, ["==", "!=", ">=", "<=", "=", "<", ">", "EOF"])

    def test_comentario_ignorado(self):
        tokens = AnalisadorLexico("x // comentario @@@\ny").tokenizar()
        self.assertEqual([t.lexema for t in tokens[:-1]], ["x", "y"])
        self.assertEqual(tokens[1].linha, 2)

    def test_caractere_invalido(self):
        with self.assertRaises(ErroLexico):
            AnalisadorLexico("x = 1 @ 2").tokenizar()

    def test_cadeia_nao_terminada(self):
        with self.assertRaises(ErroLexico):
            AnalisadorLexico('print("abc').tokenizar()


class TestSintatico(unittest.TestCase):
    def test_exemplo_valido(self):
        compilar((EXEMPLOS / "valido.txt").read_text(encoding="utf-8"))

    def test_subrotina_aninhada_com_variavel(self):
        compilar("program p; proc a() { var i int; proc b() { } i = 1; } { a(); } .")

    def test_programa_minimo(self):
        compilar("program p; { } .")

    def test_falta_ponto_e_virgula(self):
        with self.assertRaises(ErroSintatico):
            compilar("program p; var x int; { x = 1 } .")

    def test_falta_ponto_final(self):
        with self.assertRaises(ErroSintatico):
            compilar("program p; { }")

    def test_if_sem_chaves(self):
        with self.assertRaises(ErroSintatico):
            compilar("program p; var x int; { if x > 1 x = 2; } .")

    def test_relacional_nao_encadeia(self):
        with self.assertRaises(ErroSintatico):
            compilar("program p; var x int; { x = 1 < 2 < 3; } .")

    def test_lixo_apos_ponto_final(self):
        with self.assertRaises(ErroSintatico):
            compilar("program p; { } . x")


if __name__ == "__main__":
    unittest.main()
