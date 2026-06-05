"""模块说明：统一封装各个编译阶段。"""

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
    tokens: list[Token]
    program: Program
    semantic_model: SemanticModel
    ir_program: IRProgram
    optimized_program: IRProgram


def tokenize_source(source: str) -> list[Token]:
    return Lexer(source).tokenize()


def parse_source(source: str) -> tuple[list[Token], Program]:
    tokens = tokenize_source(source)
    program = Parser(tokens).parse_program()
    return tokens, program


def compile_source(source: str) -> CompilationArtifacts:
    tokens, program = parse_source(source)
    semantic_model = SemanticAnalyzer(program).analyze()
    ir_program = IRBuilder(program, semantic_model).build()
    optimized_program = lower_ir(ir_program)
    return CompilationArtifacts(tokens, program, semantic_model, ir_program, optimized_program)
