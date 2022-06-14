# Macro imported: enum
from argparse import Namespace
import tokenize
from typing import List
from macros.pyx import create_class, create_func, program
from macros.types import MacroParser, MacroTranslator
from macros.utils import camel_to_snake
from tokens import TokenCase, Tokens
class Visit():
    def visit(self, visitor: any) -> str:
        return visitor.__getattribute__(camel_to_snake(
            self.__class__.__name__))(self)

class NamespaceAST(Visit):
    def __assign_enum_types__(statement, body, namespace):
        NamespaceAST.Statement = statement
        NamespaceAST.Body = body
        NamespaceAST.Namespace = namespace
    
    def __eq__(self, other):
        return isinstance(self, other)


class Statement(NamespaceAST):
    def __init__(self, identifier: tokenize.TokenInfo):
        self.identifier = identifier
    
    def __str__(self):
        return f'Statement(identifier: {self.identifier})'


class Body(NamespaceAST):
    def __init__(self, contents: str, stmts: List[NamespaceAST]):
        self.contents = contents
        self.stmts = stmts
    
    def __str__(self):
        return f'Body(contents: {self.contents}, stmts: {self.stmts})'


class Namespace(NamespaceAST):
    def __init__(self, identifier: tokenize.TokenInfo, body: NamespaceAST):
        self.identifier = identifier
        self.body = body
    
    def __str__(self):
        return f'Namespace(identifier: {self.identifier}, body: {self.body})'

NamespaceAST.__assign_enum_types__(Statement, Body, Namespace)



del(Statement)
del(Body)
del(Namespace)

class Parser(MacroParser):
    def body(self, tokens: Tokens):
        # <body> ::= <statement> {'\n' <statement>}
        statements = []
        lines = []
        current_line = -1
        indent = 1
        tab = ' ' * 4
        while not tokens.is_at_end():
            if current_line != tokens.peek().start[0]:
                current_line = tokens.peek().start[0]
                lines.append(tokens.peek().line)
            if tokens.match(TokenCase().type(tokenize.NAME).string('export')):
                tokens.advance()
                identifier = tokens.consume(TokenCase().type(tokenize.NAME), "Expected identifier")
                statements.append(NamespaceAST.Statement(identifier))
                # Remove export from the last line
                last_line = lines.pop()
                tab = last_line.split('export')[0]
                lines.append(tab + last_line.replace('export', '', 1).strip())
            if tokens.match(TokenCase().type(tokenize.INDENT)):
                indent += 1
            elif tokens.match(TokenCase().type(tokenize.DEDENT)):
                indent -= 1
            else:
                tokens.advance()
            if indent == 0:
                break
        return NamespaceAST.Body('\n'.join([line.replace(tab, '', 1) for line in lines]), statements)
    def parse(self, tokens: Tokens) -> any:
        identifier = tokens.consume(TokenCase().type(tokenize.NAME), 'Expected namespace identifier')
        tokens.consume(TokenCase().type(tokenize.OP).string(':'), "Expected ':'")
        tokens.consume(TokenCase().type(tokenize.NEWLINE), "Expected newline")
        tokens.consume(TokenCase().type(tokenize.INDENT), "Expected indent")
        return NamespaceAST.Namespace(identifier, self.body(tokens))
class Translator(MacroTranslator):
    def statement(self, ast: NamespaceAST.Body) -> str:
        return f'{ast.identifier.string}: {ast.identifier.string}'
    def body(self, ast: NamespaceAST.Body):
        return_def = 'return { ' + ", ".join([export.visit(self) for export in ast.stmts]) + ' }'
        return program(
            *ast.contents.split('\n'),
            return_def)
    def namespace(self, ast: NamespaceAST.Namespace) -> str:
        namespace_def_function = f'__{ast.identifier.string}_namespace_creator'
        namespace_exports = [f'self.{export.identifier.string} = {export.identifier.string}' for export in ast.body.stmts]
        namespace_class = create_class(namespace_def_function, create_func('__init__', 'self', program(ast.body.contents, *namespace_exports)))
        return program(
            f'# Start of namespace {ast.identifier.string}',
            namespace_class,
            f'{ast.identifier.string} = {namespace_def_function}()', 
            f'del {namespace_def_function}', 
            '',
            '',
            f'# End of namespace {ast.identifier.string}')
    def translate(self, ast: NamespaceAST.Namespace) -> str:
        return ast.visit(self)