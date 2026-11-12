# Analisador sintático descendente recursivo (LL(1)).
# Cada regra da BNF corresponde a um método. Em caso de erro, lança ErroSintatico.

PRIMEIRO_COMANDO = {"IDENT", "return", "break", "continue", "print", "if", "while", "{"}
PRIMEIRO_EXPRESSAO = {"IDENT", "NUM", "true", "false", "(", "!", "-"}
OPERADORES_RELACIONAIS = {"==", "!=", ">", ">=", "<", "<="}

NOMES = {"IDENT": "identificador", "NUM": "número", "CADEIA": "cadeia", "EOF": "fim do arquivo"}


def _nome(tipo):
    return NOMES.get(tipo, f"'{tipo}'")


class ErroSintatico(Exception):
    pass


class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---------- utilidades ----------
    @property
    def atual(self):
        return self.tokens[self.pos]

    def _avancar(self):
        tok = self.tokens[self.pos]
        if tok.tipo != "EOF":
            self.pos += 1
        return tok

    def _consumir(self, tipo):
        if self.atual.tipo == tipo:
            return self._avancar()
        self._erro(_nome(tipo))

    def _erro(self, esperado):
        tok = self.atual
        if tok.tipo == "EOF":
            encontrado = "fim do arquivo"
        elif tok.tipo == "CADEIA":
            encontrado = f'cadeia "{tok.lexema}"'
        else:
            encontrado = f"'{tok.lexema}'"
        raise ErroSintatico(
            f"Linha {tok.linha}, coluna {tok.coluna}: esperado {esperado}, encontrado {encontrado}"
        )

    # ---------- ponto de entrada ----------
    def analisar(self):
        self.programa()

    # ---------- estrutura ----------
    def programa(self):
        self._consumir("program")
        self._consumir("IDENT")
        self._consumir(";")
        self.bloco()
        self._consumir(".")
        self._consumir("EOF")

    def bloco(self):
        while self.atual.tipo == "var":
            self.declaracao_variavel()
            self._consumir(";")
        while self.atual.tipo in ("proc", "func"):
            self.declaracao_subrotina()
        self.comandos()

    # ---------- declarações ----------
    def declaracao_variavel(self):
        self._consumir("var")
        self._consumir("IDENT")
        self.tipo()

    def tipo(self):
        if self.atual.tipo in ("int", "bool"):
            self._avancar()
        else:
            self._erro("'int' ou 'bool'")

    def declaracao_subrotina(self):
        eh_funcao = self.atual.tipo == "func"
        self._avancar()  # proc ou func
        self._consumir("IDENT")
        self._consumir("(")
        if self.atual.tipo == "IDENT":
            self.lista_parametros()
        self._consumir(")")
        if eh_funcao:
            self.tipo()
        self.corpo_subrotina()

    def corpo_subrotina(self):
        # Ajuste em relação à BNF original: no exemplo, as variáveis de
        # proc/func ficam DENTRO das chaves.
        self._consumir("{")
        while self.atual.tipo == "var":
            self.declaracao_variavel()
            self._consumir(";")
        while self.atual.tipo in ("proc", "func"):
            self.declaracao_subrotina()
        self.lista_comandos()
        self._consumir("}")

    def lista_parametros(self):
        self.parametro()
        while self.atual.tipo == ",":
            self._avancar()
            self.parametro()

    def parametro(self):
        self._consumir("IDENT")
        self.tipo()

    # ---------- comandos ----------
    def comandos(self):
        self._consumir("{")
        self.lista_comandos()
        self._consumir("}")

    def lista_comandos(self):
        while self.atual.tipo in PRIMEIRO_COMANDO:
            self.comando()

    def comando(self):
        if self.atual.tipo in ("if", "while", "{"):
            self.comando_estruturado()
        else:
            self.comando_simples()
            self._consumir(";")

    def comando_simples(self):
        t = self.atual.tipo
        if t == "IDENT":
            self.comando_iniciado_por_identificador()
        elif t == "return":
            self.comando_retorno()
        elif t in ("break", "continue"):
            self._avancar()
        elif t == "print":
            self.comando_escrita()
        else:
            self._erro("comando")

    def comando_estruturado(self):
        t = self.atual.tipo
        if t == "if":
            self.comando_condicional()
        elif t == "while":
            self.comando_enquanto()
        else:
            self.comandos()

    def comando_iniciado_por_identificador(self):
        self._consumir("IDENT")
        # <resto do comando>
        if self.atual.tipo == "=":
            self._avancar()
            self.expressao()
        elif self.atual.tipo == "(":
            self._avancar()
            if self.atual.tipo in PRIMEIRO_EXPRESSAO:
                self.lista_argumentos()
            self._consumir(")")
        else:
            self._erro("'=' ou '('")

    def comando_condicional(self):
        self._consumir("if")
        self.expressao()
        self.comandos()
        if self.atual.tipo == "else":
            self._avancar()
            self.comandos()

    def comando_enquanto(self):
        self._consumir("while")
        self.expressao()
        self.comandos()

    def comando_retorno(self):
        self._consumir("return")
        if self.atual.tipo in PRIMEIRO_EXPRESSAO:
            self.expressao()

    def comando_escrita(self):
        self._consumir("print")
        self._consumir("(")
        if self.atual.tipo == "CADEIA":
            self._avancar()
        else:
            self.expressao()
        self._consumir(")")

    def lista_argumentos(self):
        self.expressao()
        while self.atual.tipo == ",":
            self._avancar()
            self.expressao()

    # ---------- expressões ----------
    def expressao(self):
        self.expressao_ou()

    def expressao_ou(self):
        self.expressao_e()
        while self.atual.tipo == "or":
            self._avancar()
            self.expressao_e()

    def expressao_e(self):
        self.expressao_relacional()
        while self.atual.tipo == "and":
            self._avancar()
            self.expressao_relacional()

    def expressao_relacional(self):
        self.expressao_aritmetica()
        if self.atual.tipo in OPERADORES_RELACIONAIS:
            self._avancar()
            self.expressao_aritmetica()

    def expressao_aritmetica(self):
        self.termo()
        while self.atual.tipo in ("+", "-"):
            self._avancar()
            self.termo()

    def termo(self):
        self.fator()
        while self.atual.tipo in ("*", "/"):
            self._avancar()
            self.fator()

    def fator(self):
        t = self.atual.tipo
        if t == "IDENT":
            self._avancar()
            if self.atual.tipo == "(":  # chamada de função
                self._avancar()
                if self.atual.tipo in PRIMEIRO_EXPRESSAO:
                    self.lista_argumentos()
                self._consumir(")")
        elif t in ("NUM", "true", "false"):
            self._avancar()
        elif t == "(":
            self._avancar()
            self.expressao()
            self._consumir(")")
        elif t in ("!", "-"):
            self._avancar()
            self.fator()
        else:
            self._erro("expressão (identificador, número, true, false, '(', '!' ou '-')")
