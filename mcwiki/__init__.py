from .extractor import *
from .page import *
from .text import *
from .tree import *

__version__ = "0.1.2"


PARAGRAPH = TextExtractor("p")
CODE = TextExtractor("code")
CODE_BLOCK = TextExtractor("pre")
TREE = TreeExtractor()
