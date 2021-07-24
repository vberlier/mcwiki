from pathlib import Path

import pytest
import requests


@pytest.fixture
def wiki_pages(request: pytest.FixtureRequest):
    directory = Path(request.config.cache.makedir("wiki_pages"))  # type: ignore
    directory.mkdir(exist_ok=True)

    download = {
        "data_pack.html": "https://minecraft.fandom.com/wiki/Data_Pack",
        "advancement.html": "https://minecraft.fandom.com/wiki/Advancement/JSON_format",
        "loot_table.html": "https://minecraft.fandom.com/wiki/Loot_table",
        "predicate.html": "https://minecraft.fandom.com/wiki/Predicate",
        "tag.html": "https://minecraft.fandom.com/wiki/Tag",
        "item_modifier.html": "https://minecraft.fandom.com/wiki/Item_modifier",
    }

    for filename, url in download.items():
        if not (path := directory / filename).is_file():
            path.write_text(requests.get(url).text)

    return directory
