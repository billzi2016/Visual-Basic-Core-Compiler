# Visual-Basic-Core-Compiler Architecture

## 第一代总体原则

第一代实现遵循四个原则：

- 前端独立：VB 的词法、语法和语义规则独立实现，不直接套用 C 前端
- 结构清晰：每个阶段只做自己职责范围内的事
- 结果可验证：每个阶段都可以独立输出并测试
- 后端可替换：先稳定输出 IR 和 Portable C，后续再决定是否扩展原生后端

## 总体数据流

```text
source(.vb)
  -> lexer
  -> tokens
  -> parser
  -> AST
  -> semantic analyzer
  -> IR builder
  -> IR
  -> portable C generator
  -> generated C
  -> system toolchain(optional)
  -> executable(optional)
```

## 为什么第一代先输出 Portable C

第一代的关键目标不是尽快生成平台相关汇编，而是先把 VB 子集的前端、语义层和 IR 降级做稳定。先输出 Portable C 有几个直接好处：

- 可以明显降低一期实现复杂度
- 可以复用已有 `C-Core-Compiler` 的后端组织经验
- 可以用系统 C 工具链获得真实可执行结果
- 可以把“前端是否正确”和“机器相关代码生成”拆开处理
- 可以为后续新增原生后端保留稳定接口

## 模块划分

### `tokens.py`

定义 Token 类型、Token 数据结构、关键字映射和基础分类工具。

### `lexer.py`

负责把 `.vb` 源码扫描为 Token 序列，并记录行号、列号、换行位置和错误上下文。

VB 子集的 lexer 需要特别注意：

- 关键字识别
- 字符串字面量
- 比较运算符 `<> <= >=`
- 逻辑关键字 `And Or Not`
- 行结构对错误定位的影响

### `ast_nodes.py`

定义 AST 节点，用统一的数据结构表达模块、过程、函数、声明、控制流和表达式。

建议重点节点包括：

- `Program`
- `ModuleDecl`
- `SubDecl`
- `FunctionDecl`
- `Parameter`
- `Block`
- `VarDecl`
- `Assignment`
- `IfStmt`
- `WhileStmt`
- `ForStmt`
- `ReturnStmt`
- `CallExpr`
- `BinaryExpr`
- `UnaryExpr`
- `LiteralExpr`
- `NameExpr`

### `parser.py`

负责把 Token 序列解析为 AST。

第一代建议使用手写递归下降，原因是 VB 子集的语句结构明显依赖关键字边界，例如：

- `Module ... End Module`
- `Function ... End Function`
- `Sub ... End Sub`
- `If ... Then ... Else ... End If`
- `While ... End While`
- `For ... To ... Next`

表达式部分使用分层优先级递归下降，避免在一期引入额外复杂度。

### `symbol_table.py`

负责管理符号查找和作用域层次，供语义分析阶段使用。

第一代至少需要：

- 模块级作用域
- 函数级作用域
- 块级作用域
- 变量符号
- 函数符号
- 内置过程符号，例如 `Print`

### `semantic.py`

负责执行第一代所需的基础语义检查。

主要职责：

- 重复声明检查
- 未声明变量检查
- 未声明函数检查
- 参数数量和类型检查
- 返回类型检查
- 条件表达式类型检查
- 赋值类型兼容性检查

一期类型系统只支持：

- `Integer`
- `Double`
- `String`
- `Boolean`
- `Void`（内部表示）

### `ir.py`

定义一套简洁、自描述、便于打印和测试的三地址风格 IR。

IR 需要能表达：

- 常量
- 加载与存储
- 算术运算
- 比较运算
- 逻辑运算
- 函数调用
- 标签
- 条件跳转
- 无条件跳转
- 返回

### `ir_builder.py`

负责把 AST 降级为 IR。

这里是前端和后端之间的核心边界。VB 的块结构、条件分支和循环语义，会在这一层被展开成显式标签和跳转。

典型转换包括：

- `If / Else` -> 条件跳转 + 合流标签
- `While` -> 循环入口标签 + 条件判断 + 回跳
- `For` -> 初始化 + 边界比较 + 递增 + 回跳
- `Function` / `Sub` -> 独立 IR 函数单元

### `lowering.py`

负责做从高层 IR 到更便于生成 C 的标准化处理。

第一代可以保持很轻，只做这些事：

- 统一临时变量形态
- 规范基本块输出顺序
- 规范函数局部声明顺序
- 为代码生成准备稳定输入

### `codegen/portable_c.py`

负责把标准化后的 IR 生成 Portable C。

它的职责不是模拟完整 VB 运行时，而是把当前支持的语言子集稳定映射到 C。

需要处理：

- VB 基础类型到 C 类型的映射
- 函数签名输出
- 局部变量声明
- 算术与比较表达式
- 控制流语句
- `Print` 的运行时映射

### `toolchain.py`

负责选择后端、写出中间文件、调用系统 `clang` 或 `cc`，并在可选模式下生成最终可执行文件。

这里不承担语言语义职责，只负责外部工具调用和错误包装。

### `pipeline.py`

负责把各个阶段串起来，形成稳定的编译流程接口。

建议暴露的阶段能力：

- `compile_to_tokens`
- `compile_to_ast`
- `compile_to_ir`
- `compile_to_c`
- `compile_to_executable`

### `cli.py`

负责命令行入口、参数解析和阶段输出控制。

第一代应支持：

- 输入 `.vb` 文件
- 指定输出路径
- 输出 Tokens
- 输出 AST
- 输出 IR
- 输出 C
- 可选执行生成结果

## 类型系统策略

第一代类型系统刻意保持保守。

建议规则：

- `Integer -> Double` 允许隐式提升
- `Double -> Integer` 不允许隐式收缩
- `String` 不参与数值自动转换
- `Boolean` 不参与数值自动转换
- 条件位置要求布尔结果，比较表达式直接产生布尔值

这样做的目的，是避免一期把过多精力耗在历史兼容细节上。

## 错误处理策略

- Lexer 报告非法字符、字符串未闭合和位置信息
- Parser 报告期望的关键字、分隔符和块结束标记
- Semantic Analyzer 报告符号错误、类型错误和返回错误
- Toolchain Driver 报告外部编译工具失败信息

每一层都应尽量在自己的职责边界内报错，不把前面阶段的问题拖到后面。

## 与 `C-Core-Compiler` 的复用边界

优先复用或参考的部分：

- 仓库目录结构
- CLI 组织方式
- Pipeline 分层方式
- IR 文本输出习惯
- Portable C 后端组织思路
- Toolchain Driver 结构
- 测试目录与示例目录布局

需要按 VB 语言特性独立实现的部分：

- Token 定义
- Lexer 规则
- Parser
- AST 节点
- 语义检查
- 类型系统
- `For`、`If`、`End` 系列关键字驱动的块结构处理

## 第一代成功标准

满足以下条件即可认为第一代架构设计成立：

- `.vb` 输入可以稳定转换为 AST
- AST 可以稳定转换为 IR
- IR 可以稳定生成 Portable C
- 工具链层可选生成可执行文件
- 新增语法特性时，无需推翻现有前端和后端边界
