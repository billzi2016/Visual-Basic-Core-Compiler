"""模块说明：共享少量后端元数据。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BackendMeta:
    """保存后端渲染时需要附带的少量目标元数据。"""

    target_name: str
