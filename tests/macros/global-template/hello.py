from macros.types import MacroParser, MacroTranslator
from tokens import Tokens
# Macro imported: enum


class HelloAST:
    def __assign_enum_types__(HelloAST, hello):
        HelloAST.Hello = hello
    
    def __eq__(self, other):
        return isinstance(self, other)


class Hello(HelloAST):
    def __str__(self):
        return 'Hello'

HelloAST.__assign_enum_types__(HelloAST, Hello)



del(Hello)


class Parser(MacroParser):
    def parse(self, tokens: Tokens) -> HelloAST:
        return HelloAST.Hello()
class Translator(MacroTranslator):
    def translate(self, ast: HelloAST) -> str:
        return 'print("Hello World")'