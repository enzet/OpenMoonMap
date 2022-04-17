"""
Open Moon Map entry point.
"""
import argparse
import logging
import sys
from pathlib import Path

from omm.osm_xml import main as osm_main
from omm.ui import parse_arguments


def main() -> None:
    logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
    cache: Path = Path("cache")
    cache.mkdir(parents=True, exist_ok=True)
    arguments: argparse.Namespace = parse_arguments(sys.argv[1:])
    osm_main(
        cache,
        arguments.body,
        Path(arguments.output),
        map(Path, arguments.extra) if arguments.extra else [],
    )


if __name__ == "__main__":
    main()
