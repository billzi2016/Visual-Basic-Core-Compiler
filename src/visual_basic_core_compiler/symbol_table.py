"""模块说明：提供一个简单清晰的作用域栈。"""

from __future__ import annotations

from dataclasses import dataclass, field


def canonical_name(name: str) -> str:
    """把标识符转换为统一的小写形式，模拟不区分大小写的名称规则。"""

    return name.lower()


@dataclass(slots=True)
class Symbol:
    """表示符号表中登记的一项名字信息。"""

    name: str
    kind: str
    type_name: str | None = None
    params: list[str] | None = None
    is_sub: bool = False


@dataclass(slots=True)
class Scope:
    """表示单层作用域中的名字集合。"""

    symbols: dict[str, Symbol] = field(default_factory=dict)


class SymbolTable:
    """提供压栈、出栈、定义和查找能力的简单作用域栈。"""

    def __init__(self) -> None:
        """初始化一个带全局作用域的空符号表。"""

        self._scopes: list[Scope] = [Scope()]

    def push(self) -> None:
        """进入新的局部作用域。"""

        self._scopes.append(Scope())

    def pop(self) -> None:
        """退出当前局部作用域。"""

        self._scopes.pop()

    def define(self, symbol: Symbol) -> bool:
        """在当前作用域中定义符号；若重名则返回假。"""

        scope = self._scopes[-1]
        key = canonical_name(symbol.name)
        if key in scope.symbols:
            return False
        scope.symbols[key] = symbol
        return True

    def lookup(self, name: str) -> Symbol | None:
        """从内向外查找名字，返回最接近当前作用域的符号。"""

        key = canonical_name(name)
        for scope in reversed(self._scopes):
            if key in scope.symbols:
                return scope.symbols[key]
        return None
