"""Compilador ArithLang com pipeline lexer-parser-semântica-codegen-VM."""

from __future__ import annotations

from .ast_nodes import ASTPrinter, Program
from .codegen import CodeGenerator, Instruction, VirtualMachine
from .errors import CompilerError, LexerError, ParseError, SemanticError, VMRuntimeError
from .lexer import Lexer, Token, TokenType
from .parser import Parser
from .semantic import SemanticAnalyzer, SymbolTable


def compile_source(source: str) -> tuple[list[Token], Program, SymbolTable, list[Instruction]]:
    """Executa as quatro primeiras fases e retorna artefatos intermediários."""
    tokens = Lexer().tokenize(source)
    ast = Parser().parse(tokens)
    symbols = SemanticAnalyzer().analyze(ast)
    bytecode = CodeGenerator().generate(ast)
    return tokens, ast, symbols, bytecode


def run_source(source: str) -> list[str]:
    """Compila e executa um programa ArithLang, retornando as saídas."""
    _, _, _, bytecode = compile_source(source)
    return VirtualMachine().run(bytecode)


__all__ = [
    "ASTPrinter",
    "CodeGenerator",
    "CompilerError",
    "Instruction",
    "Lexer",
    "LexerError",
    "ParseError",
    "Parser",
    "Program",
    "SemanticAnalyzer",
    "SemanticError",
    "SymbolTable",
    "Token",
    "TokenType",
    "VMRuntimeError",
    "VirtualMachine",
    "compile_source",
    "run_source",
]
