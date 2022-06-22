import token
import tokenize
from typing import List
import pytest

from tokens import TokenCase, Tokens
from utils import get_tokens, tokens_to_list


class TestTokenCase:
    def test_valid_token(self):
        assert TokenCase().type(token.NL).check(
            tokenize.TokenInfo(token.NL, 'NL', (1, 1), (1, 1), ''))

    def test_invalid_token(self):
        assert not TokenCase().type(token.NL).check(
            tokenize.TokenInfo(token.NEWLINE, 'NEWLINE', (1, 1), (1, 1), ''))

    def test_valid_string(self):
        assert TokenCase().string('NL').check(
            tokenize.TokenInfo(token.NL, 'NL', (1, 1), (1, 1), ''))

    def test_invalid_string(self):
        assert not TokenCase().string('NL').check(
            tokenize.TokenInfo(token.NL, 'NEWLINE', (1, 1), (1, 1), ''))


def includes_tokens(checker: TokenCase, tokens: List[tokenize.TokenInfo]):
    for individual_token in tokens:
        if checker.check(individual_token):
            return True

    return False


class TestTokens:
    def get_example_tokens(self) -> List[tokenize.TokenInfo]:
        return tokens_to_list(get_tokens('./tests/units/example.py'))

    def test_initialization(self):
        tokens = Tokens(self.get_example_tokens(), 'example.py')

        assert includes_tokens(TokenCase().type(token.NEWLINE),
                               tokens.internal_token)

        assert not includes_tokens(TokenCase().type(token.NL),
                                   tokens.internal_token)
        assert not includes_tokens(TokenCase().type(token.COMMENT),
                                   tokens.internal_token)

    def test_peek(self):
        tokens = Tokens(self.get_example_tokens(), 'example.py')

        assert tokens.peek().type == token.NAME
        assert tokens.peek().string == 'for'

    def test_advance(self):
        tokens = Tokens(self.get_example_tokens(), 'example.py')
        first_token = tokens.advance()

        assert first_token.type == token.NAME
        assert first_token.string == 'for'

    def test_previous(self):
        tokens = Tokens(self.get_example_tokens(), 'example.py')
        tokens.advance()

        assert tokens.previous().type == token.NAME
        assert tokens.previous().string == 'for'

    def test_is_at_end(self):
        tokens = Tokens(self.get_example_tokens(), 'example.py')

        for _ in range(len(tokens.internal_token) - 1):
            assert not tokens.is_at_end()
            tokens.advance()

        assert tokens.is_at_end()

    def test_consume(self):
        tokens = Tokens(self.get_example_tokens(), 'example.py')

        assert tokens.consume(TokenCase().type(token.NAME).string('for'),
                              'Expected "for"')

        with pytest.raises(Exception):
            # This will throw an Exception
            tokens.consume(TokenCase().type(token.NAME).string('for'),
                           'Expected "for"')

    def test_check(self):
        tokens = Tokens(self.get_example_tokens(), 'example.py')

        assert tokens.check(TokenCase().type(token.NAME).string('for'))
        assert not tokens.check(TokenCase().type(token.OP).string('_'))

        for _ in range(len(tokens.internal_token) - 1):
            tokens.advance()

        # At the end it should return false
        assert tokens.is_at_end()
        assert not tokens.check(TokenCase().type(token.NAME).string('for'))

    def test_match(self):
        tokens = Tokens(self.get_example_tokens(), 'example.py')

        assert tokens.match(TokenCase().type(token.NAME).string('for'),
                            TokenCase().type(token.OP).string('_'))
        assert tokens.current_token_index == 1
        assert not tokens.match(TokenCase().type(token.NAME).string('for'),
                                TokenCase().type(token.NAME).string('in'))

    def test_iterator(self):
        tokens = Tokens(self.get_example_tokens(), 'example.py')

        for _ in tokens:
            pass

        assert tokens.is_at_end()
        with pytest.raises(StopIteration):
            next(tokens)
