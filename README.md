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
- 表达式：`+ - * /`
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
