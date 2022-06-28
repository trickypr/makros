import json
from os.path import isfile, join
from os import listdir
from pathlib import Path
import tokenize
from typing import List, Tuple
import hashlib

from registration.macro_def import MacroDef
from registration.resolver import Resolver
from tokens import Tokens
from utils import get_tokens, progressBar, tokens_to_list
import macros.macro_import as macro_import

BOOTSTRAP_FOLDERS = ['macros', 'registration']
HASH_FILE = Path(__file__).parent.joinpath('macros').__str__() + '.json'


def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()


class PyMacro:
    """Keeps track of global state and is used for transpiling files. You should
     avoid creating multiple instances of this in your application as required 
     tasks (e.g. Bootstraping) will be run multiple times and may cause a race 
     condition
    """
    def __init__(self):
        self.resolver = Resolver()
        self.bootstrap()
        self.resolver.add_lib(self)

    def bootstrap_file(self, folder_path, file, macro_hash):
        """Will bootstrap a specific file if a similar version of that file has
        not already been boostraped

        Args:
            folder_path (str): THe folder the file will be contained in
            file (str): The file name and extension to be transpiled
            macro_hash (dict): A dictionary containing the hashes of all of the already transpiled files

        Returns:
            str: (Optional) the hash of the newly created file, if any
        """

        # If the file doesn't exist or doesn't end with .mpy, we do not want to
        # attempt to parse it
        if not isfile(join(folder_path, file)) or not file.endswith('.mpy'):
            return

        # The sha256 checksum of the file, used to determine if the file has been
        # chanced since the last time it was parsed
        file_hash = sha256sum(join(folder_path, file))

        # Will will skip if all of the following conditions are true
        #  - The macro_hash object has been defined
        #  - The macro_hash object contains this file
        #  - The file hash matches the macro_hash of this file
        if macro_hash is not None and macro_hash.__contains__(
                folder_path + file) and file_hash == macro_hash[folder_path +
                                                                file]:
            return

        self.parse_file(Path(join(folder_path, file)))

        # Return the new macro hash so it can be updated
        return file_hash

    def bootstrap(self) -> None:
        """Will parse and convert all of the mpy files into py files so that
        other parts makros can use them, reducing the amount of code I have to
        write
        """

        # Define a fallback dictionary in case the HASH_FILE has not yet been
        # created
        macro_hash = {}

        if isfile(HASH_FILE):
            macro_hash = json.loads(open(HASH_FILE).read())

        for folder in BOOTSTRAP_FOLDERS:
            folder_path = Path(__file__).parent.joinpath(folder).__str__()

            # For all of the files in this folder, run bootstrap then update the
            # macro hash if it has changed to avoid future recompiles
            for file in progressBar(listdir(folder_path), 'Parsing macros'):
                new_hash = self.bootstrap_file(folder_path, file, macro_hash)

                if new_hash:
                    macro_hash[folder_path + file] = new_hash

        # Write the hash file back to disk
        with open(HASH_FILE, 'w') as file:
            file.write(json.dumps(macro_hash))

    def parse_macro(self, tokens: Tokens, token: tokenize.Token,
                    available_macros: List[MacroDef]) -> Tuple[bool, str]:
        """This function is called on every name token to see if it matches one
        of the custom imported macros.

        Args:
            tokens (Tokens): All of the tokens after the trigger token in the file
            token (tokenize.Token): The trigger token
            available_macros (List[MacroDef]): A list of all of the available macros

        Returns:
            Tuple[bool, str]: The status of the macro, the first one is if a macro was found and the second one is its output
        """

        for macro in available_macros:
            if macro.trigger_token.string == token.string:
                Parser = macro.parser_module.Parser
                parser = Parser()

                macro_ast = parser.parse(tokens)

                # If there is a linter, we should run it. There is not
                # currently any linters, but may as well add the
                # infrastructure.
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
                return [True, "\n" + translator.translate(macro_ast) + "\n"]

        return [False, ""]

    def parse_file(self, file_path: Path) -> None:
        """Will parse a file and write it to the same folder on the disk

        Args:
            file_path (Path): The path to the file you want to parse
        """

        # Used to keep track of the macros referenced by the current file
        available_macros: List[MacroDef] = []

        # Take advantage of pythons tokenizer to tokenise the file and build a
        # helper object around it
        raw_tokens = get_tokens(str(file_path))
        tokens = Tokens(tokens_to_list(raw_tokens), str(file_path))

        # Give the resolver the current working directory, it will need this to
        # find local macros
        self.resolver.cwd = file_path.parent

        current_line = 0
        output = ""

        for token in tokens:
            # If the token is of type name, we need to check if the token will
            # trigger a macro and, if it will, pass it over to that macro to
            # handle
            if token.type == tokenize.NAME:
                # This handles the import macro, which has been hard coded to
                # because it requires some more complex logic than a standard
                # macro, i.e. access to the available_macros List
                if token.string == 'macro':
                    parser = macro_import.Parser()

                    macro_ast = parser.parse(tokens)
                    macro_string = macro_ast.module.string

                    if macro_ast.macro:
                        macro_string += "."
                        macro_string += macro_ast.macro.string

                    available_macros.append(
                        self.resolver.resolve(macro_string))
                    output += f"# Macro imported: {macro_string}\n"

                    continue

                enabled, returned = self.parse_macro(tokens, token,
                                                     available_macros)

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
        out_path = str(file_path).replace('.mpy', '.py')
        with open(out_path, 'w') as file:
            file.write(output)


def get_files(folder_name: str) -> List[str]:
    all_items = [join(folder_name, item) for item in listdir(folder_name)]

    folders = [item for item in all_items if not isfile(item)]
    files = [item for item in all_items if isfile(item)]

    for folder in folders:
        files.extend(get_files(folder))

    return files


def translate_file(
    file_name: str, macro_instance: PyMacro = PyMacro()) -> PyMacro:
    macro_instance.parse_file(Path(file_name))

    return macro_instance


def translate_folder(
    folder_name: str, macro_instance: PyMacro = PyMacro()) -> PyMacro:
    files = [
        Path(file) for file in get_files(folder_name) if file.endswith('.mpy')
    ]

    for file in progressBar(files):
        macro_instance.parse_file(file)

    return macro_instance
