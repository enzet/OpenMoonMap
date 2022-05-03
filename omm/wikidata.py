"""
Wikidata-specific data.
"""
from enum import Enum

import urllib3

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


class Item(Enum):
    MARS = 111
    MOON = 405
    VOLCANO = 8072
    MOUNTAIN = 8502
    EQUATOR = 23538
    IMPACT_CRATER = 55818
    METEORITE = 60186
    GEOGRAPHIC_REGION = 82794
    LUNAR_MARE = 180874
    LANDFORM = 271669
    MONS = 429088
    WRINKLE_RIDGE = 667575
    SCULPTURE = 860861
    PALUS = 948516
    ALBEDO = 1051581
    LUNAR_CRATER = 1348589
    RILLE = 1432092
    VALLIS = 2249285
    LAUNCH_LANDING_SITE = 2333223
    LUNAR_CIRCUS = 2542653
    LACUS = 3215913
    CRATER = 3240715
    OCEANUS = 3880745
    PROMONTORIUM = 3922925
    SINUS = 3961951
    MONUMENT = 4989906
    LUNAR_IMPACT = 16643332
    SATELLITE_CRATER = 101142982

    def __repr__(self):
        return f"Q{self.value}"

    def __str__(self):
        return f"Q{self.value}"


class Property(Enum):
    INSTANCE_OF = 31
    SUBCLASS_OF = 279
    LOCATED_ON_ASTRONOMICAL_BODY = 376
    APPLIES_TO_PART = 518
    COORDINATE_LOCATION = 625
    RADIUS = 2120
    DIAMETER = 2386

    def __repr__(self):
        return f"P{self.value}"

    def __str__(self):
        return f"P{self.value}"


def wikidata_item_to_osm_tags(wikidata_id: int) -> dict[str, str]:
    """Convert Wikidata item into OpenStreetMap tags dictionary."""

    if wikidata_id == Item.VOLCANO.value:
        return {"natural": "volcano"}
    if wikidata_id in [
        Item.CRATER.value,
        Item.SATELLITE_CRATER.value,
        Item.LUNAR_CRATER.value,
        Item.IMPACT_CRATER.value,
    ]:
        return {"natural": "crater"}
    if wikidata_id in [Item.MOUNTAIN.value, Item.MONS.value]:
        return {"natural": "peak"}
    if wikidata_id == Item.MONUMENT.value:
        return {"historic": "monument"}
    if wikidata_id == Item.SCULPTURE.value:
        return {"tourism": "artwork", "artwork_type": "sculpture"}
    return {}


class WikidataItem:
    """
    Wikidata item (elements starting with Q).
    """

    def __init__(self, wikidata_id: int, data: dict) -> None:
        self.data: dict = data["entities"][f"Q{wikidata_id}"]
        self.labels: dict = self.data["labels"]
        self.claims: dict = self.data["claims"]

    @staticmethod
    def get_float_value(claim: dict) -> float:
        """Parse float value from claim."""
        return float(claim["mainsnak"]["datavalue"]["value"]["amount"])

    def get_label(self, language: str = "en") -> str:
        """Get label of item."""
        return self.labels[language]["value"]

    def get_equator_radius(self) -> float:
        """
        Get equator radius or any radius if equator radius is not specified or
        0 otherwise.
        """
        if str(Property.RADIUS) not in self.claims:
            return 0

        radius: float = 0

        for radius_structure in self.claims[str(Property.RADIUS)]:
            radius: float = self.get_float_value(radius_structure) * 1000.0
            if (
                "qualifiers" in radius_structure
                and str(Property.APPLIES_TO_PART)
                in radius_structure["qualifiers"]
                and radius_structure["qualifiers"][
                    str(Property.APPLIES_TO_PART)
                ][0]["datavalue"]["value"]["numeric-id"]
                == Item.EQUATOR.value
            ):
                return radius

        return radius


def get_object_query(astronomical_object_wikidata_id: int) -> str:
    """
    Get a SPARQL query for every object that has coordinates and is located on
    the astronomical body with specified Wikidata id.

    Query response:
        item: object Wikidata id
        itemLabel: object English label
        geo: location coordinates on the astronomical body
        type: object type
    """
    return f"""\
SELECT ?item ?geo ?type ?itemLabel
WHERE {{
    ?item wdt:{Property.LOCATED_ON_ASTRONOMICAL_BODY}
              wd:Q{astronomical_object_wikidata_id};
          wdt:{Property.COORDINATE_LOCATION} ?geo;
          wdt:{Property.INSTANCE_OF} ?type.
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}"""


def get_object_property_query(
    astronomical_object_wikidata_id: int,
    should_be_instance_of: Item,
    property_wikidata_id: Property,
    property_field: str,
) -> str:
    """
    Get the specified property of all objects located on the astronomical body.
    """
    return f"""\
SELECT ?item ?{property_field}
WHERE {{
    ?item wdt:{Property.LOCATED_ON_ASTRONOMICAL_BODY}
              wd:Q{astronomical_object_wikidata_id};
          wdt:{Property.INSTANCE_OF}/wdt:{Property.SUBCLASS_OF}*
              wd:{should_be_instance_of};
          wdt:{property_wikidata_id} ?{property_field};
          wdt:{Property.COORDINATE_LOCATION} ?geo.
}}"""


def request_sparql(query: str) -> bytes:
    """
    Request Wikidata with SPARQL query.  See
    https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service

    :param query: SPARQL query
    """
    return urllib3.PoolManager().request(
        "GET",
        "https://query.wikidata.org/sparql",
        {"format": "json", "query": query},
    ).data  # fmt: skip


def get_wikidata_item(wikidata_id: str) -> bytes:
    """Get Wikidata item structure."""
    return urllib3.PoolManager().request(
        "GET",
        f"https://www.wikidata.org/wiki/Special:EntityData/Q{wikidata_id}.json",
    ).data  # fmt: skip
