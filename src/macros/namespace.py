# Macro imported: enum
from argparse import Namespace
import tokenize
from typing import List
from macros.types import MacroParser
from tokens import TokenCase, Tokens

class NamespaceAST:
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

assert True
class Parser(MacroParser):
    def body(self, tokens: Tokens):
        statements = []
        lines = []
        current_line = -1
        indent = 1
        while not tokens.is_at_end():
            if current_line != tokens.peek().start[0]:
                current_line = tokens.peek().start[0]
                lines.append(tokens.peek().line)
            print(TokenCase().type(tokenize.NAME).string('export').check(tokens.peek()))
            if tokens.match(TokenCase().type(tokenize.NAME).string('export')):
                tokens.advance()
                identifier = tokens.consume(TokenCase().type(tokenize.NAME), "Expected identifier")
                statements.append(NamespaceAST.Statement(identifier))
                last_line = lines.pop()
                lines.append(last_line.replace('export', '', 1))
            if tokens.match(TokenCase().type(tokenize.INDENT)):
                indent += 1
            if tokens.match(TokenCase().type(tokenize.DEDENT)):
                indent -= 1
            if indent == 0:
                break
            tokens.advance()
        return NamespaceAST.Body('\n'.join(lines), statements)
    def parse(self, tokens: Tokens) -> any:
        identifier = tokens.consume(TokenCase().type(tokenize.NAME), 'Expected namespace identifier')
        tokens.consume(TokenCase().type(tokenize.OP).string(':'), "Expected ':'")
        tokens.consume(TokenCase().type(tokenize.NEWLINE), "Expected newline")
        tokens.consume(TokenCase().type(tokenize.INDENT), "Expected indent")
        return NamespaceAST.Namespace(identifier, self.body(tokens))
