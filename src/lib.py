from os.path import isfile, join
from os import listdir
from pathlib import Path
import tokenize
from typing import Generator, List

from registration.macro_def import MacroDef
from tokens import Tokens
from utils import progressBar
import macros.macro_import as macro_import


def macro_file(file_name: str) -> str:
    return Path(__file__).parent.joinpath('macros').joinpath(
        file_name).__str__()


# macro_import = MacroDef('macro',
#                         tokenize.TokenInfo(1, 'macro', (1, 1), (1, 1), ''),
#                         macro_file('macroImport.py'))


class PyMacro:
    def get_tokens(
            self, file_path: str) -> Generator[tokenize.TokenInfo, None, None]:
        with tokenize.open(file_path) as file:
            tokens = tokenize.generate_tokens(file.readline)
            for token in tokens:
                yield token

    def tokens_to_list(
        self, tokens: Generator[tokenize.TokenInfo, None, None]
    ) -> List[tokenize.TokenInfo]:
        return [token for token in tokens]

    def parse_file(self, file_path: Path) -> None:
        available_macros: List[MacroDef] = []
        raw_tokens = self.get_tokens(str(file_path))
        tokens = Tokens(self.tokens_to_list(raw_tokens))

        current_line = 0
        output = ""

        for token in tokens:
            if token.type == 1:
                if token.string == 'macro':
                    parser = macro_import.Parser()

                    macro_ast = parser.parse(tokens)
                    # TODO: Better module resolution
                    available_macros.append(
                        MacroDef(
                            macro_ast.module.string,
                            tokenize.TokenInfo(1, macro_ast.module.string,
                                               (1, 1), (1, 1), ''),
                            macro_file(macro_ast.module.string + '.py')))
                    output += f"# Macro imported: {macro_ast.module.string}\n"

                    continue

                found_macro = False

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
                        output += translator.translate(macro_ast)

                        found_macro = True
                        break

                if found_macro:
                    continue

                # We want to only keep one of each line, and only lines without
                # a macro on them. This is my current solution, but if you have
                # a better one, feel free to create a PR
                if token.start[0] != current_line:
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


def translate_folder(folder_name: str, macro_instance: PyMacro = PyMacro()):
    files = [
        Path(file) for file in get_files(folder_name) if file.endswith('.mpy')
    ]

    for file in progressBar(files):
        macro_instance.parse_file(file)
