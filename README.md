# Visual-Basic-Core-Compiler

A Visual Basic core compiler implemented in Python.

The current version focuses on a compact and converged subset of VB, with the goal of reliably completing the full pipeline:

```text
.vb source -> tokens -> AST -> semantic -> IR -> Portable C -> executable(optional)
```

## Currently Supported

- `Module ... End Module`
- `Sub ... End Sub`
- `Function ... End Function`
- `Dim name As Type = ...`
- `Dim name(upperBound) As Type`
- Types: `Integer`, `Double`, `String`, `Boolean`
- Expressions: `+ - * / Mod`
- Comparisons: `= <> < <= > >=`
- Logic: `And Or Not`
- `If ... Then ... ElseIf ... Else ... End If`
- `Select Case ... Case ... Case Else ... End Select`
- `While ... End While`
- `For ... To ... [Step ...] ... Next`
- `Return`
- Function calls
- One-dimensional array reads and writes: `nums(i)`, `nums(i) = value`
- Built-in `Print(...)`

## Not Supported

- `Class`, `Property`, `Structure`
- Multidimensional arrays
- Arrays as function parameters
- Object system
- `Do ... Loop`
- Complete standard library and runtime
- Multi-file compilation

## Why Generate C First

This is a VB compiler, but the first-generation backend does not directly generate native macOS executables. Instead, it first emits Portable C and then lets the system `clang/cc` toolchain compile it.

This is not because macOS cannot run VB. It is because directly emitting native macOS object code would require the project to handle:

- `arm64` or other architecture-specific assembly generation
- the `Mach-O` object format
- calling conventions and stack frame details
- platform-specific runtime details

By contrast, the C toolchain on macOS is already mature. The current path is therefore:

```text
VB source -> tokens -> AST -> semantic -> IR -> Portable C -> clang/cc -> executable
```

This keeps the current implementation focused on:

- VB lexical analysis
- VB parsing
- VB semantic checking
- IR design and lowering
- correctness of the end-to-end compilation pipeline

If the project is extended later, a real native backend can be added while keeping the frontend unchanged.

## Usage

Inspect tokens:

```bash
python -m visual_basic_core_compiler examples/hello.vb --emit-tokens
```

Inspect the AST:

```bash
python -m visual_basic_core_compiler examples/hello.vb --emit-ast
```

Inspect IR:

```bash
python -m visual_basic_core_compiler examples/hello.vb --emit-ir
```

Inspect generated C:

```bash
python -m visual_basic_core_compiler examples/hello.vb --emit-c
```

Generate an executable:

```bash
python -m visual_basic_core_compiler examples/hello.vb -o build/hello
```

Compile and run directly:

```bash
python -m visual_basic_core_compiler examples/hello.vb --run
```

Run all examples in batch and save the results:

```bash
sh scripts/run_examples.sh
```

## Directory Structure

```text
src/visual_basic_core_compiler/
tests/
examples/
scripts/
build/results_stdout/
build/results_return/
PRD.md
TASKS.md
ARCHITECTURE.md
```

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py"
```

The repository also includes archived results for the full example suite:

- `build/results_stdout/`: stores `generated.c`, `stdout.txt`, `stderr.txt`, and `exit.txt` for each example
- `build/results_return/`: stores the same result set for unified comparison and archival

The current examples cover:

- basic arithmetic and function calls
- conditional branches, `ElseIf`, and `Select Case`
- `While`, `For`, and `For Step`
- recursion and number-theory programs
- one-dimensional array scanning and array-style exercises

Current test status:

- `74` `unittest` cases pass
- all examples under `examples/` have been compiled, run, and archived
