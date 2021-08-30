__all__ = [
    "load",
    "load_file",
    "from_markup",
    "collect_elements",
    "PageSection",
]


import re
from copy import copy
from pathlib import Path
from typing import Dict, Iterator, Mapping, Optional, TypeVar, Union

import requests
from bs4 import BeautifulSoup, PageElement, Tag

from .extractor import Extractor, ScanResult
from .utils import normalize_string

BASE_URL = "https://minecraft.fandom.com/wiki/"


def load(page: str) -> "PageSection":
    if not page.startswith("http"):
        page = BASE_URL + re.sub(r"[\s_]+", "_", page)
    return from_markup(requests.get(page).text)


def load_file(filepath: Union[str, Path]) -> "PageSection":
    return from_markup(Path(filepath).read_text())


def from_markup(markup: str) -> "PageSection":
    html = BeautifulSoup(markup, "html.parser")
    content = html.find("div", "mw-parser-output").extract()
    return PageSection(content)


def collect_elements(start: Tag) -> Iterator[PageElement]:
    for sibling in start.next_siblings:
        tag = sibling.name
        if tag and tag.startswith("h") and tag <= start.name:
            break
        yield sibling


T = TypeVar("T")


class PageSection(Mapping[str, "PageSection"]):
    html: BeautifulSoup
    subsections: Dict[str, Union[Tag, "PageSection"]]

    def __init__(self, html: BeautifulSoup) -> None:
        self.html = html
        self.subsections = {
            heading.text.lower(): heading.parent
            for heading in html.find_all("span", "mw-headline")
        }

    def __getitem__(self, heading: str) -> "PageSection":
        heading = heading.lower()
        section = self.subsections[heading]

        if not isinstance(section, PageSection):
            content = BeautifulSoup(features="html.parser")
            content.extend(map(copy, collect_elements(section)))
            section = PageSection(content)
            self.subsections[heading] = section

        return section

    def __iter__(self) -> Iterator[str]:
        return iter(self.subsections)

    def __len__(self) -> int:
        return len(self.subsections)

    @property
    def text(self):
        return normalize_string(self.html.text)

    def extract_all(
        self,
        extractor: Extractor[T],
        limit: Optional[int] = None,
    ) -> ScanResult[Extractor[T], T]:
        return extractor.scan(self.html, limit=limit)

    def extract(self, extractor: Extractor[T], index: int = 0) -> Optional[T]:
        items = self.extract_all(extractor, limit=index + 1)
        return items[index] if index < len(items) else None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {list(self)}>"
