from abc import ABC, abstractmethod

from makros.tokens import Tokens


class MacroParser(ABC):
    @abstractmethod
    def parse(self, tokens: Tokens) -> any:  # type: ignore
        pass


class MacroTranslator(ABC):
    @abstractmethod
    def translate(self, ast: any) -> str:  # type: ignore
        pass
