import tokenize
from macros.types import MacroParser, MacroTranslator
from macros.utils import camel_to_snake
from tokens import Tokens

import macros.pyx as pyx


class ASTBase():
    def __assign_enum_types__(enum: any, enum_body: any):
        ASTBase.Enum = enum
        ASTBase.EnumBody = enum_body

    def visit(self, visitor: any) -> str:
        return visitor.__getattribute__(camel_to_snake(
            self.__class__.__name__))(self)


class Enum(ASTBase):
    def __init__(self, name: str, body: ASTBase):
        self.name = name
        self.body = body

    def __str__(self):
        return f'''Enum(
    {self.name},
    {self.body}
)'''


class EnumBody(ASTBase):
    def __init__(self, identifiers: list):
        self.identifiers = identifiers

    def __str__(self):
        return f'''EnumBody(
    {[str(ident) for ident in self.identifiers]}
)'''


class EnumBasicItem(ASTBase):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f'''EnumBasicItem({self.name})'''


class EnumTupleArg(ASTBase):
    def __init__(self, name: str, item_type: str or None):
        self.name = name
        self.item_type = item_type

    def __str__(self):
        return f'''EnumTupleArg({self.name}, {self.item_type})'''


class EnumTupleItem(ASTBase):
    def __init__(self, name: str, args: list[EnumTupleArg]):
        self.name = name
        self.args = args

    def __str__(self):
        return f'''EnumTupleItem(
    {self.name}
    {[str(arg) for arg in self.args]}
)'''


# print(ASTBase.__dict__)
ASTBase.__assign_enum_types__(Enum, EnumBody)
# print(ASTBase.__dict__)


class Parser(MacroParser):
    def arg_definition(self, tokens: Tokens):
        # <arg_definition> ::= <tuple_args>
        # <tuple_args> ::= '(' <tuple_arg> {',' <tuple_arg>} ')'

        tokens.verify_current("checking for opening of a tuple enum '('",
                              type=tokenize.OP,
                              string='(')

        args = []

        # This is a jank hack because of the lack of do while loops. Maybe that
        # is a macro to add later :)
        do_while = True

        while do_while:
            # <tuple_arg> ::= <identifier> [':' <type_specifier>]

            identifier = tokens.verify_next(
                "checking for enum item identifier", type=tokenize.NAME).string
            type = None

            if tokens.check_next(type=tokenize.OP, string=":"):
                type = tokens.verify_next("checking for enum item type",
                                          type=tokenize.NAME).string

            args.append(EnumTupleArg(identifier, type))

            do_while = tokens.check_next(type=tokenize.OP, string=",")

        tokens.verify_current("checking for closing of a tuple enum ')'",
                              type=tokenize.OP,
                              string=')')
        tokens.next()

        return args

    def get_enum_item_identifier(self, tokens: Tokens) -> ASTBase:
        # <enum_body> ::= <identifier> [<arg_definition>] '\n'

        identifier = tokens.verify_current("checking for enum item identifier",
                                           tokenize.NAME).string
        args = None

        if tokens.check_next(type=tokenize.OP, string="("):
            args = self.arg_definition(tokens)

        tokens.verify_current("checking for newline", type=tokenize.NEWLINE)

        if args is not None:
            return EnumTupleItem(identifier, args)

        return EnumBasicItem(identifier)

    def enum_body(self, tokens: Tokens) -> ASTBase.EnumBody:
        items = []

        # {<enum_body>}
        while True:
            if tokens.check_next(type=tokenize.DEDENT):
                break

            items.append(self.get_enum_item_identifier(tokens))

        return EnumBody(items)

    def enum(self, tokens: Tokens) -> EnumBody:
        tokens.consume(tokenize.INDENT, "checking for indent")
        return self.enum_body(tokens)

    def parse(self, tokens: Tokens) -> any:
        identifier = tokens.verify_next("checking for enum name",
                                        type=tokenize.NAME).string

        tokens.consume(tokenize.OP, "checking for ':'", string=":")
        tokens.consume(tokenize.NEWLINE, "checking for newline")

        return Enum(identifier, self.enum(tokens))


class Translator(MacroTranslator):
    parent_name: str

    def enum(self, ast: Enum):
        self.parent_name = ast.name

        assign_function = pyx.create_func(
            '__assign_enum_types__', ', '.join(
                [camel_to_snake(arg.name) for arg in ast.body.identifiers]),
            '\n'.join([
                f"{self.parent_name}.{arg.name} = {camel_to_snake(arg.name)}"
                for arg in ast.body.identifiers
            ]))

        return pyx.program(
            pyx.create_class(ast.name, assign_function),
            pyx.program(
                ast.body.visit(self),
                f"{self.parent_name}.__assign_enum_types__({', '.join(arg.name for arg in ast.body.identifiers)})\n\n\n"
            ))

    def enum_body(self, ast: EnumBody) -> str:
        return pyx.program("\n".join(
            [item.visit(self) for item in ast.identifiers]))

    def enum_basic_item(self, ast: EnumBasicItem) -> str:
        return pyx.create_class(ast.name, 'pass', extends=self.parent_name)

    def enum_tuple_arg(self, ast: EnumTupleArg) -> str:
        return f"{ast.name}{f': {ast.item_type}' if ast.item_type else ''}"

    def enum_tuple_item(self, ast: EnumTupleItem) -> str:
        return pyx.create_class(
            ast.name,
            pyx.create_func(
                '__init__',
                'self, ' + ', '.join([arg.visit(self) for arg in ast.args]),
                '\n'.join(
                    [f"self.{arg.name} = {arg.name}" for arg in ast.args])),
            extends=self.parent_name)

    def translate(self, ast: Enum) -> str:
        return ast.visit(self)
