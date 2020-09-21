__all__ = ["normalize_string"]


import re
import unicodedata


def normalize_string(string: str) -> str:
    return re.sub(r"^[\s:]+|\s+$", "", unicodedata.normalize("NFKD", string))
