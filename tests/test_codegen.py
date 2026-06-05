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


if __name__ == "__main__":
    unittest.main()
