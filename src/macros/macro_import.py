import tokenize
import token

from macros.types import MacroParser
from tokens import Tokens, TokenCase


class MacroAST:
    pass


class Import(MacroAST):
    def __init__(self, module: tokenize.TokenInfo):
        self.module = module


class Parser(MacroParser):
    def parse(self, tokens: Tokens) -> Import:
        # tokens.consume(TokenCase().type(token.NAME).string('macro'),
        #                "Expected keyword 'macro'")
        tokens.consume(TokenCase().type(token.NAME).string("import"),
                       "Expected the keyword 'import'")

        return Import(
            tokens.consume(TokenCase().type(token.NAME),
                           "Expected the name of your module"))
