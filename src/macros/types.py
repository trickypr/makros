from abc import ABC, abstractmethod
from typing import Generator

from tokens import Tokens


class MacroParser(ABC):
    @abstractmethod
    def parse(self, tokens: Tokens) -> any:
        pass


class MacroTranslator(ABC):
    @abstractmethod
    def translate(self, ast: any) -> str:
        pass