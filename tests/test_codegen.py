"""代码生成测试。"""

from __future__ import annotations

import unittest

from _helpers import artifacts_from_source
from visual_basic_core_compiler.toolchain import ToolchainDriver


class CodegenTests(unittest.TestCase):
    def test_emits_portable_c_with_runtime_helpers(self) -> None:
        artifacts = artifacts_from_source(
            """
            Module Program
                Sub Main()
                    Print("hello")
                    Print(True)
                End Sub
            End Module
            """
        )
        text = ToolchainDriver("portable-c").emit_backend_text(artifacts.optimized_program)
        self.assertIn("vb_print_string", text)
        self.assertIn("vb_print_bool", text)
        self.assertIn("Program__Main", text)

    def test_maps_function_call_and_entry_point(self) -> None:
        artifacts = artifacts_from_source(
            """
            Module Program
                Function Add(x As Integer, y As Integer) As Integer
                    Return x + y
                End Function

                Function Main() As Integer
                    Return Add(1, 2)
                End Function
            End Module
            """
        )
        text = ToolchainDriver("portable-c").emit_backend_text(artifacts.optimized_program)
        self.assertIn("int Program__Add(int x, int y)", text)
        self.assertIn("return Program__Main();", text)

    def test_emits_mod_operator_and_boolean_print(self) -> None:
        artifacts = artifacts_from_source(
            """
            Module Program
                Function IsPalindrome(value As Integer) As Boolean
                    Return value Mod 2 = 0
                End Function

                Sub Main()
                    Print(IsPalindrome(12))
                End Sub
            End Module
            """
        )
        text = ToolchainDriver("portable-c").emit_backend_text(artifacts.optimized_program)
        self.assertIn("%", text)
        self.assertIn("vb_print_bool", text)

    def test_emits_dynamic_for_step_loop(self) -> None:
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
        text = ToolchainDriver("portable-c").emit_backend_text(artifacts.optimized_program)
        self.assertIn("__vb_for_step_", text)
        self.assertIn("__vb_for_end_", text)
        self.assertIn(">= 0", text)

    def test_emits_select_case_and_array_assignment(self) -> None:
        artifacts = artifacts_from_source(
            """
            Module Program
                Sub Main()
                    Dim nums(2) As Integer
                    nums(0) = 10
                    Select Case nums(0)
                        Case 10
                            Print("ten")
                        Case Else
                            Print("other")
                    End Select
                End Sub
            End Module
            """
        )
        text = ToolchainDriver("portable-c").emit_backend_text(artifacts.optimized_program)
        self.assertIn("nums[0] = 10;", text)
        self.assertIn("__vb_select_", text)
        self.assertIn("if (", text)

    def test_emits_string_equality_with_strcmp(self) -> None:
        artifacts = artifacts_from_source(
            """
            Module Program
                Sub Main()
                    If "alpha" = "alpha" Then
                        Print("same")
                    End If
                End Sub
            End Module
            """
        )
        text = ToolchainDriver("portable-c").emit_backend_text(artifacts.optimized_program)
        self.assertIn("#include <string.h>", text)
        self.assertIn("strcmp(", text)


if __name__ == "__main__":
    unittest.main()
