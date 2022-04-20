"""
Open Moon Map entry point.
"""
import argparse
import logging
import sys
from pathlib import Path

from omm.osm_xml import main as osm_main
from omm.ui import parse_arguments

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def main() -> None:
    """Run main OpenMoonMap workflow."""

    logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
    (cache := Path("cache")).mkdir(parents=True, exist_ok=True)
    arguments: argparse.Namespace = parse_arguments(sys.argv[1:])

    osm_main(
        cache,
        arguments.body,
        Path(arguments.output),
        map(Path, arguments.extra) if arguments.extra else [],
    )


if __name__ == "__main__":
    main()
