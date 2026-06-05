"""模块说明：执行名称解析和基础类型检查。"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import ast_nodes as ast
from .symbol_table import Symbol, SymbolTable, canonical_name

VOID = "Void"
NUMERIC_TYPES = {"Integer", "Double"}
PRIMITIVE_TYPES = {"Integer", "Double", "String", "Boolean"}


class SemanticError(ValueError):
    """当 AST 违反当前语言规则时抛出。"""


@dataclass(slots=True)
class FunctionSignature:
    """保存函数或过程的签名信息，便于后续调用检查。"""

    name: str
    return_type: str
    param_types: list[str]
    is_sub: bool
    decl: ast.CallableDecl | None = None


@dataclass(slots=True)
class SemanticModel:
    """保存语义分析阶段产出的类型与符号查询结果。"""

    module_name: str
    functions: dict[str, FunctionSignature]
    expression_types: dict[int, str]

    def expression_type(self, expr: ast.Expression) -> str:
        """返回表达式在语义分析阶段推导出的最终类型。"""

        return self.expression_types[id(expr)]

    def lookup_function(self, name: str) -> FunctionSignature | None:
        """按不区分大小写的规则查找函数签名。"""

        return self.functions.get(canonical_name(name))


@dataclass(slots=True)
class SemanticAnalyzer:
    """执行名称解析、类型检查和基础语言规则验证。"""

    program: ast.Program
    symbols: SymbolTable = field(init=False, default_factory=SymbolTable)
    functions: dict[str, FunctionSignature] = field(init=False, default_factory=dict)
    expression_types: dict[int, str] = field(init=False, default_factory=dict)
    current_return_type: str = field(init=False, default=VOID)
    current_is_sub: bool = field(init=False, default=False)
    current_function_name: str = field(init=False, default="")
    saw_return: bool = field(init=False, default=False)

    def analyze(self) -> SemanticModel:
        """完成整棵 AST 的语义分析并返回结果模型。"""

        module = self.program.module
        self.functions = {}
        self.expression_types = {}
        self.symbols = SymbolTable()
        self._install_builtins()

        for member in module.members:
            key = canonical_name(member.name)
            if key in self.functions:
                self._error(member, f"duplicate callable '{member.name}'")
            if isinstance(member, ast.SubDecl):
                signature = FunctionSignature(member.name, VOID, [param.type_name for param in member.params], True, member)
            else:
                signature = FunctionSignature(
                    member.name,
                    member.return_type,
                    [param.type_name for param in member.params],
                    False,
                    member,
                )
            self.functions[key] = signature
            self.symbols.define(
                Symbol(
                    member.name,
                    "function",
                    type_name=signature.return_type,
                    params=signature.param_types,
                    is_sub=signature.is_sub,
                )
            )

        for member in module.members:
            self._analyze_callable(member)

        return SemanticModel(module.name, self.functions, self.expression_types)

    def _install_builtins(self) -> None:
        """注册当前编译器支持的最小内置过程集合。"""

        self.functions[canonical_name("Print")] = FunctionSignature("Print", VOID, ["Any"], True, None)
        self.symbols.define(Symbol("Print", "function", type_name=VOID, params=["Any"], is_sub=True))

    def _analyze_callable(self, member: ast.CallableDecl) -> None:
        """分析单个 `Sub` 或 `Function` 的参数、语句和返回行为。"""

        self.symbols.push()
        self.current_function_name = member.name
        if isinstance(member, ast.SubDecl):
            self.current_return_type = VOID
            self.current_is_sub = True
        else:
            self.current_return_type = member.return_type
            self.current_is_sub = False
        self.saw_return = False

        for param in member.params:
            if not self.symbols.define(Symbol(param.name, "variable", type_name=param.type_name)):
                self._error(param, f"duplicate parameter '{param.name}'")

        for stmt in member.body:
            self._visit_stmt(stmt)

        self.symbols.pop()
        if not self.current_is_sub and not self.saw_return:
            self._error(member, f"function '{member.name}' must contain a return statement")

    def _visit_stmt(self, stmt: ast.Statement) -> None:
        """按语句类型分派对应的语义检查逻辑。"""

        if isinstance(stmt, ast.VarDeclStmt):
            if not self.symbols.define(Symbol(stmt.name, "variable", type_name=stmt.type_name)):
                self._error(stmt, f"duplicate variable '{stmt.name}'")
            if stmt.initializer is not None:
                source_type = self._visit_expr(stmt.initializer)
                self._ensure_assignable(stmt, stmt.type_name, source_type)
            return

        if isinstance(stmt, ast.AssignmentStmt):
            symbol = self.symbols.lookup(stmt.name)
            if symbol is None or symbol.kind != "variable":
                self._error(stmt, f"undefined variable '{stmt.name}'")
            source_type = self._visit_expr(stmt.value)
            assert symbol.type_name is not None
            self._ensure_assignable(stmt, symbol.type_name, source_type)
            return

        if isinstance(stmt, ast.IfStmt):
            condition_type = self._visit_expr(stmt.condition)
            if condition_type != "Boolean":
                self._error(stmt.condition, "if condition must be Boolean")
            self.symbols.push()
            for item in stmt.then_body:
                self._visit_stmt(item)
            self.symbols.pop()
            if stmt.else_body is not None:
                self.symbols.push()
                for item in stmt.else_body:
                    self._visit_stmt(item)
                self.symbols.pop()
            return

        if isinstance(stmt, ast.WhileStmt):
            condition_type = self._visit_expr(stmt.condition)
            if condition_type != "Boolean":
                self._error(stmt.condition, "while condition must be Boolean")
            self.symbols.push()
            for item in stmt.body:
                self._visit_stmt(item)
            self.symbols.pop()
            return

        if isinstance(stmt, ast.ForStmt):
            variable = self.symbols.lookup(stmt.variable)
            if variable is None or variable.kind != "variable":
                self._error(stmt, f"undefined variable '{stmt.variable}'")
            assert variable.type_name is not None
            if variable.type_name != "Integer":
                self._error(stmt, "for-loop variable must be Integer in the current compiler")
            start_type = self._visit_expr(stmt.start)
            end_type = self._visit_expr(stmt.end)
            step_type = self._visit_expr(stmt.step) if stmt.step is not None else variable.type_name
            self._ensure_assignable(stmt.start, variable.type_name, start_type)
            self._ensure_assignable(stmt.end, variable.type_name, end_type)
            assert step_type is not None
            self._ensure_assignable(stmt.step or stmt, variable.type_name, step_type)
            self.symbols.push()
            for item in stmt.body:
                self._visit_stmt(item)
            self.symbols.pop()
            return

        if isinstance(stmt, ast.ReturnStmt):
            self.saw_return = True
            if self.current_is_sub:
                if stmt.value is not None:
                    self._error(stmt, "Sub cannot return a value")
                return
            if stmt.value is None:
                self._error(stmt, "Function must return a value")
            source_type = self._visit_expr(stmt.value)
            self._ensure_assignable(stmt, self.current_return_type, source_type)
            return

        if isinstance(stmt, ast.ExpressionStmt):
            expr_type = self._visit_expr(stmt.expression)
            if not isinstance(stmt.expression, ast.CallExpr):
                self._error(stmt, "only call expressions can be used as standalone statements")
            if expr_type != VOID:
                return
            return

        raise AssertionError(f"unhandled statement type: {type(stmt)!r}")

    def _visit_expr(self, expr: ast.Expression) -> str:
        """递归分析表达式，并返回该表达式推导出的类型。"""

        if isinstance(expr, ast.IntegerLiteral):
            return self._record_type(expr, "Integer")
        if isinstance(expr, ast.DoubleLiteral):
            return self._record_type(expr, "Double")
        if isinstance(expr, ast.StringLiteral):
            return self._record_type(expr, "String")
        if isinstance(expr, ast.BooleanLiteral):
            return self._record_type(expr, "Boolean")
        if isinstance(expr, ast.NameExpr):
            symbol = self.symbols.lookup(expr.identifier)
            if symbol is None or symbol.kind != "variable":
                self._error(expr, f"undefined variable '{expr.identifier}'")
            assert symbol.type_name is not None
            return self._record_type(expr, symbol.type_name)
        if isinstance(expr, ast.UnaryExpr):
            operand_type = self._visit_expr(expr.operand)
            operator = expr.operator.lower()
            if operator in {"+", "-"}:
                if operand_type not in NUMERIC_TYPES:
                    self._error(expr, f"operator '{expr.operator}' requires a numeric operand")
                return self._record_type(expr, operand_type)
            if operator == "not":
                if operand_type != "Boolean":
                    self._error(expr, "operator 'Not' requires a Boolean operand")
                return self._record_type(expr, "Boolean")
            raise AssertionError(f"unsupported unary operator: {expr.operator}")
        if isinstance(expr, ast.BinaryExpr):
            left_type = self._visit_expr(expr.left)
            right_type = self._visit_expr(expr.right)
            operator = expr.operator.lower()
            if operator in {"+", "-", "*", "/", "mod"}:
                if left_type not in NUMERIC_TYPES or right_type not in NUMERIC_TYPES:
                    self._error(expr, f"operator '{expr.operator}' requires numeric operands")
                if operator == "mod" and (left_type != "Integer" or right_type != "Integer"):
                    self._error(expr, "operator 'Mod' requires Integer operands")
                return self._record_type(expr, _wider_numeric_type(left_type, right_type))
            if operator in {"=", "<>"}:
                if _comparable_for_equality(left_type, right_type):
                    return self._record_type(expr, "Boolean")
                self._error(expr, f"cannot compare {left_type} with {right_type}")
            if operator in {"<", "<=", ">", ">="}:
                if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
                    return self._record_type(expr, "Boolean")
                self._error(expr, f"operator '{expr.operator}' requires numeric operands")
            if operator in {"and", "or"}:
                if left_type == "Boolean" and right_type == "Boolean":
                    return self._record_type(expr, "Boolean")
                self._error(expr, f"operator '{expr.operator}' requires Boolean operands")
        if isinstance(expr, ast.CallExpr):
            if canonical_name(expr.callee) == canonical_name("Print"):
                if len(expr.args) != 1:
                    self._error(expr, "Print expects exactly one argument")
                argument_type = self._visit_expr(expr.args[0])
                if argument_type not in PRIMITIVE_TYPES:
                    self._error(expr, f"Print does not support type {argument_type}")
                return self._record_type(expr, VOID)
            signature = self.functions.get(canonical_name(expr.callee))
            if signature is None:
                self._error(expr, f"undefined function '{expr.callee}'")
            if len(expr.args) != len(signature.param_types):
                self._error(
                    expr,
                    f"function '{expr.callee}' expects {len(signature.param_types)} arguments but got {len(expr.args)}",
                )
            for arg, expected_type in zip(expr.args, signature.param_types):
                actual_type = self._visit_expr(arg)
                self._ensure_assignable(arg, expected_type, actual_type)
            return self._record_type(expr, signature.return_type)
        raise AssertionError(f"unhandled expression type: {type(expr)!r}")

    def _record_type(self, expr: ast.Expression, type_name: str) -> str:
        """记录表达式类型，供后端和测试复用。"""

        self.expression_types[id(expr)] = type_name
        return type_name

    def _ensure_assignable(self, node: ast.Node, target_type: str, source_type: str) -> None:
        """检查源类型是否可以赋值给目标类型。"""

        if not types_compatible(target_type, source_type):
            self._error(node, f"cannot assign {source_type} to {target_type}")

    def _error(self, node: ast.Node, message: str) -> None:
        """抛出带源码位置的语义错误。"""

        raise SemanticError(f"{message} at {node.line}:{node.column}")


def types_compatible(target_type: str, source_type: str) -> bool:
    """判断当前项目约束下两种类型是否允许赋值。"""

    if target_type == source_type:
        return True
    if target_type == "Double" and source_type == "Integer":
        return True
    return False


def _wider_numeric_type(left_type: str, right_type: str) -> str:
    """返回两个数值类型参与运算后更宽的结果类型。"""

    if "Double" in {left_type, right_type}:
        return "Double"
    return "Integer"


def _comparable_for_equality(left_type: str, right_type: str) -> bool:
    """判断两种类型是否允许参与相等性比较。"""

    if left_type == right_type:
        return left_type in PRIMITIVE_TYPES
    return {left_type, right_type} == {"Integer", "Double"}
