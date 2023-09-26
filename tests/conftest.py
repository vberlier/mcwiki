from pathlib import Path

import pytest
import requests


@pytest.fixture
def wiki_pages(request: pytest.FixtureRequest):
    directory = Path(request.config.cache.makedir("wiki_pages"))  # type: ignore
    directory.mkdir(exist_ok=True)

    download = {
        "data_pack.html": "https://minecraft.wiki/w/Data_Pack",
        "advancement.html": "https://minecraft.wiki/w/Advancement/JSON_format",
        "loot_table.html": "https://minecraft.wiki/w/Loot_table",
        "predicate.html": "https://minecraft.wiki/w/Predicate",
        "tag.html": "https://minecraft.wiki/w/Tag",
        "item_modifier.html": "https://minecraft.wiki/w/Item_modifier",
    }

    for filename, url in download.items():
        if not (path := directory / filename).is_file():
            path.write_text(requests.get(url).text)

    return directory
