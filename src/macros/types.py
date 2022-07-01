from abc import ABC, abstractmethod
from tokenize import TokenInfo
from typing import List

from tokens import Tokens


class MacroParser(ABC):
    @abstractmethod
    def parse(self, tokens: Tokens) -> any:
        pass


class MacroTranslator(ABC):
    @abstractmethod
    def translate(self, ast: any) -> List[TokenInfo]:
        pass