import sys
from pathlib import Path

from src.wikidata import request_sparql


def harvest(request_path: Path, output_path: Path) -> None:
    with request_path.open() as request_file:
        with output_path.open("bw+") as output_file:
            output_file.write(request_sparql(request_file.read()))


if __name__ == "__main__":
    harvest(Path(sys.argv[1]), Path(sys.argv[2]))
