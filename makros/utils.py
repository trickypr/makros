import hashlib
import tokenize
from typing import Generator, List, TypeVar


def getFileHash(path: str):
    pass


def progressBar(iterable,
                prefix='',
                suffix='',
                decimals=1,
                length=100,
                fill='█',
                printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)

    Note: This progress bar was stolen from stack overflow:
    https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    """
    total = len(iterable)

    # Progress Bar Printing Function
    def printProgressBar(iteration):
        # Don't even bother displaying the progress bar if there are none or
        # only one file to be parsed.
        if len(iterable) <= 1:
            return

        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        # print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)

    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)

    # This code is a modification by me, hence why it is so bad. It will grab an
    # estimate of the length of the progress bar and then print out the same
    # amount of spaces. Because the progress bar uses carage returns, it will
    # clear the rest of the screen.
    #
    # The additional carage return ensures that the next print statement will
    # appear on the same line.
    #
    # Inelegant, inefficient, but functional
    max_length = len(f"{prefix} |{fill * length}| {'100.0%'} {suffix}")
    # print(" " * max_length, end=printEnd)


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
