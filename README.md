Open Moon Map
=============

Small research project on using OpenStreetMap XML format to create open map of
Moon and displaying this data with
[Map Machine](https://github.com/enzet/map-machine).

Idea from
[Mapping the Moon](https://wiki.openstreetmap.org/wiki/Mapping_the_Moon) wiki
page.

Install
-------

**Requirements**: Python 3.9.

```bash
pip install -r requirements.txt
pip install git+https://github.com/enzet/map-machine
pip install .
```

Get your own open Moon map
--------------------------

![Preview](doc/moon.png)

### Construct OSM XML file ###

Run

```bash
openmoonmap --body 405 --output moon.osm
```

to request objects on the surface of the Moon (Wikidata id
[Q405](https://www.wikidata.org/wiki/Q405)) Wikidata through SPARQL, and parse
results into OSM XML file `moon.osm`.

### Draw map with Map Machine ###

Using Map Machine one can draw SVG map `moon.svg`:

```bash
map-machine render \
    --input moon.osm \
    --output moon.svg \
    --zoom 2
```

or construct tiles for interactive map and run it:

1. Draw tiles for zoom levels 0—4: `map-machine tile -i moon.osm -z 0-4`.
2. Run Map Machine tile server: `map-machine server`.
3. Open `data/leaflet.html` in browser.

Process other astronomical bodies
---------------------------------

The same process can be done for other astronomical bodies.  To do so one
should know its Wikidata identifier.

Example for Mars (Wikidata id [Q111](https://www.wikidata.org/wiki/Q111)):

```bash
openmoonmap --body 111 --output mars.osm
```

OSM XML file extension
----------------------

Resulting OSM XML file has additional XML element `object` with `equator`
attribute, that contains object's equator length in meters.
