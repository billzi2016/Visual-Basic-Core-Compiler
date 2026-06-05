"""模块说明：把 AST 显式下降为便于检查的三地址风格 IR。"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import ast_nodes as ast
from .ir import IRFunction, IRInstruction, IRProgram
from .semantic import SemanticModel


@dataclass(slots=True)
class IRBuilder:
    program: ast.Program
    semantic_model: SemanticModel
    current: IRFunction = field(init=False)
    temp_index: int = field(init=False, default=0)
    label_index: int = field(init=False, default=0)
    module_name: str = field(init=False, default="")

    def build(self) -> IRProgram:
        self.module_name = self.program.module.name
        functions = [self._build_callable(member) for member in self.program.module.members]
        return IRProgram(functions, source_program=self.program, semantic_model=self.semantic_model)

    def _build_callable(self, member: ast.CallableDecl) -> IRFunction:
        self.current = IRFunction(self._qualified_name(member.name), [param.name for param in member.params])
        self.temp_index = 0
        self.label_index = 0
        self._emit("label", f"fn_{member.name}_entry")
        for stmt in member.body:
            self._visit_stmt(stmt)
        if not self.current.instructions or self.current.instructions[-1].opcode not in {"return", "return_void"}:
            if isinstance(member, ast.SubDecl):
                self._emit("return_void")
            else:
                temp = self._emit_const("0")
                self._emit("return", temp)
        return self.current

    def _visit_stmt(self, stmt: ast.Statement) -> None:
        if isinstance(stmt, ast.VarDeclStmt):
            self._declare_local(stmt.name)
            if stmt.initializer is not None:
                value = self._visit_expr(stmt.initializer)
                self._emit("store", stmt.name, value)
            return
        if isinstance(stmt, ast.AssignmentStmt):
            value = self._visit_expr(stmt.value)
            self._emit("store", stmt.name, value)
            return
        if isinstance(stmt, ast.ExpressionStmt):
            self._visit_expr(stmt.expression)
            return
        if isinstance(stmt, ast.IfStmt):
            cond = self._visit_expr(stmt.condition)
            then_label = self._new_label("if_then")
            else_label = self._new_label("if_else") if stmt.else_body is not None else None
            end_label = self._new_label("if_end")
            self._emit("cjump", cond, then_label, else_label or end_label)
            self._emit("label", then_label)
            for item in stmt.then_body:
                self._visit_stmt(item)
            self._emit("jump", end_label)
            if stmt.else_body is not None:
                self._emit("label", else_label)
                for item in stmt.else_body:
                    self._visit_stmt(item)
                self._emit("jump", end_label)
            self._emit("label", end_label)
            return
        if isinstance(stmt, ast.WhileStmt):
            cond_label = self._new_label("while_cond")
            body_label = self._new_label("while_body")
            end_label = self._new_label("while_end")
            self._emit("jump", cond_label)
            self._emit("label", cond_label)
            cond = self._visit_expr(stmt.condition)
            self._emit("cjump", cond, body_label, end_label)
            self._emit("label", body_label)
            for item in stmt.body:
                self._visit_stmt(item)
            self._emit("jump", cond_label)
            self._emit("label", end_label)
            return
        if isinstance(stmt, ast.ForStmt):
            end_slot = self._new_temp()
            start_value = self._visit_expr(stmt.start)
            end_value = self._visit_expr(stmt.end)
            self._emit("store", stmt.variable, start_value)
            self._emit("copy", end_slot, end_value)
            cond_label = self._new_label("for_cond")
            body_label = self._new_label("for_body")
            end_label = self._new_label("for_end")
            self._emit("jump", cond_label)
            self._emit("label", cond_label)
            current_value = self._emit_load(stmt.variable)
            cond_temp = self._new_temp()
            self._emit("binary", cond_temp, "<=", current_value, end_slot)
            self._emit("cjump", cond_temp, body_label, end_label)
            self._emit("label", body_label)
            for item in stmt.body:
                self._visit_stmt(item)
            incremented = self._new_temp()
            reloaded = self._emit_load(stmt.variable)
            one = self._emit_const("1")
            self._emit("binary", incremented, "+", reloaded, one)
            self._emit("store", stmt.variable, incremented)
            self._emit("jump", cond_label)
            self._emit("label", end_label)
            return
        if isinstance(stmt, ast.ReturnStmt):
            if stmt.value is None:
                self._emit("return_void")
            else:
                value = self._visit_expr(stmt.value)
                self._emit("return", value)
            return
        raise AssertionError(f"unhandled statement type: {type(stmt)!r}")

    def _visit_expr(self, expr: ast.Expression) -> str:
        if isinstance(expr, ast.IntegerLiteral):
            return self._emit_const(str(expr.value))
        if isinstance(expr, ast.DoubleLiteral):
            return self._emit_const(repr(expr.value))
        if isinstance(expr, ast.StringLiteral):
            return self._emit_const(self._quote_string(expr.value))
        if isinstance(expr, ast.BooleanLiteral):
            return self._emit_const("True" if expr.value else "False")
        if isinstance(expr, ast.NameExpr):
            return self._emit_load(expr.identifier)
        if isinstance(expr, ast.UnaryExpr):
            operand = self._visit_expr(expr.operand)
            temp = self._new_temp()
            self._emit("unary", temp, expr.operator, operand)
            return temp
        if isinstance(expr, ast.BinaryExpr):
            left = self._visit_expr(expr.left)
            right = self._visit_expr(expr.right)
            temp = self._new_temp()
            self._emit("binary", temp, expr.operator, left, right)
            return temp
        if isinstance(expr, ast.CallExpr):
            args = [self._visit_expr(arg) for arg in expr.args]
            if expr.callee.lower() == "print":
                self._emit("call_void", "Print", *args)
                return self._emit_const("0")
            temp = self._new_temp()
            self._emit("call", temp, self._qualified_name(expr.callee), *args)
            return temp
        raise AssertionError(f"unhandled expression type: {type(expr)!r}")

    def _declare_local(self, name: str) -> None:
        if name not in self.current.locals and name not in self.current.params:
            self.current.locals.append(name)

    def _emit_load(self, name: str) -> str:
        temp = self._new_temp()
        self._emit("load", temp, name)
        return temp

    def _emit_const(self, value: str) -> str:
        temp = self._new_temp()
        self._emit("const", temp, value)
        return temp

    def _new_temp(self) -> str:
        name = f"t{self.temp_index}"
        self.temp_index += 1
        self.current.temporaries.append(name)
        return name

    def _new_label(self, prefix: str) -> str:
        name = f"{prefix}_{self.label_index}"
        self.label_index += 1
        return name

    def _emit(self, opcode: str, *args: str) -> None:
        self.current.instructions.append(IRInstruction(opcode, tuple(args)))

    def _qualified_name(self, name: str) -> str:
        return f"{self.module_name}.{name}"

    def _quote_string(self, value: str) -> str:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
