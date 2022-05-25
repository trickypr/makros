import token
import tokenize
from typing import List
from xmlrpc.client import boolean
from more_itertools import peekable


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
            print("Token type mismatch")
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

    def __init__(self, tokens: List[tokenize.TokenInfo]):
        self.internal_token = tokens

    def error(self, token: tokenize.TokenInfo, message: str):
        # TODO: Better error handling
        raise Exception(
            f"At line {token.start[1]} ({token.string}, {token.type}), {message}"
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

        match_cases = []

        if self.filter_logical_lines:
            match_cases.append(TokenCase().type(token.NL))

        if self.filter_new_lines:
            match_cases.append(TokenCase().type(token.NEWLINE))

        if self.filter_comments:
            match_cases.append(TokenCase().type(token.COMMENT))

        self.match(*match_cases)

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

    # def check(self, checker: TokenCase) -> bool:
    #     if self.is_at_end(): return False

    #     return checker.check(self.peek())

    # def consume(self, checker: TokenCase, failure_message: str):
    #     if self.check(checker):
    #         return self.advance()

    #     self.error(self.current(), failure_message)

    # def advance(self):
    #     previous = self.current_token
    #     self.current_token = next(self.internal_token)

    #     # There are some tokens that a parser may want to filter
    #     # out. This will implement the functionality for them to do
    #     # that
    #     # REVIEW: Is this code to heavy? Should it be made more performant?
    #     match_cases = []

    #     if self.filter_logical_lines:
    #         match_cases.append(TokenCase().type(token.NL))

    #     if self.filter_new_lines:
    #         match_cases.append(TokenCase().type(token.NEWLINE))

    #     if self.filter_comments:
    #         match_cases.append(TokenCase().type(token.COMMENT))

    #     # Whilst all of the cases specifed above match, we should
    #     # continue to loop, consuming all of them
    #     while self.match(*match_cases):
    #         pass

    #     print(f"Prev: {previous}, Current: {self.current_token}")

    #     return previous

    # def current(self) -> tokenize.TokenInfo:
    #     if self.current_token is None:
    #         self.advance()

    #     return self.current_token

    # def set_filter_new_lines(self, filter_new_lines: bool) -> None:
    #     self.filter_new_lines = filter_new_lines

    # def next(self) -> tokenize.TokenInfo:
    #     self.current_token = next(self.internal_token)

    #     # print(self.current_token)

    #     if (self.filter_logical_lines and self.current_token.type == token.NL
    #         ) or (self.filter_new_lines
    #               and self.current_token.type == tokenize.NEWLINE) or (
    #                   self.filter_comments
    #                   and self.current_token.type == tokenize.COMMENT):
    #         return self.next()

    #     return self.current_token

    # def check_internal(self,
    #                    token: tokenize.TokenInfo,
    #                    type: int = None,
    #                    string: str = None) -> bool:
    #     if type is not None and type != token.type:
    #         return False

    #     if string is not None and string != token.string:
    #         return False

    #     return True

    # def check_current(self, type: int = None, string: str = None) -> bool:
    #     return self.check_internal(self.current(), type=type, string=string)

    # def check_next(self, type: int = None, string: str = None) -> bool:
    #     return self.check_internal(self.next(), type, string)

    # def verify_internal(self,
    #                     token: tokenize.TokenInfo,
    #                     location: str,
    #                     type: int = None,
    #                     string: str = None) -> tokenize.TokenInfo:

    #     error = ""

    #     if type is not None and type != token.type:
    #         error = f"Expected {type}, found {token.type}"

    #     if string is not None and string != token.string:
    #         error = f"Expected {string}, found {token.string}"

    #     if error:
    #         raise Exception(f"Error {location}\n\t{error}")

    #     return token

    # def verify_current(self,
    #                    location: str,
    #                    type: int = None,
    #                    string: str = None) -> tokenize.TokenInfo:
    #     return self.verify_internal(self.current(), location, type, string)

    # def verify_next(self,
    #                 location: str,
    #                 type: int = None,
    #                 string: str = None) -> tokenize.TokenInfo:
    #     return self.verify_internal(self.next(), location, type, string)

    # # def consume(self, token_type: int, location: str, string=None):
    # #     matches = True
    # #     error = ""
    # #     self.next()

    # #     if token_type != self.current().type:
    # #         matches = False
    # #         error = f"Expected {token_type}, found {self.current().type}"

    # #     if string is not None and string != self.current().string:
    # #         matches = False
    # #         error = f"Expected {string}, found {self.current().string}"

    # #     if not matches:
    # #         raise Exception(f"Error {location}\n\t{error}")
