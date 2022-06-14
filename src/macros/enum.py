import tokenize
from macros.types import MacroParser, MacroTranslator
from macros.utils import camel_to_snake
from tokens import TokenCase, Tokens

import macros.pyx as pyx


class ASTBase():
    def __assign_enum_types__(enum: any, enum_body: any):
        ASTBase.Enum = enum
        ASTBase.EnumBody = enum_body

    def visit(self, visitor: any) -> str:
        return visitor.__getattribute__(camel_to_snake(
            self.__class__.__name__))(self)


class Enum(ASTBase):
    def __init__(self, name: tokenize.TokenInfo, extends: str or None,
                 body: ASTBase):
        self.name = name
        self.extends = extends
        self.body = body

    def __str__(self):
        return f'''Enum(
    {self.name},
    {self.extends},
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
    def __init__(self, name: tokenize.TokenInfo):
        self.name = name

    def __str__(self):
        return f'''EnumBasicItem({self.name})'''


class EnumTupleArg(ASTBase):
    def __init__(self, name: tokenize.TokenInfo, item_type: str or None):
        self.name = name
        self.item_type = item_type

    def __str__(self):
        return f'''EnumTupleArg({self.name}, {self.item_type})'''


class EnumTupleItem(ASTBase):
    def __init__(self, name: tokenize.TokenInfo, args: list[EnumTupleArg]):
        self.name = name
        self.args = args

    def __str__(self):
        return f'''EnumTupleItem(
    {self.name}
    {[str(arg) for arg in self.args]}
)'''


ASTBase.__assign_enum_types__(Enum, EnumBody)


class Parser(MacroParser):
    def arg_definition(self, tokens: Tokens):
        # <arg_definition> ::= <tuple_args>
        # <tuple_args> ::= '(' <tuple_arg> {',' <tuple_arg>} ')'

        args = []

        # This is a jank hack because of the lack of do while loops. Maybe that
        # is a macro to add later :)
        do_while = True

        while do_while:
            # <tuple_arg> ::= <identifier> [':' <type_specifier>]

            identifier = tokens.consume(TokenCase().type(tokenize.NAME),
                                        "checking for enum item identifier")
            type = ''

            if tokens.match(TokenCase().type(tokenize.OP).string(":")):
                type = tokens.consume(TokenCase().type(tokenize.NAME),
                                      "checking for enum item type").string

                while tokens.match(TokenCase().type(tokenize.OP).string("."),
                                   TokenCase().type(tokenize.OP).string("["),
                                   TokenCase().type(tokenize.OP).string("]")):
                    type += tokens.previous().string

                    if tokens.peek().type == tokenize.OP and tokens.peek(
                    ).string == ")":
                        break

                    type += tokens.consume(TokenCase().type(
                        tokenize.NAME), "checking for enum item type").string

            args.append(EnumTupleArg(identifier, type))

            do_while = tokens.match(TokenCase().type(tokenize.OP).string(","))

        tokens.consume(TokenCase().type(tokenize.OP).string(')'),
                       "checking for closing of a tuple enum ')'")

        return args

    def get_enum_item_identifier(self, tokens: Tokens) -> ASTBase:
        # <enum_body> ::= <identifier> [<arg_definition>] '\n'

        identifier = tokens.consume(TokenCase().type(tokenize.NAME),
                                    "checking for enum item identifier")
        args = None

        if tokens.match(TokenCase().type(tokenize.OP).string("(")):
            args = self.arg_definition(tokens)

        tokens.consume(TokenCase().type(tokenize.NEWLINE),
                       "checking for newline")

        if args is not None:
            return EnumTupleItem(identifier, args)

        return EnumBasicItem(identifier)

    def enum_body(self, tokens: Tokens) -> ASTBase.EnumBody:
        items = []

        # {<enum_body>}
        while True:
            if tokens.check(TokenCase().type(tokenize.NEWLINE)):
                continue

            if tokens.match(TokenCase().type(tokenize.DEDENT)):
                break

            items.append(self.get_enum_item_identifier(tokens))

        return EnumBody(items)

    def enum(self, tokens: Tokens) -> EnumBody:
        tokens.consume(TokenCase().type(tokenize.INDENT), "Expected indent")
        return self.enum_body(tokens)

    def parse(self, tokens: Tokens) -> any:
        identifier = tokens.consume(TokenCase().type(tokenize.NAME),
                                    "Expected the enum name")

        do_while = tokens.match(TokenCase().type(tokenize.OP).string("("))
        extends = '' if do_while else None

        while do_while:
            extends += tokens.advance().string
            do_while = not tokens.match(TokenCase().type(
                tokenize.OP).string(")"))

        tokens.consume(TokenCase().type(tokenize.OP), "Expected ':'")
        tokens.consume(TokenCase().type(tokenize.NEWLINE), "Expected newline")

        return Enum(identifier, extends, self.enum(tokens))


class Translator(MacroTranslator):
    parent_name: str

    def enum(self, ast: Enum):
        self.parent_name = ast.name.string

        assign_function = pyx.create_func(
            '__assign_enum_types__', ', '.join([
                camel_to_snake(arg.name.string) for arg in ast.body.identifiers
            ]), '\n'.join([
                f"{self.parent_name}.{arg.name.string} = {camel_to_snake(arg.name.string )}"
                for arg in ast.body.identifiers
            ]))

        equal_override = pyx.create_func('__eq__', 'self, other',
                                         "return isinstance(self, other)")

        return pyx.program(
            pyx.create_class(ast.name.string,
                             pyx.program(assign_function, equal_override),
                             extends=ast.extends),
            pyx.program(
                ast.body.visit(self),
                f"{self.parent_name}.__assign_enum_types__({', '.join(arg.name.string for arg in ast.body.identifiers)})\n\n\n",
                *[f'del({arg.name.string})'
                  for arg in ast.body.identifiers], '\n'))

    def enum_body(self, ast: EnumBody) -> str:
        return pyx.program("\n".join(
            [item.visit(self) for item in ast.identifiers]))

    def enum_basic_item(self, ast: EnumBasicItem) -> str:
        return pyx.create_class(ast.name.string,
                                pyx.create_func('__str__', 'self',
                                                f"return '{ast.name.string}'"),
                                extends=self.parent_name)

    def enum_tuple_arg(self, ast: EnumTupleArg) -> str:
        return f"{ast.name.string}{f': {ast.item_type}' if ast.item_type else ''}"

    def enum_tuple_item(self, ast: EnumTupleItem) -> str:
        return pyx.create_class(
            ast.name.string,
            pyx.program(
                pyx.create_func(
                    '__init__',
                    'self, ' + ', '.join([arg.visit(self)
                                          for arg in ast.args]),
                    '\n'.join([
                        f"self.{arg.name.string} = {arg.name.string}"
                        for arg in ast.args
                    ])),

                # Responsible for handling converting the output to a string
                pyx.create_func(
                    '__str__', 'self',
                    f"return f'{ast.name.string}({', '.join([arg.name.string + ': {self.' + arg.name.string + '}' for arg in ast.args])})'"
                )),
            extends=self.parent_name)

    def translate(self, ast: Enum) -> str:
        return ast.visit(self)
