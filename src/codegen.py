"""Geração de bytecode e Máquina Virtual da ArithLang."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
from .errors import VMRuntimeError


@dataclass(frozen=True)
class Instruction:
    """Instrução de bytecode para a máquina de pilha."""

    op: str
    args: tuple[Any, ...] = ()
    line: int | None = None

    def __iter__(self):
        yield self.op
        yield from self.args

    def __repr__(self) -> str:
        parts = [self.op, *(repr(arg) for arg in self.args)]
        if self.line is not None:
            parts.append(f"@L{self.line}")
        return " ".join(parts)


class CodeGenerator(Visitor[None]):
    """Gera instruções lineares por percurso pós-ordem da AST."""

    OPS = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV"}

    def __init__(self) -> None:
        self.instructions: list[Instruction] = []

    def generate(self, program: Program) -> list[Instruction]:
        self.instructions = []
        program.accept(self)
        self.instructions.append(Instruction("HALT"))
        return self.instructions

    def emit(self, op: str, *args: Any, line: int | None = None) -> None:
        self.instructions.append(Instruction(op, args, line))

    def visit_program(self, node: Program) -> None:
        for statement in node.statements:
            statement.accept(self)
        return None

    def visit_let_statement(self, node: LetStatement) -> None:
        node.value.accept(self)
        self.emit("STORE", node.name, line=node.line)
        return None

    def visit_assign_statement(self, node: AssignStatement) -> None:
        node.value.accept(self)
        self.emit("STORE", node.name, line=node.line)
        return None

    def visit_print_statement(self, node: PrintStatement) -> None:
        node.value.accept(self)
        self.emit("PRINT", line=node.line)
        return None

    def visit_binary_op(self, node: BinaryOp) -> None:
        node.left.accept(self)
        node.right.accept(self)
        self.emit(self.OPS[node.op], line=node.line)
        return None

    def visit_unary_op(self, node: UnaryOp) -> None:
        node.operand.accept(self)
        self.emit("NEG", line=node.line)
        return None

    def visit_int_literal(self, node: IntLiteral) -> None:
        self.emit("PUSH", node.value, line=node.line)
        return None

    def visit_float_literal(self, node: FloatLiteral) -> None:
        self.emit("PUSH", node.value, line=node.line)
        return None

    def visit_identifier(self, node: Identifier) -> None:
        self.emit("LOAD", node.name, line=node.line)
        return None


class VirtualMachine:
    """Executor de bytecode baseado em pilha."""

    def __init__(self) -> None:
        self.stack: list[Any] = []
        self.env: dict[str, Any] = {}
        self.output: list[str] = []

    def run(self, instructions: list[Instruction]) -> list[str]:
        """Executa instruções e retorna as linhas impressas."""
        self.stack = []
        self.env = {}
        self.output = []

        for instruction in instructions:
            op = instruction.op
            args = instruction.args

            if op == "PUSH":
                self.stack.append(args[0])
            elif op == "LOAD":
                self.stack.append(self.env[args[0]])
            elif op == "STORE":
                self.env[args[0]] = self.stack.pop()
            elif op == "ADD":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)
            elif op == "SUB":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a - b)
            elif op == "MUL":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a * b)
            elif op == "DIV":
                b, a = self.stack.pop(), self.stack.pop()
                if b == 0:
                    raise VMRuntimeError("divisão por zero", instruction.line)
                self.stack.append(a / b)
            elif op == "NEG":
                self.stack.append(-self.stack.pop())
            elif op == "PRINT":
                self.output.append(str(self.stack.pop()))
            elif op == "HALT":
                break
            else:
                raise VMRuntimeError(f"instrução desconhecida '{op}'", instruction.line)

        return self.output
