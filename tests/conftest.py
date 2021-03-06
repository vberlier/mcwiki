from pathlib import Path

import pytest
import requests


@pytest.fixture
def wiki_pages(request):
    directory = Path(request.config.cache.makedir("wiki_pages"))
    directory.mkdir(exist_ok=True)

    download = {
        "data_pack.html": "https://minecraft.gamepedia.com/Data_Pack",
        "advancement.html": "https://minecraft.gamepedia.com/Advancement/JSON_format",
        "loot_table.html": "https://minecraft.gamepedia.com/Loot_table",
        "predicate.html": "https://minecraft.gamepedia.com/Predicate",
        "tag.html": "https://minecraft.gamepedia.com/Tag",
    }

    for filename, url in download.items():
        if not (path := directory / filename).is_file():
            path.write_text(requests.get(url).text)

    return directory
