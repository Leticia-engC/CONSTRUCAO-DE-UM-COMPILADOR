"""Análise semântica e tabela de símbolos da ArithLang."""

from __future__ import annotations

from .ast_nodes import (
    AssignStatement,
    BinaryOp,
    FloatLiteral,
    Identifier,
    IntLiteral,
    LetStatement,
    PrintStatement,
    Program,
    UnaryOp,
    Visitor,
)
from .errors import SemanticError


class SymbolTable:
    """Tabela de símbolos de escopo global único."""

    def __init__(self) -> None:
        self.symbols: dict[str, str] = {}

    def define(self, name: str, type_: str, line: int) -> None:
        if name in self.symbols:
            raise SemanticError(f"variável '{name}' já declarada", line)
        self.symbols[name] = type_

    def assign(self, name: str, type_: str, line: int) -> None:
        if name not in self.symbols:
            raise SemanticError(f"use 'let {name} = ...' para declarar", line)
        self.symbols[name] = self._promote(self.symbols[name], type_)

    def lookup(self, name: str, line: int) -> str:
        if name not in self.symbols:
            raise SemanticError(f"variável '{name}' usada sem declaração", line)
        return self.symbols[name]

    @staticmethod
    def _promote(left: str, right: str) -> str:
        if left == "float" or right == "float":
            return "float"
        return "int"


class SemanticAnalyzer(Visitor[str | None]):
    """Visitante semântico que valida variáveis e infere tipos."""

    def __init__(self) -> None:
        self.symbol_table = SymbolTable()

    def analyze(self, program: Program) -> SymbolTable:
        program.accept(self)
        return self.symbol_table

    def visit_program(self, node: Program) -> None:
        for statement in node.statements:
            statement.accept(self)
        return None

    def visit_let_statement(self, node: LetStatement) -> None:
        value_type = node.value.accept(self)
        assert isinstance(value_type, str)
        self.symbol_table.define(node.name, value_type, node.line)
        return None

    def visit_assign_statement(self, node: AssignStatement) -> None:
        value_type = node.value.accept(self)
        assert isinstance(value_type, str)
        self.symbol_table.assign(node.name, value_type, node.line)
        return None

    def visit_print_statement(self, node: PrintStatement) -> None:
        node.value.accept(self)
        return None

    def visit_binary_op(self, node: BinaryOp) -> str:
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)
        assert isinstance(left_type, str) and isinstance(right_type, str)
        if node.op == "/":
            return "float"
        if left_type == "float" or right_type == "float":
            return "float"
        return "int"

    def visit_unary_op(self, node: UnaryOp) -> str:
        operand_type = node.operand.accept(self)
        assert isinstance(operand_type, str)
        return operand_type

    def visit_int_literal(self, node: IntLiteral) -> str:
        return "int"

    def visit_float_literal(self, node: FloatLiteral) -> str:
        return "float"

    def visit_identifier(self, node: Identifier) -> str:
        return self.symbol_table.lookup(node.name, node.line)
