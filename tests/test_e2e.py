"""端到端测试。"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from _helpers import PROJECT_ROOT, artifacts_from_source, compiler_available
from visual_basic_core_compiler.toolchain import ToolchainDriver


class EndToEndTests(unittest.TestCase):
    def test_example_compiles_to_ir_and_c(self) -> None:
        source = (PROJECT_ROOT / "examples" / "function_call.vb").read_text(encoding="utf-8")
        artifacts = artifacts_from_source(source)
        ir_text = "\n".join(instruction.opcode for instruction in artifacts.optimized_program.functions[0].instructions)
        c_text = ToolchainDriver("portable-c").emit_backend_text(artifacts.optimized_program)
        self.assertIn("label", ir_text)
        self.assertIn("Program__Twice", c_text)

    @unittest.skipUnless(compiler_available(), "requires clang or cc")
    def test_builds_and_runs_executable(self) -> None:
        source = """
        Module Program
            Sub Main()
                Dim i As Integer = 1
                For i = 1 To 3
                    Print(i)
                Next
            End Sub
        End Module
        """
        artifacts = artifacts_from_source(source)
        driver = ToolchainDriver("portable-c")
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "program"
            driver.build_executable(artifacts.optimized_program, output_path)
            completed = subprocess.run([str(output_path)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout.strip().splitlines(), ["1", "2", "3"])

    @unittest.skipUnless(compiler_available(), "requires clang or cc")
    def test_fibonacci_example_runs(self) -> None:
        self._assert_example_output("fib.vb", ["0", "1", "1", "2", "3", "5", "8", "13"])

    @unittest.skipUnless(compiler_available(), "requires clang or cc")
    def test_prime_numbers_example_runs(self) -> None:
        self._assert_example_output("prime_numbers.vb", ["2", "3", "5", "7", "11", "13", "17", "19"])

    @unittest.skipUnless(compiler_available(), "requires clang or cc")
    def test_leetcode_palindrome_example_runs(self) -> None:
        self._assert_example_output("leetcode_palindrome_number.vb", ["True", "False", "True"])

    @unittest.skipUnless(compiler_available(), "requires clang or cc")
    def test_leetcode_climbing_stairs_example_runs(self) -> None:
        self._assert_example_output("leetcode_climbing_stairs.vb", ["8"])

    def _assert_example_output(self, filename: str, expected_lines: list[str]) -> None:
        source = (PROJECT_ROOT / "examples" / filename).read_text(encoding="utf-8")
        artifacts = artifacts_from_source(source)
        driver = ToolchainDriver("portable-c")
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "program"
            driver.build_executable(artifacts.optimized_program, output_path)
            completed = subprocess.run([str(output_path)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout.strip().splitlines(), expected_lines)


if __name__ == "__main__":
    unittest.main()
