"""
Parse Wikidata SPARQL query result.
"""
import json
import logging
import re
from pathlib import Path
from typing import Callable

import numpy as np
from roentgen.osm_reader import OSMNode

from wikidata import (
    CRATER,
    DIAMETER,
    WikidataItem,
    get_object_property_query,
    get_object_query,
    get_wikidata_item,
    request_sparql,
    wikidata_item_to_osm_tags,
)

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

MAX_LATITUDE: float = 80.0
MAX_LONGITUDE: float = 180.0

ITEM_PATTERN: re.Pattern = re.compile(
    "http://www.wikidata.org/entity/Q(?P<id>.*)"
)
GEO_PATTERN: re.Pattern = re.compile(
    "<http://www.wikidata.org/entity/Q(?P<id>.*)> "
    "Point\\((?P<longitude>.*) (?P<latitude>.*)\\)"
)


def get_data(cache_path: Path, function: Callable, argument: str) -> bytes:
    """
    Get some data from the cache if cache file exists, otherwise get it using
    function and store it to the cache.
    """
    if cache_path.exists():
        with cache_path.open("rb") as input_file:
            return input_file.read()
    logging.info(f"Request {cache_path}.")
    data: bytes = function(argument)
    with cache_path.open("wb") as output_file:
        output_file.write(data)
    return data


def main(
    cache_path: Path,
    body_wikidata_id: int,
    output_path: Path,
    extra: list[Path],
) -> None:
    """
    Parse Wikidata SPARQL query result and construct OSM XML file.

    :param cache_path: path to storage for query results
    :param body_wikidata_id: astronomical body Wikidata identifier
    :param output_path: path to output OSM XML file
    :param extra: list of paths to extra files
    """
    _: WikidataItem = WikidataItem(
        body_wikidata_id,
        json.loads(
            get_data(
                cache_path / f"{body_wikidata_id}.json",
                get_wikidata_item,
                str(body_wikidata_id),
            ).decode()
        ),
    )

    object_data: dict = json.loads(
        get_data(
            cache_path / f"{body_wikidata_id}_object.json",
            request_sparql,
            get_object_query(body_wikidata_id),
        ).decode()
    )["results"]["bindings"]

    volcano_data: dict[int, float] = {}
    for record in json.loads(
        get_data(
            cache_path / f"{body_wikidata_id}_crater.json",
            request_sparql,
            get_object_property_query(
                body_wikidata_id, CRATER, DIAMETER, "diameter"
            ),
        ).decode()
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

    for extra_path in extra:
        with extra_path.open() as jsom_file:
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
