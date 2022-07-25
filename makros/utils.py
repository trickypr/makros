import hashlib
import tokenize
from typing import Generator, List, TypeVar


class ReadableString:
    def __init__(self, string: str):
        self.contents = string.split('\n')
        self.line_number = 0

    def readline(self):
        if self.line_number >= len(self.contents):
            raise StopIteration()

        line = self.contents[self.line_number]
        self.line_number += 1
        return f"{line}\n"


def _get_tokens(readline) -> Generator[tokenize.TokenInfo, None, None]:
    return tokenize.generate_tokens(readline)


def get_tokens_from_string(string: str) -> Generator[tokenize.TokenInfo, None, None]:
    tokens = _get_tokens(ReadableString(string).readline)
    for token in tokens:
        yield token


def get_tokens_from_file(file_path: str) -> Generator[tokenize.TokenInfo, None, None]:
    with tokenize.open(file_path) as file:
        tokens = _get_tokens(file.readline)
        for token in tokens:
            yield token


T = TypeVar('T')


def tokens_to_list(tokens: Generator[T, None, None]) -> List[T]:
    return [token for token in tokens]


def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()
