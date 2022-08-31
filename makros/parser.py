from pathlib import Path
import tokenize
from typing import Generator, List, Tuple

from makros.registration.macro_def import MacroDef
from makros.tokens import Tokens
from makros.utils import get_tokens_from_file, get_tokens_from_string, tokens_to_list
import makros.macros.macro_import as macro_import


class MakroParser:
    """
    Provides an api for parsing a single file. You should avoid constructing 
    this class directly and instead use ``Makros.get()``. This provides the 
    following methods for parsing a file:

    - parse: Parses the file at the path that is passed into the constructor and writes content do disk
    - parse_path: Parses the file at the provided path and writes content to disk
    - parse_string: Parses the string provided to the method and returns the output as a string
    - parse_tokens: Parses the tokens provided to the method and returns the output as a string

    Internally, the following state is maintained, it is generally good to avoid
    changing it:

    - available_macros
    - current_indentation

    Because internal state is maintained, it is generally a good idea to create
    a new parser instance for each file that is being parsed.
    """

    available_macros: List[MacroDef] = []
    """The macros that have been imported into the file
    """

    current_indentation: str = ''
    """The current indentation level of the macro file
    """

    def __init__(self, file_path: Path,
                 global_controller: "makros.makros.Makros"):
        self.file_path = file_path
        self.global_controller = global_controller

    def parse_tokens(
            self, raw_tokens: Generator[tokenize.TokenInfo, None,
                                        None]) -> str:
        """
        This is the base parsing method, which will convert a number of 
        tokens into a valid python file.

        Args:
            raw_tokens (Generator[tokenize.TokenInfo, None, None]): The tokens that will be used by the parser

        Returns:
            str: The python file generated from expanding any containing macros
        """

        tokens = Tokens(tokens_to_list(raw_tokens), str(self.file_path))

        # Note that we set this when parsing as some users may wish to parse
        # different files at different times
        self.global_controller._resolver.cwd = self.file_path.parent

        current_line = -1  # We are starting at -1 to make sure we include the first line of the file
        output = ""

        for token in tokens:
            # We need to keep track of by how much each line is indented, so if
            # a macro is inside of an indented block (e.g. a function), the
            # code that is outputted will still correctly execute.
            if token.type == tokenize.INDENT:
                self.current_indentation += token.string

                # Indentation tokens are done before macro parsing, so they can
                # lead to the macro value being passed through to the output
                continue
            
            if  token.type == tokenize.DEDENT:
                self.current_indentation = self.current_indentation[:-len(token.string)]
            
            # End of indentation correction

            # If the token is of type name, we need to check if the token will
            # trigger a macro and, if it will, pass it over to that macro to
            # handle
            if token.type == tokenize.NAME:
                # This handles the import macro, which has been hard coded to
                # because it requires some more complex logic than a standard
                # macro, i.e. access to the available_macros List
                if token.string == 'macro':
                    # Grab a copy of the parser
                    parser = macro_import.Parser()

                    # Parse the macro. Note that we will not be using the
                    # translate module of the macro, as we have to handle custom
                    # state within this class regarding it
                    macro_ast = parser.parse(tokens)
                    macro_string = macro_ast.module.string

                    # If the macro attribute is specified, it means that it is
                    # an external macro, which needs to have a different path
                    if macro_ast.macro:
                        macro_string += "."
                        macro_string += macro_ast.macro.string

                    # Add the macro to the list of available macros after the
                    # resolver method has found it
                    self.available_macros.append(
                        self.global_controller._resolver.resolve(macro_string))

                    # Provide a reference comment to the developer
                    output += f"# Macro imported: {macro_string}\n"
                    
                    # Don't let anything else touch this macro
                    continue

                # Check if the macro is actually a macro. If it is, enabled will
                # be set to true. The logic is not here, because it is messy
                enabled, returned = self._parse_macro(tokens, token)

                # The returned value will be empty if the macro is not enabled
                output += returned

                # Enabled will only be true if parse_macro has found a macro. So
                # we should only skip the token if it has found a macro,
                # otherwise, we want other like-based token logic to run
                if enabled:
                    continue

            # We want to only keep one of each line, and only lines without
            # a macro on them. This is my current solution, but if you have
            # a better one, feel free to create a PR
            #
            # NOTE: Might it be a good idea to use the untokenise part of the
            # python tokeniser and just get the macros to return a list of tokens
            # rather than a string? That might reduce the number of bugs with
            # string handling and simplify this kind of code.
            if token.start[
                    0] > current_line and token.type != tokenize.DEDENT and token.type != tokenize.NEWLINE:
                output += token.line
                current_line = token.start[0]

        # Write the macro to the disk
        return output

    def parse_string(self, string: str) -> str:
        """Expand any macros used in the inputted string

        Args:
            string (str): The string that contains macros to be expanded

        Returns:
            str: The python generated from expanding the containing macros.
        """

        # Take advantage of pythons tokenizer to tokenise the file and build a
        # helper object around it
        raw_tokens = get_tokens_from_string(string)
        return self.parse_tokens(raw_tokens)

    def parse(self) -> None:
        """Reads the file provided in the Parser constructor, expands any of the
        containing macros and outputs them back to the disk. 
        """

        self.parse_path(self.file_path)

    def parse_path(self, path: Path) -> None:
        """Parses the provided path and writes the contents to disk

        Args:
            path (Path): The path you wish to parse
        """

        # Take advantage of pythons tokenizer to tokenise the file and build a
        # helper object around it
        raw_tokens = get_tokens_from_file(str(path))

        output = self.parse_tokens(raw_tokens)

        # Write the macro to the disk
        out_path = str(path).replace('.mpy', '.py')
        with open(out_path, 'w') as file:
            file.write(output)

    def _parse_macro(self, tokens: Tokens,
                    token: tokenize.TokenInfo) -> Tuple[bool, str]:
        """This function is called on every name token to see if it matches one
        of the custom imported macros.

        Args:
            tokens (Tokens): All of the tokens after the trigger token in the file
            token (tokenize.Token): The trigger token

        Returns:
            Tuple[bool, str]: The status of the macro, the first one is if a macro was found and the second one is its output
        """

        # Search through the macros that have been imported into this file and
        # see if the trigger token of any of them matches the current token
        for macro in self.available_macros:
            if macro.trigger_token.string == token.string:
                # The parser class is imported when the macro is imported. Here
                # we just retrieve the parser class
                Parser = macro.parser_module.Parser
                parser = Parser()

                # Parsers **MUST** always have a parse function, otherwise they
                # are not a parser. This is layed out in the implementation docs
                macro_ast = parser.parse(tokens)

                # If there is a linter, we should run it. There is not
                # currently any linters, and the code is not tested, but may as 
                # well add the infrastructure.
                if hasattr(macro.parser_module, 'Linter'):
                    Linter = macro.parser_module.Linter
                    linter = Linter()
                    linter.lint(macro_ast)

                # Passes the AST into a translator module. Responsible
                # for creating python string from the AST.
                Translator = macro.parser_module.Translator
                translator = Translator()

                # Don't trust the developer (probably me) to provide leading and
                # trailing new lines
                return (True, "\n" + f'\n{self.current_indentation}'.join(translator.translate(macro_ast).split('\n')) + "\n")

        return (False, "")
