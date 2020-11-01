__all__ = ["FileSystemPath", "normalize_string"]


import os
import unicodedata
from typing import Union

FileSystemPath = Union[str, os.PathLike]


def normalize_string(string: str) -> str:
    return unicodedata.normalize("NFKD", string).strip()
