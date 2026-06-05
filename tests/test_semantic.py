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


if __name__ == "__main__":
    unittest.main()
