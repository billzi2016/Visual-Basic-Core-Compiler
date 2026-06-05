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

    def test_emits_nested_loop_and_mod_logic(self) -> None:
        ir_program = ir_from_source(
            """
            Module Program
                Function IsPrime(n As Integer) As Boolean
                    If n < 2 Then
                        Return False
                    End If
                    Dim i As Integer = 2
                    While i * i <= n
                        If n Mod i = 0 Then
                            Return False
                        End If
                        i = i + 1
                    End While
                    Return True
                End Function
            End Module
            """
        )
        text = format_ir(ir_program)
        self.assertIn("while_cond_", text)
        self.assertIn("binary", text)
        self.assertIn("Mod", text)

    def test_emits_signed_for_step_control_flow(self) -> None:
        ir_program = ir_from_source(
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
        text = format_ir(ir_program)
        self.assertIn("for_pos_", text)
        self.assertIn("for_neg_", text)
        self.assertIn(">=", text)


if __name__ == "__main__":
    unittest.main()
