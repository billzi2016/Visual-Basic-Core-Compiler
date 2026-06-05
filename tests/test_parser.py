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

    def test_parses_mod_and_recursive_call(self) -> None:
        program = program_from_source(
            """
            Module Program
                Function IsOdd(value As Integer) As Boolean
                    Return value Mod 2 = 1
                End Function

                Function Fib(n As Integer) As Integer
                    If n <= 1 Then
                        Return n
                    End If
                    Return Fib(n - 1) + Fib(n - 2)
                End Function
            End Module
            """
        )
        is_odd = program.module.members[0]
        fib = program.module.members[1]
        self.assertIsInstance(is_odd.body[0], ast.ReturnStmt)
        self.assertIsInstance(fib.body[1], ast.ReturnStmt)
        expr = is_odd.body[0].value
        self.assertIsInstance(expr, ast.BinaryExpr)
        self.assertEqual(expr.left.operator, "Mod")

    def test_parses_elseif_chain_and_step_for_loop(self) -> None:
        program = program_from_source(
            """
            Module Program
                Sub Main()
                    Dim score As Integer = 3
                    If score = 1 Then
                        Print("one")
                    ElseIf score = 2 Then
                        Print("two")
                    ElseIf score = 3 Then
                        Print("three")
                    Else
                        Print("other")
                    End If

                    For score = 5 To 1 Step -2
                        Print(score)
                    Next
                End Sub
            End Module
            """
        )
        if_stmt = program.module.members[0].body[1]
        for_stmt = program.module.members[0].body[2]
        self.assertIsInstance(if_stmt, ast.IfStmt)
        self.assertIsNotNone(if_stmt.else_body)
        self.assertIsInstance(if_stmt.else_body[0], ast.IfStmt)
        self.assertIsInstance(for_stmt, ast.ForStmt)
        self.assertIsNotNone(for_stmt.step)

    def test_parses_select_case_with_multiple_values(self) -> None:
        program = program_from_source(
            """
            Module Program
                Sub Main()
                    Dim score As Integer = 2
                    Select Case score
                        Case 1
                            Print("one")
                        Case 2, 3
                            Print("mid")
                        Case Else
                            Print("other")
                    End Select
                End Sub
            End Module
            """
        )
        select_stmt = program.module.members[0].body[1]
        self.assertIsInstance(select_stmt, ast.SelectStmt)
        self.assertEqual(len(select_stmt.cases), 3)
        self.assertEqual(len(select_stmt.cases[1].values), 2)
        self.assertTrue(select_stmt.cases[2].is_else)

    def test_parses_array_declaration_and_index_assignment(self) -> None:
        program = program_from_source(
            """
            Module Program
                Sub Main()
                    Dim nums(3) As Integer
                    nums(0) = 10
                    Print(nums(0))
                End Sub
            End Module
            """
        )
        body = program.module.members[0].body
        self.assertIsInstance(body[0], ast.VarDeclStmt)
        self.assertEqual(body[0].array_bound, 3)
        self.assertIsInstance(body[1], ast.AssignmentStmt)
        self.assertIsInstance(body[1].target, ast.CallExpr)
        self.assertEqual(body[1].target.callee, "nums")
        self.assertIsInstance(body[2], ast.ExpressionStmt)


if __name__ == "__main__":
    unittest.main()
