"""Testes automatizados do compilador ArithLang."""

from __future__ import annotations

import unittest

from src import Lexer, Parser, SemanticAnalyzer, compile_source, run_source
from src.ast_nodes import BinaryOp, LetStatement, PrintStatement
from src.errors import LexerError, ParseError, SemanticError, VMRuntimeError
from src.lexer import TokenType
from src.codegen import VirtualMachine


class CompilerPipelineTests(unittest.TestCase):
    def test_operacoes_basicas(self):
        code = "let a = 10\nlet b = 3\nprint(a+b)\nprint(a-b)\nprint(a*b)\nprint(a/b)"
        self.assertEqual(run_source(code), ["13", "7", "30", "3.3333333333333335"])

    def test_precedencia_multiplicacao(self):
        self.assertEqual(run_source("let x = 2 + 3 * 4\nprint(x)"), ["14"])

    def test_parenteses_alteram_precedencia(self):
        self.assertEqual(run_source("let x = (2 + 3) * 4\nprint(x)"), ["20"])

    def test_float_em_operacao(self):
        self.assertEqual(run_source("let x = 2 + 0.5\nprint(x)"), ["2.5"])

    def test_divisao_retorna_float(self):
        self.assertEqual(run_source("let x = 4 / 2\nprint(x)"), ["2.0"])

    def test_negacao_unaria(self):
        self.assertEqual(run_source("let x = -5\nprint(x)"), ["-5"])

    def test_negacao_em_expressao(self):
        self.assertEqual(run_source("let x = 3 * -2\nprint(x)"), ["-6"])

    def test_atribuicao_variavel_existente(self):
        self.assertEqual(run_source("let x = 1\nx = x + 2\nprint(x)"), ["3"])

    def test_semicolon_como_separador(self):
        self.assertEqual(run_source("let x = 1; let y = 2; print(x + y)"), ["3"])

    def test_comentarios_sao_ignorados(self):
        self.assertEqual(run_source("# inicial\nlet x = 5 # lateral\nprint(x)"), ["5"])

    def test_linhas_em_branco_sao_ignoradas(self):
        self.assertEqual(run_source("\n\nlet x = 8\n\nprint(x)\n"), ["8"])

    def test_lexer_reconhece_tokens(self):
        tokens = Lexer().tokenize("let x = 12.5")
        types = [token.type for token in tokens]
        self.assertEqual(types[:4], [TokenType.LET, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.FLOAT])

    def test_lexer_linha_coluna(self):
        tokens = Lexer().tokenize("let x = 1\nprint(x)")
        print_token = [token for token in tokens if token.type == TokenType.PRINT][0]
        self.assertEqual((print_token.line, print_token.column), (2, 1))

    def test_lexer_erro_caractere(self):
        with self.assertRaises(LexerError):
            Lexer().tokenize("let x = @")

    def test_parser_constroi_let(self):
        tokens = Lexer().tokenize("let x = 1")
        ast = Parser().parse(tokens)
        self.assertIsInstance(ast.statements[0], LetStatement)

    def test_parser_constroi_print(self):
        tokens = Lexer().tokenize("print(1)")
        ast = Parser().parse(tokens)
        self.assertIsInstance(ast.statements[0], PrintStatement)

    def test_parser_ast_precedencia(self):
        ast = Parser().parse(Lexer().tokenize("let x = 2 + 3 * 4"))
        expr = ast.statements[0].value
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "+")
        self.assertIsInstance(expr.right, BinaryOp)
        self.assertEqual(expr.right.op, "*")

    def test_parser_parentese_nao_fechado(self):
        with self.assertRaises(ParseError):
            Parser().parse(Lexer().tokenize("print((1 + 2)"))

    def test_parser_expressao_incompleta(self):
        with self.assertRaises(ParseError):
            Parser().parse(Lexer().tokenize("let x = 1 +"))

    def test_semantica_variavel_nao_declarada(self):
        ast = Parser().parse(Lexer().tokenize("print(y)"))
        with self.assertRaises(SemanticError):
            SemanticAnalyzer().analyze(ast)

    def test_semantica_redeclaracao(self):
        ast = Parser().parse(Lexer().tokenize("let x = 1\nlet x = 2"))
        with self.assertRaises(SemanticError):
            SemanticAnalyzer().analyze(ast)

    def test_semantica_atribuicao_sem_declaracao(self):
        ast = Parser().parse(Lexer().tokenize("z = 3"))
        with self.assertRaises(SemanticError):
            SemanticAnalyzer().analyze(ast)

    def test_inferencia_int(self):
        _, _, symbols, _ = compile_source("let x = 1 + 2")
        self.assertEqual(symbols.symbols["x"], "int")

    def test_inferencia_float_promocao(self):
        _, _, symbols, _ = compile_source("let x = 1 + 2.0")
        self.assertEqual(symbols.symbols["x"], "float")

    def test_inferencia_divisao_float(self):
        _, _, symbols, _ = compile_source("let x = 1 / 2")
        self.assertEqual(symbols.symbols["x"], "float")

    def test_codegen_contem_halt(self):
        _, _, _, bytecode = compile_source("let x = 1")
        self.assertEqual(bytecode[-1].op, "HALT")

    def test_vm_divisao_por_zero(self):
        _, _, _, bytecode = compile_source("let x = 1 / 0\nprint(x)")
        with self.assertRaises(VMRuntimeError):
            VirtualMachine().run(bytecode)


if __name__ == "__main__":
    unittest.main()
