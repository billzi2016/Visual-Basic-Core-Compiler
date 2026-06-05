"""语义分析测试。"""

from __future__ import annotations

import unittest

from _helpers import artifacts_from_source
from visual_basic_core_compiler.semantic import SemanticError


class SemanticTests(unittest.TestCase):
    def test_accepts_numeric_promotion_into_double(self) -> None:
        artifacts = artifacts_from_source(
            """
            Module Program
                Function Main() As Integer
                    Dim x As Double = 1
                    Return 0
                End Function
            End Module
            """
        )
        self.assertEqual(artifacts.semantic_model.module_name, "Program")

    def test_rejects_undefined_variable(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        x = 1
                    End Sub
                End Module
                """
            )

    def test_rejects_type_mismatch(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        Dim x As Integer = "oops"
                    End Sub
                End Module
                """
            )

    def test_rejects_non_boolean_condition(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        If 1 Then
                            Print(1)
                        End If
                    End Sub
                End Module
                """
            )

    def test_rejects_sub_returning_value(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        Return 1
                    End Sub
                End Module
                """
            )

    def test_accepts_recursive_function_and_boolean_return(self) -> None:
        artifacts = artifacts_from_source(
            """
            Module Program
                Function Fib(n As Integer) As Integer
                    If n <= 1 Then
                        Return n
                    End If
                    Return Fib(n - 1) + Fib(n - 2)
                End Function

                Function IsOdd(n As Integer) As Boolean
                    Return n Mod 2 = 1
                End Function
            End Module
            """
        )
        self.assertIn("fib", artifacts.semantic_model.functions)
        self.assertIn("isodd", artifacts.semantic_model.functions)

    def test_rejects_mod_with_non_integer_operands(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Function Main() As Integer
                        Dim value As Double = 10.5 Mod 2
                        Return 0
                    End Function
                End Module
                """
            )

    def test_rejects_duplicate_callable_name(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Function Main() As Integer
                        Return 1
                    End Function

                    Sub Main()
                        Print(1)
                    End Sub
                End Module
                """
            )

    def test_rejects_wrong_argument_count(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Function Add(x As Integer, y As Integer) As Integer
                        Return x + y
                    End Function

                    Function Main() As Integer
                        Return Add(1)
                    End Function
                End Module
                """
            )

    def test_rejects_missing_function_return(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Function Main() As Integer
                        Dim value As Integer = 1
                    End Function
                End Module
                """
            )

    def test_rejects_non_call_expression_statement(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        1 + 2
                    End Sub
                End Module
                """
            )

    def test_rejects_print_with_wrong_argument_count(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        Print(1, 2)
                    End Sub
                End Module
                """
            )

    def test_accepts_negative_step_for_loop(self) -> None:
        artifacts = artifacts_from_source(
            """
            Module Program
                Sub Main()
                    Dim i As Integer = 0
                    For i = 5 To 1 Step -2
                        Print(i)
                    Next
                End Sub
            End Module
            """
        )
        self.assertEqual(artifacts.semantic_model.module_name, "Program")

    def test_rejects_non_numeric_step(self) -> None:
        with self.assertRaises(SemanticError):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        Dim i As Integer = 0
                        For i = 1 To 5 Step True
                            Print(i)
                        Next
                    End Sub
                End Module
                """
            )

    def test_accepts_select_case_and_array_updates(self) -> None:
        artifacts = artifacts_from_source(
            """
            Module Program
                Sub Main()
                    Dim nums(2) As Integer
                    nums(0) = 10
                    nums(1) = 20
                    Select Case nums(0)
                        Case 5
                            Print("five")
                        Case 10
                            Print("ten")
                        Case Else
                            Print("other")
                    End Select
                End Sub
            End Module
            """
        )
        self.assertEqual(artifacts.semantic_model.module_name, "Program")

    def test_rejects_bare_array_variable_use(self) -> None:
        with self.assertRaisesRegex(SemanticError, "requires an index"):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        Dim nums(1) As Integer
                        Print(nums)
                    End Sub
                End Module
                """
            )

    def test_rejects_non_integer_array_index(self) -> None:
        with self.assertRaisesRegex(SemanticError, "must be Integer"):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        Dim nums(1) As Integer
                        nums(True) = 1
                    End Sub
                End Module
                """
            )

    def test_rejects_array_index_out_of_range_literal(self) -> None:
        with self.assertRaisesRegex(SemanticError, "out of range"):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        Dim nums(1) As Integer
                        nums(3) = 1
                    End Sub
                End Module
                """
            )

    def test_rejects_case_else_before_last_branch(self) -> None:
        with self.assertRaisesRegex(SemanticError, "last branch"):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        Dim score As Integer = 1
                        Select Case score
                            Case Else
                                Print("other")
                            Case 1
                                Print("one")
                        End Select
                    End Sub
                End Module
                """
            )

    def test_rejects_select_case_type_mismatch(self) -> None:
        with self.assertRaisesRegex(SemanticError, "incompatible"):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        Dim score As Integer = 1
                        Select Case score
                            Case "one"
                                Print("bad")
                        End Select
                    End Sub
                End Module
                """
            )

    def test_rejects_standalone_array_access_statement(self) -> None:
        with self.assertRaisesRegex(SemanticError, "array access"):
            artifacts_from_source(
                """
                Module Program
                    Sub Main()
                        Dim nums(1) As Integer
                        nums(0)
                    End Sub
                End Module
                """
            )


if __name__ == "__main__":
    unittest.main()
