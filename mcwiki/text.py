__all__ = [
    "TextExtractor",
]


from dataclasses import dataclass

from bs4 import Tag

from .extractor import Extractor
from .utils import normalize_string


@dataclass(frozen=True)
class TextExtractor(Extractor[str]):
    def process(self, element: Tag) -> str:
        return normalize_string(element.text)
