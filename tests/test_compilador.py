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

    def test_cadeia_vazia(self):
        tokens = AnalisadorLexico('""').tokenizar()
        self.assertEqual(tokens[0].tipo, "CADEIA")
        self.assertEqual(tokens[0].lexema, "")

    def test_cadeia_com_todos_simbolos(self):
        simbolos = "!#$%&'()*+,-./:;<=>?@_[]{}|"
        tokens = AnalisadorLexico(f'"{simbolos}"').tokenizar()
        self.assertEqual(tokens[0].tipo, "CADEIA")
        self.assertEqual(tokens[0].lexema, simbolos)

    def test_cadeia_caractere_proibido(self):
        for caractere in "^~\\":
            with self.subTest(caractere=caractere):
                with self.assertRaises(ErroLexico):
                    AnalisadorLexico(f'"texto{caractere}"').tokenizar()

    def test_identificador_com_underscore(self):
        tokens = AnalisadorLexico("a_b x_1").tokenizar()
        self.assertEqual([token.tipo for token in tokens], ["IDENT", "IDENT", "EOF"])
        self.assertEqual([token.lexema for token in tokens[:2]], ["a_b", "x_1"])
        with self.assertRaises(ErroLexico):
            AnalisadorLexico("_x").tokenizar()

    def test_numero_multiplos_digitos(self):
        tokens = AnalisadorLexico("007 12345").tokenizar()
        self.assertEqual([token.tipo for token in tokens], ["NUM", "NUM", "EOF"])
        self.assertEqual([token.lexema for token in tokens[:2]], ["007", "12345"])

    def test_posicao_apos_quebra_linha(self):
        tokens = AnalisadorLexico("\n  x").tokenizar()
        self.assertEqual((tokens[0].linha, tokens[0].coluna), (2, 3))

    def test_comentario_fim_arquivo(self):
        tokens = AnalisadorLexico("x // comentario").tokenizar()
        self.assertEqual([token.lexema for token in tokens], ["x", ""])
        self.assertEqual(tokens[-1].tipo, "EOF")

    def test_entrada_vazia(self):
        tokens = AnalisadorLexico("").tokenizar()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].tipo, "EOF")

    def test_cadeia_nao_terminada_eof(self):
        with self.assertRaises(ErroLexico):
            AnalisadorLexico('"abc').tokenizar()

    def test_caractere_null(self):
        with self.assertRaises(ErroLexico):
            AnalisadorLexico("\x00").tokenizar()

    def test_simbolos_consecutivos(self):
        tokens = AnalisadorLexico("(){};.").tokenizar()
        self.assertEqual(
            [token.tipo for token in tokens],
            ["(", ")", "{", "}", ";", ".", "EOF"],
        )

    def test_tab_e_cr_como_espaco(self):
        tokens = AnalisadorLexico("\t x\r y").tokenizar()
        self.assertEqual([token.lexema for token in tokens], ["x", "y", ""])

    def test_erro_lexico_exibe_trecho_e_ponteiro(self):
        with self.assertRaises(ErroLexico) as contexto:
            AnalisadorLexico("x\n  @").tokenizar()
        mensagem = str(contexto.exception)
        self.assertIn("  @", mensagem)
        self.assertIn("  ^", mensagem)


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

    def test_funcao_com_retorno_e_variaveis_locais(self):
        compilar("program p; func f() int { var r int; return r; } { } .")

    def test_chamada_funcao_em_expressao(self):
        compilar("program p; var x int; { x = f(1) + 2; } .")

    def test_precedencia_completa(self):
        compilar("program p; var x int; { x = a + b * c - d / e; } .")

    def test_operadores_logicos_e_relacionais(self):
        compilar("program p; var b bool; { b = x > 1 and y < 2 or !z; } .")

    def test_bloco_aninhado_como_comando(self):
        compilar("program p; { { } } .")

    def test_print_com_expressao_complexa(self):
        compilar("program p; { print(a + b * 2); } .")

    def test_print_com_cadeia_vazia(self):
        compilar('program p; { print(""); } .')

    def test_cadeia_fora_de_print_falha(self):
        with self.assertRaises(ErroSintatico):
            compilar('program p; var x int; { x = "hello"; } .')

    def test_break_e_continue_exigem_ponto_virgula(self):
        compilar("program p; { while true { break; continue; } } .")
        with self.assertRaises(ErroSintatico):
            compilar("program p; { while true { break } } .")
        with self.assertRaises(ErroSintatico):
            compilar("program p; { while true { continue } } .")

    def test_return_com_e_sem_expressao(self):
        compilar(
            "program p; proc a() { return; } "
            "func b() int { return 1; } { a(); b(); } ."
        )

    def test_procedimento_sem_parametros(self):
        compilar("program p; proc a() { } { a(); } .")

    def test_funcao_com_multiplos_parametros(self):
        compilar(
            "program p; func f(a int, b int, c bool) int "
            "{ return a + b; } { f(1, 2, true); } ."
        )

    def test_while_com_expressao_complexa(self):
        compilar("program p; { while x > 0 and !done { break; } } .")

    def test_var_depois_de_subrotina_falha(self):
        with self.assertRaises(ErroSintatico):
            compilar("program p; proc a() { } var x int; { } .")

    def test_programa_sem_bloco_comandos(self):
        with self.assertRaises(ErroSintatico):
            compilar("program p; .")

    def test_negacao_dupla(self):
        compilar("program p; var x int; var b bool; { x = - - 5; b = !!true; } .")

    def test_parenteses_aninhados(self):
        compilar("program p; var x int; { x = ((1 + 2) * 3); } .")

    def test_chamada_procedimento_com_argumentos(self):
        compilar("program p; proc a(x int, y int, z int) { } { a(1, 2, 3); } .")

    def test_erro_sintatico_exibe_trecho_e_ponteiro(self):
        with self.assertRaises(ErroSintatico) as contexto:
            compilar("program p;\n{\n  x = ;\n} .")
        mensagem = str(contexto.exception)
        self.assertIn("  x = ;", mensagem)
        self.assertIn("      ^", mensagem)

    def test_recuperacao_reporta_multiplos_erros(self):
        codigo = "program p;\n{\n  x = ;\n  y = ;\n} ."
        tokens = AnalisadorLexico(codigo).tokenizar()
        with self.assertRaises(ErroSintatico) as contexto:
            AnalisadorSintatico(tokens).analisar()
        self.assertEqual(len(contexto.exception.erros), 2)
if __name__ == "__main__":
    unittest.main()
