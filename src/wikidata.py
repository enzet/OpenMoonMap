"""
Wikidata-specific data.
"""
import logging
import urllib3

VOLCANO: int = 8072
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


def wikidata_item_to_osm_tags(wikidata_id: int) -> dict[str, str]:
    """Convert Wikidata item into OpenStreetMap tags dictionary."""
    if wikidata_id == VOLCANO:
        return {"natural": "volcano"}
    if wikidata_id in [CRATER, SATELLITE_CRATER, LUNAR_CRATER, IMPACT_CRATER]:
        return {"natural": "crater"}
    if wikidata_id == MONS:
        return {"natural": "peak"}
    if wikidata_id == MONUMENT:
        return {"historic": "monument"}
    if wikidata_id == SCULPTURE:
        return {"tourism": "artwork", "artwork_type": "sculpture"}
    return {}


def request_sparql(query: str) -> bytes:
    """
    Request Wikidata with SPARQL query.  See
    https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service

    :param query: SPARQL query
    """
    http = urllib3.PoolManager()
    return http.request(
        "GET",
        "https://query.wikidata.org/sparql",
        {"format": "json", "query": query},
    ).data
