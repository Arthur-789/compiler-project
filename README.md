<p align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="90" alt="Python Logo" />
</p>

<h1 align="center">Compilador Educacional</h1>

<p align="center">
  Analisadores léxico e sintático descendente recursivo LL(1) para a disciplina de Compiladores da UFAPE.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.7+" />
  <img src="https://img.shields.io/badge/Parser-LL(1)-blueviolet?style=for-the-badge" alt="Parser LL(1)" />
  <img src="https://img.shields.io/badge/Testes-unittest-green?style=for-the-badge" alt="Testes unittest" />
</p>

## Sobre o projeto

Este projeto implementa um compilador educacional em Python, desenvolvido para a disciplina de Compiladores da Universidade Federal do Agreste de Pernambuco (UFAPE). O trabalho é de autoria de **Arthur Roberto Araújo Tavares** e **Luís Henrique Domingos da Silva** e valida programas conforme a gramática BNF fornecida pela disciplina.

## Estrutura

```text
.
├── compilador/
│   ├── analisador_lexico.py
│   ├── analisador_sintatico.py
│   ├── tokens.py
│   └── __main__.py
├── exemplos/                 # Programas válidos e casos de erro
├── tests/
│   └── test_compilador.py
├── main.py                   # Interface de linha de comando
├── gramatica.pdf             # Especificação BNF
└── melhorias.md              # Próximas melhorias planejadas
```

## Pré-requisitos

- Python 3.7 ou superior

Verifique a versão instalada:

```bash
python --version
```

## Como usar

Analise um programa com o script principal:

```bash
python main.py exemplos/valido.txt
```

Ou execute o pacote como módulo:

```bash
python -m compilador exemplos/valido.txt
```

Para exibir a tabela de tokens:

```bash
python main.py exemplos/valido.txt --tokens
```

O comando informa o resultado da análise léxica e sintática. Em caso de erro, a mensagem apresenta a linha do código, a coluna e um ponteiro visual:

```text
[ERRO SINTÁTICO] Linha 4, coluna 9: esperado expressão, encontrado ';'
        x = ;
            ^
```

O parser utiliza recuperação em modo pânico, sincronizando em `;`, `}` ou `{` para continuar a análise e reportar múltiplos erros sintáticos na mesma execução.

## Arquitetura

### Analisador léxico

`compilador/analisador_lexico.py` transforma o código-fonte em tokens:

- palavras reservadas, identificadores e números;
- operadores e símbolos da linguagem;
- cadeias de caracteres com validação;
- comentários de linha e espaços em branco;
- erros com posição, trecho da linha e ponteiro visual.

A construção de lexemas usa buffers de caracteres e `"".join()` para evitar
concatenação repetida de strings.

### Analisador sintático

`compilador/analisador_sintatico.py` implementa um parser descendente recursivo
LL(1), mantendo a gramática BNF da disciplina intacta. O parser valida:

- estrutura do programa e blocos;
- variáveis, funções e procedimentos;
- comandos condicionais, laços e desvios;
- chamadas e expressões com precedência;
- recuperação de erros e agregação de diagnósticos.

## Testes

A suíte usa somente `unittest` da biblioteca padrão:

```bash
python -m unittest discover tests
```

Para executar com detalhes:

```bash
python -m unittest discover tests -v
```

Os testes cobrem o lexer, o parser, expressões, sub-rotinas, escopos, comandos de controle, cadeias, casos inválidos, diagnósticos visuais e recuperação de múltiplos erros.

## Licença

Consulte [LICENSE](LICENSE).
