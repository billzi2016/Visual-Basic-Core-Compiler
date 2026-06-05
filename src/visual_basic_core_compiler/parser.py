"""模块说明：使用递归下降把 Token 序列解析成 VB AST。"""

from __future__ import annotations

from dataclasses import dataclass

from . import ast_nodes as ast
from .tokens import Token, TokenKind


class ParseError(ValueError):
    """当输入不符合当前支持的语法时抛出。"""


@dataclass(slots=True)
class Parser:
    """手写递归下降解析器，负责把 Token 序列转换为 AST。"""

    tokens: list[Token]
    index: int = 0

    def parse_program(self) -> ast.Program:
        """解析完整输入，要求顶层必须是单个 Module。"""

        self._skip_newlines()
        module = self._parse_module()
        self._skip_newlines()
        self._consume(TokenKind.EOF, "expected end of file")
        return ast.Program(module.line, module.column, module)

    def _parse_module(self) -> ast.ModuleDecl:
        """解析顶层 `Module ... End Module` 结构。"""

        keyword = self._consume(TokenKind.KW_MODULE, "expected 'Module'")
        name = self._consume(TokenKind.IDENTIFIER, "expected module name")
        self._consume_statement_end("expected newline after module declaration")
        members: list[ast.CallableDecl] = []
        self._skip_newlines()
        while not self._at_end_marker(TokenKind.KW_END, TokenKind.KW_MODULE):
            members.append(self._parse_member())
            self._skip_newlines()
        self._consume(TokenKind.KW_END, "expected 'End Module'")
        self._consume(TokenKind.KW_MODULE, "expected 'End Module'")
        return ast.ModuleDecl(keyword.line, keyword.column, name.value, members)

    def _parse_member(self) -> ast.CallableDecl:
        """根据关键字分派 `Sub` 或 `Function` 顶层成员。"""

        if self._match(TokenKind.KW_SUB):
            return self._parse_sub()
        if self._match(TokenKind.KW_FUNCTION):
            return self._parse_function()
        raise self._error(self._peek(), "expected 'Sub' or 'Function'")

    def _parse_sub(self) -> ast.SubDecl:
        """解析 `Sub` 过程声明。"""

        keyword = self._previous()
        name = self._consume(TokenKind.IDENTIFIER, "expected sub name")
        params = self._parse_parameter_list()
        self._consume_statement_end("expected newline after sub signature")
        body = self._parse_statement_block_until(lambda: self._at_end_marker(TokenKind.KW_END, TokenKind.KW_SUB))
        self._consume(TokenKind.KW_END, "expected 'End Sub'")
        self._consume(TokenKind.KW_SUB, "expected 'End Sub'")
        return ast.SubDecl(keyword.line, keyword.column, name.value, params, body)

    def _parse_function(self) -> ast.FunctionDecl:
        """解析 `Function` 声明及其返回类型。"""

        keyword = self._previous()
        name = self._consume(TokenKind.IDENTIFIER, "expected function name")
        params = self._parse_parameter_list()
        self._consume(TokenKind.KW_AS, "expected 'As' in function signature")
        return_type = self._parse_type_name()
        self._consume_statement_end("expected newline after function signature")
        body = self._parse_statement_block_until(
            lambda: self._at_end_marker(TokenKind.KW_END, TokenKind.KW_FUNCTION)
        )
        self._consume(TokenKind.KW_END, "expected 'End Function'")
        self._consume(TokenKind.KW_FUNCTION, "expected 'End Function'")
        return ast.FunctionDecl(keyword.line, keyword.column, name.value, params, body, return_type)

    def _parse_parameter_list(self) -> list[ast.Parameter]:
        """解析括号内的参数列表。"""

        self._consume(TokenKind.LPAREN, "expected '('")
        params: list[ast.Parameter] = []
        if self._match(TokenKind.RPAREN):
            return params
        while True:
            name = self._consume(TokenKind.IDENTIFIER, "expected parameter name")
            self._consume(TokenKind.KW_AS, "expected 'As' in parameter declaration")
            type_name = self._parse_type_name()
            params.append(ast.Parameter(name.line, name.column, name.value, type_name))
            if self._match(TokenKind.RPAREN):
                return params
            self._consume(TokenKind.COMMA, "expected ',' between parameters")

    def _parse_statement_block_until(self, is_done) -> list[ast.Statement]:
        """持续解析语句，直到调用方提供的结束条件满足。"""

        statements: list[ast.Statement] = []
        self._skip_newlines()
        while not is_done():
            statements.append(self._parse_statement())
            self._skip_newlines()
        return statements

    def _parse_statement(self) -> ast.Statement:
        """按起始关键字或语法形态分派具体语句解析。"""

        if self._match(TokenKind.KW_DIM):
            return self._parse_var_decl()
        if self._match(TokenKind.KW_IF):
            return self._parse_if()
        if self._match(TokenKind.KW_SELECT):
            return self._parse_select()
        if self._match(TokenKind.KW_WHILE):
            return self._parse_while()
        if self._match(TokenKind.KW_FOR):
            return self._parse_for()
        if self._match(TokenKind.KW_RETURN):
            return self._parse_return()
        if self._check(TokenKind.IDENTIFIER):
            return self._parse_identifier_led_statement()

        expr = self._parse_expression()
        self._consume_statement_end("expected newline after statement")
        return ast.ExpressionStmt(expr.line, expr.column, expr)

    def _parse_identifier_led_statement(self) -> ast.Statement:
        """解析以标识符开头的语句，例如赋值、数组写入或调用。"""

        target = self._parse_reference()
        if self._match(TokenKind.EQ):
            value = self._parse_expression()
            self._consume_statement_end("expected newline after assignment")
            return ast.AssignmentStmt(target.line, target.column, target, value)
        self._consume_statement_end("expected newline after statement")
        return ast.ExpressionStmt(target.line, target.column, target)

    def _parse_var_decl(self) -> ast.VarDeclStmt:
        """解析 `Dim` 变量声明语句。"""

        keyword = self._previous()
        name = self._consume(TokenKind.IDENTIFIER, "expected variable name")
        array_bound = None
        if self._match(TokenKind.LPAREN):
            bound_token = self._consume(TokenKind.INTEGER, "expected array upper bound integer")
            array_bound = int(bound_token.value)
            self._consume(TokenKind.RPAREN, "expected ')' after array upper bound")
        self._consume(TokenKind.KW_AS, "expected 'As' in variable declaration")
        type_name = self._parse_type_name()
        initializer = None
        if self._match(TokenKind.EQ):
            initializer = self._parse_expression()
        self._consume_statement_end("expected newline after variable declaration")
        return ast.VarDeclStmt(keyword.line, keyword.column, name.value, type_name, array_bound, initializer)

    def _parse_assignment(self) -> ast.AssignmentStmt:
        """解析简单变量赋值语句。"""

        name = self._consume(TokenKind.IDENTIFIER, "expected assignment target")
        self._consume(TokenKind.EQ, "expected '=' in assignment")
        value = self._parse_expression()
        self._consume_statement_end("expected newline after assignment")
        return ast.AssignmentStmt(name.line, name.column, ast.NameExpr(name.line, name.column, name.value), value)

    def _parse_if(self) -> ast.IfStmt:
        """解析 If / ElseIf / Else 条件分支链。"""

        return self._parse_if_after_keyword(self._previous(), consume_terminal=True)

    def _parse_if_after_keyword(self, keyword: Token, consume_terminal: bool) -> ast.IfStmt:
        """在已消费 `If` 或 `ElseIf` 关键字后继续解析条件分支主体。"""

        condition = self._parse_expression()
        self._consume(TokenKind.KW_THEN, "expected 'Then'")
        self._consume_statement_end("expected newline after If condition")
        then_body = self._parse_statement_block_until(
            lambda: self._check(TokenKind.KW_ELSE, TokenKind.KW_ELSEIF)
            or self._at_end_marker(TokenKind.KW_END, TokenKind.KW_IF)
        )
        else_body: list[ast.Statement] | None = None
        if self._match(TokenKind.KW_ELSEIF):
            else_if = self._parse_if_after_keyword(self._previous(), consume_terminal=False)
            else_body = [else_if]
        elif self._match(TokenKind.KW_ELSE):
            self._consume_statement_end("expected newline after Else")
            else_body = self._parse_statement_block_until(
                lambda: self._at_end_marker(TokenKind.KW_END, TokenKind.KW_IF)
            )
        if consume_terminal:
            self._consume(TokenKind.KW_END, "expected 'End If'")
            self._consume(TokenKind.KW_IF, "expected 'End If'")
        return ast.IfStmt(keyword.line, keyword.column, condition, then_body, else_body)

    def _parse_select(self) -> ast.SelectStmt:
        """解析 `Select Case ... End Select` 分支结构。"""

        keyword = self._previous()
        self._consume(TokenKind.KW_CASE, "expected 'Case' after 'Select'")
        expression = self._parse_expression()
        self._consume_statement_end("expected newline after Select Case header")

        cases: list[ast.CaseClause] = []
        self._skip_newlines()
        while not self._at_end_marker(TokenKind.KW_END, TokenKind.KW_SELECT):
            cases.append(self._parse_case_clause())
            self._skip_newlines()

        self._consume(TokenKind.KW_END, "expected 'End Select'")
        self._consume(TokenKind.KW_SELECT, "expected 'End Select'")
        return ast.SelectStmt(keyword.line, keyword.column, expression, cases)

    def _parse_case_clause(self) -> ast.CaseClause:
        """解析 `Case` 或 `Case Else` 分支。"""

        case_token = self._consume(TokenKind.KW_CASE, "expected 'Case'")
        is_else = False
        values: list[ast.Expression] = []
        if self._match(TokenKind.KW_ELSE):
            is_else = True
        else:
            values.append(self._parse_expression())
            while self._match(TokenKind.COMMA):
                values.append(self._parse_expression())
        self._consume_statement_end("expected newline after Case clause")
        body = self._parse_statement_block_until(
            lambda: self._check(TokenKind.KW_CASE) or self._at_end_marker(TokenKind.KW_END, TokenKind.KW_SELECT)
        )
        return ast.CaseClause(case_token.line, case_token.column, values, body, is_else)

    def _parse_while(self) -> ast.WhileStmt:
        """解析 `While ... End While` 循环。"""

        keyword = self._previous()
        condition = self._parse_expression()
        self._consume_statement_end("expected newline after While condition")
        body = self._parse_statement_block_until(
            lambda: self._at_end_marker(TokenKind.KW_END, TokenKind.KW_WHILE)
        )
        self._consume(TokenKind.KW_END, "expected 'End While'")
        self._consume(TokenKind.KW_WHILE, "expected 'End While'")
        return ast.WhileStmt(keyword.line, keyword.column, condition, body)

    def _parse_for(self) -> ast.ForStmt:
        """解析 `For ... To ... [Step ...] ... Next` 循环。"""

        keyword = self._previous()
        name = self._consume(TokenKind.IDENTIFIER, "expected for-loop variable")
        self._consume(TokenKind.EQ, "expected '=' in for-loop")
        start = self._parse_expression()
        self._consume(TokenKind.KW_TO, "expected 'To' in for-loop")
        end = self._parse_expression()
        step = None
        if self._match(TokenKind.KW_STEP):
            step = self._parse_expression()
        self._consume_statement_end("expected newline after For header")
        body = self._parse_statement_block_until(lambda: self._check(TokenKind.KW_NEXT))
        self._consume(TokenKind.KW_NEXT, "expected 'Next'")
        if self._check(TokenKind.IDENTIFIER):
            self._advance()
        return ast.ForStmt(keyword.line, keyword.column, name.value, start, end, step, body)

    def _parse_return(self) -> ast.ReturnStmt:
        """解析 `Return` 语句。"""

        keyword = self._previous()
        value = None
        if not self._check(TokenKind.NEWLINE, TokenKind.EOF):
            value = self._parse_expression()
        self._consume_statement_end("expected newline after Return")
        return ast.ReturnStmt(keyword.line, keyword.column, value)

    def _parse_expression(self) -> ast.Expression:
        """解析表达式入口，从最低优先级开始下沉。"""

        return self._parse_or()

    def _parse_or(self) -> ast.Expression:
        """解析逻辑或表达式。"""

        expr = self._parse_and()
        while self._match(TokenKind.KW_OR):
            operator = self._previous()
            right = self._parse_and()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_and(self) -> ast.Expression:
        """解析逻辑与表达式。"""

        expr = self._parse_equality()
        while self._match(TokenKind.KW_AND):
            operator = self._previous()
            right = self._parse_equality()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_equality(self) -> ast.Expression:
        """解析相等与不等比较。"""

        expr = self._parse_comparison()
        while self._match(TokenKind.EQ, TokenKind.NE):
            operator = self._previous()
            right = self._parse_comparison()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_comparison(self) -> ast.Expression:
        """解析大小比较表达式。"""

        expr = self._parse_additive()
        while self._match(TokenKind.LT, TokenKind.LE, TokenKind.GT, TokenKind.GE):
            operator = self._previous()
            right = self._parse_additive()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_additive(self) -> ast.Expression:
        """解析加减表达式。"""

        expr = self._parse_multiplicative()
        while self._match(TokenKind.PLUS, TokenKind.MINUS):
            operator = self._previous()
            right = self._parse_multiplicative()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_multiplicative(self) -> ast.Expression:
        """解析乘除和 Mod 表达式。"""

        expr = self._parse_unary()
        while self._match(TokenKind.STAR, TokenKind.SLASH, TokenKind.KW_MOD):
            operator = self._previous()
            right = self._parse_unary()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_unary(self) -> ast.Expression:
        """解析一元正负号和 Not。"""

        if self._match(TokenKind.PLUS, TokenKind.MINUS, TokenKind.KW_NOT):
            operator = self._previous()
            operand = self._parse_unary()
            return ast.UnaryExpr(operator.line, operator.column, operator.value, operand)
        return self._parse_primary()

    def _parse_primary(self) -> ast.Expression:
        """解析字面量、名称、调用和括号表达式。"""

        if self._match(TokenKind.INTEGER):
            token = self._previous()
            return ast.IntegerLiteral(token.line, token.column, int(token.value))
        if self._match(TokenKind.DOUBLE):
            token = self._previous()
            return ast.DoubleLiteral(token.line, token.column, float(token.value))
        if self._match(TokenKind.STRING):
            token = self._previous()
            return ast.StringLiteral(token.line, token.column, token.value[1:-1])
        if self._match(TokenKind.KW_TRUE):
            token = self._previous()
            return ast.BooleanLiteral(token.line, token.column, True)
        if self._match(TokenKind.KW_FALSE):
            token = self._previous()
            return ast.BooleanLiteral(token.line, token.column, False)
        if self._check(TokenKind.IDENTIFIER):
            return self._parse_reference()
        if self._match(TokenKind.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenKind.RPAREN, "expected ')' after expression")
            return expr
        raise self._error(self._peek(), f"unexpected token {self._peek().kind.name}")

    def _parse_reference(self) -> ast.Expression:
        """解析名称本身，以及名称后跟括号的一元访问或调用。"""

        token = self._consume(TokenKind.IDENTIFIER, "expected identifier")
        if self._match(TokenKind.LPAREN):
            args: list[ast.Expression] = []
            if not self._check(TokenKind.RPAREN):
                while True:
                    args.append(self._parse_expression())
                    if not self._match(TokenKind.COMMA):
                        break
            self._consume(TokenKind.RPAREN, "expected ')' after arguments")
            return ast.CallExpr(token.line, token.column, token.value, args)
        return ast.NameExpr(token.line, token.column, token.value)

    def _parse_type_name(self) -> ast.VBType:
        """解析基础类型名。"""

        if self._match(TokenKind.KW_INTEGER):
            return "Integer"
        if self._match(TokenKind.KW_DOUBLE):
            return "Double"
        if self._match(TokenKind.KW_STRING):
            return "String"
        if self._match(TokenKind.KW_BOOLEAN):
            return "Boolean"
        raise self._error(self._peek(), "expected a type name")

    def _consume_statement_end(self, message: str) -> None:
        """消费语句结尾的换行，允许连续空行。"""

        if self._match(TokenKind.NEWLINE):
            while self._match(TokenKind.NEWLINE):
                pass
            return
        if self._check(TokenKind.EOF):
            return
        raise self._error(self._peek(), message)

    def _skip_newlines(self) -> None:
        """跳过当前游标位置上的连续换行。"""

        while self._match(TokenKind.NEWLINE):
            pass

    def _at_end_marker(self, first: TokenKind, second: TokenKind) -> bool:
        """检查当前位置是否命中一对块结束关键字。"""

        return self._check(first) and self._check_next(second)

    def _match(self, *kinds: TokenKind) -> bool:
        """若当前 Token 属于给定集合则消费它并返回真。"""

        if self._check(*kinds):
            self.index += 1
            return True
        return False

    def _consume(self, kind: TokenKind, message: str) -> Token:
        """强制消费指定类型的 Token，否则抛出语法错误。"""

        if self._check(kind):
            self.index += 1
            return self._previous()
        raise self._error(self._peek(), message)

    def _check(self, *kinds: TokenKind) -> bool:
        """检查当前 Token 是否属于给定集合。"""

        return self._peek().kind in kinds

    def _check_next(self, kind: TokenKind) -> bool:
        """检查下一个 Token 是否为指定类型。"""

        if self.index + 1 >= len(self.tokens):
            return False
        return self.tokens[self.index + 1].kind == kind

    def _peek(self) -> Token:
        """返回当前游标所指向的 Token。"""

        return self.tokens[self.index]

    def _previous(self) -> Token:
        """返回上一个已消费的 Token。"""

        return self.tokens[self.index - 1]

    def _advance(self) -> Token:
        """前进一个 Token 并返回原位置的 Token。"""

        token = self._peek()
        self.index += 1
        return token

    def _error(self, token: Token, message: str) -> ParseError:
        """构造带精确位置的语法错误对象。"""

        found = f"{token.kind.name}({token.value!r})"
        return ParseError(f"{message} at {token.line}:{token.column}; found {found}")
