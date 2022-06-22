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


def macro_file(file_name: str) -> str:
    return Path(__file__).parent.joinpath('macros').joinpath(
        file_name).__str__()


def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()


class PyMacro:
    def __init__(self):
        self.resolver = Resolver()
        self.bootstrap()
        self.resolver.add_lib(self)

    def bootstrap_file(self, folder_path, file, macro_hash):
        if not isfile(join(folder_path, file)):
            return

        if not file.endswith('.mpy'):
            return

        file_hash = sha256sum(join(folder_path, file))
        if macro_hash is not None and macro_hash.__contains__(
                folder_path + file) and file_hash == macro_hash[folder_path +
                                                                file]:
            return

        self.parse_file(Path(join(folder_path, file)))

        return file_hash

    def bootstrap(self) -> None:
        folders = ['macros', 'registration']
        hash_file = Path(__file__).parent.joinpath(
            'macros').__str__() + '.json'

        macro_hash = {}

        if isfile(hash_file):
            macro_hash = json.loads(open(hash_file).read())

        for folder in folders:
            folder_path = Path(__file__).parent.joinpath(folder).__str__()

            for file in progressBar(listdir(folder_path), 'Parsing macros'):
                new_hash = self.bootstrap_file(folder_path, file, macro_hash)

                if new_hash:
                    macro_hash[folder_path + file] = new_hash

        with open(hash_file, 'w') as file:
            file.write(json.dumps(macro_hash))

    def parse_macro(self, tokens: Tokens, token: tokenize.Token,
                    available_macros: List[MacroDef]) -> Tuple[bool, str]:
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
        available_macros: List[MacroDef] = []
        raw_tokens = get_tokens(str(file_path))
        tokens = Tokens(tokens_to_list(raw_tokens), str(file_path))

        self.resolver.cwd = file_path.parent

        current_line = 0
        output = ""

        for token in tokens:
            if token.type == tokenize.NAME:
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
            if token.start[
                    0] > current_line and token.type != tokenize.DEDENT and token.type != tokenize.NEWLINE:
                output += token.line
                current_line = token.start[0]

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
