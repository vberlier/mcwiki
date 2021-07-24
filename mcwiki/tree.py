__all__ = [
    "Tree",
    "TreeEntry",
    "TreeNode",
    "TreeExtractor",
]


import re
import textwrap
from dataclasses import dataclass, field
from typing import (
    Dict,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

from bs4 import Tag

from .extractor import Extractor
from .page import load
from .utils import normalize_string

TreeNodeType = TypeVar("TreeNodeType", int, "TreeNode")
TreeEntry = Union[Tuple[str, TreeNodeType], Tuple[None, str]]


class Tree(NamedTuple):
    extractor: "TreeExtractor"
    entries: Tuple[TreeEntry[int], ...]

    @property
    def children(self) -> Iterator[Tuple[str, "TreeNode"]]:
        for key, ref in self.entries:
            if isinstance(ref, str):
                if not (tree := self.extractor.templates.get(ref)):
                    tree = self.extractor.process(load(ref).html.li.ul)
                    self.extractor.templates[ref] = tree
                yield from tree.children
            elif key is not None:
                yield key, self.extractor.nodes[ref]

    def as_dict(self) -> Dict[str, "TreeNode"]:
        return dict(self.children)

    def format(
        self,
        prefix: str = "",
        parents: Optional[Set["Tree"]] = None,
    ) -> Iterator[str]:
        parents = parents or set()

        if self in parents:
            yield f"{prefix}└─ <...>"
            return

        children = list(self.children)
        if not parents and len(children) == 1:
            indents = [""]
        else:
            indents = ["├─ "] * (len(children) - 1) + ["└─ "]

        for indent, (name, node) in zip(indents, children):
            icons = ", ".join(node.icons)

            if not name:
                name, icons = f"[{icons}]", ""
            if name:
                yield prefix + indent + name

            indent = "│  " if indent == "├─ " else " " * len(indent)

            if icons:
                yield prefix + indent + f"[{icons}]"

            yield from [prefix + indent + line for line in textwrap.wrap(node.text)]

            yield from node.content.format(prefix + indent, parents | {self})

    def __str__(self):
        return "\n".join(self.format())


class TreeNode(NamedTuple):
    text: str
    icons: Tuple[str, ...]
    content: Tree


@dataclass(frozen=True, eq=False)
class TreeExtractor(Extractor[Tree]):
    selector: str = ".treeview > ul"

    nodes: List[TreeNode] = field(default_factory=list, repr=False)
    references: Dict[TreeNode, int] = field(default_factory=dict, repr=False)
    templates: Dict[str, Tree] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        if not self.nodes:
            self.nodes.append(TreeNode("", (), Tree(self, ())))

    def process(self, element: Tag) -> Tree:
        nodes: Dict[str, TreeNode] = {}
        inherit: Dict[None, str] = {}

        for key, node in self.collect_children(element):
            if isinstance(node, str):
                inherit[None] = node
                continue
            if not isinstance(key, str):
                continue
            if previous := nodes.get(key):
                node = TreeNode(
                    f"{previous.text} {node.text}".strip(),
                    previous.icons + node.icons,
                    Tree(self, previous.content.entries + node.content.entries),
                )
            nodes[key] = node

        entries: Dict[str, int] = {}

        for key, node in nodes.items():
            if not (ref := self.references.get(node)):
                node = nodes[key]
                ref = len(self.nodes)
                self.nodes.append(node)
                self.references[node] = ref
            entries[key] = ref

        return Tree(self, tuple(entries.items()) + tuple(inherit.items()))

    def collect_children(self, element: Tag) -> Iterator[TreeEntry[TreeNode]]:
        for list_item in element.children:
            if not list_item.name:
                continue

            if "nbttree-inherited" in list_item.get("class", ""):
                yield None, list_item.get("data-page")
                continue

            text = ""
            icons: List[str] = []
            children: List[TreeEntry[int]] = []

            for child in list_item.children:
                if not child.name:
                    text += child
                elif child.span and "sprite" in child.span.get("class", ""):
                    icons.append(child["title"])
                elif child.name == "ul" or child.ul and (child := child.ul):
                    children.extend(self.process(child).entries)
                else:
                    text += child.text

            name, text = map(
                normalize_string, re.split(r":\s| - |$", text + " ", maxsplit=1)
            )

            if name or icons or children:
                if not text and " " in name and name[0] not in "<([{":
                    name, text = text, name
                yield name, TreeNode(
                    text,
                    tuple(icons),
                    Tree(self, tuple(children)),
                )

    def __hash__(self):
        return hash(id(self))
