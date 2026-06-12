"""Interface de linha de comando para a ArithLang."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import ASTPrinter, CompilerError, VirtualMachine, compile_source


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m compilador",
        description="Compilador e executor da linguagem ArithLang.",
    )
    parser.add_argument("file", nargs="?", help="arquivo fonte .al a executar")
    parser.add_argument("-c", "--code", help="código ArithLang inline")
    parser.add_argument("-v", "--verbose", action="store_true", help="exibe tokens, AST e bytecode")
    return parser


def read_source(args: argparse.Namespace) -> str:
    if args.code is not None:
        return args.code
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    raise SystemExit("Informe um arquivo fonte ou use -c para código inline.")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        source = read_source(args)
        tokens, ast, symbols, bytecode = compile_source(source)

        if args.verbose:
            visible_tokens = [token for token in tokens]
            print("TOKENS:")
            for token in visible_tokens:
                print(f"  {token}")
            print("\nAST:")
            print(ASTPrinter().print(ast))
            print("\nTABELA DE SÍMBOLOS:")
            for name, type_ in symbols.symbols.items():
                print(f"  {name}: {type_}")
            print("\nBYTECODE:")
            for index, instruction in enumerate(bytecode):
                print(f"  {index:03d}: {instruction}")
            print("\nSAÍDA:")

        output = VirtualMachine().run(bytecode)
        for line in output:
            print(line)
        return 0
    except CompilerError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Arquivo não encontrado: {exc.filename}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
