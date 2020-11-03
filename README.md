# mcwiki

[![Build Status](https://travis-ci.com/vberlier/mcwiki.svg?branch=main)](https://travis-ci.com/vberlier/mcwiki)
[![PyPI](https://img.shields.io/pypi/v/mcwiki.svg)](https://pypi.org/project/mcwiki/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mcwiki.svg)](https://pypi.org/project/mcwiki/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

> A scraping library for the [Minecraft Wiki](https://minecraft.gamepedia.com/Minecraft_Wiki).

```python
import mcwiki

page = mcwiki.load("Data Pack")
print(page["pack.mcmeta"].extract(mcwiki.TREE))
```

```
[TAG_Compound]
The root object.
└─ pack
   [TAG_Compound]
   Holds the data pack information.
   ├─ description
   │  [TAG_String, TAG_List, TAG_Compound]
   │  A JSON text that appears when hovering over the data pack's name in
   │  the list given by the /datapack list command, or when viewing the pack
   │  in the Create World screen.
   └─ pack_format
      [TAG_Int]
      Pack version. If this number does not match the current required
      number, the data pack displays a warning and requires additional
      confirmation to load the pack. Requires 4 for 1.13–1.14.4, 5 for
      1.15–1.16.1 and 6 for 1.16.2–1.16.3.
```

## Introduction

The Minecraft Wiki is a well-maintained source of information but is a bit too organic to be used as anything more than a reference. This project tries its best to make it possible to locate and extract the information you're interested in and use it as a programmatic source of truth for developing Minecraft-related tooling.

### Features

- Easily navigate through page sections
- Extract paragraphs, code blocks and recursive tree-like hierarchies
- Create custom extractors or extend the provided ones

## Installation

The package can be installed with `pip`.

```bash
$ pip install mcwiki
```

## Getting Started

The `load` function allows you to load a page from the Minecraft Wiki. The page can be specified by providing a URL or simply the title of the page.

```python
mcwiki.load("https://minecraft.gamepedia.com/Data_Pack")
mcwiki.load("Data Pack")
```

You can use the `load_file` function to read from a page downloaded locally or the `from_markup` function if you already have the html loaded in a string.

```python
mcwiki.load_file("Data_Pack.html")
mcwiki.from_markup("<!DOCTYPE html>\n<html ...")
```

Page sections can then be manipulated like dictionaries. Keys are case-insensitive and are associated to subsections.

```python
page = mcwiki.load("https://minecraft.gamepedia.com/Advancement/JSON_format")

print(page["List of triggers"])
```

```
<PageSection ['minecraft:bee_nest_destroyed', 'minecraft:bred_animals', ...]>
```

## Extracting Data

There are 3 built-in extractors. Extractors are instantiated with a CSS selector and define a `process` method that produces an item for each element returned by the selector.

| Extractor    | Type                   | Extracted Item                                            |
| ------------ | ---------------------- | --------------------------------------------------------- |
| `PARAGRAPH`  | `TextExtractor("p")`   | String containing the text content of a paragraph         |
| `CODE_BLOCK` | `TextExtractor("pre")` | String containing the text content of a code block        |
| `TREE`       | `TreeExtractor()`      | An instance of `mcwiki.Tree` containing the treeview data |

Page sections can invoke extractors by using the `extract` and `extract_all` methods. The `extract` method will return the first item in the page section or `None` if the extractor couldn't extract anything.

```python
print(page.extract(mcwiki.PARAGRAPH))
```

```
Custom advancements in data packs of a Minecraft world store the advancement data for that world as separate JSON files.
```

You can use the `index` argument to specify which paragraph to extract.

```python
print(page.extract(mcwiki.PARAGRAPH, index=1))
```

```
All advancement JSON files are structured according to the following format:
```

The `extract_all` method will return a lazy sequence-like container of all the items the extractor could extract from the page section.

```python
for paragraph in page.extract_all(mcwiki.PARAGRAPH):
    print(paragraph)
```

You can use the `limit` argument or slice the returned sequence to limit the number of extracted items.

```python
# Both yield exactly the same list
paragraphs = page.extract_all(mcwiki.PARAGRAPH)[:10]
paragraphs = list(page.extract_all(mcwiki.PARAGRAPH, limit=10))
```

## Tree Structures

The `TREE` extractor returns recursive tree-like hierarchies. You can use the `children` property to iterate through the direct children of a tree.

```python
def print_nodes(tree: mcwiki.Tree):
    for key, node in tree.children:
        print(key, node.text, node.icons)
        print_nodes(node.content)

print_nodes(section.extract(mcwiki.TREE))
```

Folded entries are automatically fetched, inlined, and cached. This means that iterating over the `children` property can yield a node that's already been visited so make sure to handle infinite recursions where appropriate.

Tree nodes have 3 attributes that can all be empty:

- The `text` attribute holds the text content of the node
- The `icons` attribute is a tuple that stores the names of the icons associated to the node
- The `content` attribute is a tree containing the children of the node

You can transform the tree into a shallow dictionary with the `as_dict` method.

```python
# Both yield exactly the same dictionary
nodes = tree.as_dict()
nodes = dict(tree.children)
```

## Contributing

Contributions are welcome. Make sure to first open an issue discussing the problem or the new feature before creating a pull request. The project uses [`poetry`](https://python-poetry.org).

```bash
$ poetry install
```

You can run the tests with `poetry run pytest`.

```bash
$ poetry run pytest
```

The project must type-check with [`mypy`](http://mypy-lang.org) and [`pylint`](https://www.pylint.org) shouldn't report any error.

```bash
$ poetry run mypy
$ poetry run pylint mcwiki tests
```

The code follows the [`black`](https://github.com/psf/black) code style. Import statements are sorted with [`isort`](https://pycqa.github.io/isort/).

```bash
$ poetry run isort mcwiki tests
$ poetry run black mcwiki tests
$ poetry run black --check mcwiki tests
```

---

License - [MIT](https://github.com/vberlier/mcwiki/blob/master/LICENSE)
