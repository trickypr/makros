import tokenize
import token
from typing import Optional

from makros.macros.types import MacroParser
from makros.tokens import TokenCase, Tokens


class MacroAST:
    pass


class Import(MacroAST):
    def __init__(self, module: tokenize.TokenInfo,
                 macro: Optional[tokenize.TokenInfo]):
        self.module = module
        self.macro = macro


class Parser(MacroParser):
    def parse(self, tokens: Tokens) -> Import:
        tokens.consume(TokenCase().type(token.NAME).string("import"),
                       "Expected the keyword 'import'")

        module = tokens.consume(TokenCase().type(token.NAME),
                                "Expected the name of your module")
        macro = None

        if tokens.match(TokenCase().type(token.OP).string('.')):
            macro = tokens.consume(TokenCase().type(token.NAME),
                                   "Expected the name of the macro file")

        return Import(module, macro)
