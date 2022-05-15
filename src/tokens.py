import token
import tokenize
from typing import Generator
from xmlrpc.client import boolean


class Tokens:
    current_token: tokenize.TokenInfo

    filter_new_lines = False
    filter_logical_lines = True
    filter_comments = True
    """
    Filters logical line tokens. For more information about this type of token,
    see: https://docs.python.org/3/library/token.html#token.NL
    """
    def __init__(self, tokens: Generator[tokenize.TokenInfo, None, None]):
        self.internal_token = tokens

    def current(self) -> tokenize.TokenInfo:
        return self.current_token

    def set_filter_new_lines(self, filter_new_lines: bool) -> None:
        self.filter_new_lines = filter_new_lines

    def next(self) -> tokenize.TokenInfo:
        self.current_token = next(self.internal_token)

        # print(self.current_token)

        if (self.filter_logical_lines and self.current_token.type == token.NL
            ) or (self.filter_new_lines
                  and self.current_token.type == tokenize.NEWLINE) or (
                      self.filter_comments
                      and self.current_token.type == tokenize.COMMENT):
            return self.next()

        return self.current_token

    def check_internal(self,
                       token: tokenize.TokenInfo,
                       type: int = None,
                       string: str = None) -> bool:
        if type is not None and type != token.type:
            return False

        if string is not None and string != token.string:
            return False

        return True

    def check_current(self, type: int = None, string: str = None) -> bool:
        return self.check_internal(self.current(), type=type, string=string)

    def check_next(self, type: int = None, string: str = None) -> bool:
        return self.check_internal(self.next(), type, string)

    def verify_internal(self,
                        token: tokenize.TokenInfo,
                        location: str,
                        type: int = None,
                        string: str = None) -> tokenize.TokenInfo:

        error = ""

        if type is not None and type != token.type:
            error = f"Expected {type}, found {token.type}"

        if string is not None and string != token.string:
            error = f"Expected {string}, found {token.string}"

        if error:
            raise Exception(f"Error {location}\n\t{error}")

        return token

    def verify_current(self,
                       location: str,
                       type: int = None,
                       string: str = None) -> tokenize.TokenInfo:
        return self.verify_internal(self.current(), location, type, string)

    def verify_next(self,
                    location: str,
                    type: int = None,
                    string: str = None) -> tokenize.TokenInfo:
        return self.verify_internal(self.next(), location, type, string)

    def consume(self, token_type: int, location: str, string=None):
        matches = True
        error = ""
        self.next()

        if token_type != self.current().type:
            matches = False
            error = f"Expected {token_type}, found {self.current().type}"

        if string is not None and string != self.current().string:
            matches = False
            error = f"Expected {string}, found {self.current().string}"

        if not matches:
            raise Exception(f"Error {location}\n\t{error}")
