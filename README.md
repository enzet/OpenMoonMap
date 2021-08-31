Open Moon Map
=============

Small research project on using OpenStreetMap XML format to create open map of
Moon and displaying this data with [Röntgen](https://github.com/enzet/Roentgen).

Idea from
[Mapping the Moon](https://wiki.openstreetmap.org/wiki/Mapping_the_Moon) wiki
page.

Install
-------

**Requirements**: Python 3.9.

```bash
pip install -r requirements
```

Get your own open Moon map
--------------------------

Request Wikidata through SPARQL and parse results:

```bash
python main.py
```

OSM XML file will be written into `moon.osm` file.

### Draw SVG map ###

```bash
roentgen render \
    --input moon.osm \
    --output moon.svg \
    --zoom-level 2
```

or

### Run tile server ###

1. Draw tiles for zoom levels 0—4: `roentgen tile -i moon.osm -z 0-4`.
2. Run Röntgen tile server: `roentgen server`.
3. Open `data/leaflet.html` in browser.