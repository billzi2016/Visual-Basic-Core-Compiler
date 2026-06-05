"""模块说明：定义 Visual Basic 子集前端使用的 Token 体系。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenKind(Enum):
    EOF = auto()
    NEWLINE = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    DOUBLE = auto()
    STRING = auto()

    KW_MODULE = auto()
    KW_END = auto()
    KW_SUB = auto()
    KW_FUNCTION = auto()
    KW_DIM = auto()
    KW_AS = auto()
    KW_INTEGER = auto()
    KW_DOUBLE = auto()
    KW_STRING = auto()
    KW_BOOLEAN = auto()
    KW_IF = auto()
    KW_THEN = auto()
    KW_ELSE = auto()
    KW_WHILE = auto()
    KW_FOR = auto()
    KW_TO = auto()
    KW_NEXT = auto()
    KW_RETURN = auto()
    KW_AND = auto()
    KW_OR = auto()
    KW_NOT = auto()
    KW_MOD = auto()
    KW_TRUE = auto()
    KW_FALSE = auto()

    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()


KEYWORDS = {
    "module": TokenKind.KW_MODULE,
    "end": TokenKind.KW_END,
    "sub": TokenKind.KW_SUB,
    "function": TokenKind.KW_FUNCTION,
    "dim": TokenKind.KW_DIM,
    "as": TokenKind.KW_AS,
    "integer": TokenKind.KW_INTEGER,
    "double": TokenKind.KW_DOUBLE,
    "string": TokenKind.KW_STRING,
    "boolean": TokenKind.KW_BOOLEAN,
    "if": TokenKind.KW_IF,
    "then": TokenKind.KW_THEN,
    "else": TokenKind.KW_ELSE,
    "while": TokenKind.KW_WHILE,
    "for": TokenKind.KW_FOR,
    "to": TokenKind.KW_TO,
    "next": TokenKind.KW_NEXT,
    "return": TokenKind.KW_RETURN,
    "and": TokenKind.KW_AND,
    "or": TokenKind.KW_OR,
    "not": TokenKind.KW_NOT,
    "mod": TokenKind.KW_MOD,
    "true": TokenKind.KW_TRUE,
    "false": TokenKind.KW_FALSE,
}


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    value: str
    line: int
    column: int

    def display(self) -> str:
        return f"{self.kind.name}({self.value!r})@{self.line}:{self.column}"
