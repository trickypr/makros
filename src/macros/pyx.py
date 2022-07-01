import tokenize
from typing import List, Optional


def program(*args: tokenize.TokenInfo) -> List[tokenize.TokenInfo]:
    return_val: List[tokenize.TokenInfo] = []

    for arg in args:
        return_val.append(arg)

    return return_val


def string_as_token(string: str) -> tokenize.TokenInfo:
    return tokenize.TokenInfo(tokenize.OP, string, (0, 0), (0, 0), '')


def tokens_as_string(tokens: List[tokenize.TokenInfo]) -> str:
    return ''.join([token.string for token in tokens])


def indent(contents: List[tokenize.TokenInfo], indentation: str = '    ') -> List[tokenize.TokenInfo]:
    return [tokenize.TokenInfo(tokenize.INDENT, indentation, (0, 0), (0, 0), '')] + contents + [tokenize.TokenInfo(tokenize.DEDENT, '', (0, 0), (0, 0), '')]


def create_func(name: str, args: str, body: List[tokenize.TokenInfo]) -> List[tokenize.TokenInfo]:
    return [tokenize.TokenInfo(tokenize.NAME, 'def', (0, 0), (0, 0), ''),
            tokenize.TokenInfo(tokenize.NAME, name, (0, 0), (0, 0), ''),
            tokenize.TokenInfo(tokenize.OP, '(', (0, 0), (0, 0), ''),
            tokenize.TokenInfo(tokenize.OP, args, (0, 0), (0, 0), ''),
            tokenize.TokenInfo(tokenize.OP, ')', (0, 0), (0, 0), ''),
            tokenize.TokenInfo(tokenize.NEWLINE, '\n', (0, 0), (0, 0), '')] + indent(body)


def create_class(name: str, body: List[tokenize.TokenInfo], extends: Optional[str] = None) -> List[tokenize.TokenInfo]:
    return [tokenize.TokenInfo(tokenize.NAME, 'class', (0, 0), (0, 0), ''),
            tokenize.TokenInfo(tokenize.NAME, name, (0, 0), (0, 0), '')
            ] + ([tokenize.TokenInfo(tokenize.OP, '(' + extends + ')', (0, 0), (0, 0), '')] if extends else []
                 ) + indent(body)
