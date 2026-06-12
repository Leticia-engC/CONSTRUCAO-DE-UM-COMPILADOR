"""Analisador léxico manual da linguagem ArithLang."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from .errors import LexerError


class TokenType(Enum):
    """Tipos de tokens reconhecidos pela linguagem."""

    INTEGER = auto()
    FLOAT = auto()
    IDENTIFIER = auto()
    LET = auto()
    PRINT = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    ASSIGN = auto()
    LPAREN = auto()
    RPAREN = auto()
    SEMICOLON = auto()
    NEWLINE = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """Token produzido pelo lexer com posição de origem."""

    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:C{self.column})"


class Lexer:
    """Lexer implementado por varredura caractere a caractere."""

    KEYWORDS = {"let": TokenType.LET, "print": TokenType.PRINT}
    SINGLE_CHAR_TOKENS = {
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.STAR,
        "/": TokenType.SLASH,
        "=": TokenType.ASSIGN,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
        ";": TokenType.SEMICOLON,
    }

    def tokenize(self, source: str) -> list[Token]:
        """Converte código-fonte em uma lista completa de tokens."""
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: list[Token] = []

        while not self._is_at_end():
            char = self._peek()

            if char in " \t\r":
                self._advance()
                continue

            if char == "#":
                self._skip_comment()
                continue

            if char == "\n":
                self.tokens.append(Token(TokenType.NEWLINE, "\\n", self.line, self.col))
                self._advance()
                continue

            if char.isdigit():
                self.tokens.append(self._read_number())
                continue

            if char.isalpha() or char == "_":
                self.tokens.append(self._read_identifier())
                continue

            token_type = self.SINGLE_CHAR_TOKENS.get(char)
            if token_type is not None:
                self.tokens.append(Token(token_type, char, self.line, self.col))
                self._advance()
                continue

            raise LexerError(f"caractere '{char}' não reconhecido", self.line, self.col)

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return self.tokens

    def _is_at_end(self) -> bool:
        return self.pos >= len(self.source)

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.pos]

    def _peek_next(self) -> str:
        if self.pos + 1 >= len(self.source):
            return "\0"
        return self.source[self.pos + 1]

    def _advance(self) -> str:
        char = self.source[self.pos]
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return char

    def _skip_comment(self) -> None:
        while not self._is_at_end() and self._peek() != "\n":
            self._advance()

    def _read_number(self) -> Token:
        start_line = self.line
        start_col = self.col
        start_pos = self.pos

        while self._peek().isdigit():
            self._advance()

        is_float = False
        if self._peek() == "." and self._peek_next().isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()

        lexeme = self.source[start_pos:self.pos]
        if is_float:
            return Token(TokenType.FLOAT, float(lexeme), start_line, start_col)
        return Token(TokenType.INTEGER, int(lexeme), start_line, start_col)

    def _read_identifier(self) -> Token:
        start_line = self.line
        start_col = self.col
        start_pos = self.pos

        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        lexeme = self.source[start_pos:self.pos]
        token_type = self.KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        return Token(token_type, lexeme, start_line, start_col)
