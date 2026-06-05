"""模块说明：使用递归下降把 Token 序列解析成 VB AST。"""

from __future__ import annotations

from dataclasses import dataclass

from . import ast_nodes as ast
from .tokens import Token, TokenKind


class ParseError(ValueError):
    """当输入不符合当前支持的语法时抛出。"""


@dataclass(slots=True)
class Parser:
    tokens: list[Token]
    index: int = 0

    def parse_program(self) -> ast.Program:
        self._skip_newlines()
        module = self._parse_module()
        self._skip_newlines()
        self._consume(TokenKind.EOF, "expected end of file")
        return ast.Program(module.line, module.column, module)

    def _parse_module(self) -> ast.ModuleDecl:
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
        if self._match(TokenKind.KW_SUB):
            return self._parse_sub()
        if self._match(TokenKind.KW_FUNCTION):
            return self._parse_function()
        raise self._error(self._peek(), "expected 'Sub' or 'Function'")

    def _parse_sub(self) -> ast.SubDecl:
        keyword = self._previous()
        name = self._consume(TokenKind.IDENTIFIER, "expected sub name")
        params = self._parse_parameter_list()
        self._consume_statement_end("expected newline after sub signature")
        body = self._parse_statement_block_until(lambda: self._at_end_marker(TokenKind.KW_END, TokenKind.KW_SUB))
        self._consume(TokenKind.KW_END, "expected 'End Sub'")
        self._consume(TokenKind.KW_SUB, "expected 'End Sub'")
        return ast.SubDecl(keyword.line, keyword.column, name.value, params, body)

    def _parse_function(self) -> ast.FunctionDecl:
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
        statements: list[ast.Statement] = []
        self._skip_newlines()
        while not is_done():
            statements.append(self._parse_statement())
            self._skip_newlines()
        return statements

    def _parse_statement(self) -> ast.Statement:
        if self._match(TokenKind.KW_DIM):
            return self._parse_var_decl()
        if self._match(TokenKind.KW_IF):
            return self._parse_if()
        if self._match(TokenKind.KW_WHILE):
            return self._parse_while()
        if self._match(TokenKind.KW_FOR):
            return self._parse_for()
        if self._match(TokenKind.KW_RETURN):
            return self._parse_return()
        if self._check(TokenKind.IDENTIFIER) and self._check_next(TokenKind.EQ):
            return self._parse_assignment()

        expr = self._parse_expression()
        self._consume_statement_end("expected newline after statement")
        return ast.ExpressionStmt(expr.line, expr.column, expr)

    def _parse_var_decl(self) -> ast.VarDeclStmt:
        keyword = self._previous()
        name = self._consume(TokenKind.IDENTIFIER, "expected variable name")
        self._consume(TokenKind.KW_AS, "expected 'As' in variable declaration")
        type_name = self._parse_type_name()
        initializer = None
        if self._match(TokenKind.EQ):
            initializer = self._parse_expression()
        self._consume_statement_end("expected newline after variable declaration")
        return ast.VarDeclStmt(keyword.line, keyword.column, name.value, type_name, initializer)

    def _parse_assignment(self) -> ast.AssignmentStmt:
        name = self._consume(TokenKind.IDENTIFIER, "expected assignment target")
        self._consume(TokenKind.EQ, "expected '=' in assignment")
        value = self._parse_expression()
        self._consume_statement_end("expected newline after assignment")
        return ast.AssignmentStmt(name.line, name.column, name.value, value)

    def _parse_if(self) -> ast.IfStmt:
        keyword = self._previous()
        condition = self._parse_expression()
        self._consume(TokenKind.KW_THEN, "expected 'Then'")
        self._consume_statement_end("expected newline after If condition")
        then_body = self._parse_statement_block_until(
            lambda: self._check(TokenKind.KW_ELSE) or self._at_end_marker(TokenKind.KW_END, TokenKind.KW_IF)
        )
        else_body: list[ast.Statement] | None = None
        if self._match(TokenKind.KW_ELSE):
            self._consume_statement_end("expected newline after Else")
            else_body = self._parse_statement_block_until(
                lambda: self._at_end_marker(TokenKind.KW_END, TokenKind.KW_IF)
            )
        self._consume(TokenKind.KW_END, "expected 'End If'")
        self._consume(TokenKind.KW_IF, "expected 'End If'")
        return ast.IfStmt(keyword.line, keyword.column, condition, then_body, else_body)

    def _parse_while(self) -> ast.WhileStmt:
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
        keyword = self._previous()
        name = self._consume(TokenKind.IDENTIFIER, "expected for-loop variable")
        self._consume(TokenKind.EQ, "expected '=' in for-loop")
        start = self._parse_expression()
        self._consume(TokenKind.KW_TO, "expected 'To' in for-loop")
        end = self._parse_expression()
        self._consume_statement_end("expected newline after For header")
        body = self._parse_statement_block_until(lambda: self._check(TokenKind.KW_NEXT))
        self._consume(TokenKind.KW_NEXT, "expected 'Next'")
        if self._check(TokenKind.IDENTIFIER):
            self._advance()
        return ast.ForStmt(keyword.line, keyword.column, name.value, start, end, body)

    def _parse_return(self) -> ast.ReturnStmt:
        keyword = self._previous()
        value = None
        if not self._check(TokenKind.NEWLINE, TokenKind.EOF):
            value = self._parse_expression()
        self._consume_statement_end("expected newline after Return")
        return ast.ReturnStmt(keyword.line, keyword.column, value)

    def _parse_expression(self) -> ast.Expression:
        return self._parse_or()

    def _parse_or(self) -> ast.Expression:
        expr = self._parse_and()
        while self._match(TokenKind.KW_OR):
            operator = self._previous()
            right = self._parse_and()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_and(self) -> ast.Expression:
        expr = self._parse_equality()
        while self._match(TokenKind.KW_AND):
            operator = self._previous()
            right = self._parse_equality()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_equality(self) -> ast.Expression:
        expr = self._parse_comparison()
        while self._match(TokenKind.EQ, TokenKind.NE):
            operator = self._previous()
            right = self._parse_comparison()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_comparison(self) -> ast.Expression:
        expr = self._parse_additive()
        while self._match(TokenKind.LT, TokenKind.LE, TokenKind.GT, TokenKind.GE):
            operator = self._previous()
            right = self._parse_additive()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_additive(self) -> ast.Expression:
        expr = self._parse_multiplicative()
        while self._match(TokenKind.PLUS, TokenKind.MINUS):
            operator = self._previous()
            right = self._parse_multiplicative()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_multiplicative(self) -> ast.Expression:
        expr = self._parse_unary()
        while self._match(TokenKind.STAR, TokenKind.SLASH, TokenKind.KW_MOD):
            operator = self._previous()
            right = self._parse_unary()
            expr = ast.BinaryExpr(operator.line, operator.column, operator.value, expr, right)
        return expr

    def _parse_unary(self) -> ast.Expression:
        if self._match(TokenKind.PLUS, TokenKind.MINUS, TokenKind.KW_NOT):
            operator = self._previous()
            operand = self._parse_unary()
            return ast.UnaryExpr(operator.line, operator.column, operator.value, operand)
        return self._parse_primary()

    def _parse_primary(self) -> ast.Expression:
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
        if self._match(TokenKind.IDENTIFIER):
            token = self._previous()
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
        if self._match(TokenKind.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenKind.RPAREN, "expected ')' after expression")
            return expr
        raise self._error(self._peek(), f"unexpected token {self._peek().kind.name}")

    def _parse_type_name(self) -> ast.VBType:
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
        if self._match(TokenKind.NEWLINE):
            while self._match(TokenKind.NEWLINE):
                pass
            return
        if self._check(TokenKind.EOF):
            return
        raise self._error(self._peek(), message)

    def _skip_newlines(self) -> None:
        while self._match(TokenKind.NEWLINE):
            pass

    def _at_end_marker(self, first: TokenKind, second: TokenKind) -> bool:
        return self._check(first) and self._check_next(second)

    def _match(self, *kinds: TokenKind) -> bool:
        if self._check(*kinds):
            self.index += 1
            return True
        return False

    def _consume(self, kind: TokenKind, message: str) -> Token:
        if self._check(kind):
            self.index += 1
            return self._previous()
        raise self._error(self._peek(), message)

    def _check(self, *kinds: TokenKind) -> bool:
        return self._peek().kind in kinds

    def _check_next(self, kind: TokenKind) -> bool:
        if self.index + 1 >= len(self.tokens):
            return False
        return self.tokens[self.index + 1].kind == kind

    def _peek(self) -> Token:
        return self.tokens[self.index]

    def _previous(self) -> Token:
        return self.tokens[self.index - 1]

    def _advance(self) -> Token:
        token = self._peek()
        self.index += 1
        return token

    def _error(self, token: Token, message: str) -> ParseError:
        return ParseError(f"{message} at {token.line}:{token.column}")
