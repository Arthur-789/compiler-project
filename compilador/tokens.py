# Definição de Token e das palavras reservadas da linguagem.

from dataclasses import dataclass

PALAVRAS_RESERVADAS = {
    "program", "var", "func", "proc", "int", "bool", "if", "else",
    "while", "return", "break", "continue", "print", "true", "false",
    "and", "or",
}


@dataclass
class Token:
    """
    tipo:
      - palavras reservadas e símbolos: o próprio texto (ex: "program", "==", "{")
      - demais: "IDENT", "NUM", "CADEIA" ou "EOF"
    """
    tipo: str
    lexema: str
    linha: int
    coluna: int
