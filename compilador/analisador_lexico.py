# Analisador léxico - transforma o código-fonte em uma lista de tokens.

import string
from typing import List, NoReturn, Set

from .tokens import PALAVRAS_RESERVADAS, Token

SIMBOLOS_DUPLOS: Set[str] = {"==", "!=", ">=", "<="}
SIMBOLOS_SIMPLES: Set[str] = set("+-*/=<>!(){};,.")
ESPACOS: Set[str] = {" ", "\t", "\r", "\n"}

# Caracteres permitidos dentro de uma cadeia
CARACTERES_CADEIA: Set[str] = (
    set(string.ascii_letters + string.digits + "!#$%&'()*+,-./:;<=>?@_[]{}|")
    | {" "}
)


class ErroLexico(Exception):
    pass


class AnalisadorLexico:
    def __init__(self, codigo: str) -> None:
        self.codigo = codigo
        self.linhas = codigo.split("\n")
        self.pos = 0
        self.linha = 1
        self.coluna = 1

    # ---------- utilidades ----------
    def _atual(self) -> str:
        return self.codigo[self.pos] if self.pos < len(self.codigo) else ""

    def _proximo(self) -> str:
        return self.codigo[self.pos + 1] if self.pos + 1 < len(self.codigo) else ""

    def _avancar(self) -> str:
        c = self.codigo[self.pos]
        self.pos += 1
        if c == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c

    def _erro(self, mensagem: str, linha: int, coluna: int) -> NoReturn:
        trecho = self.linhas[linha - 1] if linha <= len(self.linhas) else ""
        ponteiro = " " * max(coluna - 1, 0) + "^"
        raise ErroLexico(
            f"Linha {linha}, coluna {coluna}: {mensagem}\n"
            f"{trecho}\n{ponteiro}"
        )

    @staticmethod
    def _eh_letra(c: str) -> bool:
        return c.isascii() and c.isalpha()

    @staticmethod
    def _eh_digito(c: str) -> bool:
        return c.isascii() and c.isdigit()

    # ---------- análise ----------
    def tokenizar(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            self._ignorar_espacos_e_comentarios()
            if self.pos >= len(self.codigo):
                break
            tokens.append(self._proximo_token())
        tokens.append(self._token("EOF", "", self.linha, self.coluna))
        return tokens

    def _token(self, tipo: str, lexema: str, linha: int, coluna: int) -> Token:
        trecho = self.linhas[linha - 1] if linha <= len(self.linhas) else ""
        return Token(tipo, lexema, linha, coluna, trecho)

    def _ignorar_espacos_e_comentarios(self) -> None:
        while True:
            c = self._atual()
            if c in ESPACOS:
                self._avancar()
            elif c == "/" and self._proximo() == "/":
                while self._atual() != "" and self._atual() != "\n":
                    self._avancar()
            else:
                break

    def _proximo_token(self) -> Token:
        linha, coluna = self.linha, self.coluna
        c = self._atual()

        if self._eh_letra(c):
            return self._identificador(linha, coluna)
        if self._eh_digito(c):
            return self._numero(linha, coluna)
        if c == '"':
            return self._cadeia(linha, coluna)

        par = c + self._proximo()
        if par in SIMBOLOS_DUPLOS:
            self._avancar()
            self._avancar()
            return self._token(par, par, linha, coluna)
        if c in SIMBOLOS_SIMPLES:
            self._avancar()
            return self._token(c, c, linha, coluna)

        self._erro(f"caractere inválido '{c}'", linha, coluna)

    def _identificador(self, linha: int, coluna: int) -> Token:
        partes: List[str] = []
        while self._eh_letra(self._atual()) or self._eh_digito(self._atual()) or self._atual() == "_":
            partes.append(self._avancar())
        lexema = "".join(partes)
        tipo = lexema if lexema in PALAVRAS_RESERVADAS else "IDENT"
        return self._token(tipo, lexema, linha, coluna)

    def _numero(self, linha: int, coluna: int) -> Token:
        partes: List[str] = []
        while self._eh_digito(self._atual()):
            partes.append(self._avancar())
        return self._token("NUM", "".join(partes), linha, coluna)

    def _cadeia(self, linha: int, coluna: int) -> Token:
        self._avancar()  # abre aspas
        partes: List[str] = []
        while True:
            c = self._atual()
            if c == "" or c == "\n":
                self._erro("cadeia não terminada (faltou fechar aspas)", linha, coluna)
            if c == '"':
                self._avancar()  # fecha aspas
                return self._token("CADEIA", "".join(partes), linha, coluna)
            if c not in CARACTERES_CADEIA:
                self._erro(f"caractere inválido '{c}' dentro da cadeia", self.linha, self.coluna)
            partes.append(self._avancar())
