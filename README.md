# Visual-Basic-Core-Compiler

一个使用 Python 实现的 Visual Basic 核心编译器项目。

当前版本聚焦一个收敛的 VB 子集，目标是稳定打通：

```text
.vb source -> tokens -> AST -> semantic -> IR -> Portable C -> executable(optional)
```

## 当前支持

- `Module ... End Module`
- `Sub ... End Sub`
- `Function ... End Function`
- `Dim name As Type = ...`
- 类型：`Integer`、`Double`、`String`、`Boolean`
- 表达式：`+ - * / Mod`
- 比较：`= <> < <= > >=`
- 逻辑：`And Or Not`
- `If ... Then ... Else ... End If`
- `While ... End While`
- `For ... To ... Next`
- `Return`
- 函数调用
- 内置 `Print(...)`

## 不支持

- `Class`、`Property`、`Structure`
- 数组和对象系统
- `Select Case`
- `Do ... Loop`
- 完整标准库和完整运行时
- 多文件编译

## 为什么先生成 C

这个项目是 VB 编译器，但当前第一代后端没有直接生成 macOS 原生可执行文件，而是先生成 Portable C，再交给系统 `clang/cc` 编译。

这样做不是因为 macOS 不能运行 VB，而是因为当前项目如果直接输出 macOS 原生目标代码，就需要自己处理：

- `arm64` 或其他架构的汇编生成
- `Mach-O` 目标格式
- 调用约定和栈帧细节
- 平台相关的运行时细节

相比之下，macOS 上的 C 工具链已经非常成熟，所以当前路线是：

```text
VB source -> tokens -> AST -> semantic -> IR -> Portable C -> clang/cc -> executable
```

这样可以把当前阶段的实现重点放在：

- VB 词法分析
- VB 语法分析
- VB 语义检查
- IR 设计与降级
- 端到端编译链路的正确性

后续如果要继续扩展，可以在保持前端不变的前提下，再增加真正的原生后端。

## 使用方式

查看 tokens：

```bash
python -m visual_basic_core_compiler examples/hello.vb --emit-tokens
```

查看 AST：

```bash
python -m visual_basic_core_compiler examples/hello.vb --emit-ast
```

查看 IR：

```bash
python -m visual_basic_core_compiler examples/hello.vb --emit-ir
```

查看生成的 C：

```bash
python -m visual_basic_core_compiler examples/hello.vb --emit-c
```

生成可执行文件：

```bash
python -m visual_basic_core_compiler examples/hello.vb -o build/hello
```

## 目录结构

```text
src/visual_basic_core_compiler/
tests/
examples/
PRD.md
TASKS.md
ARCHITECTURE.md
```

## 测试

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py"
```
