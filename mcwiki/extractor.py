__all__ = ["Extractor", "ExtractResult"]


from dataclasses import dataclass, field
from typing import Generic, TypeVar, List, Sequence, Union, overload

from bs4 import BeautifulSoup, Tag


T = TypeVar("T")
ExtractorType = TypeVar("ExtractorType", bound="Extractor")


@dataclass(frozen=True)
class ExtractResult(Generic[ExtractorType, T], Sequence[T]):
    extractor: ExtractorType
    elements: List[Union[Tag, T]] = field(repr=False)

    @overload
    def __getitem__(self, index: int) -> T:
        pass

    @overload
    def __getitem__(self, index: slice) -> Sequence[T]:
        pass

    def __getitem__(self, index: Union[int, slice]) -> Union[T, Sequence[T]]:
        if index < 0:
            index %= len(self)
        index_slice = slice(index, index + 1) if isinstance(index, int) else index

        self.elements[index_slice] = [
            self.extractor.transform(item) if isinstance(item, Tag) else item
            for item in self.elements[index_slice]
        ]

        return self.elements[index]

    def __len__(self) -> int:
        return len(self.elements)


@dataclass(frozen=True)
class Extractor(Generic[T]):
    selector: str

    def extract_all(
        self: ExtractorType, html: BeautifulSoup, limit: int = None
    ) -> ExtractResult[ExtractorType, T]:
        return ExtractResult(self, html.select(self.selector, limit=limit))

    def transform(self, element: Tag) -> T:
        raise NotImplementedError()
