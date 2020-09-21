from .extractor import *
from .page import *
from .text import *
from .tree import *


__version__ = "0.0.0"


ELEMENT = TextExtractor()
PARAGRAPH = TextExtractor(selector="p")
CODE_BLOCK = TextExtractor(selector="pre")
TREE = TreeExtractor()
