"""模块说明：把 VB 源码拆成带精确位置的 Token 序列。"""

from __future__ import annotations

from dataclasses import dataclass

from .tokens import KEYWORDS, Token, TokenKind


class LexError(ValueError):
    """当词法分析器遇到非法字符序列时抛出。"""


@dataclass(slots=True)
class Lexer:
    """手写词法分析器，负责把源码字符流拆成 Token 序列。"""

    source: str
    index: int = 0
    line: int = 1
    column: int = 1

    def tokenize(self) -> list[Token]:
        """执行完整词法分析，并返回按顺序排列的 Token 列表。"""

        tokens: list[Token] = []
        while not self._at_end():
            ch = self._peek()
            start_line = self.line
            start_column = self.column

            if ch in " \t\r":
                self._advance()
                continue

            if ch == "\n":
                self._advance()
                tokens.append(Token(TokenKind.NEWLINE, "\\n", start_line, start_column))
                continue

            if ch == "'":
                self._skip_comment()
                continue

            if ch.isalpha() or ch == "_":
                text = self._scan_identifier()
                kind = KEYWORDS.get(text.lower(), TokenKind.IDENTIFIER)
                tokens.append(Token(kind, text, start_line, start_column))
                continue

            if ch.isdigit():
                kind, text = self._scan_number()
                tokens.append(Token(kind, text, start_line, start_column))
                continue

            if ch == '"':
                text = self._scan_string()
                tokens.append(Token(TokenKind.STRING, text, start_line, start_column))
                continue

            two_char = self.source[self.index : self.index + 2]
            if two_char in _DOUBLE_CHAR_TOKENS:
                self._advance()
                self._advance()
                tokens.append(Token(_DOUBLE_CHAR_TOKENS[two_char], two_char, start_line, start_column))
                continue

            if ch in _SINGLE_CHAR_TOKENS:
                self._advance()
                tokens.append(Token(_SINGLE_CHAR_TOKENS[ch], ch, start_line, start_column))
                continue

            raise LexError(f"unexpected character {ch!r} at {start_line}:{start_column}")

        tokens.append(Token(TokenKind.EOF, "", self.line, self.column))
        return tokens

    def _scan_identifier(self) -> str:
        """扫描标识符或关键字候选文本。"""

        start = self.index
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()
        return self.source[start:self.index]

    def _scan_number(self) -> tuple[TokenKind, str]:
        """扫描整数或浮点数字面量。"""

        start = self.index
        while not self._at_end() and self._peek().isdigit():
            self._advance()
        if not self._at_end() and self._peek() == ".":
            dot_index = self.index
            self._advance()
            if self._at_end() or not self._peek().isdigit():
                raise LexError(f"malformed floating-point literal at {self.line}:{self.column}")
            while not self._at_end() and self._peek().isdigit():
                self._advance()
            return TokenKind.DOUBLE, self.source[start:self.index]
        return TokenKind.INTEGER, self.source[start:self.index]

    def _scan_string(self) -> str:
        """扫描双引号包裹的字符串字面量。"""

        start = self.index
        self._advance()
        while not self._at_end() and self._peek() != '"':
            if self._peek() == "\n":
                raise LexError(f"unterminated string literal at {self.line}:{self.column}")
            self._advance()
        if self._at_end():
            raise LexError(f"unterminated string literal at {self.line}:{self.column}")
        self._advance()
        return self.source[start:self.index]

    def _skip_comment(self) -> None:
        """跳过从单引号开始直到行尾的注释文本。"""

        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _peek(self) -> str:
        """查看当前字符但不移动游标。"""

        return self.source[self.index]

    def _advance(self) -> str:
        """消费当前字符，并同步更新行号和列号。"""

        ch = self.source[self.index]
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _at_end(self) -> bool:
        """判断游标是否已经到达输入末尾。"""

        return self.index >= len(self.source)


_SINGLE_CHAR_TOKENS = {
    "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
    ",": TokenKind.COMMA,
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.STAR,
    "/": TokenKind.SLASH,
    "=": TokenKind.EQ,
    "<": TokenKind.LT,
    ">": TokenKind.GT,
}

_DOUBLE_CHAR_TOKENS = {
    "<>": TokenKind.NE,
    "<=": TokenKind.LE,
    ">=": TokenKind.GE,
}
