"""模块说明：提供一个简单清晰的作用域栈。"""

from __future__ import annotations

from dataclasses import dataclass, field


def canonical_name(name: str) -> str:
    return name.lower()


@dataclass(slots=True)
class Symbol:
    name: str
    kind: str
    type_name: str | None = None
    params: list[str] | None = None
    is_sub: bool = False


@dataclass(slots=True)
class Scope:
    symbols: dict[str, Symbol] = field(default_factory=dict)


class SymbolTable:
    def __init__(self) -> None:
        self._scopes: list[Scope] = [Scope()]

    def push(self) -> None:
        self._scopes.append(Scope())

    def pop(self) -> None:
        self._scopes.pop()

    def define(self, symbol: Symbol) -> bool:
        scope = self._scopes[-1]
        key = canonical_name(symbol.name)
        if key in scope.symbols:
            return False
        scope.symbols[key] = symbol
        return True

    def lookup(self, name: str) -> Symbol | None:
        key = canonical_name(name)
        for scope in reversed(self._scopes):
            if key in scope.symbols:
                return scope.symbols[key]
        return None
