import re

from omm.osm_xml import GEO_PATTERN, ITEM_PATTERN


def test_item_pattern() -> None:
    """Test patterns."""
    item_matcher: re.Match = ITEM_PATTERN.match(
        "http://www.wikidata.org/entity/Q630162"
    )
    assert item_matcher.group("id") == "630162"


def test_geo_pattern() -> None:
    geo_matcher: re.Match = GEO_PATTERN.match(
        "<http://www.wikidata.org/entity/Q405> Point(176.5 7.0)"
    )
    assert geo_matcher.group("longitude") == "176.5"
    assert geo_matcher.group("latitude") == "7.0"
