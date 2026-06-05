"""模块说明：预留标准化阶段，当前先保持为无损直通。"""

from __future__ import annotations

from .ir import IRProgram


def lower_ir(program: IRProgram) -> IRProgram:
    """预留 IR 标准化步骤，当前版本先直接原样返回。"""

    return program
