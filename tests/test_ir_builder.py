"""IR 构建测试。"""

from __future__ import annotations

import unittest

from _helpers import ir_from_source
from visual_basic_core_compiler.ir import format_ir


class IRBuilderTests(unittest.TestCase):
    def test_emits_control_flow_labels(self) -> None:
        ir_program = ir_from_source(
            """
            Module Program
                Sub Main()
                    Dim i As Integer = 0
                    While i < 2
                        i = i + 1
                    End While
                End Sub
            End Module
            """
        )
        text = format_ir(ir_program)
        self.assertIn("while_cond_", text)
        self.assertIn("cjump", text)
        self.assertIn("jump", text)

    def test_emits_call_and_return(self) -> None:
        ir_program = ir_from_source(
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
        text = format_ir(ir_program)
        self.assertIn("call", text)
        self.assertIn("Program.Add", text)
        self.assertIn("return", text)


if __name__ == "__main__":
    unittest.main()
