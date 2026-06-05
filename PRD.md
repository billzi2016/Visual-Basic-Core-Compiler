# Visual-Basic-Core-Compiler PRD

## 1. 项目概述

### 1.1 项目名称

`Visual-Basic-Core-Compiler`

### 1.2 项目定位

这是一个使用 Python 实现的 Visual Basic 核心编译器项目，目标是在一个严格收敛的语言子集内，完成从 `.vb` 源码输入到中间表示、目标代码输出与可执行结果产出的完整链路。

项目强调以下几点：

- 只做核心闭环，不追求完整 Visual Basic 兼容
- 保持编译器前端、语义层与后端边界清晰
- 尽量复用 `C-Core-Compiler` 中已经验证过的工程结构
- 优先保证正确性、可维护性和可扩展性
- 让后续功能扩展时不需要推翻整体架构

### 1.3 项目目标

本项目的目标不是实现一个完整的 Visual Basic 编译器，而是实现一个“范围明确、结构完整、结果可信、可持续演进”的 VB 子集编译器。

一期目标应至少覆盖以下链路：

- 词法分析
- 语法分析
- 抽象语法树构建
- 基础语义分析
- 类型检查
- 中间表示生成
- 基础控制流表达
- 目标代码输出

一期后端以“可复用、可验证、实现成本可控”为原则，优先采用：

- 输出自定义 IR
- 输出可读的 Portable C
- 在具备系统 C 编译器时，可选生成本机可执行文件

### 1.4 项目价值

该项目应体现以下工程特征：

- 能针对一门不同于 C 的语言设计单独前端
- 能处理块结构、声明语义、函数边界和控制流
- 能将 VB 风格语法稳定映射到统一 IR
- 能复用已有编译器项目中的成熟组件，而不是重复搭建基础设施
- 能在控制范围内保留足够清晰的扩展路径

## 2. 产品愿景

项目最终应呈现以下特征：

- 它是一个完整的核心编译链路，而不是零散脚本拼接
- 它能够清楚展示 VB 子集从源码到目标产物的转换过程
- 它的模块划分足够稳定，后续新增语法时不需要重做核心架构
- 它优先保证错误信息、测试能力、可读性和分层设计
- 它在工程组织上与 `C-Core-Compiler` 保持家族化一致，但语言前端保持独立

## 3. 范围定义

### 3.1 一期目标

一期聚焦 Visual Basic 风格语法的最小核心子集，输入为单文件 `.vb`，完成前端、语义层和基础后端闭环。

建议一期支持：

- `Module ... End Module`
- `Sub ... End Sub`
- `Function ... End Function`
- `Dim` 变量声明
- 显式类型标注：`As Integer`、`As Double`、`As String`、`As Boolean`
- 变量初始化与赋值
- 字面量：整数、浮点数、字符串、布尔值
- 表达式：`+ - * /`
- 比较运算：`= <> < <= > >=`
- 逻辑运算：`And Or Not`
- 圆括号优先级
- `If ... Then ... Else ... End If`
- `While ... End While`
- `For ... To ... Next`
- `Return`
- 函数调用
- 内置输出过程：`Print(...)`

### 3.2 明确不做

为保证范围稳定，一期不支持以下能力：

- `Class`
- `Interface`
- `Property`
- `Structure`
- `Enum`
- `Select Case`
- `Do ... Loop`
- `Try ... Catch`
- 事件系统
- 委托、泛型、反射
- 数组、多维数组
- 对象实例化
- 命名空间导入系统
- 完整标准库兼容
- VB6 与 VB.NET 的全部历史差异兼容
- 多文件编译
- 增量编译
- 字节码虚拟机

### 3.3 二期预留

二期可扩展如下能力：

- `ElseIf`
- 一维数组
- `ByRef` / `ByVal` 区分
- 字符串拼接与类型提升细化
- 局部常量 `Const`
- 更完整的作用域与符号遮蔽规则
- 常量折叠
- 死代码删除
- 更清晰的 IR 可视化
- 更完整的内置函数集合

## 4. 语言子集定义

### 4.1 目标语法风格

一期采用统一、收敛、易解析的 VB 风格语法，不同时兼容 VB6 与 VB.NET 的所有写法，而是定义一套稳定子集。

示例：

```vb
Module Program
    Function Add(x As Integer, y As Integer) As Integer
        Return x + y
    End Function

    Sub Main()
        Dim result As Integer = Add(1, 2)
        If result > 2 Then
            Print(result)
        Else
            Print(0)
        End If
    End Sub
End Module
```

### 4.2 基础语义规则

一期建议采用以下规则：

- 变量必须先声明再使用
- 变量不允许重复声明于同一作用域
- 函数参数名在同一函数内唯一
- `Function` 必须满足返回类型约束
- `Sub` 不允许返回值
- `Boolean` 条件表达式只能来自布尔表达式或可显式转换的比较表达式
- 赋值左右类型必须一致，或符合项目定义的有限隐式转换规则
- 函数调用参数个数必须匹配
- 函数调用参数类型必须匹配

### 4.3 类型系统策略

一期仅支持：

- `Integer`
- `Double`
- `String`
- `Boolean`
- `Void`（仅内部表示，用于 `Sub`）

隐式转换策略建议尽量保守：

- `Integer -> Double` 允许
- `Double -> Integer` 默认不允许隐式转换
- `String` 不参与数值自动转换
- `Boolean` 不参与数值自动转换

## 5. 用户与使用场景

### 5.1 目标读者

- 想实现一门非 C 风格语言前端的工程师
- 希望复用已有编译器架构构建第二门语言的人
- 关注语法设计、语义约束和 IR 降级过程的开发者
- 需要一个可持续扩展的核心编译器仓库维护者

### 5.2 关键场景

- 使用者可以输入一个 `.vb` 文件并获得 tokens、AST、IR 或目标代码
- 阅读者可以明确看出 VB 前端如何区别于 C 前端
- 开发者可以在已有 `C-Core-Compiler` 架构基础上快速定位可复用模块
- 后续新增语法特性时，不需要推翻当前核心模块

## 6. 核心需求

### 6.1 输入输出需求

输入：

- 单个 `.vb` 源文件

输出：

- Tokens（可选）
- AST（可选）
- 语义错误信息
- 自定义 IR（可选）
- Portable C 代码（一期建议的主要目标代码）
- 在本机存在 C 工具链时，可选输出可执行文件

命令形式建议：

```bash
python -m visual_basic_core_compiler input.vb -o out
```

可选参数建议：

```bash
--emit-tokens
--emit-ast
--emit-ir
--emit-c
--run
--no-build
```

### 6.2 后端策略

一期后端建议分两层：

1. 必做层：将 VB AST 降级为统一 IR
2. 可选层：将统一 IR 生成为 Portable C

这样设计的原因：

- 可以最大化复用 `C-Core-Compiler` 中已存在的 IR 思路与代码生成经验
- 避免在一期过早进入平台相关汇编生成复杂度
- 便于先验证 VB 前端和语义层是否稳定
- 后续如果需要生成原生汇编，可以在 IR 之后增加新的后端，而不重写前端

### 6.3 运行策略

一期优先保证以下能力：

- 能稳定输出 IR
- 能稳定输出 Portable C
- 若系统中存在 `clang` 或 `cc`，则可选构建可执行文件

这意味着一期项目的最低成功标准不是“必须直接产出机器码”，而是“必须完成可靠的编译链路与目标代码输出”。

## 7. 技术路线

### 7.1 技术选型

项目主体使用 Python 实现，尽量只依赖标准库。

建议使用：

- `re`
- `dataclasses`
- `enum`
- `typing`
- `pathlib`
- `subprocess`
- `textwrap`
- `json`
- `unittest` 或 `pytest`

原则：

- 不依赖第三方 parser generator
- 不依赖大型编译基础设施
- 不将外部工具链作为前端正确性的前提

### 7.2 编译架构

推荐采用如下分层：

1. Lexer
2. Parser
3. AST
4. Semantic Analyzer
5. IR Builder
6. Lowering / Normalizer
7. C Code Generator
8. Toolchain Driver

### 7.3 解析策略

推荐手写递归下降语法分析器。

原因：

- VB 子集中的块结构和关键字驱动语句非常适合手写解析
- 更容易处理 `End If`、`End Function`、`End Module` 这类成对关键字
- 更容易输出高质量错误信息
- 更利于后续逐步扩展语法

表达式解析建议采用分层优先级递归下降。

### 7.4 中间表示设计

建议使用简洁的三地址码风格 IR，并引入基础块与标签。

示例：

```text
func Program.Main
entry:
  t1 = const 1
  t2 = const 2
  t3 = call Add, t1, t2
  br_if_gt t3, 2, then_1, else_1
then_1:
  call Print, t3
  jump end_1
else_1:
  call Print, 0
end_1:
  ret
```

IR 的目标：

- 与具体语法解耦
- 便于语义检查后的统一降级
- 便于未来增加优化与多后端输出
- 便于测试中做结构级断言

## 8. 模块设计

### 8.1 建议目录结构

```text
Visual-Basic-Core-Compiler/
  PRD.md
  README.md
  ARCHITECTURE.md
  TASKS.md
  pyproject.toml
  src/
    visual_basic_core_compiler/
      __init__.py
      __main__.py
      cli.py
      tokens.py
      lexer.py
      ast_nodes.py
      parser.py
      symbol_table.py
      semantic.py
      ir.py
      ir_builder.py
      lowering.py
      codegen/
        __init__.py
        portable_c.py
      pipeline.py
      toolchain.py
  tests/
    test_lexer.py
    test_parser.py
    test_semantic.py
    test_ir_builder.py
    test_codegen.py
    test_cli.py
    test_e2e.py
  examples/
    hello.vb
    arithmetic.vb
    if_else.vb
    while_loop.vb
    function_call.vb
```

### 8.2 复用策略

以下内容建议优先从 `C-Core-Compiler` 复用或局部改造：

- CLI 组织方式
- Pipeline 分层方式
- AST/IR 测试方法
- 错误收集与输出风格
- Toolchain Driver 结构
- `portable_c` 后端思路
- 示例、测试、文档的仓库组织方式

以下内容应按 VB 语法语义重写：

- Token 定义
- Lexer 关键字与换行策略
- Parser 语句与块结构处理
- 语义规则
- 类型系统
- 名称解析逻辑
- IR 降级中的 VB 特有控制流建模

## 9. 错误处理要求

项目必须具备基础错误处理能力，至少覆盖：

- 非法字符
- 非法或不完整语句
- 缺失 `End If` / `End Function` / `End Module`
- 未声明变量
- 重复声明
- 返回类型不匹配
- 参数数量不匹配
- 参数类型不匹配
- 条件表达式类型错误

错误信息建议至少包含：

- 文件名
- 行号
- 列号
- 错误类别
- 简明原因

## 10. 测试策略

### 10.1 测试层级

一期建议至少覆盖以下测试：

- Lexer 单测
- Parser 单测
- Semantic 单测
- IR Builder 单测
- Codegen 单测
- CLI 单测
- 端到端测试

### 10.2 样例覆盖

应至少覆盖：

- 变量声明
- 表达式优先级
- 函数定义与调用
- `If / Else`
- `While`
- `For`
- `Return`
- 类型不匹配错误
- 未声明变量错误
- 参数不匹配错误

### 10.3 成功标准

一期至少满足：

- 所有核心子集语法均有示例
- 所有核心模块均有测试
- 一个最小程序可成功输出 IR
- 一个最小程序可成功输出 Portable C
- 在存在系统 C 编译器时，至少一个程序可生成可执行文件并运行成功

## 11. 里程碑规划

### M1：项目骨架与语言定义

目标：

- 建立仓库结构
- 固化 PRD
- 补齐 README / TASKS / ARCHITECTURE
- 固化一期语法子集与类型系统

### M2：前端闭环

目标：

- 完成 token 定义
- 完成 lexer
- 完成 parser
- 完成 AST
- 跑通基础解析测试

### M3：语义层闭环

目标：

- 完成符号表
- 完成名称解析
- 完成类型检查
- 完成函数签名检查
- 跑通语义错误测试

### M4：IR 与后端闭环

目标：

- 完成 IR 定义
- 完成 AST 到 IR 的降级
- 完成 Portable C 生成
- 跑通代码生成测试

### M5：可执行结果与文档完善

目标：

- 接入系统工具链
- 跑通最小端到端示例
- 完善错误信息
- 补齐示例与文档

## 12. 非目标与边界约束

本项目当前不追求：

- 完整兼容任何一个历史版本的 Visual Basic
- 完整的标准库与运行时
- 高级优化器
- 完整平台适配矩阵
- IDE 集成
- 调试器
- 高性能代码生成

本项目当前优先保证：

- 子集定义稳定
- 编译流程完整
- 架构便于扩展
- 文档与测试同步推进
- 与 `C-Core-Compiler` 的复用边界清晰

## 13. 验收标准

满足以下条件即可认为一期 PRD 对应目标达成：

- 仓库内存在一条完整且可解释的 VB 编译链路
- 能处理约定子集中的核心声明、表达式、控制流与函数
- 能输出结构化 IR
- 能输出可读的 Portable C
- 在有系统 C 编译器时可以完成至少一个示例程序的构建与运行
- 测试可以证明前端、语义层和后端的基本正确性

## 14. 下一步实施建议

建议按以下顺序推进：

1. 先补 `TASKS.md`，把一期拆成可执行任务
2. 定义 tokens 与关键字表
3. 写 AST 节点与语法子集样例
4. 完成 parser
5. 完成 semantic
6. 完成 IR builder
7. 完成 Portable C 后端
8. 最后接入 toolchain 与端到端测试

