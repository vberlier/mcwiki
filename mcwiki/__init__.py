from .extractor import *
from .page import *
from .text import *
from .tree import *

__version__ = "0.1.0"


PARAGRAPH = TextExtractor("p")
CODE_BLOCK = TextExtractor("pre")
TREE = TreeExtractor()
