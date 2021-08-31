import re

from src.parser import GEO_PATTERN, ITEM_PATTERN


def test() -> None:
    """Test patterns."""
    item_matcher: re.Match = ITEM_PATTERN.match(
        "http://www.wikidata.org/entity/Q630162"
    )
    assert item_matcher.group("id") == "630162"

    geo_matcher: re.Match = GEO_PATTERN.match(
        "<http://www.wikidata.org/entity/Q405> Point(176.5 7.0)"
    )
    assert geo_matcher.group("latitude") == "176.5"
    assert geo_matcher.group("longitude") == "7.0"
