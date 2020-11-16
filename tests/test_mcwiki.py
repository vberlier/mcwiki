import json
from pathlib import Path

from pytest_insta import SnapshotFixture

import mcwiki


def test_case_insensitive_headings(wiki_pages: Path):
    page = mcwiki.load_file(wiki_pages / "data_pack.html")
    assert page["folder structure"] is page["FoLdEr STRUcture"]


def test_data_pack_headings(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "data_pack.html")
    assert snapshot("json") == list(page)


def test_data_pack_folder_structure(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "data_pack.html")
    assert snapshot() == str(page["folder structure"].extract(mcwiki.TREE))


def test_data_pack_mcmeta(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "data_pack.html")
    assert snapshot() == str(page["pack.mcmeta"].extract(mcwiki.TREE))


def test_advancement_headings(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "advancement.html")
    assert snapshot("json") == list(page["list of triggers"])


def test_advancement_file_format(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "advancement.html")
    assert snapshot() == str(page["file format"].extract(mcwiki.TREE))


def test_advancement_entity_killed_player(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "advancement.html")
    assert snapshot() == str(
        page["minecraft:entity_killed_player"].extract(mcwiki.TREE)
    )


def test_advancement_item_used_on_block(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "advancement.html")
    example = page["minecraft:item_used_on_block"].extract(mcwiki.CODE_BLOCK)
    assert example
    assert snapshot("json") == json.loads(example)


def test_advancement_slept_in_bed(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "advancement.html")
    assert snapshot() == str(page["minecraft:slept_in_bed"].extract(mcwiki.PARAGRAPH))


def test_loot_table_tags(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "loot_table.html")
    assert snapshot() == str(page["tags"].extract(mcwiki.TREE))


def test_loot_table_functions(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "loot_table.html")
    section = page["functions"]
    assert snapshot() == str(section.extract(mcwiki.TREE))
    assert snapshot() == str(section.extract(mcwiki.TREE, index=1))


def test_predicate(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "predicate.html")
    assert snapshot() == str(page.extract(mcwiki.TREE))
    assert snapshot() == str(page.extract(mcwiki.TREE, index=1))


def test_data_pack_tag(wiki_pages: Path, snapshot: SnapshotFixture):
    page = mcwiki.load_file(wiki_pages / "tag.html")
    assert snapshot() == str(page["JSON format"].extract(mcwiki.TREE))
