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


if __name__ == "__main__":
    unittest.main()
