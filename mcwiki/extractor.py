__all__ = ["Extractor", "ScanResult"]


from dataclasses import dataclass, field
from typing import Generic, List, Sequence, TypeVar, Union, overload

from bs4 import BeautifulSoup, Tag

T = TypeVar("T")
ExtractorType = TypeVar("ExtractorType", bound="Extractor")


@dataclass(frozen=True)
class ScanResult(Generic[ExtractorType, T], Sequence[T]):
    extractor: ExtractorType
    elements: List[Union[Tag, T]] = field(repr=False)

    @overload
    def __getitem__(self, index: int) -> T:
        pass

    @overload
    def __getitem__(self, index: slice) -> Sequence[T]:
        pass

    def __getitem__(self, index: Union[int, slice]) -> Union[T, Sequence[T]]:
        index_slice = (
            slice(index % len(self), (index % len(self)) + 1)
            if isinstance(index, int)
            else index
        )

        self.elements[index_slice] = [
            self.extractor.process(item) if isinstance(item, Tag) else item
            for item in self.elements[index_slice]
        ]

        return self.elements[index]

    def __len__(self) -> int:
        return len(self.elements)


@dataclass(frozen=True)
class Extractor(Generic[T]):
    selector: str

    def scan(
        self: ExtractorType, html: BeautifulSoup, limit: int = None
    ) -> ScanResult[ExtractorType, T]:
        return ScanResult(self, html.select(self.selector, limit=limit))

    def process(self, element: Tag) -> T:
        raise NotImplementedError()
