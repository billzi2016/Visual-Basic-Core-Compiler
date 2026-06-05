"""语法分析测试。"""

from __future__ import annotations

import unittest

from _helpers import program_from_source
from visual_basic_core_compiler import ast_nodes as ast
from visual_basic_core_compiler.parser import ParseError


class ParserTests(unittest.TestCase):
    def test_parses_function_and_sub(self) -> None:
        program = program_from_source(
            """
            Module Program
                Function Add(x As Integer, y As Integer) As Integer
                    Return x + y
                End Function

                Sub Main()
                    Print(Add(1, 2))
                End Sub
            End Module
            """
        )
        self.assertEqual(program.module.name, "Program")
        self.assertEqual(len(program.module.members), 2)
        self.assertIsInstance(program.module.members[0], ast.FunctionDecl)
        self.assertIsInstance(program.module.members[1], ast.SubDecl)

    def test_preserves_expression_precedence(self) -> None:
        program = program_from_source(
            """
            Module Program
                Function Main() As Integer
                    Return 1 + 2 * 3
                End Function
            End Module
            """
        )
        return_stmt = program.module.members[0].body[0]
        self.assertIsInstance(return_stmt, ast.ReturnStmt)
        expr = return_stmt.value
        self.assertIsInstance(expr, ast.BinaryExpr)
        self.assertEqual(expr.operator, "+")
        self.assertIsInstance(expr.right, ast.BinaryExpr)
        self.assertEqual(expr.right.operator, "*")

    def test_parses_if_while_and_for(self) -> None:
        program = program_from_source(
            """
            Module Program
                Sub Main()
                    Dim i As Integer = 0
                    While i < 3
                        i = i + 1
                    End While
                    If i = 3 Then
                        Print(i)
                    Else
                        Print(0)
                    End If
                    For i = 1 To 2
                        Print(i)
                    Next
                End Sub
            End Module
            """
        )
        body = program.module.members[0].body
        self.assertIsInstance(body[1], ast.WhileStmt)
        self.assertIsInstance(body[2], ast.IfStmt)
        self.assertIsInstance(body[3], ast.ForStmt)

    def test_reports_missing_end_if(self) -> None:
        with self.assertRaises(ParseError):
            program_from_source(
                """
                Module Program
                    Sub Main()
                        If True Then
                            Print(1)
                    End Sub
                End Module
                """
            )


if __name__ == "__main__":
    unittest.main()
