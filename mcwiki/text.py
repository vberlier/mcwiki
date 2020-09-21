__all__ = ["TextExtractor"]


from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

from .extractor import Extractor
from .utils import normalize_string


@dataclass(frozen=True)
class TextExtractor(Extractor[str]):
    selector: str = "*"

    def extract_from_html(self, html: BeautifulSoup) -> str:
        if elements := html.select(self.selector, limit=self.nth):
            return self.extract(elements[-1])
        return ""

    def extract(self, element: Tag) -> str:
        return normalize_string(element.text)
