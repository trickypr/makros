import token
import tokenize
from typing import List
from xmlrpc.client import boolean


class TokenCase:
    token_type: int = None
    token_string: str = None

    def type(self, new_type: int):
        self.token_type = new_type
        return self

    def string(self, new_str: str):
        self.token_string = new_str
        return self

    def check(self, token: tokenize.TokenInfo) -> bool:
        if self.token_type is not None and self.token_type != token.type:
            return False

        if self.token_string is not None and self.token_string != token.string:
            return False

        return True


class Tokens:

    current_token: tokenize.TokenInfo = None
    current_token_index: int = 0

    filter_new_lines = False
    filter_logical_lines = True
    """
    Filters logical line tokens. For more information about this type of token,
    see: https://docs.python.org/3/library/token.html#token.NL
    """
    filter_comments = True

    def __init__(self, tokens: List[tokenize.TokenInfo], filename: str):
        # self.internal_token = tokens
        self.filename = filename
        self.internal_token = list(
            filter(lambda x: x.type != token.NL and x.type != token.COMMENT,
                   tokens))

    def error(self, token_something_else: tokenize.TokenInfo, message: str):
        # TODO: Better error handling
        raise Exception(
            f"At line {token_something_else.start[1]} ({token.tok_name[token_something_else.type]}['{token_something_else.string}']) in {self.filename}, {message}\n\t|{token_something_else.line}"
        )

    def peek(self) -> tokenize.TokenInfo:
        """
        Returns what the next token will be without modifying the current toke
        in the buffer
        """
        return self.internal_token[self.current_token_index]

    def previous(self) -> tokenize.TokenInfo:
        return self.internal_token[self.current_token_index - 1]

    def advance(self) -> tokenize.TokenInfo:
        if not self.is_at_end():
            self.current_token_index += 1

        return self.previous()

    def is_at_end(self) -> boolean:
        """
        Returns true if the next token is an end marker
        """
        return self.peek().type == token.ENDMARKER

    # ==============
    # Code functions
    # ==============

    def consume(self, checker: TokenCase,
                failure_message: str) -> tokenize.TokenInfo:
        if self.check(checker):
            return self.advance()

        self.error(self.peek(), failure_message)

    def check(self, checker: TokenCase) -> boolean:
        if self.is_at_end():
            return False

        return checker.check(self.peek())

    def match(self, *types: TokenCase) -> bool:
        for checker in types:
            if checker.check(self.peek()):
                self.advance()
                return True

        return False

    def __iter__(self):
        """The actual iterator is created in the __next__ function"""
        return self

    def __next__(self) -> tokenize.TokenInfo:
        """
        This allows for me to use for loops on this class and everything will
        work mostly perfectly
        """
        if self.is_at_end():
            raise StopIteration

        return self.advance()