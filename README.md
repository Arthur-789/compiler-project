# Analisadores Léxico e Sintático

Projeto de Compiladores: o código passa primeiro pelo analisador léxico e depois pelo sintático (descendente recursivo, LL(1)).

## Requisitos
- Python 3.7 ou superior

## Como usar
```bash
python main.py exemplos/valido.txt            # analisa um arquivo
python main.py exemplos/valido.txt --tokens   # também mostra a tabela de tokens
python main.py exemplos/erro_lexico.txt       # exemplo de erro léxico
python main.py exemplos/erro_sintatico.txt    # exemplo de erro sintático
```

Saída para um programa válido:
```
[1/2] Análise léxica concluída: 230 tokens
[2/2] Análise sintática concluída: programa válido
```

Saída para erros (a análise para no primeiro erro):
```
[ERRO LÉXICO] Linha 4, coluna 11: caractere inválido '@'
[ERRO SINTÁTICO] Linha 5, coluna 5: esperado ';', encontrado 'print'
```

## Testes
```bash
python -m unittest discover tests
```

## Estrutura
```
.
├── main.py                              # ponto de entrada (léxico -> sintático)
├── compilador/
│   ├── tokens.py                        # classe Token e palavras reservadas
│   ├── analisador_lexico.py             # AnalisadorLexico, ErroLexico
│   └── analisador_sintatico.py          # AnalisadorSintatico, ErroSintatico
├── exemplos/                            # programas de teste
└── tests/test_compilador.py             # testes automatizados
```

## Como funciona
| Etapa | Entrada | Saída |
|-------|---------|-------|
| Léxico | texto do programa | lista de `Token(tipo, lexema, linha, coluna)` |
| Sintático | lista de tokens | sucesso, ou `ErroSintatico` com linha e coluna |

- Tokens de palavras reservadas e símbolos têm como `tipo` o próprio texto (`"program"`, `"=="`, `"{"`).
- Os demais tipos são `IDENT`, `NUM`, `CADEIA` e `EOF`.
- Cada regra da BNF é um método do `AnalisadorSintatico` com o mesmo nome (ex: `<comando condicional>` é `comando_condicional`).
- Comentários `//` são removidos no léxico.
- Cadeias aceitam apenas os caracteres definidos na BNF (letras ASCII sem acento, dígitos, símbolos listados e espaço).