__all__ = ["load", "from_markup", "collect_elements", "PageSection"]


import re
from copy import copy
from typing import TypeVar, Mapping, Dict, Union, Iterator

import requests
from bs4 import BeautifulSoup, Tag, PageElement

from .extractor import Extractor
from .utils import normalize_string


BASE_URL = "https://minecraft.gamepedia.com/"


def load(page: str) -> "PageSection":
    if not page.startswith("http"):
        page = BASE_URL + re.sub(r"[\s_]+", "_", page)
    return from_markup(requests.get(page).text)


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

    def __init__(self, html: BeautifulSoup):
        self.html = html
        self.subsections = {
            heading.text: heading.parent
            for heading in html.find_all("span", "mw-headline")
        }

    def __getitem__(self, heading) -> "PageSection":
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

    def extract(self, extractor: Extractor[T]) -> T:
        return extractor.extract_from_html(self.html)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {list(self)}>"
