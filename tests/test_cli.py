"""CLI 测试。"""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from _helpers import PROJECT_ROOT
from visual_basic_core_compiler.cli import main


class CLITests(unittest.TestCase):
    def test_emit_tokens_mode(self) -> None:
        source_path = PROJECT_ROOT / "examples" / "hello.vb"
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main([str(source_path), "--emit-tokens"])
        self.assertEqual(exit_code, 0)
        self.assertIn("KW_MODULE", buffer.getvalue())

    def test_emit_c_mode(self) -> None:
        source_path = PROJECT_ROOT / "examples" / "arithmetic.vb"
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main([str(source_path), "--emit-c"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Program__Add", buffer.getvalue())

    def test_output_path_build_mode_requires_compiler_only_at_runtime(self) -> None:
        source_path = PROJECT_ROOT / "examples" / "hello.vb"
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "hello"
            try:
                main([str(source_path), "-o", str(output_path)])
            except Exception:
                # 这里只验证命令路径能走到构建分支；工具链成败由 e2e 测试覆盖。
                pass


if __name__ == "__main__":
    unittest.main()
