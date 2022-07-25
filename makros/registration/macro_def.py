from tokenize import TokenInfo
import importlib.util as _importlib_util


class MacroDef:
    macro_name: str

    trigger_token: TokenInfo
    parser_file_location: str

    def __init__(self, macro_name: str, trigger_token: TokenInfo,
                 parser_file_location: str) -> None:
        self.macro_name = macro_name
        self.trigger_token = trigger_token
        self.parser_file_location = parser_file_location

        spec = _importlib_util.spec_from_file_location(
            macro_name, parser_file_location)
        module = _importlib_util.module_from_spec(spec)

        if module is None:
            raise Exception("Module is None")

        spec.loader.exec_module(module)
        self.parser_module = module
