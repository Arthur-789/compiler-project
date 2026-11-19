# Analisador sintático descendente recursivo (LL(1)).
# Cada regra da BNF corresponde a um método. Em caso de erro, lança ErroSintatico.

from __future__ import annotations

from typing import Dict, List, NoReturn, Optional, Sequence, Set

from .tokens import Token

PRIMEIRO_COMANDO: Set[str] = {
    "IDENT", "return", "break", "continue", "print", "if", "while", "{"
}
PRIMEIRO_EXPRESSAO: Set[str] = {"IDENT", "NUM", "true", "false", "(", "!", "-"}
OPERADORES_RELACIONAIS: Set[str] = {"==", "!=", ">", ">=", "<", "<="}

NOMES: Dict[str, str] = {
    "IDENT": "identificador",
    "NUM": "número",
    "CADEIA": "cadeia",
    "EOF": "fim do arquivo",
}


def _nome(tipo: str) -> str:
    return NOMES.get(tipo, f"'{tipo}'")


class ErroSintatico(Exception):
    def __init__(
        self, mensagem: str, erros: Optional[List["ErroSintatico"]] = None
    ) -> None:
        super().__init__(mensagem)
        self.erros = erros if erros is not None else [self]


class AnalisadorSintatico:
    def __init__(self, tokens: Sequence[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.erros: List[ErroSintatico] = []

    # ---------- utilidades ----------
    @property
    def atual(self) -> Token:
        return self.tokens[self.pos]

    def _avancar(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.tipo != "EOF":
            self.pos += 1
        return tok

    def _consumir(self, tipo: str) -> Token:
        if self.atual.tipo == tipo:
            return self._avancar()
        self._erro(_nome(tipo))

    def _erro(self, esperado: str) -> NoReturn:
        tok = self.atual
        if tok.tipo == "EOF":
            encontrado = "fim do arquivo"
        elif tok.tipo == "CADEIA":
            encontrado = f'cadeia "{tok.lexema}"'
        else:
            encontrado = f"'{tok.lexema}'"
        mensagem = (
            f"Linha {tok.linha}, coluna {tok.coluna}: "
            f"esperado {esperado}, encontrado {encontrado}"
        )
        if tok.trecho:
            mensagem += f"\n{tok.trecho}\n{' ' * max(tok.coluna - 1, 0)}^"
        raise ErroSintatico(mensagem)

    def _sincronizar(self) -> None:
        sincronizacao: Set[str] = {";", "}", "{"}
        while self.atual.tipo not in sincronizacao and self.atual.tipo != "EOF":
            self._avancar()
        if self.atual.tipo == ";":
            self._avancar()

    def _registrar_e_sincronizar(self, erro: ErroSintatico) -> None:
        self.erros.append(erro)
        self._sincronizar()

    # ---------- ponto de entrada ----------
    def analisar(self) -> None:
        try:
            self.programa()
        except ErroSintatico as erro:
            self._registrar_e_sincronizar(erro)
        if self.erros:
            mensagem = "\n\n".join(str(erro) for erro in self.erros)
            raise ErroSintatico(mensagem, self.erros)

    # ---------- estrutura ----------
    def programa(self) -> None:
        self._consumir("program")
        self._consumir("IDENT")
        self._consumir(";")
        self.bloco()
        self._consumir(".")
        self._consumir("EOF")

    def bloco(self) -> None:
        while self.atual.tipo == "var":
            try:
                self.declaracao_variavel()
                self._consumir(";")
            except ErroSintatico as erro:
                self._registrar_e_sincronizar(erro)
        while self.atual.tipo in ("proc", "func"):
            try:
                self.declaracao_subrotina()
            except ErroSintatico as erro:
                self._registrar_e_sincronizar(erro)
        self.comandos()

    # ---------- declarações ----------
    def declaracao_variavel(self) -> None:
        self._consumir("var")
        self._consumir("IDENT")
        self.tipo()

    def tipo(self) -> None:
        if self.atual.tipo in ("int", "bool"):
            self._avancar()
        else:
            self._erro("'int' ou 'bool'")

    def declaracao_subrotina(self) -> None:
        eh_funcao = self.atual.tipo == "func"
        self._avancar()
        self._consumir("IDENT")
        self._consumir("(")
        if self.atual.tipo == "IDENT":
            self.lista_parametros()
        self._consumir(")")
        if eh_funcao:
            self.tipo()
        self.corpo_subrotina()

    def corpo_subrotina(self) -> None:
        self._consumir("{")
        while self.atual.tipo == "var":
            try:
                self.declaracao_variavel()
                self._consumir(";")
            except ErroSintatico as erro:
                self._registrar_e_sincronizar(erro)
        while self.atual.tipo in ("proc", "func"):
            try:
                self.declaracao_subrotina()
            except ErroSintatico as erro:
                self._registrar_e_sincronizar(erro)
        self.lista_comandos()
        self._consumir("}")

    def lista_parametros(self) -> None:
        self.parametro()
        while self.atual.tipo == ",":
            self._avancar()
            self.parametro()

    def parametro(self) -> None:
        self._consumir("IDENT")
        self.tipo()

    # ---------- comandos ----------
    def comandos(self) -> None:
        self._consumir("{")
        self.lista_comandos()
        self._consumir("}")

    def lista_comandos(self) -> None:
        while self.atual.tipo in PRIMEIRO_COMANDO:
            try:
                self.comando()
            except ErroSintatico as erro:
                self._registrar_e_sincronizar(erro)

    def comando(self) -> None:
        if self.atual.tipo in ("if", "while", "{"):
            self.comando_estruturado()
        else:
            self.comando_simples()
            self._consumir(";")

    def comando_simples(self) -> None:
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

    def comando_estruturado(self) -> None:
        t = self.atual.tipo
        if t == "if":
            self.comando_condicional()
        elif t == "while":
            self.comando_enquanto()
        else:
            self.comandos()

    def comando_iniciado_por_identificador(self) -> None:
        self._consumir("IDENT")
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

    def comando_condicional(self) -> None:
        self._consumir("if")
        self.expressao()
        self.comandos()
        if self.atual.tipo == "else":
            self._avancar()
            self.comandos()

    def comando_enquanto(self) -> None:
        self._consumir("while")
        self.expressao()
        self.comandos()

    def comando_retorno(self) -> None:
        self._consumir("return")
        if self.atual.tipo in PRIMEIRO_EXPRESSAO:
            self.expressao()

    def comando_escrita(self) -> None:
        self._consumir("print")
        self._consumir("(")
        if self.atual.tipo == "CADEIA":
            self._avancar()
        else:
            self.expressao()
        self._consumir(")")

    def lista_argumentos(self) -> None:
        self.expressao()
        while self.atual.tipo == ",":
            self._avancar()
            self.expressao()

    # ---------- expressões ----------
    def expressao(self) -> None:
        self.expressao_ou()

    def expressao_ou(self) -> None:
        self.expressao_e()
        while self.atual.tipo == "or":
            self._avancar()
            self.expressao_e()

    def expressao_e(self) -> None:
        self.expressao_relacional()
        while self.atual.tipo == "and":
            self._avancar()
            self.expressao_relacional()

    def expressao_relacional(self) -> None:
        self.expressao_aritmetica()
        if self.atual.tipo in OPERADORES_RELACIONAIS:
            self._avancar()
            self.expressao_aritmetica()

    def expressao_aritmetica(self) -> None:
        self.termo()
        while self.atual.tipo in ("+", "-"):
            self._avancar()
            self.termo()

    def termo(self) -> None:
        self.fator()
        while self.atual.tipo in ("*", "/"):
            self._avancar()
            self.fator()

    def fator(self) -> None:
        t = self.atual.tipo
        if t == "IDENT":
            self._avancar()
            if self.atual.tipo == "(":
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
