"""
Parse Wikidata SPARQL query result.
"""
import json
import re
from pathlib import Path

from src.wikidata import wikidata_item_to_osm_tags

MAX_LATITUDE: float = 85.0

ITEM_PATTERN: re.Pattern = re.compile(
    "http://www.wikidata.org/entity/Q(?P<id>.*)"
)
GEO_PATTERN: re.Pattern = re.compile(
    "<http://www.wikidata.org/entity/Q(?P<id>.*)> "
    "Point\\((?P<latitude>.*) (?P<longitude>.*)\\)"
)


def parse(input_path: Path, output_path: Path) -> None:
    """Parse Wikidata SPARQL query result."""
    with (input_path / "object.json").open() as input_file:
        object_data: dict = json.load(input_file)["results"]["bindings"]
    with (input_path / "volcano.json").open() as input_file:
        volcano_data: dict[int, float] = {}
        for record in json.load(input_file)["results"]["bindings"]:
            item: re.Match = ITEM_PATTERN.match(record["item"]["value"])
            volcano_data[int(item.group("id"))] = float(
                record["diameter"]["value"]
            ) * 1000

    with output_path.open("w+") as output_file:
        output_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output_file.write('<osm version="0.6">\n')
        output_file.write(
            ' <bounds minlat="-85.0000000" minlon="-180.0000000" '
            'maxlat="85.0000000" maxlon="180.0000000"/>\n'
        )
        for id_, record in enumerate(object_data):
            item: re.Match = ITEM_PATTERN.match(record["item"]["value"])
            type_: re.Match = ITEM_PATTERN.match(record["type"]["value"])
            geo: re.Match = GEO_PATTERN.match(record["geo"]["value"])
            wikidata_id: int = int(item.group("id"))
            latitude: float = float(geo.group("latitude"))
            if not (-MAX_LATITUDE <= latitude <= MAX_LATITUDE):
                continue
            output_file.write(
                f' <node id="{id_ + 1}" '
                f'lat="{latitude}" lon="{geo.group("longitude")}">\n'
            )
            tags: dict[str, str] = {
                "wikidata": f'Q{wikidata_id}',
                "name": record["itemLabel"]["value"],
                "name:en": record["itemLabel"]["value"],
            }
            tags |= wikidata_item_to_osm_tags(int(type_.group("id")))
            if wikidata_id in volcano_data:
                tags["diameter"] = str(volcano_data[wikidata_id])

            for key, value in tags.items():
                output_file.write(
                    f'  <tag k="{key}" v="{value}"/>\n'
                )
            output_file.write(" </node>\n")
        with Path("work/spacecraft.osm").open() as osm_file:
            output_file.write(osm_file.read())
        output_file.write("</osm>\n")