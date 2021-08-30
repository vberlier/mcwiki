__all__ = [
    "normalize_string",
]


import unicodedata


def normalize_string(string: str) -> str:
    return unicodedata.normalize("NFKD", string).strip()
