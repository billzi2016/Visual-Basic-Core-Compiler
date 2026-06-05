"""模块说明：定义前端和后端之间使用的简洁 IR。"""

from __future__ import annotations

from dataclasses import dataclass, field

from .ast_nodes import Program
from .semantic import SemanticModel


@dataclass(slots=True)
class IRInstruction:
    opcode: str
    args: tuple[str, ...]


@dataclass(slots=True)
class IRFunction:
    name: str
    params: list[str]
    locals: list[str] = field(default_factory=list)
    temporaries: list[str] = field(default_factory=list)
    instructions: list[IRInstruction] = field(default_factory=list)


@dataclass(slots=True)
class IRProgram:
    functions: list[IRFunction]
    source_program: Program | None = None
    semantic_model: SemanticModel | None = None


def format_ir(program: IRProgram) -> str:
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
