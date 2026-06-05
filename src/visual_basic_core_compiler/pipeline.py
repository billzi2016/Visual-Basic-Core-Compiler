"""模块说明：统一封装词法、语法、语义、IR 和后端准备阶段。"""

from __future__ import annotations

from dataclasses import dataclass

from .ast_nodes import Program
from .ir import IRProgram
from .ir_builder import IRBuilder
from .lexer import Lexer
from .lowering import lower_ir
from .parser import Parser
from .semantic import SemanticAnalyzer, SemanticModel
from .tokens import Token


@dataclass(slots=True)
class CompilationArtifacts:
    """汇总一次编译过程中各关键阶段的产物，便于调试与测试。"""

    tokens: list[Token]
    program: Program
    semantic_model: SemanticModel
    ir_program: IRProgram
    optimized_program: IRProgram


def tokenize_source(source: str) -> list[Token]:
    """只执行词法分析，返回 Token 列表。"""

    return Lexer(source).tokenize()


def parse_source(source: str) -> tuple[list[Token], Program]:
    """执行到 AST 阶段，适合前端调试和解析测试。"""

    tokens = tokenize_source(source)
    program = Parser(tokens).parse_program()
    return tokens, program


def compile_source(source: str) -> CompilationArtifacts:
    """按统一顺序执行当前编译器支持的完整主链路。"""

    tokens, program = parse_source(source)
    semantic_model = SemanticAnalyzer(program).analyze()
    ir_program = IRBuilder(program, semantic_model).build()
    optimized_program = lower_ir(ir_program)
    return CompilationArtifacts(tokens, program, semantic_model, ir_program, optimized_program)
