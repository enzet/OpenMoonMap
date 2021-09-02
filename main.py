"""
Open Moon Map entry point.
"""
from pathlib import Path

from src.parser import main
from src.wikidata import MOON


if __name__ == "__main__":
    cache: Path = Path("cache")
    cache.mkdir(parents=True, exist_ok=True)
    main(cache, "moon", MOON, Path("moon.osm"))
