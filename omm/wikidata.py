"""
Wikidata-specific data.
"""
import urllib3

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

MARS: int = 111
MOON: int = 405
VOLCANO: int = 8072
MOUNTAIN: int = 8502
EQUATOR: int = 23538
IMPACT_CRATER: int = 55818
METEORITE: int = 60186
GEOGRAPHIC_REGION: int = 82794
LUNAR_MARE: int = 180874
LANDFORM: int = 271669
MONS: int = 429088
WRINKLE_RIDGE: int = 667575
SCULPTURE: int = 860861
PALUS: int = 948516
ALBEDO: int = 1051581
LUNAR_CRATER: int = 1348589
RILLE: int = 1432092
VALLIS: int = 2249285
LAUNCH_LANDING_SITE: int = 2333223
LUNAR_CIRCUS: int = 2542653
LACUS: int = 3215913
CRATER: int = 3240715
OCEANUS: int = 3880745
PROMONTORIUM: int = 3922925
SINUS: int = 3961951
MONUMENT: int = 4989906
LUNAR_IMPACT: int = 16643332
SATELLITE_CRATER: int = 101142982

INSTANCE_OF: int = 31
SUBCLASS_OF: int = 279
LOCATED_ON_ASTRONOMICAL_BODY: int = 376
APPLIES_TO_PART: int = 518
COORDINATE_LOCATION: int = 625
RADIUS: int = 2120
DIAMETER: int = 2386


def wikidata_item_to_osm_tags(wikidata_id: int) -> dict[str, str]:
    """Convert Wikidata item into OpenStreetMap tags dictionary."""
    if wikidata_id == VOLCANO:
        return {"natural": "volcano"}
    if wikidata_id in [CRATER, SATELLITE_CRATER, LUNAR_CRATER, IMPACT_CRATER]:
        return {"natural": "crater"}
    if wikidata_id in [MOUNTAIN, MONS]:
        return {"natural": "peak"}
    if wikidata_id == MONUMENT:
        return {"historic": "monument"}
    if wikidata_id == SCULPTURE:
        return {"tourism": "artwork", "artwork_type": "sculpture"}
    return {}


class WikidataItem:
    def __init__(self, wikidata_id: int, data: dict) -> None:
        self.data: dict = data["entities"][f"Q{wikidata_id}"]

    def get_label(self, language: str = "en") -> str:
        return self.data["labels"][language]["value"]

    def get_equator_radius(self) -> float:
        radius: float = 0
        for radius_structure in self.data["claims"][f"P{RADIUS}"]:
            if (
                radius_structure["qualifiers"][f"P{APPLIES_TO_PART}"][0][
                    "datavalue"
                ]["value"]["numeric-id"]
                == EQUATOR
            ):
                radius = (
                    float(
                        radius_structure["mainsnak"]["datavalue"]["value"][
                            "amount"
                        ]
                    )
                    * 1000.0
                )
                break
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
    return f"""SELECT ?item ?geo ?type ?itemLabel
WHERE {{
    ?item wdt:P{LOCATED_ON_ASTRONOMICAL_BODY}
              wd:Q{astronomical_object_wikidata_id};
          wdt:P{COORDINATE_LOCATION} ?geo;
          wdt:P{INSTANCE_OF} ?type.
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}"""


def get_object_property_query(
    astronomical_object_wikidata_id: int,
    should_be_instance_of: int,
    property_wikidata_id: int,
    property_field: str,
) -> str:
    """
    Get some property of objects located on the specified astronomical body.
    """
    return f"""SELECT ?item ?{property_field}
WHERE {{
    ?item wdt:P{LOCATED_ON_ASTRONOMICAL_BODY}
              wd:Q{astronomical_object_wikidata_id};
          wdt:P{INSTANCE_OF}/wdt:P{SUBCLASS_OF}* wd:Q{should_be_instance_of};
          wdt:P{property_wikidata_id} ?{property_field};
          wdt:P{COORDINATE_LOCATION} ?geo.
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
