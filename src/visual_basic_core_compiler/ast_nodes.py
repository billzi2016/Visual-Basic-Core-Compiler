"""模块说明：定义 Visual Basic 子集的抽象语法树。"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Iterable


@dataclass(slots=True)
class Node:
    """所有 AST 节点的共同基类，统一记录源码位置。"""

    line: int
    column: int


VBType = str


@dataclass(slots=True)
class Program(Node):
    """表示单文件输入对应的整棵语法树根节点。"""

    module: "ModuleDecl"


@dataclass(slots=True)
class ModuleDecl(Node):
    """表示 `Module ... End Module` 顶层结构。"""

    name: str
    members: list["CallableDecl"]


@dataclass(slots=True)
class Parameter(Node):
    """表示函数或过程的单个参数声明。"""

    name: str
    type_name: VBType


@dataclass(slots=True)
class CallableDecl(Node):
    """表示 `Sub` 和 `Function` 共用的声明信息。"""

    name: str
    params: list[Parameter]
    body: list["Statement"]


@dataclass(slots=True)
class SubDecl(CallableDecl):
    """表示无返回值的过程声明。"""

    pass


@dataclass(slots=True)
class FunctionDecl(CallableDecl):
    """表示带返回类型的函数声明。"""

    return_type: VBType


@dataclass(slots=True)
class Statement(Node):
    """所有语句节点的共同基类。"""

    pass


@dataclass(slots=True)
class VarDeclStmt(Statement):
    """表示 `Dim name As Type = value` 变量声明语句。"""

    name: str
    type_name: VBType
    initializer: "Expression | None"


@dataclass(slots=True)
class AssignmentStmt(Statement):
    """表示简单变量赋值语句。"""

    name: str
    value: "Expression"


@dataclass(slots=True)
class IfStmt(Statement):
    """表示 If / ElseIf / Else 整体条件分支结构。"""

    condition: "Expression"
    then_body: list[Statement]
    else_body: list[Statement] | None


@dataclass(slots=True)
class WhileStmt(Statement):
    """表示 `While ... End While` 循环。"""

    condition: "Expression"
    body: list[Statement]


@dataclass(slots=True)
class ForStmt(Statement):
    """表示 `For ... To ... [Step ...] ... Next` 循环。"""

    variable: str
    start: "Expression"
    end: "Expression"
    step: "Expression | None"
    body: list[Statement]


@dataclass(slots=True)
class ReturnStmt(Statement):
    """表示 `Return` 语句。"""

    value: "Expression | None"


@dataclass(slots=True)
class ExpressionStmt(Statement):
    """表示以表达式形式出现的独立语句。"""

    expression: "Expression"


@dataclass(slots=True)
class Expression(Node):
    """所有表达式节点的共同基类。"""

    pass


@dataclass(slots=True)
class IntegerLiteral(Expression):
    """表示整数字面量。"""

    value: int


@dataclass(slots=True)
class DoubleLiteral(Expression):
    """表示浮点数字面量。"""

    value: float


@dataclass(slots=True)
class StringLiteral(Expression):
    """表示字符串字面量。"""

    value: str


@dataclass(slots=True)
class BooleanLiteral(Expression):
    """表示布尔字面量。"""

    value: bool


@dataclass(slots=True)
class NameExpr(Expression):
    """表示变量名或参数名引用。"""

    identifier: str


@dataclass(slots=True)
class UnaryExpr(Expression):
    """表示一元运算表达式。"""

    operator: str
    operand: Expression


@dataclass(slots=True)
class BinaryExpr(Expression):
    """表示二元运算表达式。"""

    operator: str
    left: Expression
    right: Expression


@dataclass(slots=True)
class CallExpr(Expression):
    """表示函数或内置过程调用。"""

    callee: str
    args: list[Expression] = field(default_factory=list)


def format_ast(node: Node) -> str:
    """把 AST 渲染成稳定文本，便于调试和测试快照。"""

    return "\n".join(_format_lines(node))


def _format_lines(value: object, indent: int = 0) -> Iterable[str]:
    """递归格式化节点、列表和普通值。"""

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
    """格式化具名字段，保证输出结构清晰稳定。"""

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
