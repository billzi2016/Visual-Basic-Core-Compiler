"""模块说明：调用系统工具链，把生成的 C 代码变成可执行文件。"""

from __future__ import annotations

import platform
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .codegen import get_backend
from .ir import IRProgram


class ToolchainError(RuntimeError):
    """当外部工具链失败时抛出。"""


def detect_default_target() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "macos-x86_64"
    if system == "linux":
        return "linux-x86_64"
    return "portable-c"


def find_c_compiler() -> str | None:
    return shutil.which("clang") or shutil.which("cc")


@dataclass(slots=True)
class ToolchainDriver:
    target: str

    def emit_backend_text(self, program: IRProgram) -> str:
        backend = get_backend(self.target)
        return backend.emit(program)

    def build_executable(self, program: IRProgram, output_path: Path) -> Path:
        compiler = find_c_compiler()
        if compiler is None:
            raise ToolchainError("no C compiler found; expected clang or cc")

        generated = self.emit_backend_text(program)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        generated_path = output_path.with_suffix(".generated.c")
        generated_path.write_text(generated, encoding="utf-8")

        command = [compiler, str(generated_path), "-o", str(output_path)]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != 0:
            raise ToolchainError(
                "toolchain command failed:\n"
                + " ".join(command)
                + "\n"
                + completed.stderr.strip()
            )
        return output_path

    def run_program(self, program: IRProgram) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory(prefix="vbcc-run-") as temp_dir:
            output_path = Path(temp_dir) / "program"
            self.build_executable(program, output_path)
            return subprocess.run([str(output_path)], capture_output=True, text=True)
