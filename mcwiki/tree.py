__all__ = ["Tree", "TreeEntry", "TreeNode", "TreeExtractor", "TreeExtractorState"]


import textwrap
from dataclasses import dataclass, field
from typing import TypeVar, NamedTuple, Tuple, Dict, List, Set, Iterator, Union

from bs4 import BeautifulSoup, Tag

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
                if not (tree := self.extractor.state.templates.get(ref)):
                    tree = self.extractor.extract(load(ref).html.li.ul)
                    self.extractor.state.templates[ref] = tree
                yield from tree.children
            elif key is not None:
                yield key, self.extractor.state.nodes[ref]

    def as_dict(self) -> Dict[str, "TreeNode"]:
        return dict(self.children)

    def format(self, prefix: str = "", parents: Set["Tree"] = None) -> Iterator[str]:
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


@dataclass(frozen=True)
class TreeExtractorState:
    nodes: List[TreeNode] = field(default_factory=list)
    references: Dict[TreeNode, int] = field(default_factory=dict)
    templates: Dict[str, Tree] = field(default_factory=dict)

    def __hash__(self):
        return hash(id(self))


@dataclass(frozen=True, repr=False)
class TreeExtractor(Extractor[Tree]):
    state: TreeExtractorState = field(default_factory=TreeExtractorState)

    def __post_init__(self):
        if not self.state.nodes:
            self.state.nodes.append(TreeNode("", (), Tree(self, ())))

    def extract_from_html(self, html: BeautifulSoup) -> Tree:
        if elements := html.select("div.treeview > ul", limit=self.nth):
            return self.extract(elements[-1])
        return Tree(self, ())

    def extract(self, element: Tag) -> Tree:
        nodes: Dict[str, TreeNode] = {}
        inherit: Dict[None, str] = {}

        for key, node in self.collect(element):
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
            if not (ref := self.state.references.get(node)):
                node = nodes[key]
                ref = len(self.state.nodes)
                self.state.nodes.append(node)
                self.state.references[node] = ref
            entries[key] = ref

        return Tree(self, tuple(entries.items()) + tuple(inherit.items()))

    def collect(self, element: Tag) -> Iterator[TreeEntry[TreeNode]]:
        for list_item in element.children:
            if not list_item.name:
                continue

            if "nbttree-inherited" in list_item.get("class", ""):
                yield None, list_item.span.a.text
                continue

            name = ""
            text = ""
            icons: List[str] = []
            children: List[TreeEntry[int]] = []

            for child in list_item.children:
                if not child.name:
                    text += child
                elif child.span and "sprite" in child.span.get("class", ""):
                    icons.append(child["title"])
                elif child.name == "ul" or child.ul and (child := child.ul):
                    children.extend(self.extract(child).entries)
                elif not name and child.name == "span":
                    name = child.text
                else:
                    text += child.text

            name, text = map(normalize_string, [name, text])

            if name or text or children:
                if not (name or icons):
                    name = text
                    text = ""
                yield name, TreeNode(
                    text,
                    tuple(icons),
                    Tree(self, tuple(children)),
                )
