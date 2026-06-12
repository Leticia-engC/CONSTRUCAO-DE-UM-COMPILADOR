"""Exceções do compilador ArithLang."""

from __future__ import annotations


class CompilerError(Exception):
    """Classe-base para erros localizados do compilador."""

    phase = "Compilador"

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        if self.line is not None and self.column is not None:
            return f"Erro {self.phase} (L{self.line}:C{self.column}): {self.message}"
        if self.line is not None:
            return f"Erro {self.phase} (L{self.line}): {self.message}"
        return f"Erro {self.phase}: {self.message}"


class LexerError(CompilerError):
    """Erro encontrado durante a análise léxica."""

    phase = "Léxico"


class ParseError(CompilerError):
    """Erro encontrado durante a análise sintática."""

    phase = "Sintático"


class SemanticError(CompilerError):
    """Erro encontrado durante a análise semântica."""

    phase = "Semântico"


class VMRuntimeError(CompilerError):
    """Erro encontrado durante a execução da máquina virtual."""

    phase = "de Execução"

    def __str__(self) -> str:
        if self.line is not None:
            return f"Erro de Execução: {self.message} na linha {self.line}"
        return f"Erro de Execução: {self.message}"
