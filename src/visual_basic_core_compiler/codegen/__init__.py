"""模块说明：根据目标选择后端实现。"""

from __future__ import annotations

from .portable_c import emit_portable_c
from .typing import BackendMeta


class PortableCBackend:
    """把 Portable C 后端封装成统一的 `emit` 接口。"""

    def __init__(self, target_name: str) -> None:
        """保存当前后端的目标名称元数据。"""

        self.meta = BackendMeta(target_name)

    def emit(self, program):
        """调用 Portable C 发射函数生成最终后端文本。"""

        return emit_portable_c(program, self.meta)


def get_backend(target: str):
    """根据目标名称选择对应的后端实现。"""

    if target in {"portable-c", "macos-x86_64", "linux-x86_64"}:
        return PortableCBackend(target)
    raise ValueError(f"unsupported target: {target}")
