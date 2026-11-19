# Uso: python main.py <arquivo> [--tokens]

import argparse
import sys
from typing import Optional, Sequence

from compilador.analisador_lexico import AnalisadorLexico, ErroLexico
from compilador.analisador_sintatico import AnalisadorSintatico, ErroSintatico


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Analisadores léxico e sintático.")
    ap.add_argument("arquivo", help="arquivo com o código-fonte")
    ap.add_argument("--tokens", action="store_true", help="exibe a tabela de tokens")
    args = ap.parse_args(argv)

    try:
        with open(args.arquivo, encoding="utf-8-sig") as f:
            codigo = f.read()
    except OSError as e:
        print(f"Não foi possível abrir o arquivo: {e}")
        return 1

    # 1) Análise léxica
    try:
        tokens = AnalisadorLexico(codigo).tokenizar()
    except ErroLexico as e:
        print(f"[ERRO LÉXICO] {e}")
        return 1
    print(f"[1/2] Análise léxica concluída: {len(tokens) - 1} tokens")

    if args.tokens:
        print(f"{'LINHA':<6}{'COL':<6}{'TIPO':<12}LEXEMA")
        for t in tokens:
            print(f"{t.linha:<6}{t.coluna:<6}{t.tipo:<12}{t.lexema}")

    # 2) Análise sintática
    try:
        AnalisadorSintatico(tokens).analisar()
    except ErroSintatico as e:
        print(f"[ERRO SINTÁTICO] {e}")
        return 1
    print("[2/2] Análise sintática concluída: programa válido")
    return 0


if __name__ == "__main__":
    sys.exit(main())
