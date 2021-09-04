"""
Open Moon Map entry point.
"""
import argparse
import logging
import sys
from pathlib import Path

from osm_xml import main
from ui import parse_arguments


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
    cache: Path = Path("cache")
    cache.mkdir(parents=True, exist_ok=True)
    arguments: argparse.Namespace = parse_arguments(sys.argv[1:])
    main(
        cache,
        arguments.body,
        Path(arguments.output),
        map(Path, arguments.extra) if arguments.extra else [],
    )
