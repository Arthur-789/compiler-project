# Analisador léxico - transforma o código-fonte em uma lista de tokens.

import string
from .tokens import PALAVRAS_RESERVADAS, Token

SIMBOLOS_DUPLOS = {"==", "!=", ">=", "<="}
SIMBOLOS_SIMPLES = set("+-*/=<>!(){};,.")
ESPACOS = {" ", "\t", "\r", "\n"}

# Caracteres permitidos dentro de uma cadeia
CARACTERES_CADEIA = (
    set(string.ascii_letters + string.digits + "!#$%&'()*+,-./:;<=>?@_[]{}|")
    | {" "}
)


class ErroLexico(Exception):
    pass


class AnalisadorLexico:
    def __init__(self, codigo):
        self.codigo = codigo
        self.pos = 0
        self.linha = 1
        self.coluna = 1

    # ---------- utilidades ----------
    def _atual(self):
        return self.codigo[self.pos] if self.pos < len(self.codigo) else ""

    def _proximo(self):
        return self.codigo[self.pos + 1] if self.pos + 1 < len(self.codigo) else ""

    def _avancar(self):
        c = self.codigo[self.pos]
        self.pos += 1
        if c == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c

    def _erro(self, mensagem, linha, coluna):
        raise ErroLexico(f"Linha {linha}, coluna {coluna}: {mensagem}")

    @staticmethod
    def _eh_letra(c):
        return c.isascii() and c.isalpha()

    @staticmethod
    def _eh_digito(c):
        return c.isascii() and c.isdigit()

    # ---------- análise ----------
    def tokenizar(self):
        tokens = []
        while True:
            self._ignorar_espacos_e_comentarios()
            if self.pos >= len(self.codigo):
                break
            tokens.append(self._proximo_token())
        tokens.append(Token("EOF", "", self.linha, self.coluna))
        return tokens

    def _ignorar_espacos_e_comentarios(self):
        while True:
            c = self._atual()
            if c in ESPACOS:
                self._avancar()
            elif c == "/" and self._proximo() == "/":
                while self._atual() != "" and self._atual() != "\n":
                    self._avancar()
            else:
                break

    def _proximo_token(self):
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
            return Token(par, par, linha, coluna)
        if c in SIMBOLOS_SIMPLES:
            self._avancar()
            return Token(c, c, linha, coluna)

        self._erro(f"caractere inválido '{c}'", linha, coluna)

    def _identificador(self, linha, coluna):
        lexema = ""
        while self._eh_letra(self._atual()) or self._eh_digito(self._atual()) or self._atual() == "_":
            lexema += self._avancar()
        tipo = lexema if lexema in PALAVRAS_RESERVADAS else "IDENT"
        return Token(tipo, lexema, linha, coluna)

    def _numero(self, linha, coluna):
        lexema = ""
        while self._eh_digito(self._atual()):
            lexema += self._avancar()
        return Token("NUM", lexema, linha, coluna)

    def _cadeia(self, linha, coluna):
        self._avancar()  # abre aspas
        conteudo = ""
        while True:
            c = self._atual()
            if c == "" or c == "\n":
                self._erro("cadeia não terminada (faltou fechar aspas)", linha, coluna)
            if c == '"':
                self._avancar()  # fecha aspas
                return Token("CADEIA", conteudo, linha, coluna)
            if c not in CARACTERES_CADEIA:
                self._erro(f"caractere inválido '{c}' dentro da cadeia", self.linha, self.coluna)
            conteudo += self._avancar()
