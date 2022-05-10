from importlib.machinery import SourceFileLoader
from tokenize import TokenInfo


class MacroDef:
    macro_name: str

    trigger_token: TokenInfo
    parser_file_location: str

    def __init__(self, macro_name: str, trigger_token: TokenInfo,
                 parser_file_location: str) -> None:
        self.macro_name = macro_name
        self.trigger_token = trigger_token
        self.parser_file_location = parser_file_location

        self.parser_module = SourceFileLoader(
            macro_name, parser_file_location).load_module()