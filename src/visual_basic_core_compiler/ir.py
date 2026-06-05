"""模块说明：定义连接前端和后端的简洁中间表示 IR。"""

from __future__ import annotations

from dataclasses import dataclass, field

from .ast_nodes import Program
from .semantic import SemanticModel


@dataclass(slots=True)
class IRInstruction:
    """表示一条无类型但结构稳定的 IR 指令。"""

    opcode: str
    args: tuple[str, ...]


@dataclass(slots=True)
class IRFunction:
    """表示一个函数在 IR 层的全部控制流和临时变量信息。"""

    name: str
    params: list[str]
    locals: list[str] = field(default_factory=list)
    temporaries: list[str] = field(default_factory=list)
    instructions: list[IRInstruction] = field(default_factory=list)


@dataclass(slots=True)
class IRProgram:
    """表示整个模块在 IR 层的函数集合及其关联上下文。"""

    functions: list[IRFunction]
    source_program: Program | None = None
    semantic_model: SemanticModel | None = None


def format_ir(program: IRProgram) -> str:
    """把 IR 渲染成稳定文本，便于测试和人工检查。"""

    lines: list[str] = []
    for function in program.functions:
        lines.append(f"func {function.name}({', '.join(function.params)})")
        if function.locals:
            lines.append(f"  locals: {', '.join(function.locals)}")
        if function.temporaries:
            lines.append(f"  temps: {', '.join(function.temporaries)}")
        for instruction in function.instructions:
            lines.append(f"  {instruction.opcode} {' '.join(instruction.args)}".rstrip())
    return "\n".join(lines)
