import tokenize

from macros.types import MacroParser
from tokens import Tokens


class MacroAST:
    pass


class MacroAST:
    class Import(MacroAST):
        def __init__(self, module: str):
            self.module = module


class Parser(MacroParser):
    def parse(self, tokens: Tokens) -> MacroAST:
        tokens.consume(tokenize.NAME, "checking for imports", string="import")
        return MacroAST.Import(
            tokens.verify_next("checking for module name",
                               type=tokenize.NAME).string)
