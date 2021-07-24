__all__ = [
    "Extractor",
    "ScanResult",
]


from dataclasses import dataclass, field
from typing import Any, Generic, List, Optional, Sequence, TypeVar, Union, overload

from bs4 import BeautifulSoup, Tag

T = TypeVar("T")
ExtractorType = TypeVar("ExtractorType", bound="Extractor[Any]")


@dataclass(frozen=True)
class ScanResult(Generic[ExtractorType, T], Sequence[T]):
    extractor: ExtractorType
    elements: List[Union[Tag, T]] = field(repr=False)

    @overload
    def __getitem__(self, index: int) -> T:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[T]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[T, Sequence[T]]:  # type: ignore
        index_slice = (
            slice(index % len(self), (index % len(self)) + 1)
            if isinstance(index, int)
            else index
        )

        self.elements[index_slice] = [
            self.extractor.process(item) if isinstance(item, Tag) else item
            for item in self.elements[index_slice]
        ]

        return self.elements[index]  # type: ignore

    def __len__(self) -> int:
        return len(self.elements)


@dataclass(frozen=True)
class Extractor(Generic[T]):
    selector: str

    def scan(
        self: ExtractorType,
        html: BeautifulSoup,
        limit: Optional[int] = None,
    ) -> ScanResult[ExtractorType, T]:
        return ScanResult[ExtractorType, T](
            self, html.select(self.selector, limit=limit)  # type: ignore
        )

    def process(self, element: Tag) -> T:
        raise NotImplementedError()
