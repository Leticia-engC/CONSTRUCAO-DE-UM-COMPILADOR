"""Nós da Árvore Sintática Abstrata (AST) da ArithLang."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar


R = TypeVar("R")


class Visitor(Protocol[R]):
    """Interface de visitante para percorrer a AST."""

    def visit_program(self, node: "Program") -> R: ...
    def visit_let_statement(self, node: "LetStatement") -> R: ...
    def visit_assign_statement(self, node: "AssignStatement") -> R: ...
    def visit_print_statement(self, node: "PrintStatement") -> R: ...
    def visit_binary_op(self, node: "BinaryOp") -> R: ...
    def visit_unary_op(self, node: "UnaryOp") -> R: ...
    def visit_int_literal(self, node: "IntLiteral") -> R: ...
    def visit_float_literal(self, node: "FloatLiteral") -> R: ...
    def visit_identifier(self, node: "Identifier") -> R: ...


class Node:
    """Classe-base dos nós da AST."""

    def accept(self, visitor: Visitor[R]) -> R:
        raise NotImplementedError


class Statement(Node):
    """Classe-base para comandos."""


class Expression(Node):
    """Classe-base para expressões."""


@dataclass
class Program(Node):
    statements: list[Statement]

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_program(self)


@dataclass
class LetStatement(Statement):
    name: str
    value: Expression
    line: int

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_let_statement(self)


@dataclass
class AssignStatement(Statement):
    name: str
    value: Expression
    line: int

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_assign_statement(self)


@dataclass
class PrintStatement(Statement):
    value: Expression
    line: int

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_print_statement(self)


@dataclass
class BinaryOp(Expression):
    op: str
    left: Expression
    right: Expression
    line: int

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_binary_op(self)


@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression
    line: int

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_unary_op(self)


@dataclass
class IntLiteral(Expression):
    value: int
    line: int

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_int_literal(self)


@dataclass
class FloatLiteral(Expression):
    value: float
    line: int

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_float_literal(self)


@dataclass
class Identifier(Expression):
    name: str
    line: int

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_identifier(self)


class ASTPrinter(Visitor[str]):
    """Produz representação legível da AST para depuração."""

    def print(self, node: Node) -> str:
        return node.accept(self)

    def visit_program(self, node: Program) -> str:
        body = "\n".join("  " + stmt.accept(self) for stmt in node.statements)
        return f"Program(\n{body}\n)" if body else "Program()"

    def visit_let_statement(self, node: LetStatement) -> str:
        return f"Let({node.name}, {node.value.accept(self)})"

    def visit_assign_statement(self, node: AssignStatement) -> str:
        return f"Assign({node.name}, {node.value.accept(self)})"

    def visit_print_statement(self, node: PrintStatement) -> str:
        return f"Print({node.value.accept(self)})"

    def visit_binary_op(self, node: BinaryOp) -> str:
        return f"({node.op} {node.left.accept(self)} {node.right.accept(self)})"

    def visit_unary_op(self, node: UnaryOp) -> str:
        return f"({node.op} {node.operand.accept(self)})"

    def visit_int_literal(self, node: IntLiteral) -> str:
        return str(node.value)

    def visit_float_literal(self, node: FloatLiteral) -> str:
        return str(node.value)

    def visit_identifier(self, node: Identifier) -> str:
        return node.name
