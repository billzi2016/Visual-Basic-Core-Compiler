"""模块说明：定义 Visual Basic 子集前端使用的 Token 体系。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenKind(Enum):
    """枚举当前 VB 子集前端需要识别的全部 Token 类型。"""

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
    KW_ELSEIF = auto()
    KW_WHILE = auto()
    KW_FOR = auto()
    KW_TO = auto()
    KW_STEP = auto()
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
    "elseif": TokenKind.KW_ELSEIF,
    "while": TokenKind.KW_WHILE,
    "for": TokenKind.KW_FOR,
    "to": TokenKind.KW_TO,
    "step": TokenKind.KW_STEP,
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
    """保存 Token 的类别、原始文本和值在源码中的精确位置。"""

    kind: TokenKind
    value: str
    line: int
    column: int

    def display(self) -> str:
        """返回稳定的调试文本，便于 CLI 输出和测试断言。"""

        return f"{self.kind.name}({self.value!r})@{self.line}:{self.column}"
