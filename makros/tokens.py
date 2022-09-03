import tokenize
from typing import List, Optional


class TokenCase:
    """Used to check if a token matches specific details
    """

    _token_type: Optional[int] = None
    _token_string: Optional[str] = None

    def type(self, new_type: int):
        """Specifies the token type to check against

        Args:
            new_type (int): The token type to check against

        Returns:
            TokenCase: This TokenCase instance, used for checking
        """
        self._token_type = new_type
        return self

    def string(self, new_str: str):
        """Specifies a string to be checked against to see if it matches

        Args:
            new_str (str): The string to check against

        Returns:
            TokenCase: This TokenCase instance, used for chaining
        """

        self._token_string = new_str
        return self

    def check(self, token: tokenize.TokenInfo) -> bool:
        """Checks a specific token against the information provided here

        Args:
            token (tokenize.TokenInfo): The token to check against

        Returns:
            bool: If it matches or not
        """

        if self._token_type is not None and self._token_type != token.type:
            return False

        if self._token_string is not None and self._token_string != token.string:
            return False

        return True

class TokenException(Exception):
    pass

class Tokens:
    """
    A helper class that wraps around a list of tokens, providing common methods
    that might be needed for writing a recursive decent parser
    """

    _current_token_index: int = 0

    def __init__(self, tokens: List[tokenize.TokenInfo], filename: str):
        self.filename = filename

        # Filter logical newlines and comments, as they are not handled well by
        # the macros that are implemented and provide no good value
        self.internal_token = list(
            filter(lambda x: x.type not in (tokenize.NL, tokenize.COMMENT),
                   tokens))

    def error(self, token_something_else: tokenize.TokenInfo, message: str):
        """Will print an error message at the specific token, including context,
        to help the programmer figure out what is going wrong

        Args:
            token_something_else (tokenize.TokenInfo): The token that the error occurred at
            message (str): Your human readable error message

        Raises:
            Exception: The error for a stack trace
        """

        from rich import print

        # f-strings cannot contain backslashes and this has a new line at the 
        # end
        line = token_something_else.line.replace('\n', '')

        print(
            f"[bold red]Error at line {token_something_else.start[1]}:[/bold red] {message}"
        )
        print(f"\t[white] | {line}[/white]")
        # NOTE: This will not correctly handle multiline tokens
        print(
            f"\t[yellow]    {' ' * token_something_else.start[0]}{'¯' * (token_something_else.end[1] - token_something_else.start[0])}[/yellow]"
        )
        print(f"\t[yellow]    {' ' * token_something_else.start[0]}Error found here[/yellow]")

        # Throw us out of the parser. This error will be caught by the CLI but
        # should still provide a backtrace if anyone is using this in a custom
        # build system
        raise TokenException()

    def peek(self) -> tokenize.TokenInfo:
        """
        Returns what the next token will be without modifying the current toke
        in the buffer
        """
        return self.internal_token[self._current_token_index]

    def previous(self) -> tokenize.TokenInfo:
        """Returns the token before the current one

        Returns:
            tokenize.TokenInfo: The last token
        """

        return self.internal_token[self._current_token_index - 1]

    def advance(self) -> tokenize.TokenInfo:
        """Goes forward one token

        Returns:
            tokenize.TokenInfo: The token that was just passed over
        """
        
        if not self.is_at_end():
            self._current_token_index += 1

        return self.previous()

    def is_at_end(self) -> bool:
        """
        Returns true if the next token is an end marker
        """
        return self.peek().type == tokenize.ENDMARKER

    def consume(self, checker: TokenCase,
                failure_message: str) -> tokenize.TokenInfo:
        """Will consume the next token if it matches the checker, otherwise it
        will raise an error

        Args:
            checker (TokenCase): The case that will be checked against
            failure_message (str): The error message that you want to provide to the user

        Returns:
            tokenize.TokenInfo: The consumed token
        """

        if self.check(checker):
            return self.advance()

        self.error(self.peek(), f"{failure_message}, found '{self.peek().string}'")

    def check(self, checker: TokenCase) -> bool:
        """Checks the next token against the next token in the buffer

        Args:
            checker (TokenCase): The token checking case that you want to check

        Returns:
            bool: If the token matches the case
        """

        if self.is_at_end():
            return False

        return checker.check(self.peek())

    def match(self, *types: TokenCase) -> bool:
        """Matches any of the provided cases against the next token. Advances if
        it finds a new one

        Returns:
            bool: If it has found a match to any of the different checkers
        """
        
        for checker in types:
            if checker.check(self.peek()):
                self.advance()
                return True

        return False

    # Iterator methods are used by the for loop in MakroParser

    def __iter__(self):
        """The actual iterator is created in the __next__ function."""
        return self

    def __next__(self) -> tokenize.TokenInfo:
        """
        This allows for me to use for loops on this class and everything will
        work mostly perfectly
        """
        if self.is_at_end():
            raise StopIteration

        return self.advance()
