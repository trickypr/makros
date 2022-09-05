import tokenize
from typing import List, Optional
from makros.macros.types import MacroParser, MacroTranslator
from makros.macros.utils import camel_to_snake
from makros.tokens import TokenCase, Tokens

import makros.macros.pyx as pyx


#
# These are the classes for the AST. This will be so much cleaner when we get
# access to the enum macro... But we can't use it whilst inside the enum macro.
#

class ASTBase():
    def __assign_enum_types__(enum: any, enum_body: any):  # type: ignore
        ASTBase.Enum = enum
        ASTBase.EnumBody = enum_body

    def visit(self, visitor: any) -> str:  # type: ignore
        return visitor.__getattribute__(camel_to_snake(
            self.__class__.__name__))(self)


class Enum(ASTBase):
    def __init__(self, name: tokenize.TokenInfo, extends: Optional[str],
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
    def __init__(self, name: tokenize.TokenInfo, args: List[EnumTupleArg]):
        self.name = name
        self.args = args

    def __str__(self):
        return f'''EnumTupleItem(
    {self.name}
    {[str(arg) for arg in self.args]}
)'''


ASTBase.__assign_enum_types__(Enum, EnumBody)


class Parser(MacroParser):
    def is_complex_args(self, tokens: Tokens): 
        return tokens.match(TokenCase().type(tokenize.OP).string("."),
                            TokenCase().type(tokenize.OP).string("["),
                            TokenCase().type(tokenize.OP).string("]"))

    def arg_definition(self, tokens: Tokens):
        # <arg_definition> ::= <tuple_args>
        # <tuple_args> ::= '(' <tuple_arg> {',' <tuple_arg>} ')'

        args = []

        # This is a jank hack because of the lack of do while loops. Maybe that
        # is a macro to add later :)
        still_arguments = True

        while still_arguments:
            # <tuple_arg> ::= <identifier> [':' <type_specifier>]

            identifier = tokens.consume(TokenCase().type(tokenize.NAME),
                                        "checking for enum item identifier")
            type = ''

            # Types are optional, so we should only include them if the user has
            # specified them
            if tokens.match(TokenCase().type(tokenize.OP).string(":")):
                type = tokens.consume(TokenCase().type(tokenize.NAME),
                                      "checking for enum item type").string

                # Sometimes types have a dot in them or takes in parameters, so
                # we need to allow the user to specify these without compile
                # time errors
                while self.is_complex_args(tokens):
                    type += tokens.previous().string

                    # Jank, if there is an end token, we want to jump out of the
                    # loop, because why not
                    if tokens.check(TokenCase().type(tokenize.OP).string(")")):
                        break
                        
                    if tokens.match(TokenCase().type(tokenize.NAME)):
                        type += tokens.previous().string

                # type += tokens.consume(TokenCase().type(
                #     tokenize.NAME), "checking for enum item type").string

            args.append(EnumTupleArg(identifier, type))

            # If there are still arguments, we want to continue the loop    
            still_arguments = tokens.match(TokenCase().type(tokenize.OP).string(","))

        tokens.consume(TokenCase().type(tokenize.OP).string(')'),
                       "checking for closing of a tuple enum ')'")

        return args

    def get_enum_item(self, tokens: Tokens) -> ASTBase:
        # <enum_body> ::= <identifier> [<arg_definition>] '\n'

        identifier = tokens.consume(TokenCase().type(tokenize.NAME),
                                    "checking for enum item identifier")
        args = None

        # If there is an opening token, the enum will take in arguments, so we
        # have to parse those arguments and specify them
        if tokens.match(TokenCase().type(tokenize.OP).string("(")):
            args = self.arg_definition(tokens)

        tokens.consume(TokenCase().type(tokenize.NEWLINE),
                       "checking for newline")

        # If there are no arguments, return basic enum item, otherwise return a
        # tuple enum.
        #
        # TODO: Might be a good idea to rename tuple enums to argument enums
        return EnumTupleItem(identifier, args) if args is not None else EnumBasicItem(identifier)

    def enum_body(self, tokens: Tokens) -> ASTBase.EnumBody:
        """Parses the list of items in the enum body
        """

        items = []

        # {<enum_body>}
        while True:
            # Tokens to ignore. We don't care about newlines or docstrings
            if tokens.match(TokenCase().type(tokenize.NEWLINE), 
                TokenCase().type(tokenize.STRING)):
                continue

            # The enum body ends on a dedent. We can just keep looping until we
            # find one
            if tokens.match(TokenCase().type(tokenize.DEDENT)):
                break

            enum_item = self.get_enum_item(tokens)
            items.append(enum_item)

        return EnumBody(items)

    def enum(self, tokens: Tokens) -> EnumBody:
        # These are tokens that start the body
        tokens.consume(TokenCase().type(tokenize.OP), "Expected ':'")
        tokens.consume(TokenCase().type(tokenize.NEWLINE), "Expected newline")
        tokens.consume(TokenCase().type(tokenize.INDENT), "Expected indent")

        body = self.enum_body(tokens)

        return body

    def parse(self, tokens: Tokens) -> any:
        identifier = tokens.consume(TokenCase().type(tokenize.NAME),
                                    "Expected the enum name")

        # If it extends a class (or multiple), store them
        extends_a_class = tokens.match(TokenCase().type(tokenize.OP).string("("))
        extends = '' if extends_a_class else None

        while extends_a_class:
            extends += tokens.advance().string  # type: ignore
            extends_a_class = not tokens.match(TokenCase().type(
                tokenize.OP).string(")"))

        enum = self.enum(tokens)

        return Enum(identifier, extends, enum)


class Translator(MacroTranslator):
    parent_name: str

    def enum(self, ast: Enum):
        # Save the enum name so it can be used elsewhere
        self.parent_name = ast.name.string
        
        # Unless malformation AST is provided, this is the primary return of the
        # translator
        return pyx.program(
            # Base class definition
            pyx.create_class(
                # Class name
                ast.name.string,

                # Class body
                pyx.program(
                    # This is internal code that should not be accessed by the 
                    # user (hence the underscore). It assigns the provided enums
                    # to the current class.
                    #
                    # TL;DR: Black magic so you can run EnumName.Branch
                    pyx.create_func(
                        # Function name
                        '__assign_enum_types__',

                        # Function args 
                        ', '.join([
                            self.parent_name,
                            *[camel_to_snake(arg.name.string) for arg in ast.body.identifiers]
                        ]),
                        
                        # Function body
                        pyx.program(*[
                            f"{self.parent_name}.{arg.name.string} = {camel_to_snake(arg.name.string )}"
                            for arg in ast.body.identifiers  # type: ignore
                        ])
                    ), # end __assign_enum_types__

                    # This allows us to compare the enum to another enum.
                    pyx.create_func(
                        # Function name
                        '__eq__', 
                        
                        # Function args
                        'self, other',
                        
                        # Function body
                        pyx.program(
                            # If comparing types that are not instances (e.g.
                            # a string with an enum), a crash would occur, to
                            # fix this, we can return false if there is an error
                            'try:',
                            pyx.indent(
                                "return isinstance(self, other)"
                            ),
                            'except:',
                            pyx.indent(
                                'return type(self) is type(other)'
                            )
                        ) 
                    ) # end __eq__
                ),

                extends=ast.extends
            ), # end create_class

            # This code cleans up all of the objects we have created so they
            # don't cause any weird and unexpected variable conflicts
            pyx.program(
                # Generate all of the class objects for the enum
                ast.body.visit(self),

                # Assign all of the enums to the class
                f"{self.parent_name}.__assign_enum_types__({self.parent_name}, {', '.join(arg.name.string for arg in ast.body.identifiers)})\n\n\n",
                
                # Clean up the class objects
                *[f'del({arg.name.string})'
                  for arg in ast.body.identifiers], '\n'            
            )
    )

    def enum_body(self, ast: EnumBody) -> str:
        """Generates a "program" from all of the statements in the body
        """

        return pyx.program(
            *[item.visit(self) for item in ast.identifiers]
        )

    def enum_basic_item(self, ast: EnumBasicItem) -> str:
        """Creates a class that is the python representation of a basic enum time
        """

        return pyx.create_class(
            # Class name
            ast.name.string,

            # Class body
            pyx.program(
                pyx.create_func('__str__', 'self',
                                f"return '{ast.name.string}'")
            ),

            # The class extensions
            extends=self.parent_name
        )

    def enum_tuple_arg(self, ast: EnumTupleArg) -> str:
        """Function argument for a tuple enum"""
        return f"{ast.name.string}{f': {ast.item_type}' if ast.item_type else ''}"

    def enum_tuple_item(self, ast: EnumTupleItem) -> str:
        """Constructs a class for a tuple enum item"""

        return pyx.create_class(
            # Class name
            ast.name.string,

            # Class body
            pyx.program(
                pyx.create_func(
                    # Function name
                    '__init__',

                    # Args
                    ', '.join([
                        'self',
                        *[arg.visit(self) for arg in ast.args]
                    ]),

                    # Function body
                    pyx.program(*[
                        f"self.{arg.name.string} = {arg.name.string}"
                        for arg in ast.args
                    ])
                ), # End of __init__ function

                # Responsible for handling converting the output to a string
                pyx.create_func(
                    # Function name
                    '__str__', 

                    # Args
                    'self',

                    # Function body
                    f"return f'{ast.name.string}({', '.join([arg.name.string + ': {self.' + arg.name.string + '}' for arg in ast.args])})'"
                ) # End of __str__ function
            ), # End of class body

            extends=self.parent_name
        )

    def translate(self, ast: Enum) -> str:
        # Macro translation uses the Visitor Pattern for a structure. Structure
        # based off my memory of the Crafting Interpreters section on this
        # adapted from translation rather than execution
        #
        # https://craftinginterpreters.com/evaluating-expressions.html
        return ast.visit(self)
