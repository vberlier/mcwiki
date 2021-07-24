__all__ = [
    "PathLike",
    "FileSystemPath",
    "normalize_string",
]


import unicodedata
from typing import Protocol, Union


class PathLike(Protocol):
    def __fspath__(self) -> str:
        ...


FileSystemPath = Union[str, PathLike]


def normalize_string(string: str) -> str:
    return unicodedata.normalize("NFKD", string).strip()
