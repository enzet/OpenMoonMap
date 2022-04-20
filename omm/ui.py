"""
Argument parsing.
"""
import argparse

from omm.wikidata import MOON

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser()

    parser.add_argument(
        "-b",
        "--body",
        metavar="<integer>",
        help=f"astronomical body Wikidata id without Q (e.g. {MOON} for Moon)",
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
