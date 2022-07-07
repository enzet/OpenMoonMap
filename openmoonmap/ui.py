"""
Argument parsing.
"""
import argparse

from openmoonmap.wikidata import Item

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    """Parse copenmoonmapand-line arguments."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    parser.add_argument(
        "-b",
        "--body",
        metavar="<integer>",
        help=f"astronomical body Wikidata id without Q (e.g. {Item.MOON} for Moon)",
        type=int,
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="<path>",
        help="output OSM XML file path",
    )
    parser.add_argument(
        "-e",
        "--extra",
        metavar="<path>",
        help="extra JSON data with node description",
        nargs="*",
    )
    return parser.parse_args(arguments)
