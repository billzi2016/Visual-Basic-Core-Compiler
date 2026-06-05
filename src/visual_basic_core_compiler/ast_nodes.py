"""模块说明：定义 Visual Basic 子集的抽象语法树。"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Iterable


@dataclass(slots=True)
class Node:
    line: int
    column: int


VBType = str


@dataclass(slots=True)
class Program(Node):
    module: "ModuleDecl"


@dataclass(slots=True)
class ModuleDecl(Node):
    name: str
    members: list["CallableDecl"]


@dataclass(slots=True)
class Parameter(Node):
    name: str
    type_name: VBType


@dataclass(slots=True)
class CallableDecl(Node):
    name: str
    params: list[Parameter]
    body: list["Statement"]


@dataclass(slots=True)
class SubDecl(CallableDecl):
    pass


@dataclass(slots=True)
class FunctionDecl(CallableDecl):
    return_type: VBType


@dataclass(slots=True)
class Statement(Node):
    pass


@dataclass(slots=True)
class VarDeclStmt(Statement):
    name: str
    type_name: VBType
    initializer: "Expression | None"


@dataclass(slots=True)
class AssignmentStmt(Statement):
    name: str
    value: "Expression"


@dataclass(slots=True)
class IfStmt(Statement):
    condition: "Expression"
    then_body: list[Statement]
    else_body: list[Statement] | None


@dataclass(slots=True)
class WhileStmt(Statement):
    condition: "Expression"
    body: list[Statement]


@dataclass(slots=True)
class ForStmt(Statement):
    variable: str
    start: "Expression"
    end: "Expression"
    body: list[Statement]


@dataclass(slots=True)
class ReturnStmt(Statement):
    value: "Expression | None"


@dataclass(slots=True)
class ExpressionStmt(Statement):
    expression: "Expression"


@dataclass(slots=True)
class Expression(Node):
    pass


@dataclass(slots=True)
class IntegerLiteral(Expression):
    value: int


@dataclass(slots=True)
class DoubleLiteral(Expression):
    value: float


@dataclass(slots=True)
class StringLiteral(Expression):
    value: str


@dataclass(slots=True)
class BooleanLiteral(Expression):
    value: bool


@dataclass(slots=True)
class NameExpr(Expression):
    identifier: str


@dataclass(slots=True)
class UnaryExpr(Expression):
    operator: str
    operand: Expression


@dataclass(slots=True)
class BinaryExpr(Expression):
    operator: str
    left: Expression
    right: Expression


@dataclass(slots=True)
class CallExpr(Expression):
    callee: str
    args: list[Expression] = field(default_factory=list)


def format_ast(node: Node) -> str:
    return "\n".join(_format_lines(node))


def _format_lines(value: object, indent: int = 0) -> Iterable[str]:
    prefix = "  " * indent
    if isinstance(value, Node):
        yield f"{prefix}{value.__class__.__name__}"
        for item in fields(value):
            if item.name in {"line", "column"}:
                continue
            field_value = getattr(value, item.name)
            yield from _format_named(item.name, field_value, indent + 1)
        return

    if isinstance(value, list):
        yield f"{prefix}[]"
        for item in value:
            yield from _format_lines(item, indent + 1)
        return

    yield f"{prefix}{value!r}"


def _format_named(name: str, value: object, indent: int) -> Iterable[str]:
    prefix = "  " * indent
    if isinstance(value, Node):
        yield f"{prefix}{name}:"
        yield from _format_lines(value, indent + 1)
    elif isinstance(value, list):
        yield f"{prefix}{name}:"
        if not value:
            yield f"{prefix}  []"
        else:
            for item in value:
                yield from _format_lines(item, indent + 1)
    else:
        yield f"{prefix}{name}: {value!r}"
