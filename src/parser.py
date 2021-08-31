"""
Parse Wikidata SPARQL query result.
"""
import json
import re
import sys
from pathlib import Path

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
    with input_path.open() as input_file:
        query_result: list[dict[str, str]] = json.load(input_file)
    with output_path.open("w+") as output_file:
        output_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output_file.write('<osm version="0.6">\n')
        output_file.write(
            ' <bounds minlat="-85.0000000" minlon="-180.0000000" '
            'maxlat="85.0000000" maxlon="180.0000000"/>\n'
        )
        for id_, record in enumerate(query_result):
            item: re.Match = ITEM_PATTERN.match(record["item"])
            geo: re.Match = GEO_PATTERN.match(record["geo"])
            latitude: float = float(geo.group("latitude"))
            if not (-MAX_LATITUDE <= latitude <= MAX_LATITUDE):
                continue
            output_file.write(
                f' <node id="{id_ + 1}" '
                f'lat="{latitude}" lon="{geo.group("longitude")}">\n'
            )
            output_file.write(
                f'  <tag k="wikidata" v="Q{item.group("id")}"/>\n'
            )
            output_file.write(" </node>\n")
        output_file.write("</osm>\n")


if __name__ == "__main__":
    parse(Path(sys.argv[1]), Path(sys.argv[2]))
