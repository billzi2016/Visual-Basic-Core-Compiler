"""词法分析测试。"""

from __future__ import annotations

import unittest

from _helpers import tokens_from_source
from visual_basic_core_compiler.lexer import LexError
from visual_basic_core_compiler.tokens import TokenKind


class LexerTests(unittest.TestCase):
    def test_recognizes_keywords_literals_and_operators(self) -> None:
        tokens = tokens_from_source(
            'Module Program\nDim x As Integer = 1\nDim y As Double = 1.5\nIf x <= 2 Then\nPrint("ok")\nEnd If\nEnd Module\n'
        )
        kinds = [token.kind for token in tokens[:18]]
        self.assertEqual(
            kinds,
            [
                TokenKind.KW_MODULE,
                TokenKind.IDENTIFIER,
                TokenKind.NEWLINE,
                TokenKind.KW_DIM,
                TokenKind.IDENTIFIER,
                TokenKind.KW_AS,
                TokenKind.KW_INTEGER,
                TokenKind.EQ,
                TokenKind.INTEGER,
                TokenKind.NEWLINE,
                TokenKind.KW_DIM,
                TokenKind.IDENTIFIER,
                TokenKind.KW_AS,
                TokenKind.KW_DOUBLE,
                TokenKind.EQ,
                TokenKind.DOUBLE,
                TokenKind.NEWLINE,
                TokenKind.KW_IF,
            ],
        )

    def test_skips_comments_and_tracks_positions(self) -> None:
        tokens = tokens_from_source("Module Program\n' comment\nPrint(True)\nEnd Module\n")
        print_token = [token for token in tokens if token.value == "Print"][0]
        self.assertEqual((print_token.line, print_token.column), (3, 1))

    def test_reports_unterminated_string(self) -> None:
        with self.assertRaises(LexError):
            tokens_from_source('Module Program\nPrint("oops)\nEnd Module\n')


if __name__ == "__main__":
    unittest.main()
