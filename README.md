# Compilador ArithLang

Este repositório contém um compilador completo para a mini-linguagem **ArithLang**, desenvolvido para a disciplina de Compiladores e Linguagens Formais. O projeto implementa, de forma modular, as fases de análise léxica, análise sintática, construção da AST, análise semântica, geração de bytecode e execução em uma máquina virtual de pilha.

## Funcionalidades

A ArithLang suporta declarações com `let`, atribuições a variáveis já declaradas, comando `print`, comentários iniciados por `#`, números inteiros, números reais, negação unária e as quatro operações aritméticas básicas: soma, subtração, multiplicação e divisão. A precedência matemática é respeitada por um parser de descida recursiva, sem uso de geradores automáticos como PLY, ANTLR, Lark ou similares.

| Recurso | Status |
|---|---:|
| Lexer manual com linha e coluna | Implementado |
| Parser de descida recursiva | Implementado |
| AST com Visitor | Implementado |
| Análise semântica e tabela de símbolos | Implementado |
| Geração de bytecode para VM | Implementado |
| Máquina virtual de pilha | Implementado |
| CLI com arquivo, `-c` e `-v` | Implementado |
| Testes automatizados | 26 casos |

## Estrutura

```text
compilador_aritmetico/
├── compilador/              # pacote executável para python -m compilador
├── src/                     # fases do compilador
│   ├── lexer.py
│   ├── ast_nodes.py
│   ├── parser.py
│   ├── semantic.py
│   ├── codegen.py
│   ├── cli.py
│   └── errors.py
├── tests/
│   └── test_compiler.py
├── examples/
│   ├── exemplo1.al
│   ├── exemplo2.al
│   └── exemplo3.al
├── docs/
│   └── relatorio.pdf
├── README.md
└── .gitignore
```

## Como executar

É necessário Python 3.11 ou superior. A partir da raiz do repositório, execute um arquivo fonte com:

```bash
python -m compilador examples/exemplo1.al
```

Também é possível executar código inline com:

```bash
python -m compilador -c "let x = 10 * 2\nprint(x)"
```

Para visualizar tokens, AST, tabela de símbolos e bytecode antes da saída, use o modo verbose:

```bash
python -m compilador -v examples/exemplo2.al
```

## Como testar

A suíte usa apenas a biblioteca padrão `unittest`. Para executar todos os testes, rode:

```bash
python -m unittest discover -s tests -v
```

## Exemplo de programa

```arithlang
# Precedência e parênteses
let x = 2 + 3 * 4
let y = (2 + 3) * 4
print(x)
print(y)
print(x + y)
```

A saída esperada é:

```text
14
20
34
```

## Observação sobre uso de IA

Este projeto foi desenvolvido com auxílio de IA para aceleração de implementação, organização documental e revisão de testes. O relatório técnico declara explicitamente esse uso, conforme solicitado na atividade. Recomenda-se que os integrantes estudem cada módulo antes da apresentação oral, pois o código foi escrito de forma modular para facilitar a explicação linha a linha.
