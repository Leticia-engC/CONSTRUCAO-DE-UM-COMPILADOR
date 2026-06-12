"""Parser de descida recursiva da ArithLang."""

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
    Statement,
    UnaryOp,
)
from .errors import ParseError
from .lexer import Token, TokenType


class Parser:
    """Consome tokens e constrói a AST respeitando precedência."""

    def parse(self, tokens: list[Token]) -> Program:
        self.tokens = tokens
        self.current = 0
        statements: list[Statement] = []

        self._skip_separators()
        while not self._check(TokenType.EOF):
            statements.append(self._statement())
            self._consume_statement_end()
            self._skip_separators()

        return Program(statements)

    def _statement(self) -> Statement:
        if self._match(TokenType.LET):
            return self._let_statement(self._previous())
        if self._check(TokenType.PRINT):
            return self._print_statement()
        if self._check(TokenType.IDENTIFIER):
            return self._assign_statement()

        token = self._peek()
        raise ParseError(f"'{token.value}' inesperado neste contexto", token.line)

    def _let_statement(self, let_token: Token) -> LetStatement:
        name = self._consume(TokenType.IDENTIFIER, "identificador esperado após 'let'")
        self._consume(TokenType.ASSIGN, "'=' esperado após identificador")
        value = self._expression()
        return LetStatement(name.value, value, let_token.line)

    def _assign_statement(self) -> AssignStatement:
        name = self._advance()
        self._consume(TokenType.ASSIGN, "'=' esperado após identificador")
        value = self._expression()
        return AssignStatement(name.value, value, name.line)

    def _print_statement(self) -> PrintStatement:
        print_token = self._advance()
        self._consume(TokenType.LPAREN, "'(' esperado após 'print'")
        value = self._expression()
        self._consume(TokenType.RPAREN, "')' esperado")
        return PrintStatement(value, print_token.line)

    def _expression(self):
        return self._term()

    def _term(self):
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            if self._is_expression_end(self._peek()):
                raise ParseError(f"expressão incompleta após '{operator.value}'", operator.line)
            right = self._factor()
            expr = BinaryOp(operator.value, expr, right, operator.line)
        return expr

    def _factor(self):
        expr = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            operator = self._previous()
            if self._is_expression_end(self._peek()):
                raise ParseError(f"expressão incompleta após '{operator.value}'", operator.line)
            right = self._unary()
            expr = BinaryOp(operator.value, expr, right, operator.line)
        return expr

    def _unary(self):
        if self._match(TokenType.MINUS):
            operator = self._previous()
            if self._is_expression_end(self._peek()):
                raise ParseError("expressão incompleta após '-'", operator.line)
            right = self._unary()
            return UnaryOp(operator.value, right, operator.line)
        return self._primary()

    def _primary(self):
        if self._match(TokenType.INTEGER):
            token = self._previous()
            return IntLiteral(token.value, token.line)
        if self._match(TokenType.FLOAT):
            token = self._previous()
            return FloatLiteral(token.value, token.line)
        if self._match(TokenType.IDENTIFIER):
            token = self._previous()
            return Identifier(token.value, token.line)
        if self._match(TokenType.LPAREN):
            open_token = self._previous()
            expr = self._expression()
            if not self._match(TokenType.RPAREN):
                found = self._peek()
                found_text = "EOF" if found.type == TokenType.EOF else repr(found.value)
                raise ParseError(f"')' esperado, encontrado {found_text}", open_token.line)
            return expr

        token = self._peek()
        if token.type == TokenType.EOF:
            raise ParseError("expressão incompleta", token.line)
        raise ParseError(f"'{token.value}' inesperado neste contexto", token.line)

    def _consume_statement_end(self) -> None:
        if self._check(TokenType.EOF):
            return
        if self._match(TokenType.SEMICOLON, TokenType.NEWLINE):
            return
        token = self._peek()
        raise ParseError(f"separador esperado antes de '{token.value}'", token.line)

    def _skip_separators(self) -> None:
        while self._match(TokenType.SEMICOLON, TokenType.NEWLINE):
            pass

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        token = self._peek()
        raise ParseError(message, token.line)

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end() and token_type != TokenType.EOF:
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _is_expression_end(self, token: Token) -> bool:
        return token.type in {TokenType.NEWLINE, TokenType.SEMICOLON, TokenType.RPAREN, TokenType.EOF}
