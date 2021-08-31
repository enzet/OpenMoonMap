"""
Open Moon Map entry point.
"""
from pathlib import Path

from src.harvest import harvest
from src.parser import parse

if __name__ == "__main__":
    cache: Path = Path("cache")
    cache.mkdir(parents=True, exist_ok=True)
    for name in ["object", "volcano"]:
        output_path: Path = cache / f"{name}.json"
        if not output_path.exists():
            harvest(Path(f"data/query/{name}.sparql"), output_path)
    parse(cache, Path("moon.osm"))
