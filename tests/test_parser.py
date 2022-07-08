import re

from openmoonmap.osm_xml import GEO_PATTERN, ITEM_PATTERN

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_item_pattern() -> None:
    """Test Wikidata pattern."""
    item_matcher: re.Match = ITEM_PATTERN.match(
        "http://www.wikidata.org/entity/Q630162"
    )
    assert item_matcher.group("id") == "630162"


def test_geo_pattern() -> None:
    """Test geographical coordinates Wikidata value."""
    geo_matcher: re.Match = GEO_PATTERN.match(
        "<http://www.wikidata.org/entity/Q405> Point(176.5 7.0)"
    )
    assert geo_matcher.group("longitude") == "176.5"
    assert geo_matcher.group("latitude") == "7.0"
