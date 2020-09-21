__all__ = ["Extractor"]


from dataclasses import dataclass, field, replace
from typing import Generic, TypeVar

from bs4 import BeautifulSoup, Tag


T = TypeVar("T")
ExtractorType = TypeVar("ExtractorType", bound="Extractor")


@dataclass(frozen=True)
class Extractor(Generic[T]):
    nth: int = field(default=1, compare=False)

    def extract_from_html(self, html: BeautifulSoup) -> T:
        return self.extract(html)

    def extract(self, element: Tag) -> T:
        raise NotImplementedError()

    def __matmul__(self: ExtractorType, nth: int) -> ExtractorType:
        return replace(self, nth=nth)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} @ {self.nth}>"
