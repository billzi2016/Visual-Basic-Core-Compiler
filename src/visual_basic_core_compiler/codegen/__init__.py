"""模块说明：根据目标选择后端实现。"""

from __future__ import annotations

from .portable_c import emit_portable_c
from .typing import BackendMeta


class PortableCBackend:
    def __init__(self, target_name: str) -> None:
        self.meta = BackendMeta(target_name)

    def emit(self, program):
        return emit_portable_c(program, self.meta)


def get_backend(target: str):
    if target in {"portable-c", "macos-x86_64", "linux-x86_64"}:
        return PortableCBackend(target)
    raise ValueError(f"unsupported target: {target}")
