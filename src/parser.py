"""
Parse Wikidata SPARQL query result.
"""
import json
import re
from pathlib import Path

import numpy as np
from roentgen.osm_reader import OSMNode

from src.wikidata import (
    CRATER,
    DIAMETER,
    get_object_property_query,
    get_object_query,
    request_sparql,
    wikidata_item_to_osm_tags,
)

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

MAX_LATITUDE: float = 85.0
MAX_LONGITUDE: float = 180.0

ITEM_PATTERN: re.Pattern = re.compile(
    "http://www.wikidata.org/entity/Q(?P<id>.*)"
)
GEO_PATTERN: re.Pattern = re.compile(
    "<http://www.wikidata.org/entity/Q(?P<id>.*)> "
    "Point\\((?P<longitude>.*) (?P<latitude>.*)\\)"
)


def request(cache_path: Path, query: str, name: str) -> dict:
    """
    Request data from Wikidata using SPARQL query.

    :param cache_path: path to storage for query results
    :param query: SPARQL query
    :param name: query identifier
    """
    cache_file_path: Path = cache_path / f"{name}.json"
    if cache_file_path.exists():
        with cache_file_path.open() as cache_file:
            return json.load(cache_file)
    data: bytes = request_sparql(query)
    with cache_file_path.open("wb") as cache_file:
        cache_file.write(data)
    return json.loads(data.decode())


def main(
    cache_path: Path, body_name: str, body_wikidata_id: int, output_path: Path
) -> None:
    """
    Parse Wikidata SPARQL query result and construct OSM XML file.

    :param cache_path: path to storage for query results
    :param body_name: astronomical body string identifier
    :param body_wikidata_id: astronomical body Wikidata identifier
    :param output_path: path to output OSM XML file
    """
    object_data: dict = request(
        cache_path, get_object_query(body_wikidata_id), f"{body_name}_object"
    )["results"]["bindings"]

    volcano_data: dict[int, float] = {}
    for record in request(
        cache_path,
        get_object_property_query(
            body_wikidata_id, CRATER, DIAMETER, "diameter"
        ),
        f"{body_name}_crater",
    )["results"]["bindings"]:
        item: re.Match = ITEM_PATTERN.match(record["item"]["value"])
        volcano_data[int(item.group("id"))] = (
            float(record["diameter"]["value"]) * 1000
        )

    # Set of processed Wikidata ids.
    processed: set[int] = set()

    nodes: list[OSMNode] = []
    id_: int = 1

    for record in object_data:
        item: re.Match = ITEM_PATTERN.match(record["item"]["value"])
        wikidata_id: int = int(item.group("id"))
        if wikidata_id in processed:
            continue

        geo: re.Match = GEO_PATTERN.match(record["geo"]["value"])
        latitude: float = float(geo.group("latitude"))
        if not (-MAX_LATITUDE <= latitude <= MAX_LATITUDE):
            continue
        longitude: float = float(geo.group("longitude"))
        if longitude > 180:
            longitude -= 360
        if not (-MAX_LONGITUDE <= longitude <= MAX_LONGITUDE):
            continue

        type_: re.Match = ITEM_PATTERN.match(record["type"]["value"])
        tags: dict[str, str] = {
            "wikidata": f"Q{wikidata_id}",
            "name": record["itemLabel"]["value"],
            "name:en": record["itemLabel"]["value"],
        }
        tags |= wikidata_item_to_osm_tags(int(type_.group("id")))
        if wikidata_id in volcano_data:
            tags["diameter"] = str(volcano_data[wikidata_id])

        nodes.append(OSMNode(tags, id_, np.array((latitude, longitude))))
        id_ += 1
        processed.add(wikidata_id)

    with Path("work/spacecraft.json").open() as jsom_file:
        for record in json.load(jsom_file):
            node: OSMNode = OSMNode(
                record["tags"],
                id_,
                np.array((record["lat"], record["lon"])),
            )
            nodes.append(node)
            id_ += 1

    with output_path.open("w+") as output_file:
        output_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output_file.write('<osm version="0.6">\n')
        output_file.write(
            f' <bounds minlat="-{MAX_LATITUDE}" minlon="-{MAX_LONGITUDE}" '
            f'maxlat="{MAX_LATITUDE}" maxlon="{MAX_LONGITUDE}"/>\n'
        )
        for id_, node in enumerate(nodes):
            node: OSMNode
            output_file.write(
                f' <node id="{node.id_}" '
                f'lat="{node.coordinates[0]}" lon="{node.coordinates[1]}">\n'
            )
            for key, value in node.tags.items():
                output_file.write(f'  <tag k="{key}" v="{value}"/>\n')
            output_file.write(" </node>\n")

        output_file.write("</osm>\n")
